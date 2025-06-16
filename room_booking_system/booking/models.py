from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100, verbose_name="Room Name")
    capacity = models.PositiveIntegerField(default=10,verbose_name="Capacity")
    available = models.BooleanField(default=True, verbose_name="Available")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Room"
        verbose_name_plural = "Rooms"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    start_time = models.DateTimeField(verbose_name="Start Time")
    end_time = models.DateTimeField(verbose_name="End Time")

    def __str__(self):
        return f"{self.room.name} booked by {self.user.username}"

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"



class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')  # ✅ add this line

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True
    )

