#!/usr/bin/env python3
"""
URL Validator - Usage Examples

This file demonstrates how to use the url_validator package.
"""

from url_validator import URLValidator, URLValidationError


def example_validation():
    """Example: Validating URLs."""
    print("=" * 60)
    print("EXAMPLE 1: URL VALIDATION")
    print("=" * 60)

    validator = URLValidator()

    # Valid URLs
    valid_urls = [
        "https://example.com",
        "http://subdomain.example.com:8080",
        "https://example.com/path/to/resource?query=value#fragment",
        "ftp://ftp.example.com",
        "http://192.168.1.1",
    ]

    print("\nValid URLs:")
    for url in valid_urls:
        is_valid = validator.is_valid(url)
        print(f"  {'✓' if is_valid else '✗'} {url}")

    # Invalid URLs
    invalid_urls = [
        "not a url",
        "http://",
        "example.com",  # Missing scheme
        "javascript:alert(1)",
        "http://example.com:99999",  # Invalid port
    ]

    print("\nInvalid URLs:")
    for url in invalid_urls:
        is_valid = validator.is_valid(url)
        print(f"  {'✓' if is_valid else '✗'} {url}")


def example_parsing():
    """Example: Parsing URLs."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: URL PARSING")
    print("=" * 60)

    validator = URLValidator()

    url = "https://api.example.com:8080/v1/users?limit=10&offset=0#results"

    print(f"\nParsing: {url}\n")

    try:
        parsed = validator.parse(url)

        print(f"Scheme:   {parsed.scheme}")
        print(f"Host:     {parsed.host}")
        print(f"Port:     {parsed.port}")
        print(f"Path:     {parsed.path}")
        print(f"Query:    {parsed.query}")
        print(f"Fragment: {parsed.fragment}")

    except URLValidationError as e:
        print(f"Error: {e}")


def example_normalization():
    """Example: Normalizing URLs."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: URL NORMALIZATION")
    print("=" * 60)

    validator = URLValidator()

    # URLs to normalize
    urls = [
        "HTTP://EXAMPLE.COM/Path/",
        "https://example.com:443/page",
        "http://example.com:80",
        "http://example.com/path/to/page/",
    ]

    print("\nNormalizing URLs:")
    for url in urls:
        try:
            normalized = validator.normalize(url)
            print(f"\n  Original:   {url}")
            print(f"  Normalized: {normalized}")
        except URLValidationError as e:
            print(f"  Error: {e}")


def example_error_handling():
    """Example: Handling validation errors."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: ERROR HANDLING")
    print("=" * 60)

    validator = URLValidator()

    invalid_url = "not a valid url"

    print(f"\nTrying to parse: {invalid_url}")

    try:
        parsed = validator.parse(invalid_url)
        print(f"Parsed successfully: {parsed}")
    except URLValidationError as e:
        print(f"✗ Validation failed: {e}")
        print(f"  Invalid URL was: {e.url}")


def example_practical_use_case():
    """Example: Practical use case - validating user input."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: PRACTICAL USE CASE")
    print("=" * 60)

    validator = URLValidator()

    # Simulating user input (in real app, this would come from form/API)
    user_urls = [
        "https://github.com/anthropics/claude-code",
        "http://localhost:3000",
        "invalid url",
        "http://api.example.com/v1/data?format=json",
    ]

    print("\nValidating user-submitted URLs:")

    valid_urls = []
    invalid_urls = []

    for url in user_urls:
        if validator.is_valid(url):
            valid_urls.append(url)
            print(f"  ✓ {url}")
        else:
            invalid_urls.append(url)
            print(f"  ✗ {url}")

    print(f"\nResults:")
    print(f"  Valid:   {len(valid_urls)}")
    print(f"  Invalid: {len(invalid_urls)}")

    # Process valid URLs
    print(f"\nProcessing valid URLs:")
    for url in valid_urls:
        parsed = validator.parse(url)
        print(f"  Fetching data from {parsed.scheme}://{parsed.host}...")


def main():
    """Run all examples."""
    example_validation()
    example_parsing()
    example_normalization()
    example_error_handling()
    example_practical_use_case()

    print("\n" + "=" * 60)
    print("EXAMPLES COMPLETE")
    print("=" * 60)
    print("\nTry modifying these examples and running them again!")
    print("Check the README.md for more information.\n")


if __name__ == "__main__":
    main()
