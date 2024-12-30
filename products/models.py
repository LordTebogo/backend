from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Adding any extra fields if necessary
    is_businessperson = models.BooleanField(default=False)

    # Define the groups field with a unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_groups',  # This should be a unique related_name
        blank=True
    )

    # Define the user_permissions field with a unique related_name
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions',  # This should be a unique related_name
        blank=True
    )


class Product(models.Model):
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    businessperson = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/", null=True)
