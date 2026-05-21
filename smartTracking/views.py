import re

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta

from backendCode.geocoding import reverse_geocoding, geocoding_from_address
from backendCode.nearbyplaces import search_nearby_places
from backendCode.findBusByDirection import find_distance
from backendCode.autofare import estimate_auto_fare
from backendCode.raincheck import get_rain_alert
from home_page.models import BusInformation, Interchange, CrowdReport
from decouple import config


def _maps_js_url():
    """Build the Google Maps JS API script URL."""
    key = config('KEY2')
    return f"https://maps.googleapis.com/maps/api/js?key={key}&callback=initMap&libraries=&v=weekly"


def _rain_context():
    """Return rain alert keys to merge into any view context."""
    is_heavy, affected = get_rain_alert()
    return {'rain_alert': is_heavy, 'flood_stops': affected}


def _pair_stops(route_list):
    """Convert a flat list of stops into (a, b) pairs for the timeline template."""
    pairs = []
    for i in range(0, len(route_list), 2):
        a = route_list[i]
        b = route_list[i + 1] if i + 1 < len(route_list) else None
        pairs.append((a, b))
    return pairs


def searchnearby_address(request):
    if request.method != 'POST':
        return redirect('home')
    location = request.POST.get('userlocationaddress', '')
    data = geocoding_from_address(location)
    nearby_list = search_nearby_places(data['lat'], data['lng'])
    data.update({'nearlist': nearby_list, 'text': _maps_js_url()})
    data.update(_rain_context())
    return render(request, 'smartTracking/searchnearby.html', data)


def searchnearby_latlng(request):
    if request.method != 'POST':
        return redirect('home')
    location = str(request.POST.get('userLocation', ''))
    if not location or ',' not in location:
        return redirect('home')
    parts = location.split(sep=',', maxsplit=1)
    if len(parts) != 2:
        return redirect('home')
    lat, lng = parts
    formatted_address = reverse_geocoding(location)
    nearby_list = search_nearby_places(lat=lat, lng=lng)
    data = {
        'formatted_address': formatted_address,
        'nearlist': nearby_list,
        'text': _maps_js_url(),
        'lat': lat,
        'lng': lng,
    }
    data.update(_rain_context())
    return render(request, 'smartTracking/searchnearby.html', data)


def _google_maps_url(stops):
    """Build a Google Maps directions URL from a list of stop names."""
    encoded = [s.strip().replace(' ', '+') + ',+Bengaluru' for s in stops]
    return 'https://www.google.com/maps/dir/' + '/'.join(encoded)


def _build_bus_segment(bus, start, end):
    """Return (list_route, distance_km, duration_min, flat_stops) for the stop segment."""
    bus_raw_route = bus.route_id.routes.split(sep=',')
    start_index = end_index = None
    for i, stop in enumerate(bus_raw_route):
        if start.lower() == stop.strip().lower():
            start_index = i
        if end.lower() == stop.strip().lower():
            end_index = i
    if start_index is None or end_index is None:
        return None, None, None, None
    lo, hi = min(start_index, end_index), max(start_index, end_index)
    bus_route = bus_raw_route[lo:hi + 1]
    distance_km, duration_min = find_distance(list(bus_route))
    flat_stops = [s.strip() for s in bus_route]
    return _pair_stops(bus_route), distance_km, duration_min, flat_stops


