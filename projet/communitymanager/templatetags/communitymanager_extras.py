from django import template
from django.shortcuts import get_list_or_404

from ..models import Post, Commentary

register = template.Library()


@register.simple_tag
def nb_unread_posts(community, user):
    community_posts = Post.objects.filter(community=community)
    n_posts = community_posts.count()
    for post in community_posts:
        if user in post.readers.all():
            n_posts -= 1
    if n_posts == 0:
        reply = "no unread post"
    elif n_posts == 1:
        reply = "1 unread post"
    else:
        reply = "%d unread posts" %n_posts
    return reply


@register.simple_tag
def nb_comments(post):
    comments = Commentary.objects.filter(post=post)
    return len(comments)
