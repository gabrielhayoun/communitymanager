from django.urls import path, include

from . import views

urlpatterns = [

    # path for an account
    path('accounts/', include('django.contrib.auth.urls')),
    # path to see all the communities
    path('community', views.communities, name='communities'),
    # path to join a community
    path('join/<int:community_id>', views.join_community, name='join'),

    # path to see the community with the corresponding id
    path('community/<int:community_id>', views.community, name='community'),

    # path to see the post with the corresponding id
    path('post/<int:post_id>', views.post, name='post'),

    # path to create a post
    path('new_post/', views.new_post, name='new_post'),

    # path to change a post
    path('modif_post/<int:post_id>', views.modif_post, name='modif_post'),

    # path to see the news_feed
    path('news_feed/', views.news_feed, name='news_feed'),

    path('like_post/<int:post_id>', views.like_post, name='like_post'),

    path('unread_post/<int:post_id>', views.unread_post, name='unread_post'),

    path('calendar/<str:view>/<str:community>/<str:priority>/<str:start_date>/<str:end_date>', views.CalendarView, name='calendar'),

    path('calendar/<str:view>/<str:month>/<str:community>/<str:priority>/<str:start_date>/<str:end_date>'
         , views.CalendarView, name='calendar_form'),


]
