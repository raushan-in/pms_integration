from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pms_integration.services.query_service import get_bookings_for_hotel
from pms_integration.serializers.booking_serializer import BookingSerializer

class BookingListView(APIView):
    def get(self, request):
        hotel_id = request.query_params.get("hotel_id")

        if not hotel_id or not hotel_id.isdigit():
            return Response({"error": "Invalid or missing hotel_id"}, status=status.HTTP_400_BAD_REQUEST)

        bookings, error = get_bookings_for_hotel(int(hotel_id))
        if error:
            return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)

        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)