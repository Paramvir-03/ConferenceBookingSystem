# booking/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import login_user, RoomViewSet, get_all_users, toggle_admin_status

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user,name='register'),

    path('toggle-admin/<int:user_id>/', toggle_admin_status, name='toggle_admin_status'),
    path('users/', views.manage_users, name='manage_users'),
    path('users/<int:user_id>/', views.manage_user_detail, name='manage_user_detail'),
    path('book/', views.book_room, name='book_room'),
    path('bookings/', views.get_bookings, name='get_bookings'),
    path('bookings/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('bookings/update/<int:booking_id>/', views.update_booking, name='update_booking'),
    path('admin/bookings/', views.admin_view_all_bookings, name='admin_bookings'),

]
