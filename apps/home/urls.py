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
    path('home/managedeliverynowtraject.html', views.managedeliverynowtraject, name='managedeliverynowtraject'),
    path('get-today-deliveries/', views.get_today_deliveries, name='get_today_deliveries'),
    path('home/deliverynow_1.html', views.deliverynow_1, name='deliverynow_1'),
    path('home/deliveryaccept/<str:delivery_id>/', views.deliveryaccept, name='deliveryaccept'),
    path('home/deliveryrefuse/<str:delivery_id>/', views.deliveryrefuse, name='deliveryrefuse'),
    path('home/add_chauffeur.html', views.add_chauffeur, name='add_chauffeur'),
    path('home/manage_chauffeurs.html', views.manage_chauffeurs, name='manage_chauffeurs'),
    path('home/edit_chauffeur/<int:chauffeur_id>/', views.edit_chauffeur, name='edit_chauffeur'),
    path('home/delete/<int:user_id>/', views.delete_chauffeur, name='delete_chauffeur'),
    path('predict-delay/<str:delivery_id>/', views.predict_delay, name='predict_delay'),



    re_path(r'^.*\.*', views.pages, name='pages'),

]
