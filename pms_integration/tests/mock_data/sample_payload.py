VALID_RAW_PAYLOAD = {
    "reservation": {
        "confirmationNumber": "ABC123",
        "roomStay": {
            "timeSpan": {"start": "2025-07-01T14:00:00", "end": "2025-07-03T11:00:00"}
        },
        "reservationStatus": {"code": "confirmed"},
    },
    "guest": {"profile": {"firstName": "John", "lastName": "Doe"}},
}

INVALID_RAW_SCHEMA = {
    "reservation": {"roomStay": {}},  # Missing timeSpan
    "guest": {"profile": {"firstName": "John"}},
}

INVALID_BUSINESS_LOGIC = {
    "reservation": {
        "confirmationNumber": "ABC123",
        "roomStay": {
            "timeSpan": {
                "start": "2025-07-10T14:00:00",  # check-in
                "end": "2024-07-01T11:00:00",  # check-out before check-in
            }
        },
        "reservationStatus": {"code": "invalid_code"},  # invalid status
    },
    "guest": {"profile": {"firstName": "John"}},
}
