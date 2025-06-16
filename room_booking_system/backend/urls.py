from django.contrib import admin
from django.urls import path, include

from room_booking_system.booking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
path('api/hello/', views.hello_world, name='hello_world'),

]
