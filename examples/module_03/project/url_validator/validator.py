"""
URL Validator - Core validation logic.

This module provides the URLValidator class for validating, parsing,
and normalizing URLs according to RFC 3986.
"""

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

from .exceptions import URLValidationError


@dataclass
class ParsedURL:
    """Represents a parsed URL with all components."""

    scheme: str
    host: str
    port: Optional[int]
    path: str
    query: str
    fragment: str

    def __str__(self) -> str:
        """Return string representation of parsed URL."""
        port_str = f":{self.port}" if self.port else ""
        return (
            f"{self.scheme}://{self.host}{port_str}{self.path}"
            f"{'?' + self.query if self.query else ''}"
            f"{'#' + self.fragment if self.fragment else ''}"
        )


class URLValidator:
    """Validate, parse, and normalize URLs."""

    # Regex pattern for URL validation (simplified RFC 3986)
    URL_PATTERN = re.compile(
        r'^(?P<scheme>https?|ftp|ftps)://'  # Scheme
        r'(?P<host>'  # Host
        r'(?:[a-zA-Z0-9\-._~%]+)|'  # Domain name
        r'(?:\[[\da-fA-F:]+\])|'  # IPv6
        r'(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IPv4
        r')'
        r'(?::(?P<port>\d+))?'  # Optional port
        r'(?P<path>/[^\s?#]*)?'  # Optional path
        r'(?:\?(?P<query>[^\s#]*))?'  # Optional query
        r'(?:#(?P<fragment>[^\s]*))?$',  # Optional fragment
        re.IGNORECASE
    )

    def __init__(self):
        """Initialize URL validator."""
        pass

    def is_valid(self, url: str) -> bool:
        """
        Check if URL is valid.

        Args:
            url: URL string to validate

        Returns:
            True if valid, False otherwise

        Examples:
            >>> validator = URLValidator()
            >>> validator.is_valid("https://example.com")
            True
            >>> validator.is_valid("not a url")
            False
        """
        if not url or not isinstance(url, str):
            return False

        if len(url) > 2048:  # Max reasonable URL length
            return False

        # Basic pattern match
        match = self.URL_PATTERN.match(url)
        if not match:
            return False

        # Validate port if present
        if match.group('port'):
            try:
                port = int(match.group('port'))
                if port < 1 or port > 65535:
                    return False
            except ValueError:
                return False

        return True

    def parse(self, url: str) -> ParsedURL:
        """
        Parse URL into components.

        Args:
            url: URL string to parse

        Returns:
            ParsedURL object with all components

        Raises:
            URLValidationError: If URL is invalid

        Examples:
            >>> validator = URLValidator()
            >>> parsed = validator.parse("https://example.com:8080/path?q=1")
            >>> parsed.scheme
            'https'
            >>> parsed.port
            8080
        """
        if not self.is_valid(url):
            raise URLValidationError(f"Invalid URL: {url}", url=url)

        # Use urllib.parse for robust parsing
        parsed = urlparse(url)

        # Extract port (default ports are None)
        port = parsed.port
        if port is None:
            # Check if port was in URL but is default
            if parsed.scheme == 'http' and ':80' in url:
                port = 80
            elif parsed.scheme == 'https' and ':443' in url:
                port = 443

        return ParsedURL(
            scheme=parsed.scheme.lower(),
            host=parsed.hostname or '',
            port=port,
            path=parsed.path or '/',
            query=parsed.query or '',
            fragment=parsed.fragment or ''
        )

    def normalize(self, url: str) -> str:
        """
        Normalize URL to canonical form.

        Normalization includes:
        - Lowercase scheme and host
        - Remove default ports (80 for http, 443 for https)
        - Remove trailing slashes on path
        - Sort query parameters

        Args:
            url: URL string to normalize

        Returns:
            Normalized URL string

        Raises:
            URLValidationError: If URL is invalid

        Examples:
            >>> validator = URLValidator()
            >>> validator.normalize("HTTP://EXAMPLE.COM:80/Path/")
            'http://example.com/path'
        """
        parsed = self.parse(url)

        # Lowercase scheme and host
        scheme = parsed.scheme.lower()
        host = parsed.host.lower()

        # Remove default ports
        port_str = ""
        if parsed.port is not None:
            if not (scheme == 'http' and parsed.port == 80) and \
               not (scheme == 'https' and parsed.port == 443):
                port_str = f":{parsed.port}"

        # Clean path - remove trailing slash unless it's root
        path = parsed.path.rstrip('/') if parsed.path != '/' else '/'

        # Sort query parameters
        query = ""
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            sorted_params = sorted(params.items())
            query = urlencode(sorted_params, doseq=True)

        # Reconstruct URL
        normalized = f"{scheme}://{host}{port_str}{path}"
        if query:
            normalized += f"?{query}"
        if parsed.fragment:
            normalized += f"#{parsed.fragment}"

        return normalized
