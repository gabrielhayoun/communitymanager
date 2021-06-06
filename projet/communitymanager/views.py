# ---------------IMPORT-------------------

import calendar
from datetime import datetime
from datetime import timedelta, date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.utils.safestring import mark_safe

from .forms import NewPostForm, CommentaryForm, CalendarForm
from .forms import PriorityForm, EventForm, SearchForm
from .models import *
from .utils import Calendar


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
    posts_user = Post.objects.filter(community=one_community).order_by('-date_creation')
    # the form to filter the post displayed on the community
    priority_form = PriorityForm(request.POST or None)
    event_form = EventForm(request.POST or None)
    priorities = Priority.objects.all()
    is_event = False
    if priority_form.is_valid():
        #first if : the user doesn't choose any priority
        if priority_form.cleaned_data['name'] == "":
            if event_form.is_valid():
                is_event = event_form.cleaned_data['is_event']
                #the user want to see events
                if is_event:
                    posts_user = Post.objects.filter(community=one_community).filter(event=is_event).order_by(
                        '-date_creation')
        #second if : the user chooses a priority
        else:
            prio_id = priority_form.cleaned_data['name']
            chosen_pr = get_object_or_404(Priority, id=prio_id)
            if event_form.is_valid():
                is_event = event_form.cleaned_data['is_event']
                #the user want also to see events
                if is_event:
                    posts_user = Post.objects.filter(community=one_community).filter(
                        priority__rank__gte=chosen_pr.rank).filter(event=is_event).order_by('-date_creation')
                #the user doesn't want to see only events
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
    # Form to search through the posts
    form = SearchForm(request.POST or None)
    if form.is_valid():
        return advanced_research(request, form)
    else:
        # If the form is not valid, we show all the posts of the communities the user subscribed to
        community_user = request.user.community_set.order_by('name')
        posts_user = Post.objects.filter(community__in=community_user).order_by('-date_creation')
    return render(request, 'communitymanager/news_feed.html', locals())


@login_required()
def advanced_research(request, form):
    # Get all the information from the search
    query = form.cleaned_data['query']
    titles = form.cleaned_data['titles']
    descriptions = form.cleaned_data['descriptions']
    usernames = form.cleaned_data['usernames']
    comments = form.cleaned_data['comments']
    communities = form.cleaned_data['communities']
    date_creation_min = form.cleaned_data['date_creation_min']
    date_creation_max = form.cleaned_data['date_creation_max']
    date_event_min = form.cleaned_data['date_event_min']
    date_event_max = form.cleaned_data['date_event_max']

    posts_user = Post.objects.none()

    # If the user wishes to search in the titles
    if titles:
        posts_titles = Post.objects.filter(title__icontains=query)
        posts_user = posts_user.union(posts_titles)
    # If the user wishes to search in the descriptions of the posts
    if descriptions:
        posts_descriptions = Post.objects.filter(description__icontains=query)
        posts_user = posts_user.union(posts_descriptions)
    # If the user wishes to search in the authors' name
    if usernames:
        posts_usernames = Post.objects.filter(author__username__icontains=query)
        posts_user = posts_user.union(posts_usernames)
    # If the user wishes to search in the comments' text
    if comments:
        commentaries = Commentary.objects.filter(content__icontains=query)
        for comment in commentaries:
            posts_user = posts_user.union(Post.objects.filter(id=comment.post.id))
    # If none of these are filled, then we look through all of these possibilities
    if (not titles) and (not descriptions) and (not usernames) and (not comments):
        if query == "":
            posts_user = Post.objects.all()
        else:
            posts_user = posts_user.union(
                Post.objects.filter(title__icontains=query)
            ).union(
                Post.objects.filter(description__icontains=query)
            ).union(
                Post.objects.filter(author__username__icontains=query)
            )
            commentaries = Commentary.objects.filter(content__icontains=query)
            for comment in commentaries:
                posts_user = posts_user.union(Post.objects.filter(id=comment.post.id))
    # If the user wishes to see the posts of all communities
    if (not communities):
        posts_communities = Post.objects.filter(community__in=request.user.community_set.all())
        posts_user = posts_user.intersection(posts_communities)
    # If the user wishes to filter according to posts' date of creation
    if date_creation_min:
        posts_date = Post.objects.filter(date_creation__gte=date_creation_min)
        posts_user = posts_user.intersection(posts_date)
    if date_creation_max:
        posts_date = Post.objects.filter(date_creation__lte=date_creation_max)
        posts_user = posts_user.intersection(posts_date)
    # If the user wishes to filter according to posts' date of event
    if date_event_max:
        posts_date = Post.objects.filter(date_event__lte=date_event_max)
        posts_user = posts_user.intersection(posts_date)
    if date_event_min:
        posts_date = Post.objects.filter(date_event__gte=date_event_min)
        posts_user = posts_user.intersection(posts_date)
    posts_user = posts_user.order_by('-date_creation')


