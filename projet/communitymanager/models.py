from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Community(models.Model):
    name = models.CharField(max_length=100)
    subscribers = models.ManyToManyField(User)

    class Meta:
        verbose_name = "communitie"
        ordering = ['name']