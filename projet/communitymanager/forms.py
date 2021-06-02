from django import forms
from .models import Post, Commentary, Community
from django.db.models import Q


class NewPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author', 'date_creation', 'event', 'date_event')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(NewPostForm, self).__init__(*args, **kwargs)
        # set the communities possibility to the user's ones
        self.fields['community'].queryset = self.user.community_set.all()

    # redefine the clean for event and date_event
    def clean_event_and_date(self, request):
        # if the checkbox is crossed
        if request.POST.get('event'):
            event = True
            date_time = request.POST.get('date_event')
            final_date_time = ""
            # we put the date to the good format
            for i in range(len(date_time)):
                if date_time[i] == 'T':
                    final_date_time += ' '
                else:
                    final_date_time += date_time[i]
            return event, final_date_time
        # otherwise no event
        else:
            return False, None


class CommentaryForm(forms.ModelForm):

    class Meta:
        model = Commentary
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(CommentaryForm, self).__init__(*args, **kwargs)
        self.fields['content'].required = False


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False, label='Search in posts')


class AdvancedSearchForm(forms.Form):
    query = forms.CharField(max_length=100, label='Search in posts')
    titles = forms.BooleanField(required=False)
    descriptions = forms.BooleanField(required=False)
    comments = forms.BooleanField(required=False)
    usernames = forms.BooleanField(required=False)
    communities = forms.BooleanField(required=False)
    date_creation_min = forms.DateTimeField(required=False)
    date_creation_max = forms.DateTimeField(required=False)
    date_event_min = forms.DateTimeField(required=False)
    date_event_max = forms.DateTimeField(required=False)

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('date_event_min', 'date_event_max', 'date_creation_max', 'date_creation_min')

    def clean_dates(self, request):
        if request.POST.get('date_creation_min') :
            date_creat_min = format_date(request.POST.get('date_creation_min'))
        else :
            date_creat_min = None
        if request.POST.get('date_creation_max'):
            date_creat_max = format_date(request.POST.get('date_creation_max'))
        else:
            date_creat_max = None
        if request.POST.get('date_event_min'):
            date_event_min = format_date(request.POST.get('date_event_min'))
        else:
            date_event_min = None
        if request.POST.get('date_event_max'):
            date_event_max = format_date(request.POST.get('date_event_max'))
        else:
            date_event_max = None

        return date_creat_min, date_creat_max, date_event_min, date_event_max


def format_date(date):
    final_date = ""
    for i in range(len(date)):
        if date[i] == 'T':
            final_date += ' '
        else:
            final_date += date[i]
    return final_date

