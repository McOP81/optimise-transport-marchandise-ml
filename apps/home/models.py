# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

class Truck(models.Model):
    name_truck = models.CharField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=255, unique=True)
    model = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    tonnage = models.IntegerField()
    insurance_date = models.DateField()
    gray_card_date = models.DateField()

    class Meta:
        db_table = 'truck'
        
    def __str__(self):
        return self.name_truck

# Table Delivery
class Delivery(models.Model):
    id = models.CharField(max_length=50, primary_key=True, unique=True, editable=False)
    departure_city = models.CharField(max_length=255)
    arrival_city = models.CharField(max_length=255) 
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()
    phone_number = models.CharField(max_length=20)
    tonnage = models.IntegerField()
    loaded_trip = models.BooleanField(default=False)
    delay = models.CharField(max_length=255, null=True, blank=True)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    arrival_delivery = models.BooleanField(default=False)

    class Meta:
        db_table = 'delivery'
        
    def __str__(self):
        return f"Delivery from {self.departure_city} to {self.arrival_city}"