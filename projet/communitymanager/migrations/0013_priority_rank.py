# Generated by Django 2.1.15 on 2021-05-31 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communitymanager', '0012_auto_20210531_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='priority',
            name='rank',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
