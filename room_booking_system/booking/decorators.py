# booking/decorators.py
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.role != 'admin':
                return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
