# Generated by Django 2.1.15 on 2021-06-01 06:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communitymanager', '0013_priority_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='readers',
            field=models.ManyToManyField(related_name='reader', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
    ]
