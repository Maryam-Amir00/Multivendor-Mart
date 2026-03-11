from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Admin'),   
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Auto-fix superuser fields
        if self.is_superuser:
            self.role = "admin"
            self.is_approved = True
        super().save(*args, **kwargs)
