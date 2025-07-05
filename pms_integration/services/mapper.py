from typing import Any, Dict

from jsonpath_ng import parse as jsonpath_parse
from pms_integration.dtos.booking_dto import BookingDTO
from pms_integration.exceptions import PMSMappingError
from pms_integration.services.data_validator import DataValidator


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
