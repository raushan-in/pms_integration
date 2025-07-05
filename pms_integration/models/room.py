from django.db import models
from pms_integration.models.hotel import Hotel


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=50)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"
