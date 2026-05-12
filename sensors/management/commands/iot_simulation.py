import time
import random
from django.utils import timezone
from datetime import datetime
from django.core.management.base import BaseCommand
from sensors.models import Plant, SensorData

class Command(BaseCommand):
    help = 'Realistic IoT simulation with Manual / Automatic / Schedule modes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 IoT Simulation Started - Multi Mode Support'))
        self.stdout.write('Modes: Manual | Automatic | Schedule')

        while True:
            plants = Plant.objects.all()
            
            if not plants.exists():
                self.stdout.write(self.style.WARNING('No plants found. Waiting...'))
                time.sleep(5)
                continue

            for plant in plants:
                try:
                    # Get latest sensor data
                    latest = SensorData.objects.filter(plant=plant).first()
                    last_soil = latest.soil_moisture if latest else 45.0
                    last_temp = latest.temperature if latest else 26.0
                    last_hum = latest.humidity if latest else 55.0

                    pump_was_on = plant.pump_status
                    new_pump_status = plant.pump_status

                    # ====================== MODE LOGIC ======================
                    if plant.mode == 'automatic':
                        if last_soil < plant.moisture_threshold:
                            new_pump_status = True
                        else:
                            new_pump_status = False

                    elif plant.mode == 'schedule':
                        now = timezone.now()
                        if plant.schedule_time:
                            schedule_datetime = timezone.make_aware(
                                datetime.combine(
                                    now.date(),
                                    plant.schedule_time
                                )
                            )

                            elapsed = (now - schedule_datetime).total_seconds()

                            new_pump_status = (
                                0 <= elapsed <= plant.schedule_duration
                            )

                        else:
                            if not plant.last_watered:
                                plant.last_watered = now
                                plant.save()

                            elapsed = (
                                now - plant.last_watered
                            ).total_seconds()

                            if plant.pump_status:
                                if elapsed >= plant.schedule_duration:
                                    new_pump_status = False

                            else:
                                if elapsed >= plant.schedule_interval:
                                    new_pump_status = True
                                    plant.last_watered = now
                                    plant.save()

                    # Manual mode: Do nothing (user controls manually)

                    # Update pump status if it changed
                    if new_pump_status != pump_was_on:
                        plant.pump_status = new_pump_status
                        plant.save()

                    # ====================== SENSOR SIMULATION ======================
                    if plant.pump_status:  # Watering
                        soil = min(98.0, last_soil + random.uniform(2.0, 5.5))
                        temp = max(16.0, last_temp - random.uniform(1.2, 4.1))
                        hum = min(98.0, last_hum + random.uniform(3.0, 7.5))
                        status_str = f"💧 {plant.get_mode_display() or plant.mode} (ON)"
                    else:  # Drying
                        soil = max(10.0, last_soil - random.uniform(1.4, 4.0))
                        temp = min(45.0, last_temp + random.uniform(1.5, 4.1))
                        hum = max(30.0, last_hum - random.uniform(2.5, 6.5))
                        status_str = f"🌵 {plant.get_mode_display() or plant.mode} (OFF)"

                    # Save new sensor reading
                    SensorData.objects.create(
                        plant=plant,
                        soil_moisture=round(soil, 2),
                        temperature=round(temp, 2),
                        humidity=round(hum, 2),
                    )

                    self.stdout.write(
                        f"{status_str} → {plant.name} | "
                        f"🌱 {soil:.1f}% | 🌡️ {temp:.1f}°C | 💧 {hum:.1f}%"
                    )

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error simulating plant {plant.name}: {e}'))

            time.sleep(2)