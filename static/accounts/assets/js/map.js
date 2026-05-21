function initMap() {
  const directionsService = new google.maps.DirectionsService();
  const directionsRenderer = new google.maps.DirectionsRenderer();

  const initLat = window.NAMMA_LAT || 12.9716;
  const initLng = window.NAMMA_LNG || 77.5946;

  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 15,
    center: { lat: initLat, lng: initLng },
  });

  // Expose map so the nearby-stop marker script can access it
  window._nammaMap = map;

  directionsRenderer.setMap(map);

  // Blue pulsing dot — user's current position
  new google.maps.Marker({
    position: { lat: initLat, lng: initLng },
    map: map,
    title: "Your location",
    icon: {
      path: google.maps.SymbolPath.CIRCLE,
      scale: 10,
      fillColor: "#4285F4",
      fillOpacity: 1,
      strokeColor: "#ffffff",
      strokeWeight: 3,
    },
    zIndex: 10,
  });

  // Add bus-stop markers for each nearby stop injected by the Django view
  const stops = window.NAMMA_NEARBY_STOPS || [];
  const infoWindow = new google.maps.InfoWindow();
  stops.forEach(function (stop) {
    const marker = new google.maps.Marker({
      position: { lat: stop.lat, lng: stop.lng },
      map: map,
      title: stop.name,
      icon: {
        url: "https://maps.google.com/mapfiles/ms/icons/bus.png",
      },
    });
    marker.addListener("click", function () {
      infoWindow.setContent("<strong>" + (stop.short_name || stop.name) + "</strong>");
      infoWindow.open(map, marker);
    });
  });

  // Route directions when user picks a destination from the dropdown
  const onChangeHandler = function () {
    calculateAndDisplayRoute(directionsService, directionsRenderer);
  };
  document.getElementById("start").addEventListener("change", onChangeHandler);
  document.getElementById("end").addEventListener("change", onChangeHandler);
}

function calculateAndDisplayRoute(directionsService, directionsRenderer) {
  directionsService.route(
    {
      origin:      { query: document.getElementById("start").value },
      destination: { query: document.getElementById("end").value },
      travelMode: google.maps.TravelMode.DRIVING,
    },
    function (response, status) {
      if (status === "OK") {
        directionsRenderer.setDirections(response);
      } else {
        console.warn("Directions request failed: " + status);
      }
    }
  );
}
