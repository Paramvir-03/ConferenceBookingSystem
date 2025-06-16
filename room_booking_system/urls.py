from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import hello_api, get_room, book_room  # Use relative import with dot (.) to avoid import errors

urlpatterns = [
    path('api/hello/', hello_api, name='hello_api'),
    path('api/rooms/', get_room, name='get_rooms'),
    path('api/book/',book_room,name='book_room'),
    path('api/', include('room_booking_system.booking.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
