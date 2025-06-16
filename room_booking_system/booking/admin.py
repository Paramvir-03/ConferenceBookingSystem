from django.contrib import admin
from .models import CustomUser, Booking, Room, UserProfile
from django.contrib.auth.admin import UserAdmin

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(UserProfile)
