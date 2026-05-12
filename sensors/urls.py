from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ChangePasswordView, CurrentUserView, PlantDetailView, PlantListCreateView, RegisterView, LatestSensorDataView, SensorDataListView, PumpControlView, UserListView, UserViewSet, UserPlantsView, UserDetailView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserListView.as_view(), name='users'),
    path("users/me/", CurrentUserView.as_view()),
    path('users/<int:user_id>/change-password/', ChangePasswordView.as_view()),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:user_id>/plants/', UserPlantsView.as_view(), name='user-plants'),
    path('plants/', PlantListCreateView.as_view(), name='plant-list-create'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),
    path('plants/<int:plant_id>/pump/', PumpControlView.as_view(), name='pump-control'),
    path('sensor-data/', LatestSensorDataView.as_view(), name='latest-data'),
    path('sensor-data/latest/', LatestSensorDataView.as_view(), name='latest-data'),
    path('plants/<int:plant_id>/sensor-data/latest/', LatestSensorDataView.as_view(), name='latest-data'),
    path('plants/<int:plant_id>/sensor-data/', SensorDataListView.as_view(), name='sensor-data-list'),
]