import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
import random
import string

def generate_reference_number():
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=4))
    return letters + numbers

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    is_images_subscribed = models.BooleanField(default=False)
    is_videos_subscribed = models.BooleanField(default=False)
    is_on_premium = models.BooleanField(default=False)
    reference_number = models.CharField(max_length=6, unique=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = self.generate_unique_reference_number()
        super().save(*args, **kwargs)

    def generate_unique_reference_number(self):
        reference_number = generate_reference_number()
        while CustomUser.objects.filter(reference_number=reference_number).exists():
            reference_number = generate_reference_number()
        return reference_number

    def __str__(self):
        return self.username

class Residence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    RESIDENCE_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('bachelor', 'Bachelor'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.TextField()
    residence_type = models.CharField(max_length=10, choices=RESIDENCE_TYPE_CHOICES)
    room_price = models.DecimalField(max_digits=10, decimal_places=2)
    rooms_include = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='residence_images/', blank=True, null=True)
    rooms_available = models.BooleanField(default=True)
    number_of_rooms_available = models.PositiveIntegerField(default=0)
    room_available_date = models.DateField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    business_contacts = models.CharField(max_length=255, blank=True, null=True)
    business_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    residence = models.ForeignKey(Residence, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='extra_images/', blank=True)

    def __str__(self):
        return f"Image for {self.residence.name}"

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    residence = models.ForeignKey(Residence, related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to='residence_videos/', blank=True)

    def __str__(self):
        return f"Video for {self.residence.name}"


