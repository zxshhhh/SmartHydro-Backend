from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Plant, SensorData

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

class PlantSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)
    class Meta:
        model = Plant
        fields = ['id', 'name', 'user_username', 'mode', 'mode_display', 'pump_status', 'moisture_threshold', 'schedule_interval', 'schedule_duration', 'schedule_time', 'created_at']
        read_only_fields = ['created_at']

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['id', 'timestamp', 'soil_moisture', 'temperature', 'humidity']