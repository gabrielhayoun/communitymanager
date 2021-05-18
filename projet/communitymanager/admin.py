from django.contrib import admin
from .models import Community, Post, Priority, Commentary

# Register your models here.
admin.site.register(Community)
admin.site.register(Post)
admin.site.register(Priority)
admin.site.register(Commentary)

