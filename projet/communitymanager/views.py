# ---------------IMPORT-------------------
from django.shortcuts import render, get_object_or_404, redirect

from datetime import datetime, timedelta, date

from .forms import NewPostForm, CommentaryForm, CalendarForm
from .models import Community, Post, Commentary, Priority
from django.contrib.auth.decorators import login_required

from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic
from django.utils.safestring import mark_safe

from .models import *
from .utils import Calendar
import calendar


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
    posts = Post.objects.filter(community=one_community).order_by('-date_creation')

    return render(request, 'communitymanager/community.html', locals())


# show the wanted post
# the modif argument(bool) is useful to decide if we show a toast or not
# 0 lets not see the toast
# 1 will return the page with a toast when someone wants to change a post he is not allowed to
@login_required()
def post(request, post_id, ):
    one_post = get_object_or_404(Post, id=post_id)
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


# create a new post
@login_required()
def new_post(request):
    form = NewPostForm(user=request.user, data=request.POST or None)
    user_community = request.user.community_set.all()
    priorities = Priority.objects.order_by('id')

    if form.is_valid():
        one_post = form.save(commit=False)

        one_post.event, one_post.date_event = form.clean_event_and_date(request)
        one_post.author = request.user

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
    if request.user == one_post.author:
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


# see the news_feed
@login_required()
def news_feed(request):
    community_user = request.user.community_set.order_by('name')
    posts_user = Post.objects.filter(community__in=community_user).order_by('-date_creation')
    return render(request, 'communitymanager/news_feed.html', locals())


@login_required()
def calendar1(request):
    all_community = 0
    all_priority = 0
    form = CalendarForm(user=request.user, data=request.POST or None)
    user_community = request.user.community_set.all()
    priorities = Priority.objects.order_by('id')
    posts = Post.objects.filter(event=True, community__in=user_community)
    if form.is_valid():
        community_form = form.cleaned_data['community']
        priority_form = form.cleaned_data['priority']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        if not priority_form:
            priority_form = priorities
            all_priority = 1

        if not community_form:
            community_form = user_community
            all_community = 1

        if start_date is not None and end_date is not None:
            end_date_plus = end_date + timedelta(days=1)
            posts = Post.objects.filter(event=True, community__in=community_form,
                                        priority__in=priority_form, date_event__gt=start_date,
                                        date_event__lt=end_date_plus)
            str_start = str(start_date)
            str_end = str(end_date)
        elif start_date is not None:
            posts = Post.objects.filter(event=True, community__in=community_form,
                                        priority__in=priority_form, date_event__gt=start_date)
            str_start = str(start_date)
        elif end_date is not None:
            end_date_plus = end_date + timedelta(days=1)
            posts = Post.objects.filter(event=True, community__in=community_form,
                                        priority__in=priority_form, date_event__lt=end_date_plus)
            tr_end = str(end_date)
        else:
            posts = Post.objects.filter(event=True, community__in=community_form, priority__in=priority_form, )
        return render(request, 'communitymanager/calendar.html', locals())
    print("nope")
    return render(request, 'communitymanager/calendar.html', locals())


def CalendarView(request, **kwargs):
    def prev_month(d):
        first = d.replace(day=1)
        prev_month = first - timedelta(days=1)
        month =str(prev_month.year) + '-' + str(prev_month.month)
        print(month)
        return month

    def next_month(d):
        days_in_month = calendar.monthrange(d.year, d.month)[1]
        last = d.replace(day=days_in_month)
        next_month = last + timedelta(days=1)
        month = str(next_month.year) + '-' + str(next_month.month)
        return month

    def get_date(req_day):
        if req_day:
            year, month = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
        return datetime.today()

    # use today's date for the calendar
    d = get_date(request.GET.get('month', None))

    if kwargs :
        month=kwargs.get("month")
        date_month = datetime.strptime(month, '%Y-%m')
        cal = Calendar(d.year, int(date_month.month) )
    else :
        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

    # Call the formatmonth method, which returns our calendar as a table
    html_cal = cal.formatmonth(withyear=True)
    cal = mark_safe(html_cal)
    prev_month = prev_month(d)
    next_month = next_month(d)
    return render(request, 'communitymanager/calendar1.html', locals())
