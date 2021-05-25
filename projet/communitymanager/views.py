from django.db.models import DateTimeField
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils import timezone

from .forms import NewPostForm, CommentaryForm
from .models import Community, Post, Commentary, Priority
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required()
def communities(request):
    community_user = request.user.community_set.all()
    community_list = Community.objects.all()
    return render(request, 'communitymanager/communities.html', locals())


@login_required()
def join_community(request, community_id):
    one_community = get_object_or_404(Community, id=community_id)

    if request.user in one_community.subscribers.all():
        one_community.subscribers.remove(request.user)
    else:
        one_community.subscribers.add(request.user)
    one_community.save()

    return redirect('communities')


@login_required()
def community(request, community_id):
    one_community = get_object_or_404(Community, id=community_id)
    posts = Post.objects.filter(community=one_community).order_by('-date_creation')

    return render(request, 'communitymanager/community.html', locals())


@login_required()
def post(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)
    commentaries = Commentary.objects.filter(post=one_post).order_by('-date_creation')
    form = CommentaryForm(request.POST or None)

    if form.is_valid():
        if form.cleaned_data['content'] == "":
            return render(request, 'communitymanager/post.html', locals())
        else:
            one_comment = form.save(commit=False)
            one_comment.author = request.user
            one_comment.post = one_post
            one_comment.save()
            return render(request, 'communitymanager/post.html', locals())
    return render(request, 'communitymanager/post.html', locals())


@login_required()
def new_post(request):
    form = NewPostForm(user=request.user, data=request.POST or None)
    user_community = request.user.community_set.all()
    priorities = Priority.objects.order_by('id')
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
        if request.POST.get('event'):
            one_post.event = True
            date_time = request.POST.get('date_event')
            final_date_time = ""
            for i in range(len(date_time)):
                if date_time[i] == 'T':
                    final_date_time += ' '
                else:
                    final_date_time += date_time[i]
            one_post.date_event = final_date_time
        else:
            one_post.event = False
        one_post.author = request.user
        one_post.save()
        priorities = Priority.objects.order_by('id')

        return render(request, 'communitymanager/post.html', locals())
    else:
        print(form.errors)
        return render(request, 'communitymanager/new_post.html', locals())


@login_required()
def modif_post(request, post_id):
    form = NewPostForm(user=request.user, data=request.POST or None)
    user_community = request.user.community_set.all()
    priorities = Priority.objects.order_by('id')
    one_post = get_object_or_404(Post, id=post_id)
    if request.user == one_post.author:
        if form.is_valid():
            one_post.title = form.cleaned_data['title']
            one_post.description = form.cleaned_data['description']
            one_post.community = Community.objects.get(name=form.cleaned_data['community'])
            one_post.priority = Priority.objects.get(name=form.cleaned_data['priority'])
            one_post.date_creation = timezone.now()
            if request.POST.get('event'):
                one_post.event = True
                date_time = request.POST.get('date_event')
                final_date_time = ""
                for i in range(len(date_time)):
                    if date_time[i] == 'T':
                        final_date_time += ' '
                    else:
                        final_date_time += date_time[i]
                one_post.date_event = final_date_time
            else:
                one_post.event = False
            one_post.save()
            return redirect(post, post_id=one_post.id)
        else:
            date_time = ""
            date_event = str(one_post.date_event)
            print(date_event)
            for i in range(len(date_event) - 6):
                if date_event[i] == ' ':
                    date_time += 'T'
                else:
                    date_time += date_event[i]
            print(date_time)
            return render(request, 'communitymanager/modif_post.html', locals())
    else:
        return redirect(post, post_id=one_post.id)

@login_required()
def news_feed(request):
    community_user = request.user.community_set.order_by('name')
    posts_user = Post.objects.filter(community__in=community_user).order_by('-date_creation')
    return render(request, 'communitymanager/news_feed.html', locals())
