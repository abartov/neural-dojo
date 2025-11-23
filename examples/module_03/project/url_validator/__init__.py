"""
URL Validator - A comprehensive URL validation and parsing library.

This package provides tools for validating, parsing, and normalizing URLs
according to RFC 3986.
"""

from .validator import URLValidator, ParsedURL
from .exceptions import URLValidationError

__version__ = "1.0.0"
__all__ = ["URLValidator", "ParsedURL", "URLValidationError"]
