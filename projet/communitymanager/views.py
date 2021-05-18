from django.db.models import DateTimeField
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone

from .forms import NewPostForm
from .models import Community, Post, Commentary, Priority
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


def post(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)
    commentaries = Commentary.objects.filter(post=one_post).order_by('-date_creation')

    return render(request, 'communitymanager/post.html', locals())


def new_post(request):
    form = NewPostForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        post = Post()
        post.title = form.cleaned_data['title']
        post.description = form.cleaned_data['description']
        post.community = Community.objects.get(name=form.cleaned_data['community'])
        post.priority = Priority.objects.get(name=form.cleaned_data['priority'])
        post.event = form.cleaned_data['event']
        post.date_event = form.cleaned_data['date_event']
        post.author = request.user
        post.save()
        return render(request, 'communitymanager/post.html', {'one_post': post})
    else:
        return render(request, 'communitymanager/new_post.html', locals())
