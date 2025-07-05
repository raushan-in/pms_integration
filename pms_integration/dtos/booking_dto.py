from pydantic import BaseModel
from datetime import datetime
from pms_integration.enums.status import BookingStatus

class BookingDTO(BaseModel):
    booking_id: str
    guest_first_name: str
    check_in: datetime
    check_out: datetime
    status: BookingStatus
