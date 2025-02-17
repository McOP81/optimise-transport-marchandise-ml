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
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


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
    delay = models.IntegerField(null=True, blank=True)
    weekend = models.BooleanField(default=False)
    jour_ferie = models.BooleanField(default=False)
    truck = models.ForeignKey(Truck, on_delete=models.CASCADE)
    arrival_delivery = models.BooleanField(default=False)

    class Meta:
        db_table = 'delivery'
        
    def __str__(self):
        return f"Delivery from {self.departure_city} to {self.arrival_city}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plain_password = models.CharField(max_length=128, blank=True, null=True)