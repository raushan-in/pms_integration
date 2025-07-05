from enum import Enum


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
