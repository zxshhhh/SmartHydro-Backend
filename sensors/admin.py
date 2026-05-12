from django.contrib import admin
from .models import Plant, SensorData

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'user', 'pump_status', 'created_at']
    list_filter = ['pump_status', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    raw_id_fields = ['user']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'plant', 'plant_user', 'soil_moisture', 
                   'temperature', 'humidity', 'timestamp']
    list_filter = ['timestamp', 'plant__pump_status']
    search_fields = ['plant__name', 'plant__user__username']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'

    def plant_user(self, obj):
        return obj.plant.user.username if obj.plant and obj.plant.user else "-"
    plant_user.short_description = 'User'
    plant_user.admin_order_field = 'plant__user__username'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('plant', 'plant__user')