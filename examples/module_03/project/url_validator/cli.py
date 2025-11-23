#!/usr/bin/env python3
"""
URL Validator CLI - Command-line interface for URL validation.

Provides commands for validating, parsing, and normalizing URLs.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .validator import URLValidator
from .exceptions import URLValidationError


def validate_command(args: argparse.Namespace) -> int:
    """
    Validate a URL.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = valid, 1 = invalid)
    """
    validator = URLValidator()

    if validator.is_valid(args.url):
        print(f"✓ Valid URL: {args.url}")
        return 0
    else:
        print(f"✗ Invalid URL: {args.url}", file=sys.stderr)
        return 1


def parse_command(args: argparse.Namespace) -> int:
    """
    Parse and display URL components.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    validator = URLValidator()

    try:
        parsed = validator.parse(args.url)

        print(f"Parsed URL: {args.url}")
        print(f"  Scheme:   {parsed.scheme}")
        print(f"  Host:     {parsed.host}")
        print(f"  Port:     {parsed.port if parsed.port else '(default)'}")
        print(f"  Path:     {parsed.path}")
        print(f"  Query:    {parsed.query if parsed.query else '(none)'}")
        print(f"  Fragment: {parsed.fragment if parsed.fragment else '(none)'}")

        return 0

    except URLValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def normalize_command(args: argparse.Namespace) -> int:
    """
    Normalize a URL.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    validator = URLValidator()

    try:
        normalized = validator.normalize(args.url)
        print(normalized)
        return 0

    except URLValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def batch_command(args: argparse.Namespace) -> int:
    """
    Process a file of URLs (one per line).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 = success, 1 = error)
    """
    validator = URLValidator()

    # Read URLs from file
    try:
        urls = Path(args.file).read_text(encoding='utf-8').strip().split('\n')
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Process each URL
    results = []
    for i, url in enumerate(urls, 1):
        url = url.strip()
        if not url or url.startswith('#'):  # Skip empty lines and comments
            continue

        is_valid = validator.is_valid(url)
        results.append({
            'line': i,
            'url': url,
            'valid': is_valid
        })

        # Print progress
        status = "✓" if is_valid else "✗"
        print(f"{status} {url}")

    # Summary
    valid_count = sum(1 for r in results if r['valid'])
    total_count = len(results)
    print(f"\nProcessed {total_count} URLs: {valid_count} valid, {total_count - valid_count} invalid")

    return 0


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="URL Validator - Validate, parse, and normalize URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  url-validator validate "https://example.com"
  url-validator parse "https://example.com:8080/path?q=1"
  url-validator normalize "HTTP://EXAMPLE.COM/Path/"
  url-validator batch urls.txt

For more information: https://github.com/yourusername/url-validator
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version="url-validator 1.0.0"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a URL",
        description="Check if a URL is valid"
    )
    validate_parser.add_argument("url", help="URL to validate")

    # parse command
    parse_parser = subparsers.add_parser(
        "parse",
        help="Parse a URL",
        description="Parse URL and show components"
    )
    parse_parser.add_argument("url", help="URL to parse")

    # normalize command
    normalize_parser = subparsers.add_parser(
        "normalize",
        help="Normalize a URL",
        description="Normalize URL to canonical form"
    )
    normalize_parser.add_argument("url", help="URL to normalize")

    # batch command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Process file of URLs",
        description="Process a file containing URLs (one per line)"
    )
    batch_parser.add_argument("file", help="File containing URLs")

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == "validate":
        return validate_command(args)
    elif args.command == "parse":
        return parse_command(args)
    elif args.command == "normalize":
        return normalize_command(args)
    elif args.command == "batch":
        return batch_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
