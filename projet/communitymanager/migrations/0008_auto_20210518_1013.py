# Generated by Django 2.1.15 on 2021-05-18 10:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communitymanager', '0007_commentaries'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Commentaries',
            new_name='Commentary',
        ),
        migrations.AlterModelOptions(
            name='commentary',
            options={'ordering': ['date_creation'], 'verbose_name': 'commentarie'},
        ),
    ]