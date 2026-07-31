class APIRequestError(Exception):
    """Raised when an API request fails due to connection issues or timeouts."""

    pass


class InvalidResponseError(Exception):
    """Raised when an API response is invalid or missing required data."""

    pass


class SchemaValidationError(Exception):
    """Raised when an API response fails schema validation."""

    pass
