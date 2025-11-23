"""Custom exceptions for URL validation."""


class URLValidationError(ValueError):
    """Raised when a URL is invalid."""

    def __init__(self, message: str, url: str = None):
        self.url = url
        super().__init__(message)
