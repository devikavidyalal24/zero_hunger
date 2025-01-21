# Generated by Django 5.1.4 on 2025-01-20 05:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='volunteertask',
            name='assigned_volunteer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='volunteertask',
            name='task_type',
            field=models.CharField(choices=[('collection', 'Collection'), ('preparation', 'Meal Preparation'), ('distribution', 'Distribution')], max_length=20),
        ),
    ]
