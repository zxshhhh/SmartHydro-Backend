from django.db import models
from django.contrib.auth.models import User

class Plant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants')
    name = models.CharField(max_length=100, default="My Smart Plant")
    pump_status = models.BooleanField(default=False, verbose_name="Water Pump ON/OFF")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username}) - Pump: {'ON' if self.pump_status else 'OFF'}"

class SensorData(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='sensor_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    soil_moisture = models.FloatField(help_text="0-100%")
    temperature = models.FloatField(help_text="°C")
    humidity = models.FloatField(help_text="0-100%")

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.plant.name} @ {self.timestamp}"