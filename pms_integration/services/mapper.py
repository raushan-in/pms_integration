import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional

from jsonpath_ng import parse as jsonpath_parse
from jsonschema import ValidationError
from jsonschema import validate as jsonschema_validate
from pms_integration.dtos.booking_dto import BookingDTO
from pms_integration.exceptions import (
    PMSBusinessRuleError,
    PMSDataValidationError,
    PMSMappingError,
)


class DataValidator:
    """Multi-stage data validation pipeline"""

    def __init__(self, pms_config: dict):
        self.raw_schema = pms_config.get("raw_data_schema")
        self.validation_rules = pms_config.get("validation_rules", {})

    def validate_raw_schema(self, raw_data: dict) -> dict:
        try:
            if self.raw_schema:
                jsonschema_validate(instance=raw_data, schema=self.raw_schema)
            return raw_data
        except ValidationError as e:
            raise PMSDataValidationError(f"Raw schema validation failed: {str(e)}")

    def validate_business_rules(self, mapped_data: dict) -> dict:
        errors = []

        # Required field check
        required_fields = self.validation_rules.get("required_fields", [])
        for field in required_fields:
            if not mapped_data.get(field):
                errors.append(f"Required field '{field}' is missing or empty")

        # Field-level validation
        field_rules = self.validation_rules.get("fields", {})
        for field, rules in field_rules.items():
            val = mapped_data.get(field)

            if rules.get("type") == "date":
                parsed = self._parse_date(val, rules.get("format", "ISO8601"))
                if not parsed:
                    errors.append(f"Invalid date format for field '{field}': {val}")

            elif rules.get("type") == "decimal":
                try:
                    amount = Decimal(str(val))
                    if "min" in rules and amount < Decimal(str(rules["min"])):
                        errors.append(f"{field} below minimum value")
                    if "max" in rules and amount > Decimal(str(rules["max"])):
                        errors.append(f"{field} exceeds maximum value")
                except (InvalidOperation, TypeError):
                    errors.append(f"{field} must be a valid decimal")

            elif rules.get("type") == "enum":
                if val not in rules.get("allowed", []):
                    errors.append(f"Invalid value for '{field}': {val}")

            elif rules.get("type") == "email":
                pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if val and not re.match(pattern, val):
                    errors.append(f"Invalid email format: {val}")

        # Business logic
        check_in = self._parse_date(mapped_data.get("check_in"), "ISO8601")
        check_out = self._parse_date(mapped_data.get("check_out"), "ISO8601")
        if check_in and check_out:
            if check_out <= check_in:
                errors.append("Check-out date must be after check-in date")

            max_days = self.validation_rules.get("business_rules", {}).get(
                "max_booking_days", 365
            )
            if (check_out - check_in).days > max_days:
                errors.append(f"Booking duration exceeds {max_days} days")

        if errors:
            raise PMSBusinessRuleError("; ".join(errors))

        return mapped_data

    def sanitize_data(self, mapped_data: dict) -> dict:
        sanitized = {}
        for key, value in mapped_data.items():
            if isinstance(value, str):
                value = value.strip()
                value = value.replace("<", "&lt;").replace(">", "&gt;")
                if value == "":
                    value = None
            sanitized[key] = value
        return sanitized

    def _parse_date(self, value: Optional[str], fmt: str) -> Optional[date]:
        if not value or not isinstance(value, str):
            return None

        formats = {
            "ISO8601": "%Y-%m-%dT%H:%M:%S",
            "YYYY-MM-DD": "%Y-%m-%d",
            "DD/MM/YYYY": "%d/%m/%Y",
            "MM/DD/YYYY": "%m/%d/%Y",
        }

        pattern = formats.get(fmt)
        if not pattern:
            return None

        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            return None


class GenericJsonMapper:
    """Maps raw PMS data to internal DTO using config rules"""

    def __init__(self, config: dict):
        self.config = config
        self.validator = DataValidator(config)
        self.status_mappings = config.get("status_mappings", {})

    def map(self, raw: dict) -> BookingDTO:
        raw = self.validator.validate_raw_schema(raw)

        mapped: Dict[str, Any] = {}
        field_mappings = self.config.get("field_mappings", {})

        for field, mapping_config in field_mappings.items():
            try:
                value = self._resolve_field(mapping_config, raw)
                mapped[field] = value
            except Exception as e:
                raise PMSMappingError(f"Failed to map field '{field}': {e}")

        mapped = self.validator.validate_business_rules(mapped)
        mapped = self.validator.sanitize_data(mapped)

        try:
            return BookingDTO(**mapped)
        except Exception as e:
            raise PMSMappingError(f"Failed to create BookingDTO: {e}")

    def _resolve_field(self, config: Any, data: dict) -> Any:
        if isinstance(config, str):
            return self._extract(data, config)

        if isinstance(config, dict):
            if "template" in config and "fields" in config:
                resolved_fields = {
                    k: self._extract(data, v) for k, v in config["fields"].items()
                }
                return config["template"].format(**resolved_fields)

            if "path" in config:
                value = self._extract(data, config["path"])
                if transform := config.get("transform"):
                    return self._apply_transform(value, transform)
                return value

        raise PMSMappingError("Invalid mapping configuration")

    def _extract(self, data: dict, path: str) -> Any:
        try:
            result = jsonpath_parse(path).find(data)
            return result[0].value if result else None
        except Exception as e:
            raise PMSMappingError(f"JSONPath '{path}' failed: {e}")

    def _apply_transform(self, value: Any, transform: str) -> Any:
        if transform == "parse_date":
            return self._parse_date(value, "ISO8601")
        elif transform == "map_status":
            return self.status_mappings.get(value, None)
        return value
