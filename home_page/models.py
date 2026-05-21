from django.db import models


class TransportMode(models.TextChoices):
    BUS = 'BUS', 'BMTC Bus'
    METRO = 'METRO', 'Namma Metro'
    RAIL = 'RAIL', 'Suburban Rail'
    AUTO = 'AUTO', 'Auto Rickshaw'


class Route(models.Model):
    route_id = models.AutoField(primary_key=True)
    routes = models.TextField()


class BusInformation(models.Model):
    bus_id = models.AutoField(primary_key=True)
    bus_name = models.CharField(max_length=255)
    bus_sourcetodestination = models.CharField(max_length=80)
    bus_viaroad = models.TextField()
    bus_type = models.CharField(max_length=15)
    mode = models.CharField(max_length=10, choices=TransportMode.choices, default=TransportMode.BUS)
    route_id = models.ForeignKey('Route', on_delete=models.CASCADE)


class Map(models.Model):
    map_id = models.AutoField(primary_key=True)
    bus_id = models.ForeignKey('BusInformation', on_delete=models.CASCADE)
    way_points = models.TextField()


class CrowdReport(models.Model):
    CROWD_CHOICES = [
        ('EMPTY', 'Empty'),
        ('MODERATE', 'Moderate'),
        ('FULL', 'Full'),
        ('OVERCROWDED', 'Overcrowded'),
    ]
    bus = models.ForeignKey('BusInformation', on_delete=models.CASCADE, related_name='crowd_reports')
    status = models.CharField(max_length=15, choices=CROWD_CHOICES)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = 'reported_at'

    def __str__(self):
        return f"{self.bus.bus_name} — {self.status}"


class Interchange(models.Model):
    """Bus stops / stations where two or more transport modes connect."""
    stop_name = models.CharField(max_length=255, unique=True)
    modes_available = models.CharField(max_length=100)  # comma-separated: BUS,METRO,RAIL
    metro_station_name = models.CharField(max_length=255, blank=True)
    rail_station_name = models.CharField(max_length=255, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    def modes_list(self):
        return [m.strip() for m in self.modes_available.split(',')]

    def __str__(self):
        return f"{self.stop_name} ({self.modes_available})"
