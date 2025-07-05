from datetime import datetime
from decimal import Decimal

from pms_integration.enums.status import BookingStatus
from pydantic import BaseModel


class BookingDTO(BaseModel):
    booking_id: str
    guest_name: str
    guest_email: str | None = None
    room_type: str | None = None
    check_in: datetime
    check_out: datetime
    total_amount: Decimal | None = None
    status: BookingStatus
