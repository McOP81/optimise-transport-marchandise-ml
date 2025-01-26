# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import get_occupied_dates, get_delivery_details


urlpatterns = [

    path('', views.index, name='home'),
    path('trucks/add_truck.html', views.add_truck, name='add_truck'),
    path('trucks/manage_trucks.html', views.manage_trucks, name='manage_trucks'),
    path('trucks/edit_truck/<int:truck_id>/', views.edit_truck, name='edit_truck'),
    path('trucks/delete/<int:truck_id>/', views.delete_truck, name='delete_truck'),
    path('home/deliveryadd.html', views.deliveryadd, name='deliveryadd'),
    path('home/deliverymanage.html', views.delivery_manage, name='delivery_manage'),
    path('home/delete_delivery/<str:delivery_id>/', views.delete_delivery, name='delete_delivery'),
    path('home/deliveryedit/<str:delivery_id>/', views.deliveryedit, name='deliveryedit'),
    path('get-occupied-dates/<int:truck_id>/', get_occupied_dates, name='get_occupied_dates'),
    path('home/map.html/<str:delivery_id>/', views.map_delivery, name='map_delivery'),
    path('delay/delayadd.html', views.delayadd, name='delayadd'),
    path('get-delivery-details/<str:delivery_id>/', get_delivery_details, name='get_delivery_details'),
    path('delay/delaymanage.html', views.delaymanage, name='delaymanage'),
    path('delay/delaydelete/<str:delivery_id>/', views.delaydelete, name='delaydelete'),
    path('delay/delayupdate/<str:delivery_id>/', views.delayupdate, name='delayupdate'),
    path('home/managedeliverynow.html', views.managedeliverynow, name='managedeliverynow'),
    path('home/deliverynow_1.html', views.deliverynow_1, name='deliverynow_1'),
    path('home/deliveryaccept/<str:delivery_id>/', views.deliveryaccept, name='deliveryaccept'),
    path('home/deliveryrefuse/<str:delivery_id>/', views.deliveryrefuse, name='deliveryrefuse'),


    re_path(r'^.*\.*', views.pages, name='pages'),

]
