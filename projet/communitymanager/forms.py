from django import forms
from django.contrib.auth.models import User
from .models import Community, Priority, Post, Commentary
from collections import defaultdict, deque

'''
class NewPostForm(forms.Form):
    community = forms.ModelChoiceField(queryset=Community.objects.all())
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, max_length=5000)
    event = forms.BooleanField(required=False)
    date_event = forms.DateTimeField(widget=forms.SelectDateWidget(), required=False)

    list_priorities = []
    for i, obj in enumerate(Priority.objects.order_by('id')):
        list_priorities.append((str(i), str(obj.name)))
    priority = forms.ModelChoiceField(queryset=Priority.objects.order_by('id'))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(NewPostForm, self).__init__(*args, **kwargs)

#        list_user_communities = [('0', '-------------')]
#        for i, obj in enumerate(self.user.community_set.all()):
#            list_user_communities.append((str(i+1), str(obj.name)))
        self.fields['community'].queryset = self.user.community_set.all()


'''
class NewPostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('author', 'date_creation', 'date_event','event')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(NewPostForm, self).__init__(*args, **kwargs)

#        list_user_communities = [('0', '-------------')]
#        for i, obj in enumerate(self.user.community_set.all()):
#            list_user_communities.append((str(i + 1), str(obj.name)))
        self.fields['community'].queryset = self.user.community_set.all()
#        self.fields['date_event'].required = False
#        self.fields['event'].required = False


class CommentaryForm(forms.ModelForm):

    class Meta:
        model = Commentary
        fields = ('content',)

    def __init__(self, *args, **kwargs):
        super(CommentaryForm, self).__init__(*args, **kwargs)
        self.fields['content'].required = False
#        self.fields['content'].widget = forms.Textarea(attrs={'cols':100, 'rows':2})




