from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import Community
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required()
def community(request):
    community_user = request.user.community_set.all()
    community = Community.objects.all()
#    statut = request.user.has_perm("communitymanager.change_article")
    return render(request, 'communitymanager/community.html', locals())

def join_community(request, id):
    one_community = get_object_or_404(Community, id=id)

    if request.user in one_community.subscribers.all():
        one_community.subscribers.remove(request.user)
    else:
        one_community.subscribers.add(request.user)

    community_user = request.user.community_set.all()
    community = Community.objects.all()
    return render(request, 'communitymanager/community.html', locals())