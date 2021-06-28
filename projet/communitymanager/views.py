# ---------------IMPORT-------------------
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import NewPostForm, CommentaryForm, PriorityForm, EventForm, CommunityEditionForm, NewCommunityForm
from .forms import SearchForm
from .models import Community, Post, Commentary, Priority


# ---------------VIEWS-------------------

# see all the communities and show if the user is subscribed or not
@login_required()
def communities(request):
    community_user = request.user.community_set.all()
    community_list = Community.objects.all()
    return render(request, 'communitymanager/communities.html', locals())


# change the subscribers attribute of the right community
@login_required()
def join_community(request, community_id):
    one_community = get_object_or_404(Community, id=community_id)

    if request.user in one_community.subscribers.all():
        one_community.subscribers.remove(request.user)
    else:
        one_community.subscribers.add(request.user)
    one_community.save()

    return redirect('communities')


# show the posts of the right community
@login_required()
def community(request, community_id):
    one_community = get_object_or_404(Community, id=community_id)
    posts_user = Post.objects.filter(community=one_community).order_by('-date_creation').order_by('-sticky')
    priority_form = PriorityForm(request.POST or None)
    priorities = Priority.objects.all()
    event_form = EventForm(request.POST or None)
    is_event = False
    if event_form.is_valid():
        is_event = event_form.cleaned_data['is_event']
        if is_event:
            posts_user = Post.objects.filter(community=one_community).filter(event=is_event).order_by(
                '-date_creation')
    if priority_form.is_valid():
        if priority_form.cleaned_data['name'] == "":
            if event_form.is_valid():
                if is_event:
                    posts_user = Post.objects.filter(community=one_community).filter(event=is_event).order_by(
                        '-date_creation')
        else:
            prio_id = priority_form.cleaned_data['name']
            chosen_pr = get_object_or_404(Priority, id=prio_id)
            if event_form.is_valid():
                if is_event:
                    posts_user = Post.objects.filter(community=one_community).filter(
                        priority__rank__gte=chosen_pr.rank).filter(event=is_event).order_by('-date_creation')
                else:
                    posts_user = Post.objects.filter(community=one_community).filter(
                        priority__rank__gte=chosen_pr.rank).order_by('-date_creation')
    return render(request, 'communitymanager/community.html', locals())


# show the wanted post
# the modif argument(bool) is useful to decide if we show a toast or not
# 0 lets not see the toast
# 1 will return the page with a toast when someone wants to change a post he is not allowed to
@login_required()
def post(request, post_id, ):
    one_post = get_object_or_404(Post, id=post_id)
    banned_members = one_post.community.banned_members.all()
    readers_list = one_post.readers.all()
    commentaries = Commentary.objects.filter(post=one_post).order_by('-date_creation')
    # beginning of the form
    form = CommentaryForm(request.POST or None)

    if request.user not in readers_list:
        one_post.readers.add(request.user)
    if form.is_valid():
        if form.cleaned_data['content'] == "":
            return render(request, 'communitymanager/post.html', locals())
        else:
            one_comment = form.save(commit=False)
            one_comment.author = request.user
            one_comment.post = one_post
            # we update the database and reload the page
            one_comment.save()
            return render(request, 'communitymanager/post.html', locals())
    return render(request, 'communitymanager/post.html', locals())


# create a new post
@login_required()
def new_post(request):
    form = NewPostForm(user=request.user, data=request.POST or None)
    user_community = request.user.community_set.all()
    priorities = Priority.objects.order_by('id')
    banned_warning = False

    if form.is_valid():
        one_post = form.save(commit=False)
        if request.user in one_post.community.banned_members.all():
            banned_warning = True
            return render(request, 'communitymanager/new_post.html', locals())
        one_post.event, one_post.date_event = form.clean_event_and_date(request)
        one_post.author = request.user
        one_post.is_visible = True

        # check if the date is possible (after now)
        if one_post.event:
            try:
                compare_date = datetime.strptime(one_post.date_event, '%Y-%m-%d %H:%M')
            except:
                # otherwise we send the form again and a toast says that the format of the date has to be correct
                date = True
                return render(request, 'communitymanager/modif_post.html', locals())
            if compare_date < datetime.today():
                date_too_soon = True
                return render(request, 'communitymanager/modif_post.html', locals())

        # check if the form can be saved (especially if the date of the event has a good format)
        try:
            one_post.save()
            one_post.readers.add(request.user)
        except:
            # otherwise we send the form again and a toast says that the format of the date has to be correct
            date = True
            return render(request, 'communitymanager/modif_post.html', locals())

        priorities = Priority.objects.order_by('id')
        return render(request, 'communitymanager/post.html', locals())
    # send the form the first time
    else:
        return render(request, 'communitymanager/new_post.html', locals())


