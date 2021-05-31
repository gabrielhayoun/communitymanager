from django import forms
from .models import Post, Commentary


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





