from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.urls import views as auth_views

urlpatterns = [

    path('accounts/', include('django.contrib.auth.urls')),
    path('community', views.communities, name='communities'),
    path('join/<int:community_id>', views.join_community, name='join'),

    path('community/<int:community_id>', views.community, name='community'),

    ]