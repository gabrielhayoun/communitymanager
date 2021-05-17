from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.urls import views as auth_views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    ]