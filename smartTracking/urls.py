# same as SmartTransportSystem > urls.py 
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('searchnearby_address/', views.searchnearby_address, name='searchnearby_address'),
    path('searchnearby_latlng/', views.searchnearby_latlng, name='searchnearby_latlng'),
    path('finddirection/', views.finddirection, name='finddirection'),
    path('findspecificbus/', views.findspecificbus, name='findspecificbus'),
    path('allbuses/', views.allbuses, name='allbuses'),
    path('crowd_report/', views.crowd_report, name='crowd_report'),
    path('auto_fare/', views.auto_fare, name='auto_fare'),
]
