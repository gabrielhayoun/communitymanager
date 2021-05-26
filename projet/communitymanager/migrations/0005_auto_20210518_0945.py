# Generated by Django 2.1.15 on 2021-05-18 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('communitymanager', '0004_post_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='priority',
            options={'ordering': ['name'], 'verbose_name': 'prioritie'},
        ),
        migrations.AlterField(
            model_name='post',
            name='date_event',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date of the event'),
        ),
        migrations.AlterField(
            model_name='post',
            name='priority',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='communitymanager.Priority'),
        ),
    ]