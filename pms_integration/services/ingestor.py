from typing import Optional

from django.db import transaction
from pms_integration.dtos.booking_dto import BookingDTO
from pms_integration.models.booking import Booking
from pms_integration.models.guest import Guest
from pms_integration.models.room import Room


class BookingIngestor:
    def __init__(self, hotel_id: int):
        self.hotel_id = hotel_id

    def save_booking(self, dto: BookingDTO) -> Optional[Booking]:
        """
        Upserts a Booking for the given hotel.
        """
        with transaction.atomic():
            guest, _ = Guest.objects.get_or_create(
                name=dto.guest_name, email=dto.guest_email or None
            )

            room, _ = Room.objects.get_or_create(
                hotel_id=self.hotel_id, room_type=dto.room_type or "Standard"
            )

            booking, created = Booking.objects.update_or_create(
                hotel_id=self.hotel_id,
                booking_id=dto.booking_id,
                defaults={
                    "guest": guest,
                    "room": room,
                    "check_in": dto.check_in_date,
                    "check_out": dto.check_out_date,
                    "status": dto.status,
                    "total_amount": dto.total_amount,
                },
            )
            return booking
