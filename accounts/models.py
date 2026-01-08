from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with additional fields for LearnLux."""

    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.display_name or self.username

    def get_display_name(self):
        """Return the display name or fall back to username."""
        return self.display_name or self.username
