from typing import List

from django.db import transaction
from pms_integration.dtos.booking_dto import BookingDTO
from pms_integration.models.booking import Booking


def bulk_upsert_bookings(hotel, booking_dtos: List[BookingDTO]):
    existing = Booking.objects.filter(
        hotel=hotel, booking_id__in=[b.booking_id for b in booking_dtos]
    )
    existing_map = {b.booking_id: b for b in existing}

    to_create = []
    to_update = []

    for dto in booking_dtos:
        if dto.booking_id in existing_map:
            booking = existing_map[dto.booking_id]
            booking.guest_name = dto.guest_name
            booking.check_in = dto.check_in
            booking.check_out = dto.check_out
            booking.status = dto.status
            booking.total_amount = dto.total_amount
            to_update.append(booking)
        else:
            to_create.append(
                Booking(
                    hotel=hotel,
                    booking_id=dto.booking_id,
                    guest_name=dto.guest_name,
                    check_in=dto.check_in,
                    check_out=dto.check_out,
                    status=dto.status,
                    total_amount=dto.total_amount,
                )
            )

    with transaction.atomic():
        if to_create:
            Booking.objects.bulk_create(to_create)
        for booking in to_update:
            booking.save()
