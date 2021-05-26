from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth.urls import views as auth_views

urlpatterns = [

    path('accounts/', include('django.contrib.auth.urls')),
    path('community', views.communities, name='communities'),
    path('join/<int:community_id>', views.join_community, name='join'),

    path('community/<int:community_id>', views.community, name='community'),

    path('post/<int:post_id>', views.post, name='post'),

    path('post/<int:post_id>/<int:modif>', views.post, name='post_modif'),
    path('new_post/', views.new_post, name='new_post'),

    path('modif_post/<int:post_id>', views.modif_post, name='modif_post'),

    path('news_feed', views.news_feed, name='news_feed'),

]
