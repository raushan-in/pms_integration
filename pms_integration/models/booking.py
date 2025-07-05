from django.db import models
from pms_integration.models.hotel import Hotel
from pms_integration.models.room import Room

from decimal import Decimal

class Booking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, null=True, blank=True, on_delete=models.SET_NULL)
    booking_id = models.CharField(max_length=100)
    guest_name = models.CharField(max_length=255)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('hotel', 'booking_id')

    def __str__(self):
        return f"Booking {self.booking_id} ({self.guest_name})"