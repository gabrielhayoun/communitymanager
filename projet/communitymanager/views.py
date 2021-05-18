from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Community, Post
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required()
def communities(request):
    community_user = request.user.community_set.all()
    community_list = Community.objects.all()
#    statut = request.user.has_perm("communitymanager.change_article")
    return render(request, 'communitymanager/communities.html', locals())

def join_community(request, community_id):
    one_community = get_object_or_404(Community, id=community_id)

    if request.user in one_community.subscribers.all():
        one_community.subscribers.remove(request.user)
    else:
        one_community.subscribers.add(request.user)
    one_community.save()

    return redirect('communities')

def community(request, community_id):
    one_community = get_object_or_404(Community, id=community_id)
    posts = Post.objects.filter(community=one_community).order_by('-date_creation')

    return render(request, 'communitymanager/community.html', locals())