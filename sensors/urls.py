from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import PlantDetailView, PlantListCreateView, RegisterView, LatestSensorDataView, SensorDataListView, PumpControlView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('plants/', PlantListCreateView.as_view(), name='plant-list-create'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('plants/<int:plant_id>/pump/', PumpControlView.as_view(), name='pump-control'),
    path('sensor-data/', LatestSensorDataView.as_view(), name='latest-data'),
    path('sensor-data/latest/', LatestSensorDataView.as_view(), name='latest-data'),
    path('plants/<int:plant_id>/sensor-data/latest/', LatestSensorDataView.as_view(), name='latest-data'),
    path('plants/<int:plant_id>/sensor-data/', SensorDataListView.as_view(), name='sensor-data-list'),
]