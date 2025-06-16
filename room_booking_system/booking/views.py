from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive
from .models import Room, Booking, CustomUser
from .serializers import RoomSerializer, BookingSerializer, UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .decorators import admin_required
from rest_framework.serializers import ModelSerializer
from rest_framework import viewsets
from .models import Room
from .serializers import RoomSerializer
from .permissions import IsAdminUserRole
from django.contrib.auth import get_user_model
User = get_user_model()


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT','DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class SimpleUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff']

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def toggle_admin_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        if user == request.user:
            return Response({"error": "You cannot change your own admin status."}, status=403)
        user.is_staff = not user.is_staff
        user.save()
        return Response({"message": "User role updated.", "new_status": user.is_staff})
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@admin_required
def get_all_users(request):
    users = User.objects.all()
    serializer = SimpleUserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def manage_users(request):
    if request.method == 'GET':
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def manage_user_detail(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    if request.method == 'DELETE':
        user.delete()
        return Response({"message": "User deleted"}, status=204)

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'is_admin': user.is_staff  # or user.is_superuser depending on your use case
        })

    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@admin_required
def admin_view_all_bookings(request):
    bookings = Booking.objects.all()
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)

#@api_view(['POST'])
#@permission_classes([IsAuthenticated])
#@admin_required
#def create_room(request):
#    serializer = RoomSerializer(data=request.data)
#    if serializer.is_valid():
#        serializer.save()
#        return Response(serializer.data, status=status.HTTP_201_CREATED)
#    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#@api_view(['POST'])
#@permission_classes([IsAuthenticated, IsAdminUser])
#def add_room(request):
#    serializer = RoomSerializer(data=request.data)
#    if serializer.is_valid():
#        serializer.save()
#        return Response({'message': 'Room added successfully!'})
#    return Response(serializer.errors, status=400)


@api_view(['GET'])
def get_rooms(request):
    available_rooms = Room.objects.filter(available=True)
    serializer = RoomSerializer(available_rooms, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_room(request):
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        room = serializer.validated_data.get('room')
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')

        if isinstance(start_time, str):
            start_time = parse_datetime(start_time)
        if isinstance(end_time, str):
            end_time = parse_datetime(end_time)

        if is_naive(start_time): start_time = make_aware(start_time)
        if is_naive(end_time): end_time = make_aware(end_time)

        if end_time <= start_time:
            return Response({'error': 'End time must be after start time.'}, status=400)

        overlapping = Booking.objects.filter(
            room=room,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        if overlapping:
            return Response({'error': 'Room is already booked for this time.'}, status=400)

        # Admins can book for others, normal users book for themselves
        user = request.user
        if request.user.is_staff and 'user_id' in request.data:
            try:
                user = User.objects.get(id=request.data['user_id'])
            except User.DoesNotExist:
                return Response({'error': 'Target user not found.'}, status=404)
        print("Saving booking for user:", user.username)

        serializer.save(user=user)
        return Response({'message': 'Room booked successfully!'}, status=201)
    print("Validation error:", serializer.errors)  # Optional: debug info
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def get_bookings(request):
    user_id = request.GET.get('user_id')  # Optional: filter by user
    bookings = Booking.objects.filter(user_id=user_id) if user_id else Booking.objects.all()
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_booking(request, booking_id):
    print("Trying to delete booking ID:", booking_id)
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.delete()
        return Response({'message': 'Booking deleted successfully!'}, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)


from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, is_naive

@api_view(['PUT', 'PATCH'])
def update_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = BookingSerializer(booking, data=request.data, partial=True)
    if serializer.is_valid():
        start_time = serializer.validated_data.get('start_time', booking.start_time)
        end_time = serializer.validated_data.get('end_time', booking.end_time)
        room = serializer.validated_data.get('room', booking.room)

        if is_naive(start_time): start_time = make_aware(start_time)
        if is_naive(end_time): end_time = make_aware(end_time)

        if end_time <= start_time:
            return Response({'error': 'End time must be after start time.'}, status=status.HTTP_400_BAD_REQUEST)

        overlapping = Booking.objects.filter(
            room=room,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(id=booking.id).exists()

        if overlapping:
            return Response({'error': 'Room is already booked for this time.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({'message': 'Booking updated successfully!'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
