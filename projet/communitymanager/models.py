from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Community(models.Model):
    name = models.CharField(max_length=100)
    subscribers = models.ManyToManyField(User)

    class Meta:
        verbose_name = "communitie"
        ordering = ['name']

    def __str__(self):
        return self.name


class Priority(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "prioritie"
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=5000)
    date_creation = models.DateTimeField(default=timezone.now, verbose_name="Date of creation of the post")
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, default=1)
    event = models.BooleanField()
    date_event = models.DateTimeField(verbose_name="Date of the event", null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

