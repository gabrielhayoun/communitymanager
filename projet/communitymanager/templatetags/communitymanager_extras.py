from django import template

from ..models import Post

register = template.Library()


@register.simple_tag
def unread_posts(community, user):
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
