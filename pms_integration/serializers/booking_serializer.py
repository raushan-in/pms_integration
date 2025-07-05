from rest_framework import serializers
from pms_integration.models.booking import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "booking_id",
            "guest_name",
            "check_in",
            "check_out",
            "status",
            "total_amount",
        ]