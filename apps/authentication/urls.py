# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, edit_profile, profile_view, register_user
from django.contrib.auth.views import LogoutView
from . import views


urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('profile/', views.profile_view, name='profile'), 
    path('edit-profile/', views.edit_profile, name='edit_profile'),]
