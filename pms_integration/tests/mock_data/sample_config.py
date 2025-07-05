CONFIG = {
    "schema_version": "2.1",
    "field_mappings": {
        "booking_id": "$.reservation.confirmationNumber",
        "guest_first_name": "$.guest.profile.firstName",
        "check_in_date": "$.reservation.roomStay.timeSpan.start",
        "check_out_date": "$.reservation.roomStay.timeSpan.end",
        "status": "$.reservation.reservationStatus.code",
    },
    "validation_rules": {
        "required_fields": ["booking_id", "guest_first_name", "check_in_date"],
        "fields": {
            "check_in_date": {"type": "date", "format": "ISO8601"},
            "check_out_date": {"type": "date", "format": "ISO8601"},
            "status": {
                "type": "enum",
                "allowed": ["confirmed", "pending", "cancelled"],
            },
        },
        "business_rules": {"max_booking_days": 365},
    },
}
