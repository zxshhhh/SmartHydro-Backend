import time
import random
from django.core.management.base import BaseCommand
from sensors.models import Plant, SensorData

class Command(BaseCommand):
    help = 'Realistic IoT simulation: reacts to water pump ON/OFF'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Realistic IoT Simulation Started (Pump-aware)'))
        self.stdout.write('Pump ON → soil moisture rises fast | Pump OFF → soil dries slowly')

        while True:
            plants = Plant.objects.all()
            if not plants:
                self.stdout.write(self.style.WARNING('No plants yet. Create one via API.'))
                time.sleep(5)
                continue

            for plant in plants:
                # Get last reading or use safe defaults
                latest = SensorData.objects.filter(plant=plant).first()
                last_soil = latest.soil_moisture if latest else 45.0
                last_temp = latest.temperature if latest else 26.0
                last_hum = latest.humidity if latest else 55.0

                # Simulate based on pump status
                if plant.pump_status:  # WATERING
                    soil = min(100.0, last_soil + random.uniform(2.1, 3.8))
                    temp = max(16.0, last_temp - random.uniform(0.8, 2.2))
                    hum = min(100.0, last_hum + random.uniform(2.4, 4.4))
                    status_str = "💧 PUMP ON"
                else:  # DRYING
                    soil = max(10.0, last_soil - random.uniform(1.5, 4.5))
                    temp = last_temp + random.uniform(-1.01, 1.5)
                    hum = max(30.0, last_hum - random.uniform(2.5, 7.0))
                    status_str = "🌵 PUMP OFF"

                SensorData.objects.create(
                    plant=plant,
                    soil_moisture=round(soil, 2),
                    temperature=round(temp, 2),
                    humidity=round(hum, 2),
                )

                self.stdout.write(
                    f"{status_str} → {plant.name} | "
                    f"🌱 {soil}% | 🌡️ {temp}°C | 💧 {hum}%"
                )

            time.sleep(6)   # Realistic update every 6 seconds