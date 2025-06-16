from django.apps import AppConfig


class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'room_booking_system.booking'

def ready(self):
    import booking.signals