# Generated by Django 5.1.6 on 2025-03-08 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_habitstats_weekly_completions'),
    ]

    operations = [
        migrations.AddField(
            model_name='habit',
            name='reminder_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='habit',
            name='reminder_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
