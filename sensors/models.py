from django.db import models
from django.contrib.auth.models import User

WATERING_MODES = (
    ('manual', 'Manual'),
    ('automatic', 'Automatic'),
    ('schedule', 'Scheduled'),
)

class Plant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants')
    name = models.CharField(max_length=100, default="My Smart Plant")
    mode = models.CharField(max_length=20, choices=WATERING_MODES, default='manual')
    pump_status = models.BooleanField(default=False, verbose_name="Water Pump ON/OFF")
    moisture_threshold = models.FloatField(default=30.0, help_text="Turn on pump if soil moisture < this value (%)")
    schedule_time = models.TimeField(null=True, blank=True, help_text="Example: 07:00 or 18:30")
    schedule_interval = models.IntegerField(default=3600, help_text="How often to water (seconds)")
    schedule_duration = models.IntegerField(default=10, help_text="Pump ON duration (seconds)")
    last_watered = models.IntegerField(null=True, blank=True, help_text="Timestamp of last watering")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username}) - {self.get_mode_display()}"

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