# view to allow user to like post they read
@login_required()
def like_post(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)
    # if he already likes the post he can unlike it
    if request.user in one_post.likers.all():
        one_post.likers.remove(request.user)
    # otherwise he can like it
    else:
        one_post.likers.add(request.user)
    one_post.save()
    # the user stays at the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# view to switch read status of a read post
@login_required()
def unread_post(request, post_id):
    one_post = get_object_or_404(Post, id=post_id)
    # if he allready read it, he can set it as unread
    if request.user in one_post.readers.all():
        one_post.readers.remove(request.user)
    # if he doesn't want to see it as unread
    else:
        one_post.readers.add(request.user)
    one_post.save()
    # the user stays at the same page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# function to make the calendar works
@login_required()
def CalendarView(request, **kwargs):
    # Definition of few utils functions that overide the basic ones
    def prev_month(d):
        first = d.replace(day=1)
        prev_month = first - timedelta(days=1)
        month = str(prev_month.year) + '-' + str(prev_month.month)
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

    # return the week in which the date is (1st week, 2nd week...)
    def arg_day(theweek, date):
        for i, week in enumerate(theweek):
            for w in week:
                if int(date.day) == w[0]:
                    return i

    # use today's date for the calendar
    d = get_date(request.GET.get('month', None))
    today = str(d.year) + "-" + str(d.month)

    # If the month in html is filled then we get this month
    if kwargs.get("month") is not None:
        month = kwargs.get("month")
        # we convert the string into a datetime type
        date_month = datetime.strptime(month, '%Y-%m')
        # we initialize our calendar
        cal = Calendar(int(date_month.year), int(date_month.month))
        # we indicate the previous and the next month (in case the user wants to change)
        prev_month = prev_month(date_month)
        next_month = next_month(date_month)
        # we store the week we should show if the user wants to see the calendar in the week version
        arg = arg_day(cal.monthdays2calendar(cal.year, cal.month), date_month)
        theweek = cal.monthdays2calendar(cal.year, cal.month)[arg]
    else:
        # Instantiate our calendar class with today's year and date
        # Same comment as above
        cal = Calendar(d.year, d.month)
        month = str(d.year) + "-" + str(d.month)
        prev_month = prev_month(d)
        next_month = next_month(d)
        arg = arg_day(cal.monthdays2calendar(cal.year, cal.month), d)
        theweek = cal.monthdays2calendar(cal.year, cal.month)[arg]

    # initialization of parameters that will be needed in the template or the view
    # Advanced research, should the button be colored or not ?
    showcolor = 0
    # Advanced research, should the advanced research menu appear or not ?
    show = 0
    # If we don't select a community/priority in the search, we don't want all of them to be highlighted
    # So we indicate that none of them were selected
    all_community = 0
    all_priority = 0
    # Form initialization
    form = CalendarForm(user=request.user, data=request.POST or None)
    # The user's community, priorities and the right posts to show
    user_community = request.user.community_set.all()
    priorities = Priority.objects.order_by('id')
    posts = Post.objects.filter(event=True, community__in=user_community)

    # we get every parameters of the url file
    community_url = kwargs.get("community")
    priority_url = kwargs.get("priority")
    start_date_url = kwargs.get("start_date")
    end_date_url = kwargs.get("end_date")

    # We use a "@" character between the different communities and priorities (if multiple were selected)
    # We split them now in a list
    community_list = community_url.split("@")
    priority_list = priority_url.split("@")

    # if it is None, we want posts from all community. We don't select any community
    if community_list[0] == "None":
        community_form = Community.objects.all()
        all_community = 1
    else:
        # we have a research so the button is colored and we choose the right posts
        showcolor = 1
        # We select the community from the url
        community_form = Community.objects.filter(name__in=community_list)

    # Same thing with priority
    if priority_list[0] == "None":
        priority_form = Priority.objects.all()
        all_priority = 1
    else:
        showcolor = 1
        priority_form = Priority.objects.filter(name__in=priority_list)

    # if the form is valid
    if form.is_valid():
        # we initialize the parameters to show in the file
        all_community = 0
        all_priority = 0
        # research button is colored and the options are shown
        show = 1
        showcolor = 1
        # we get the view from the url
        view = kwargs.get("view")
        # we define them because it bugs otherwise
        nextweek = "week"
        prevweek = "week"

        # we get the data from the form
        community_form = form.cleaned_data['community']
        priority_form = form.cleaned_data['priority']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']

        # in the case there is nothing
        if not priority_form and not community_form and start_date is None and end_date is None:
            showcolor = 0

        # We build the url for the priority
        priority_url = ""
        for values in priority_form:
            priority_url += str(values) + "@"

        # same with community
        community_url = ""
        for values in community_form:
            community_url += str(values) + "@"

        # if priority form is empty
        if not priority_form:
            priority_form = priorities
            all_priority = 1
            priority_url = "None"

        # if community form is empty
        if not community_form:
            community_form = user_community
            all_community = 1
            community_url = "None"

        # Start and end date
        if start_date is not None and end_date is not None:
            end_date_plus = end_date + timedelta(days=1)
            posts = Post.objects.filter(event=True, community__in=community_form,
                                        priority__in=priority_form, date_event__gt=start_date,
                                        date_event__lt=end_date_plus,
                                        date_event__year=cal.year, date_event__month=cal.month)
            start_date_url = str(start_date)
            end_date_url = str(end_date)
        # Start Date
        elif start_date is not None:
            posts = Post.objects.filter(event=True, community__in=community_form,
                                        priority__in=priority_form, date_event__gt=start_date,
                                        date_event__year=cal.year, date_event__month=cal.month)
            start_date_url = str(start_date)
        # End Date
        elif end_date is not None:
            end_date_plus = end_date + timedelta(days=1)
            posts = Post.objects.filter(event=True, community__in=community_form,
                                        priority__in=priority_form, date_event__lt=end_date_plus,
                                        date_event__year=cal.year, date_event__month=cal.month)
            end_date_url = str(end_date)
        else:
            # Community and Priority
            posts = Post.objects.filter(event=True, community__in=community_form, priority__in=priority_form,
                                        date_event__year=cal.year, date_event__month=cal.month)

        # View for the month
        if kwargs.get("view") == "month":
            viewbtn = 0
            view = "month"
            # Call the formatmonth method, which returns our calendar as a table
            html_cal = cal.formatmonth(posts, withyear=True)
            cal = mark_safe(html_cal)
        # View for the week
        elif kwargs.get("view") == "week":
            viewbtn = 1
            # we get the week to display
            if len(kwargs.get("view")) > 4:
                arg = int(kwargs.get("view")[4])
                if 0 <= arg <= 4:
                    theweek = cal.monthdays2calendar(cal.year, cal.month)[arg]
            view = "week"
            # We get the nextweek (same month or not)
            if arg + 1 > 4:
                nextweek = view + str(0)
            else:
                nextweek = view + str(arg + 1)
                next_month = month
            # Same with the previous week
            if arg - 1 < 0:
                prevweek = view + str(4)
            else:
                prevweek = view + str(arg - 1)
                prev_month = month

            month = str(month)
            # Calendar in weeks display
            html_cal = cal.formatweektable(theweek, posts)
            cal = mark_safe(html_cal)
        return render(request, 'communitymanager/calendar.html', locals())

    # This time, we check the post to display but with the data in the url
    # Start and End Date
    if start_date_url != "None" and end_date_url != "None":
        showcolor = 1
        start_date = datetime.strptime(start_date_url, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_url, '%Y-%m-%d')
        end_date_plus = end_date + timedelta(days=1)
        posts = Post.objects.filter(event=True, community__in=community_form,
                                    priority__in=priority_form, date_event__gt=start_date, date_event__lt=end_date_plus,
                                    date_event__year=cal.year, date_event__month=cal.month)
    # Start Date
    elif start_date_url != "None":
        showcolor = 1
        start_date = datetime.strptime(start_date_url, '%Y-%m-%d')
        posts = Post.objects.filter(event=True, community__in=community_form, priority__in=priority_form,
                                    date_event__year=cal.year, date_event__month=cal.month, date_event__gt=start_date)
    # End Date
    elif end_date_url != "None":
        showcolor = 1
        end_date = datetime.strptime(end_date_url, '%Y-%m-%d')
        end_date_plus = end_date + timedelta(days=1)
        posts = Post.objects.filter(event=True, community__in=community_form, priority__in=priority_form,
                                    date_event__lt=end_date_plus, date_event__year=cal.year,
                                    date_event__month=cal.month)

    else:
        # Community and Priority
        posts = Post.objects.filter(event=True, community__in=community_form, priority__in=priority_form,
                                    date_event__year=cal.year, date_event__month=cal.month)

    # Same view for the month
    if kwargs.get("view") == "month":
        viewbtn = 0
        view = "month"
        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(posts, withyear=True)
        cal = mark_safe(html_cal)

    # View for the week
    elif "week" in kwargs.get("view"):
        viewbtn = 1
        if len(kwargs.get("view")) > 4:
            arg = int(kwargs.get("view")[4])
            if 0 <= arg <= 4:
                theweek = cal.monthdays2calendar(cal.year, cal.month)[arg]
        view = "week"
        if arg + 1 > 4:
            nextweek = view + str(0)
        else:
            nextweek = view + str(arg + 1)
            next_month = month

        if arg - 1 < 0:
            prevweek = view + str(4)
        else:
            prevweek = view + str(arg - 1)
            prev_month = month

        month = str(month)
        html_cal = cal.formatweektable(theweek, posts)
        cal = mark_safe(html_cal)
    return render(request, 'communitymanager/calendar.html', locals())