# modify a post
@login_required()
def modif_post(request, post_id):
    form = NewPostForm(user=request.user, data=request.POST or None)
    user_community = request.user.community_set.all()
    priorities = Priority.objects.order_by('id')
    # we get the post the user wants to change
    one_post = get_object_or_404(Post, id=post_id)

    # we check if the user has the right to change the post
    if request.user == one_post.author or request.user.is_superuser or request.user == community.manager:
        if form.is_valid():
            one_post.title = form.cleaned_data['title']
            one_post.description = form.cleaned_data['description']
            one_post.community = Community.objects.get(name=form.cleaned_data['community'])
            one_post.priority = Priority.objects.get(name=form.cleaned_data['priority'])
            one_post.date_creation = timezone.now()
            one_post.event, one_post.date_event = form.clean_event_and_date(request)
            # check if the date is possible (after now)
            if one_post.event:
                try:
                    compare_date = datetime.strptime(one_post.date_event, '%Y-%m-%d %H:%M')
                except:
                    # otherwise we send the form again and a toast says that the format of the date has to be correct
                    date = True
                    return render(request, 'communitymanager/modif_post.html', locals())
                if compare_date < datetime.today():
                    date_too_soon = True
                    return render(request, 'communitymanager/modif_post.html', locals())

            try:
                one_post.save()
            except:
                # otherwise we send the form again and a toast says that the format of the date has to be correct
                date = True
                return render(request, 'communitymanager/modif_post.html', locals())
            return redirect(post, post_id=one_post.id)
        else:
            # we send a date with the good format
            date_time = ""
            date_event = str(one_post.date_event)
            for i in range(len(date_event) - 6):
                if date_event[i] == ' ':
                    date_time += 'T'
                else:
                    date_time += date_event[i]
            # we return a page to modify the post
            return render(request, 'communitymanager/modif_post.html', locals())
    else:
        modif = True
        commentaries = Commentary.objects.filter(post=one_post).order_by('-date_creation')
        # beginning of the form
        form = CommentaryForm(request.POST or None)
        if form.is_valid():
            if form.cleaned_data['content'] == "":
                return render(request, 'communitymanager/post.html', locals())
            else:
                one_comment = form.save(commit=False)
                one_comment.author = request.user
                one_comment.post = one_post
                # we update the database and reload the page
                one_comment.save()
                return render(request, 'communitymanager/post.html', locals())
        return render(request, 'communitymanager/post.html', locals())


@login_required
def moderation(request, community_id):
    community = Community.objects.get(id=community_id)
    subscribers = community.subscribers.all()
    if request.user == community.manager or request.user.is_superuser:
        form = CommunityEditionForm(request.POST or None)
        if form.is_valid():
            community.name = form.cleaned_data['name']
            community.description = form.cleaned_data['description']
            community.is_closed = form.cleaned_data['is_closed']
            community.is_visible = form.cleaned_data['is_visible']
            community.save()
            return redirect('communities')
        else:
            return render(request, 'communitymanager/community_moderation.html', locals())
    else:
        return redirect('logout')

@login_required
def ban(request, community_id):
    community = Community.objects.get(id=community_id)
    subscribers = community.subscribers.all()
    banned_members = community.banned_members.all()

    if request.user == community.manager or request.user.is_superuser:
        return render(request, 'communitymanager/ban_member.html', locals())
    else:
        return redirect('logout')

