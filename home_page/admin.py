from django.contrib import admin
from .models import BusInformation, Route, Map, Interchange, CrowdReport

admin.site.register(BusInformation)
admin.site.register(Route)
admin.site.register(Map)
admin.site.register(Interchange)
admin.site.register(CrowdReport)
