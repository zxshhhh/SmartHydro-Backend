from rest_framework import generics, status
from rest_framework import viewsets
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

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "message": "Authenticated user details",
        })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAuthenticated]

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            new_password = request.data.get("password")
            if not new_password:
                return Response({"error": "Password required"}, status=400)

            user.set_password(new_password)
            user.save()

            return Response({"message": "Password updated successfully"})

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAuthenticated]

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all().values("id", "username", "email")
        return Response(list(users))

class UserPlantsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            plants = Plant.objects.filter(user=user)

            serializer = PlantSerializer(plants, many=True)
            return Response(serializer.data)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

class PlantListCreateView(generics.ListCreateAPIView):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Plant.objects.all().select_related('user')
        return self.request.user.plants.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PlantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Plant.objects.all()
        return self.request.user.plants.all()

class LatestSensorDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, plant_id):
        try:
            if request.user.is_staff:
                plant = Plant.objects.get(id=plant_id)
            else:
                plant = Plant.objects.get(id=plant_id, user=request.user)
            
            latest = SensorData.objects.filter(plant=plant).first()
            if latest:
                return Response(SensorDataSerializer(latest).data)
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
            # Admin can control any plant, normal user only their own
            if request.user.is_staff:
                plant = Plant.objects.get(id=plant_id)
            else:
                plant = Plant.objects.get(id=plant_id, user=request.user)

            # ... rest of your pump logic (status handling) ...
            status_data = request.data.get('status')
            if status_data is None:
                return Response({"error": "Missing 'status' field"}, status=400)

            new_status = bool(status_data) if isinstance(status_data, (bool, int)) else \
                        str(status_data).lower() in ['true', '1', 'on']

            plant.pump_status = new_status
            plant.save()
            self._simulate_one_reading(plant)

            return Response({
                "message": f"Pump turned {'ON' if new_status else 'OFF'}",
                "pump_status": plant.pump_status
            })

        except Plant.DoesNotExist:
            return Response({"message": "Plant not found"}, status=404)

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