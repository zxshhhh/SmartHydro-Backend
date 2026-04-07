from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth.models import User
from .models import SensorData, Plant
from .serializers import PlantSerializer, UserRegistrationSerializer, SensorDataSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

class PlantListCreateView(generics.ListCreateAPIView):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.plants.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PlantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.plants.all()

class LatestSensorDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plant_id):
        try:
            plant = Plant.objects.get(id=plant_id, user=request.user)
            latest = SensorData.objects.filter(plant=plant).first()
            if latest:
                serializer = SensorDataSerializer(latest)
                return Response(serializer.data)
            return Response({"message": "No sensor data yet"}, status=404)
        except Plant.DoesNotExist:
            return Response({"message": "Plant not found"}, status=404)

class SensorDataListView(generics.ListAPIView):
    serializer_class = SensorDataSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            plant = Plant.objects.get(id=self.kwargs['plant_id'], user=self.request.user)
            return SensorData.objects.filter(plant=plant)
        except Plant.DoesNotExist:
            return SensorData.objects.none()

class PumpControlView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, plant_id):
        try:
            plant = Plant.objects.get(id=plant_id, user=request.user)
            new_status = request.data.get('status')
            if new_status is None:
                return Response({"error": "Missing 'status' field"}, status=400)

            plant.pump_status = bool(new_status)
            plant.save()
            self._simulate_one_reading(plant)
            return Response({
                "message": f"Water pump turned {'ON' if plant.pump_status else 'OFF'}",
                "plant_id": plant.id,
                "pump_status": plant.pump_status
            })
        except Plant.DoesNotExist:
            return Response({"message": "Plant not found or not yours"}, status=404)

    def _simulate_one_reading(self, plant):
        """Force one realistic reading right after pump change"""
        latest = SensorData.objects.filter(plant=plant).first()
        last_soil = latest.soil_moisture if latest else 43.0
        last_temp = latest.temperature if latest else 26.0
        last_hum = latest.humidity if latest else 55.0

        import random
        if plant.pump_status:
            soil = min(100.0, last_soil + random.uniform(2.4, 4.2))
            temp = max(15.0, last_temp - random.uniform(0.3, 2.0))
            hum = min(100.0, last_hum + random.uniform(3.0, 8.0))
        else:
            soil = max(0.0, last_soil - random.uniform(1.8, 3.6))
            temp = last_temp + random.uniform(-1.6, 2.1)
            hum = max(30.0, last_hum - random.uniform(3, 8))

        SensorData.objects.create(
            plant=plant,
            soil_moisture=round(soil, 2),
            temperature=round(temp, 2),
            humidity=round(hum, 2)
        )