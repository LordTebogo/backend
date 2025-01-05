# Generated by Django 5.1.4 on 2025-01-05 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('residences', '0006_remove_residence_reference_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='residence',
            name='is_images_subscribed',
        ),
        migrations.RemoveField(
            model_name='residence',
            name='is_on_premium',
        ),
        migrations.RemoveField(
            model_name='residence',
            name='is_videos_subscribed',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_images_subscribed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_on_premium',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_videos_subscribed',
            field=models.BooleanField(default=False),
        ),
    ]
