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
        '''one_post = Post()
        one_post.title = form.cleaned_data['title']
        one_post.description = form.cleaned_data['description']
        one_post.community = Community.objects.get(name=form.cleaned_data['community'])
        one_post.priority = Priority.objects.get(name=form.cleaned_data['priority'])
        one_post.event = form.cleaned_data['event']
        one_post.date_event = form.cleaned_data['date_event']
        one_post.author = request.user
        one_post.save()'''

        one_post = form.save(commit=False)
        one_post.author = request.user
        one_post.save()

        return render(request, 'communitymanager/post.html', locals())
    else:
        return render(request, 'communitymanager/new_post.html', locals())

def modif_post(request, post_id):
    form = NewPostForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        one_post = form.save(commit=False)
        one_post.author = request.user
        one_post.save()
        return redirect(post, post_id=one_post.id)
    else :
        one_post = get_object_or_404(Post, id=post_id)
        form = NewPostForm(user=request.user, instance=one_post)
        return render(request, 'communitymanager/new_post.html', locals())


def news_feed(request):
    community_user = request.user.community_set.order_by('name')
    posts_user = Post.objects.filter(community__in=community_user).order_by('-date_creation')
    return render(request, 'communitymanager/news_feed.html', locals())

