class PMSIntegrationError(Exception):
    """Base class for all PMS integration errors."""
    pass

class PMSConnectionError(PMSIntegrationError):
    """Raised when connection to the PMS fails."""
    pass

class PMSDataValidationError(PMSIntegrationError):
    """Raised when required PMS fields are missing or malformed."""
    pass

class PMSMappingError(PMSIntegrationError):
    """Raised when the PMS data can't be mapped to internal format."""
    pass

class PMSBusinessRuleError(PMSIntegrationError):
    """Raised when domain-specific business rules are violated."""
    pass
