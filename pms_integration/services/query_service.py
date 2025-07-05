from django.core.exceptions import ObjectDoesNotExist
from pms_integration.models.booking import Booking
from pms_integration.models.hotel import Hotel


def get_bookings_for_hotel(hotel_id: int):
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except ObjectDoesNotExist:
        return None, "Hotel not found"

    bookings = Booking.objects.filter(hotel=hotel).order_by("-updated_at")
    return bookings, None
