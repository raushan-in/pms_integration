from datetime import datetime, timedelta

from django.urls import reverse
from pms_integration.models.booking import Booking
from pms_integration.models.hotel import Hotel
from rest_framework import status
from rest_framework.test import APITestCase


class BookingAPITestCase(APITestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Hotel Test", pms_type="mock", pms_version="v1"
        )

        Booking.objects.create(
            booking_id="B001",
            hotel=self.hotel,
            guest_first_name="John",
            check_in=datetime.now(),
            check_out=datetime.now() + timedelta(days=2),
            status="confirmed",
        )
        Booking.objects.create(
            booking_id="B002",
            hotel=self.hotel,
            guest_first_name="Jane",
            check_in=datetime.now(),
            check_out=datetime.now() + timedelta(days=3),
            status="pending",
        )

    def test_get_bookings(self):
        url = reverse("booking-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["booking_id"], "B001")
