from django.urls import path, include

from . import views

urlpatterns = [

    # path for an account
    path('accounts/', include('django.contrib.auth.urls')),
    # path to see all the communities
    path('community/', views.communities, name='communities'),
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

    path('calendar', views.calendar, name='calendar'),

    # community creation
    path('community_creation', views.community_creation, name='community_creation'),

    # community moderation
    path('moderation/<int:community_id>', views.moderation, name='moderation'),

    # delete a community
    path('delete_community/<int:community_id>', views.delete_community, name='delete_community'),

    # ban a member from a community
    path('ban/<int:community_id>', views.ban, name='ban'), # ban page
    path('apply_ban/<int:community_id>/<int:subscriber_id>', views.apply_ban, name='apply_ban'),

    # make a post visible / hide post
    path('make_post_visible/<int:post_id>', views.make_post_visible, name='make_post_visible'),
    path('hide_post/<int:post_id>', views.hide_post, name='hide_post'),

    # stick / unstick a post
    path('stick/<int:post_id>', views.stick, name='stick'),
    path('unstick/<int:post_id>', views.unstick, name='unstick'),

    #show / hide a comment
    path('show_comment/<int:comment_id>', views.show_comment, name='show_comment'),
    path('hide_comment/<int:comment_id>', views.hide_comment, name='hide_comment'),

    # warning
    path('warning/<int:post_id>', views.warning, name='warning'),
]
