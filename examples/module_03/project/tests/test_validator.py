"""
Tests for URLValidator class.

Comprehensive test suite covering valid URLs, invalid URLs, edge cases,
parsing, normalization, and error handling.
"""

import pytest
from url_validator import URLValidator, ParsedURL, URLValidationError


@pytest.fixture
def validator():
    """Create URLValidator instance for tests."""
    return URLValidator()


class TestValidation:
    """Tests for is_valid() method."""

    def test_valid_http_url(self, validator):
        """Test validation of basic HTTP URLs."""
        assert validator.is_valid("http://example.com") is True
        assert validator.is_valid("http://www.example.com") is True
        assert validator.is_valid("http://subdomain.example.com") is True

    def test_valid_https_url(self, validator):
        """Test validation of HTTPS URLs."""
        assert validator.is_valid("https://example.com") is True
        assert validator.is_valid("https://secure.example.com") is True

    def test_valid_url_with_port(self, validator):
        """Test validation of URLs with port numbers."""
        assert validator.is_valid("http://example.com:8080") is True
        assert validator.is_valid("https://example.com:443") is True
        assert validator.is_valid("http://localhost:3000") is True

    def test_valid_url_with_path(self, validator):
        """Test validation of URLs with paths."""
        assert validator.is_valid("http://example.com/path") is True
        assert validator.is_valid("http://example.com/path/to/resource") is True
        assert validator.is_valid("http://example.com/path-with-dashes") is True

    def test_valid_url_with_query(self, validator):
        """Test validation of URLs with query strings."""
        assert validator.is_valid("http://example.com?query=value") is True
        assert validator.is_valid("http://example.com?a=1&b=2") is True
        assert validator.is_valid("http://example.com/path?query=value") is True

    def test_valid_url_with_fragment(self, validator):
        """Test validation of URLs with fragments."""
        assert validator.is_valid("http://example.com#section") is True
        assert validator.is_valid("http://example.com/path#top") is True

    def test_valid_url_complete(self, validator):
        """Test validation of complete URL with all components."""
        url = "https://example.com:8080/path?query=value#fragment"
        assert validator.is_valid(url) is True

    def test_valid_ipv4_url(self, validator):
        """Test validation of URLs with IPv4 addresses."""
        assert validator.is_valid("http://192.168.1.1") is True
        assert validator.is_valid("http://127.0.0.1:8080") is True

    def test_valid_ipv6_url(self, validator):
        """Test validation of URLs with IPv6 addresses."""
        assert validator.is_valid("http://[::1]") is True
        assert validator.is_valid("http://[2001:db8::1]") is True

    def test_valid_ftp_url(self, validator):
        """Test validation of FTP URLs."""
        assert validator.is_valid("ftp://ftp.example.com") is True
        assert validator.is_valid("ftps://secure.example.com") is True

    def test_invalid_no_scheme(self, validator):
        """Test that URLs without scheme are invalid."""
        assert validator.is_valid("example.com") is False
        assert validator.is_valid("www.example.com") is False

    def test_invalid_wrong_scheme(self, validator):
        """Test that URLs with invalid schemes are invalid."""
        assert validator.is_valid("javascript:alert(1)") is False
        assert validator.is_valid("data:text/plain,hello") is False

    def test_invalid_no_host(self, validator):
        """Test that URLs without host are invalid."""
        assert validator.is_valid("http://") is False
        assert validator.is_valid("https://") is False

    def test_invalid_malformed(self, validator):
        """Test that malformed URLs are invalid."""
        assert validator.is_valid("not a url") is False
        assert validator.is_valid("http:/example.com") is False
        assert validator.is_valid("http:///example.com") is False

    def test_invalid_port(self, validator):
        """Test that URLs with invalid ports are invalid."""
        assert validator.is_valid("http://example.com:99999") is False
        assert validator.is_valid("http://example.com:0") is False
        assert validator.is_valid("http://example.com:-1") is False

    def test_invalid_empty(self, validator):
        """Test that empty string is invalid."""
        assert validator.is_valid("") is False

    def test_invalid_none(self, validator):
        """Test that None is invalid."""
        assert validator.is_valid(None) is False

    def test_invalid_too_long(self, validator):
        """Test that extremely long URLs are invalid."""
        long_url = "http://example.com/" + "a" * 3000
        assert validator.is_valid(long_url) is False


