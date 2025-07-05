import pytest
from pms_integration.exceptions import (
    PMSBusinessRuleError,
    PMSDataValidationError,
    PMSMappingError,
)
from pms_integration.services.mapper import GenericJsonMapper

from .mock_data.sample_config import CONFIG
from .mock_data.sample_payload import (
    INVALID_BUSINESS_LOGIC,
    INVALID_RAW_SCHEMA,
    VALID_RAW_PAYLOAD,
)


def test_valid_mapping():
    mapper = GenericJsonMapper(CONFIG)
    dto = mapper.map(VALID_RAW_PAYLOAD)
    assert dto.booking_id == "ABC123"
    assert dto.status == "confirmed"


def test_missing_required_field():
    mapper = GenericJsonMapper(CONFIG)
    data = VALID_RAW_PAYLOAD.copy()
    del data["reservation"]["confirmationNumber"]
    with pytest.raises(PMSMappingError):  # because confirmationNumber not mapped
        mapper.map(data)


def test_invalid_enum_value():
    mapper = GenericJsonMapper(CONFIG)
    data = VALID_RAW_PAYLOAD.copy()
    data["reservation"]["reservationStatus"]["code"] = "UNKNOWN"
    with pytest.raises(PMSBusinessRuleError):
        mapper.map(data)


def test_invalid_date_format():
    mapper = GenericJsonMapper(CONFIG)
    data = VALID_RAW_PAYLOAD.copy()
    data["reservation"]["roomStay"]["timeSpan"]["start"] = "07/05/2025"  # DD/MM/YYYY
    with pytest.raises(PMSBusinessRuleError):
        mapper.map(data)


def test_raw_schema_violation():
    mapper = GenericJsonMapper(CONFIG)
    with pytest.raises(PMSDataValidationError):
        mapper.map(INVALID_RAW_SCHEMA)


def test_invalid_business_rules():
    mapper = GenericJsonMapper(CONFIG)
    with pytest.raises(PMSBusinessRuleError) as exc_info:
        mapper.map(INVALID_BUSINESS_LOGIC)

    msg = str(exc_info.value)
    assert "Check-out date must be after check-in date" in msg
    assert "Invalid value for 'status'" in msg
