# Generated by Django 5.1.6 on 2025-03-11 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='badges',
        ),
        migrations.DeleteModel(
            name='Badge',
        ),
    ]
