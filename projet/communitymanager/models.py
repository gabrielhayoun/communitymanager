from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class Community(models.Model):
    name = models.CharField(max_length=100)
    subscribers = models.ManyToManyField(User)

    class Meta:
        verbose_name = "community"
        ordering = ['name']

    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=50)
    rank = models.IntegerField()    #to set an order relation between priorities

    class Meta:
        verbose_name = "name"

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=5000)
    date_creation = models.DateTimeField(default=timezone.now, verbose_name="Date of creation of the post")
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, default=1)
    event = models.BooleanField(null=True, blank=True)
    date_event = models.DateTimeField(verbose_name="Date of the event", null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    readers = models.ManyToManyField(User, related_name="readers")
    likers = models.ManyToManyField(User, related_name='likers')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'title'


class Commentary(models.Model):
    date_creation = models.DateTimeField(default=timezone.now, verbose_name="Date of creation of the post")
    content = models.CharField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "commentarie"
        ordering = ['date_creation']

    def __str__(self):
        return self.author.username + " " + self.post.title
