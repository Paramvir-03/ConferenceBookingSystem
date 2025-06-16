from rest_framework import serializers
from .models import Room, Booking
from django.contrib.auth.models import User
from django.utils.timezone import localtime

from rest_framework import serializers
from .models import CustomUser  # Assuming you're using a custom user model

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'is_staff']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source='room.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    start_time_local = serializers.SerializerMethodField()
    end_time_local = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'user_email',
            'room',
            'room_name',
            'start_time',
            'start_time_local',  # Localized for UI
            'end_time',
            'end_time_local'     # Localized for UI
        ]

    def get_start_time_local(self, obj):
        return localtime(obj.start_time).strftime('%Y-%m-%d %H:%M')

    def get_end_time_local(self, obj):
        return localtime(obj.end_time).strftime('%Y-%m-%d %H:%M')
