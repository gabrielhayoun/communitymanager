# Generated by Django 2.1.15 on 2021-05-18 09:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communitymanager', '0002_auto_20210517_1759'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=5000)),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date of création of the post')),
                ('event', models.BooleanField()),
                ('date_event', models.DateTimeField(verbose_name='Date of the event')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Priority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterModelOptions(
            name='community',
            options={'ordering': ['name'], 'verbose_name': 'communitie'},
        ),
        migrations.AddField(
            model_name='post',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communitymanager.Community'),
        ),
        migrations.AddField(
            model_name='post',
            name='priority',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='communitymanager.Priority'),
        ),
    ]
