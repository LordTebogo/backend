# Generated by Django 5.1.4 on 2025-01-05 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('residences', '0002_remove_residence_rooms_included_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, upload_to='residence_images/'),
        ),
        migrations.AlterField(
            model_name='residence',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='residence',
            name='rooms_include',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(blank=True, upload_to='residence_videos/'),
        ),
    ]