@login_required
def apply_ban(request, community_id, subscriber_id):
    community = Community.objects.get(id=community_id)
    user = User.objects.get(id=subscriber_id)
    if request.user == community.manager or request.user.is_superuser:
        if user in community.banned_members.all():
            community.banned_members.remove(user)
        else:
            community.banned_members.add(user)
        return redirect('ban', community_id)
    else:
        return redirect('logout')

@login_required()
def community_creation(request):
    form = NewCommunityForm(request.POST or None)
    priorities = Priority.objects.order_by('id')

    if form.is_valid():
        new_community = form.save(commit=False)
        new_community.manager = request.user
        new_community.save()
        return redirect('communities')
    return render(request, 'communitymanager/community_creation.html', locals())

@login_required()
def delete_community(request, community_id):
    community = Community.objects.get(id=community_id)
    if request.user == community.manager or request.user.is_superuser:
        community.delete()
        return redirect('communities')
    else:
        return redirect('logout')


@login_required()
def make_post_visible(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user == post.community.manager or request.user.is_superuser:
        post.is_visible = True
        post.save()
        return redirect('post', post.id)
    else:
        return redirect('logout')


@login_required()
def hide_post(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user == post.community.manager or request.user.is_superuser:
        post.is_visible = False
        post.save()
        return redirect('post', post.id)
    else:
        return redirect('logout')

@login_required()
def warning(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user.is_superuser:
        if post.warning:
            post.warning = False
            post.save()
            return redirect('post', post.id)
        else:
            post.warning = True
            post.save()
            return redirect('post', post.id)
    else:
        return redirect('logout')

@login_required()
def show_comment(request, comment_id):
    comment = Commentary.objects.get(id=comment_id)
    if request.user == comment.post.community.manager or request.user.is_superuser:
        comment.visible = True
        comment.save()
        return redirect('post', comment.post.id)
    else:
        return redirect('logout')

@login_required()
def hide_comment(request, comment_id):
    comment = Commentary.objects.get(id=comment_id)
    if request.user == comment.post.community.manager or request.user.is_superuser:
        comment.visible = False
        comment.save()
        return redirect('post', comment.post.id)
    else:
        return redirect('logout')

def stick(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user == post.community.manager or request.user.is_superuser:
        post.sticky = True
        post.save()
        return redirect('post', post.id)
    else:
        return redirect('logout')


def unstick(request, post_id):
    post = Post.objects.get(id=post_id)
    if request.user == post.community.manager or request.user.is_superuser:
        post.sticky = False
        post.save()
        return redirect('post', post.id)
    else:
        return redirect('logout')


@login_required()
def news_feed(request):
    form = SearchForm(request.POST or None)
    priority_form = PriorityForm(request.POST or None)
    event_form = EventForm(request.POST or None)
    priorities = Priority.objects.all()
    is_event = False
    community_user = request.user.community_set.order_by('name')
    posts_user = Post.objects.filter(community__in=community_user).order_by('-date_creation').order_by('-sticky')
    if form.is_valid():
        query = form.cleaned_data['query']
        if query != "":
            posts_user = Post.objects.filter(Q(title__icontains=query) |
                                             Q(description__icontains=query) |
                                             Q(author__username__icontains=query)
                                             )
            if event_form.is_valid():
                is_event = event_form.cleaned_data['is_event']
                if is_event:
                    posts_user = Post.objects.filter(community__in=community_user).filter(Q(title__icontains=query) |
                                                                                          Q(description__icontains=query) |
                                                                                          Q(author__username__icontains=query)
                                                                                          ).filter(
                        event=is_event).order_by('-date_creation')
            if priority_form.is_valid():
                if priority_form.cleaned_data['name'] == "":
                    if event_form.is_valid():
                        if is_event:
                            is_event = event_form.cleaned_data['is_event']
                            posts_user = Post.objects.filter(community__in=community_user).filter(
                                Q(title__icontains=query) |
                                Q(description__icontains=query) |
                                Q(author__username__icontains=query)
                            ).filter(event=is_event).order_by('-date_creation')
                        else:
                            posts_user = Post.objects.filter(community__in=community_user).filter(
                                Q(title__icontains=query) |
                                Q(description__icontains=query) |
                                Q(author__username__icontains=query)
                            ).order_by('-date_creation')
                else:
                    prio_id = priority_form.cleaned_data['name']
                    chosen_pr = get_object_or_404(Priority, id=prio_id)
                    if event_form.is_valid():
                        if is_event:
                            is_event = event_form.cleaned_data['is_event']
                            posts_user = Post.objects.filter(community__in=community_user).filter(
                                Q(title__icontains=query) |
                                Q(description__icontains=query) |
                                Q(author__username__icontains=query)
                            ).filter(event=is_event).filter(priority__rank__gte=chosen_pr.rank).order_by(
                                '-date_creation')
                        else:
                            posts_user = Post.objects.filter(community__in=community_user).filter(
                                Q(title__icontains=query) |
                                Q(description__icontains=query) |
                                Q(author__username__icontains=query)
                            ).filter(priority__rank__gte=chosen_pr.rank).order_by('-date_creation')
                    if is_event:
                        posts_user = Post.objects.filter(community__in=community_user).filter(
                            Q(title__icontains=query) |
                            Q(description__icontains=query) |
                            Q(author__username__icontains=query)
                        ).filter(priority__rank__gte=chosen_pr.rank).filter(event=is_event).order_by(
                            '-date_creation')
                    else:
                        posts_user = Post.objects.filter(community__in=community_user).filter(
                            priority__rank__gte=chosen_pr.rank).filter(Q(title__icontains=query) |
                                                                       Q(description__icontains=query) |
                                                                       Q(author__username__icontains=query)
                                                                       ).order_by('-date_creation')
        else:
            if event_form.is_valid():
                is_event = event_form.cleaned_data['is_event']
                if is_event:
                    posts_user = Post.objects.filter(community__in=community_user).filter(event=is_event).order_by(
                        '-date_creation')
            if priority_form.is_valid():
                if priority_form.cleaned_data['name'] == "":
                    if event_form.is_valid():
                        if is_event:
                            posts_user = Post.objects.filter(community__in=community_user).filter(
                                event=is_event).order_by('-date_creation')
                else:
                    prio_id = priority_form.cleaned_data['name']
                    chosen_pr = get_object_or_404(Priority, id=prio_id)
                    if is_event:
                        posts_user = Post.objects.filter(community__in=community_user).filter(
                            priority__rank__gte=chosen_pr.rank).filter(event=is_event).order_by('-date_creation')
                    else:
                        posts_user = Post.objects.filter(community__in=community_user).filter(
                            priority__rank__gte=chosen_pr.rank).order_by('-date_creation')
    return render(request, 'communitymanager/news_feed.html', locals())


def filter_posts(request):
    community_user = request.user.community_set.order_by('name')
    posts_user = Post.objects.filter(community__in=community_user).order_by('-date_creation')
    priority_form = PriorityForm(request.POST or None)
    priorities = Priority.objects.all()
    event_form = EventForm(request.POST or None)

    is_event = False
    if event_form.is_valid():
        is_event = event_form.cleaned_data['is_event']
        posts_user = Post.objects.filter(community__in=community_user).filter(event=is_event).order_by('-date_creation')

    if priority_form.is_valid():
        if priority_form.cleaned_data['name'] == "":
            return posts_user
        else:
            prio_id = priority_form.cleaned_data['name']
            chosen_pr = get_object_or_404(Priority, id=prio_id)
            if is_event:
                posts_user = Post.objects.filter(community__in=community_user).filter(
                    priority__rank__gte=chosen_pr.rank).filter(event=is_event).order_by('-date_creation')
                return posts_user
            else:
                posts_user = Post.objects.filter(community__in=community_user).filter(
                    priority__rank__gte=chosen_pr.rank).order_by('-date_creation')
                return posts_user
    return posts_user


@login_required()
def like_post(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)

    if request.user in one_post.likers.all():
        one_post.likers.remove(request.user)
    else:
        one_post.likers.add(request.user)
    one_post.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def calendar(request):
    return render(request, 'communitymanager/calendar.html', locals())