def finddirection(request):
    if request.method != 'POST':
        return redirect('home')
    bus_list = []
    multihop_list = []
    start = str(request.POST.get('from', '')).strip()
    end = str(request.POST.get('to', '')).strip()
    try:
        # Crowd reports from the last 30 minutes — .values() avoids full model hydration
        recent_cutoff = timezone.now() - timedelta(minutes=30)
        recent_crowd = {}
        for r in (CrowdReport.objects
                  .filter(reported_at__gte=recent_cutoff)
                  .order_by('-reported_at')
                  .values('bus_id', 'status')):
            if r['bus_id'] not in recent_crowd:
                recent_crowd[r['bus_id']] = r['status']

        # Direct routes — icontains is safe; iregex with user input risks ReDoS
        buses = (BusInformation.objects
                 .select_related('route_id')
                 .filter(bus_viaroad__icontains=start)
                 .filter(bus_viaroad__icontains=end))
        for bus in buses:
            list_route, distance_km, duration_min, flat_stops = _build_bus_segment(bus, start, end)
            if list_route is None:
                continue
            bus_list.append({
                'bus_id': 'bus' + str(bus.bus_id),
                'bus_pk': bus.bus_id,
                'bus_name': bus.bus_name,
                'bus_route': list_route,
                'distance': distance_km,
                'duration_min': duration_min,
                'mode': bus.mode,
                'mode_display': bus.get_mode_display(),
                'crowd_status': recent_crowd.get(bus.bus_id),
                'map_url': _google_maps_url(flat_stops),
            })

        # Multi-hop via interchange stops
        for interchange in Interchange.objects.all():
            ix = interchange.stop_name
            leg_a_qs = (BusInformation.objects
                        .select_related('route_id')
                        .filter(bus_viaroad__icontains=start)
                        .filter(bus_viaroad__icontains=ix))
            leg_b_qs = (BusInformation.objects
                        .select_related('route_id')
                        .filter(bus_viaroad__icontains=ix)
                        .filter(bus_viaroad__icontains=end))
            if leg_a_qs.exists() and leg_b_qs.exists():
                bus_a, bus_b = leg_a_qs[0], leg_b_qs[0]
                if bus_a.mode != bus_b.mode:
                    multihop_list.append({
                        'interchange': ix,
                        'interchange_modes': interchange.modes_available,
                        'leg_a_name': bus_a.bus_name,
                        'leg_a_mode': bus_a.mode,
                        'leg_a_mode_display': bus_a.get_mode_display(),
                        'leg_b_name': bus_b.bus_name,
                        'leg_b_mode': bus_b.mode,
                        'leg_b_mode_display': bus_b.get_mode_display(),
                    })

        context = {
            'From': start,
            'To': end,
            'Number_of_bus': len(bus_list),
            'bus_list': bus_list,
            'multihop_list': multihop_list,
        }
        context.update(_rain_context())
        return render(request, 'smartTracking/finddirection.html', context)
    except Exception:
        context = {
            'check': 1,
            'From': start,
            'To': end,
            'Number_of_bus': 0,
            'bus_list': [],
            'multihop_list': [],
        }
        context.update(_rain_context())
        return render(request, 'smartTracking/finddirection.html', context)


@require_POST
def crowd_report(request):
    """AJAX endpoint — submit a crowd status for a bus."""
    bus_pk = request.POST.get('bus_id')
    status = request.POST.get('status')
    valid_statuses = {'EMPTY', 'MODERATE', 'FULL', 'OVERCROWDED'}
    if status not in valid_statuses:
        return JsonResponse({'ok': False, 'error': 'Invalid status'}, status=400)
    try:
        bus = BusInformation.objects.get(pk=bus_pk)
        CrowdReport.objects.create(bus=bus, status=status)
        return JsonResponse({'ok': True, 'status': status})
    except BusInformation.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Bus not found'}, status=404)


@require_POST
def auto_fare(request):
    """Compute auto-rickshaw fare estimate for a given distance (km)."""
    try:
        distance_km = float(request.POST.get('distance_km', 0))
        result = estimate_auto_fare(distance_km)
        return JsonResponse({'ok': True, **result})
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid distance'}, status=400)


def findspecificbus(request):
    if request.method != 'POST':
        return redirect('home')
    bus_name_from_user = str(request.POST.get('bus_name', '')).strip()
    try:
        qs = BusInformation.objects.select_related('route_id').filter(
            bus_name__icontains=bus_name_from_user
        )
        if not qs.exists():
            numeric_prefix = re.match(r'(\d+)', bus_name_from_user)
            if numeric_prefix:
                qs = BusInformation.objects.select_related('route_id').filter(
                    bus_name__icontains=numeric_prefix.group(1)
                )
        bus = qs[0]
        ssource_destination = str(bus.bus_sourcetodestination)
        if '-' in ssource_destination:
            start, end = ssource_destination.split(sep='-', maxsplit=1)
        else:
            start, end = ssource_destination, ssource_destination
        routes = bus.route_id.routes.split(sep=',')
        flat_stops = [s.strip() for s in routes]
        data = {
            'check': 0,
            'bus_id': bus.bus_id,
            'bus_name': bus.bus_name,
            'start': start,
            'end': end,
            'routes': _pair_stops(routes),
            'mode': bus.mode,
            'mode_display': bus.get_mode_display(),
            'map_url': _google_maps_url(flat_stops),
        }
        return render(request, 'smartTracking/findspecificbus.html', data)
    except Exception:
        return render(request, 'smartTracking/findspecificbus.html',
                      {'check': 1, 'error': bus_name_from_user})


def allbuses(request):
    buses_list = []
    for bus in BusInformation.objects.select_related('route_id').all():
        ssource_destination = str(bus.bus_sourcetodestination)
        if '-' in ssource_destination:
            start, end = ssource_destination.split(sep='-', maxsplit=1)
        else:
            start, end = ssource_destination, ssource_destination
        routes = bus.route_id.routes.split(sep=',')
        design = routes[0]
        for r in range(1, len(routes) - 1):
            design = design + '<->' + routes[r]
        buses_list.append({
            'bus_id': bus.bus_id,
            'bus_name': bus.bus_name,
            'start': start,
            'end': end,
            'routes': design,
            'mode': bus.mode,
            'mode_display': bus.get_mode_display(),
        })
    return render(request, 'smartTracking/allbuses.html', {'contex': buses_list})
