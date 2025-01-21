# Generated by Django 5.1.4 on 2025-01-09 06:29

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('donations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VolunteerTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('task_type', models.CharField(choices=[('pickup', 'Food Pickup'), ('delivery', 'Food Delivery'), ('preparation', 'Food Preparation'), ('distribution', 'Food Distribution')], max_length=20)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('volunteers_needed', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('open', 'Open'), ('assigned', 'Assigned'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='open', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('donation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_tasks', to='donations.donation')),
            ],
        ),
        migrations.CreateModel(
            name='TaskNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('assignment', 'New Assignment'), ('reminder', 'Task Reminder'), ('update', 'Task Update'), ('completion', 'Task Completion'), ('feedback', 'Feedback Request')], max_length=20)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_notifications', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='volunteers.volunteertask')),
            ],
        ),
        migrations.CreateModel(
            name='VolunteerAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('is_recurring', models.BooleanField(default=True)),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availabilities', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Volunteer availabilities',
                'unique_together': {('volunteer', 'day')},
            },
        ),
        migrations.CreateModel(
            name='TaskAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('rating', models.PositiveIntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True)),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_assignments', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='volunteers.volunteertask')),
            ],
            options={
                'unique_together': {('task', 'volunteer')},
            },
        ),
    ]
