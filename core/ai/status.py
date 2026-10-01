from enum import Enum


class AIAvailability(str, Enum):

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"
    ERROR = "error"