class TestParsing:
    """Tests for parse() method."""

    def test_parse_basic_url(self, validator):
        """Test parsing basic URL."""
        parsed = validator.parse("http://example.com")
        assert parsed.scheme == "http"
        assert parsed.host == "example.com"
        assert parsed.port is None
        assert parsed.path == "/"

    def test_parse_url_with_port(self, validator):
        """Test parsing URL with port."""
        parsed = validator.parse("http://example.com:8080")
        assert parsed.port == 8080

    def test_parse_url_with_path(self, validator):
        """Test parsing URL with path."""
        parsed = validator.parse("http://example.com/path/to/resource")
        assert parsed.path == "/path/to/resource"

    def test_parse_url_with_query(self, validator):
        """Test parsing URL with query string."""
        parsed = validator.parse("http://example.com?a=1&b=2")
        assert "a=" in parsed.query
        assert "b=" in parsed.query

    def test_parse_url_with_fragment(self, validator):
        """Test parsing URL with fragment."""
        parsed = validator.parse("http://example.com#section")
        assert parsed.fragment == "section"

    def test_parse_complete_url(self, validator):
        """Test parsing complete URL."""
        url = "https://example.com:8080/path?query=value#fragment"
        parsed = validator.parse(url)
        assert parsed.scheme == "https"
        assert parsed.host == "example.com"
        assert parsed.port == 8080
        assert parsed.path == "/path"
        assert "query=value" in parsed.query
        assert parsed.fragment == "fragment"

    def test_parse_invalid_url_raises_error(self, validator):
        """Test that parsing invalid URL raises error."""
        with pytest.raises(URLValidationError):
            validator.parse("not a url")

    def test_parse_empty_raises_error(self, validator):
        """Test that parsing empty string raises error."""
        with pytest.raises(URLValidationError):
            validator.parse("")


class TestNormalization:
    """Tests for normalize() method."""

    def test_normalize_lowercase_scheme(self, validator):
        """Test normalization lowercases scheme."""
        assert validator.normalize("HTTP://example.com") == "http://example.com"
        assert validator.normalize("HTTPS://example.com") == "https://example.com"

    def test_normalize_lowercase_host(self, validator):
        """Test normalization lowercases host."""
        assert validator.normalize("http://EXAMPLE.COM") == "http://example.com"
        assert validator.normalize("http://Example.Com") == "http://example.com"

    def test_normalize_remove_default_port(self, validator):
        """Test normalization removes default ports."""
        assert validator.normalize("http://example.com:80") == "http://example.com"
        assert validator.normalize("https://example.com:443") == "https://example.com"

    def test_normalize_keep_non_default_port(self, validator):
        """Test normalization keeps non-default ports."""
        assert "8080" in validator.normalize("http://example.com:8080")

    def test_normalize_remove_trailing_slash(self, validator):
        """Test normalization removes trailing slash from path."""
        normalized = validator.normalize("http://example.com/path/")
        assert normalized == "http://example.com/path"

    def test_normalize_keep_root_slash(self, validator):
        """Test normalization keeps root slash."""
        normalized = validator.normalize("http://example.com/")
        assert normalized.endswith("/") or normalized == "http://example.com"

    def test_normalize_invalid_raises_error(self, validator):
        """Test that normalizing invalid URL raises error."""
        with pytest.raises(URLValidationError):
            validator.normalize("not a url")


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_url_with_hyphens_in_domain(self, validator):
        """Test URLs with hyphens in domain name."""
        assert validator.is_valid("http://my-domain.com") is True

    def test_url_with_underscores_in_domain(self, validator):
        """Test URLs with underscores in domain name."""
        assert validator.is_valid("http://my_domain.com") is True

    def test_url_with_numbers_in_domain(self, validator):
        """Test URLs with numbers in domain name."""
        assert validator.is_valid("http://example123.com") is True

    def test_url_with_multiple_subdomains(self, validator):
        """Test URLs with multiple subdomains."""
        assert validator.is_valid("http://a.b.c.example.com") is True

    def test_url_with_special_chars_in_path(self, validator):
        """Test URLs with special characters in path."""
        assert validator.is_valid("http://example.com/path%20with%20spaces") is True

    def test_url_with_special_chars_in_query(self, validator):
        """Test URLs with special characters in query."""
        assert validator.is_valid("http://example.com?name=value%20with%20space") is True
