# URL Validator - AI-Generated Python Package

**Module 3 Deliverable**: A complete Python package generated with AI assistance.

## What This Demonstrates

This package showcases **everything you learned** in Module 3:
- ✅ Code generation from specifications
- ✅ Test suite generation
- ✅ CLI tool creation
- ✅ Documentation generation
- ✅ Production-ready error handling
- ✅ Type hints and best practices

**Time to build**: 4-6 hours with AI assistance (would be 20+ hours manually!)

---

## Installation

```bash
# Install in development mode
pip install -e .

# Or install from PyPI (when published)
pip install url-validator
```

## Quick Start

### As a Library

```python
from url_validator import URLValidator

validator = URLValidator()

# Validate URLs
if validator.is_valid("https://example.com"):
    print("Valid URL!")

# Parse URLs
parsed = validator.parse("https://example.com:8080/path?query=value#fragment")
print(f"Scheme: {parsed.scheme}")
print(f"Host: {parsed.host}")
print(f"Port: {parsed.port}")
print(f"Path: {parsed.path}")

# Normalize URLs
normalized = validator.normalize("HTTP://EXAMPLE.COM/Path/")
# Returns: "http://example.com/path"
```

### As a CLI

```bash
# Validate a URL
url-validator validate "https://example.com"
# ✓ Valid URL

# Parse a URL
url-validator parse "https://example.com:8080/path"
# Scheme: https
# Host: example.com
# Port: 8080
# Path: /path

# Normalize a URL
url-validator normalize "HTTP://EXAMPLE.COM/Path/"
# http://example.com/path

# Process file of URLs
url-validator batch urls.txt
```

---

## Features

### URL Validation
- ✅ RFC 3986 compliant
- ✅ Supports http, https, ftp, ftps
- ✅ International domains (IDN)
- ✅ IPv4 and IPv6 addresses
- ✅ Validates port numbers
- ✅ Checks path, query, fragment

### URL Parsing
- Extracts all components (scheme, host, port, path, query, fragment)
- Handles edge cases (missing ports, empty paths, etc.)
- Type-safe with dataclasses

### URL Normalization
- Lowercases scheme and host
- Removes default ports (80 for http, 443 for https)
- Removes trailing slashes
- Sorts query parameters
- Handles percent-encoding

---

## API Reference

### `URLValidator`

Main validator class.

#### Methods

##### `is_valid(url: str) -> bool`
Check if URL is valid.

```python
validator.is_valid("https://example.com")  # True
validator.is_valid("not a url")             # False
```

##### `parse(url: str) -> ParsedURL`
Parse URL into components.

```python
parsed = validator.parse("https://example.com:8080/path?q=1#top")
# ParsedURL(scheme='https', host='example.com', port=8080, ...)
```

Raises `URLValidationError` if URL is invalid.

##### `normalize(url: str) -> str`
Normalize URL to canonical form.

```python
validator.normalize("HTTP://EXAMPLE.COM:80/Path/")
# Returns: "http://example.com/path"
```

### `ParsedURL`

Dataclass representing parsed URL components.

**Attributes**:
- `scheme: str` - URL scheme (http, https, etc.)
- `host: str` - Hostname or IP address
- `port: Optional[int]` - Port number (None if default)
- `path: str` - URL path
- `query: str` - Query string
- `fragment: str` - Fragment/anchor

### Exceptions

##### `URLValidationError`
Raised when URL is invalid.

```python
try:
    validator.parse("invalid url")
except URLValidationError as e:
    print(f"Invalid URL: {e}")
```

---

## CLI Reference

### `validate`
Check if URL is valid.

```bash
url-validator validate <url>
```

**Exit codes**:
- `0` - Valid URL
- `1` - Invalid URL

### `parse`
Show URL components.

```bash
url-validator parse <url>
```

### `normalize`
Normalize URL.

```bash
url-validator normalize <url>
```

### `batch`
Process file of URLs (one per line).

```bash
url-validator batch <file>

# Options:
--output FILE    Write results to file
--format FORMAT  Output format (text, json, csv)
```

---

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/url-validator
cd url-validator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=url_validator --cov-report=html

# Run specific test
pytest tests/test_validator.py::test_valid_urls
```

### Code Quality

```bash
# Format code
black url_validator tests

# Sort imports
isort url_validator tests

# Lint
flake8 url_validator tests

# Type check
mypy url_validator
```

---

## How This Was Built with AI

### Step 1: Core Functionality (Claude Code)
**Prompt**:
```
Generate url_validator/validator.py with URLValidator class.
Methods: is_valid, parse, normalize.
RFC 3986 compliant, handle IDN, IPv6.
Type hints, docstrings, comprehensive error handling.
```

**Time**: 10 minutes (would be 3-4 hours manually)

### Step 2: Test Suite (Claude Code)
**Prompt**:
```
Generate comprehensive pytest tests for URLValidator.
Cover: valid URLs, invalid URLs, edge cases, internationalized domains,
IPv6, normalization, error handling.
Aim for 100% coverage.
```

**Time**: 15 minutes (would be 4-5 hours manually)

### Step 3: CLI Interface (Claude Code)
**Prompt**:
```
Generate CLI in url_validator/cli.py using argparse.
Commands: validate, parse, normalize, batch.
Colorful output (rich library), exit codes, help text.
```

**Time**: 15 minutes (would be 2-3 hours manually)

### Step 4: Documentation (Claude Code)
**Prompt**:
```
Generate comprehensive README.md for url_validator package.
Installation, quick start, API reference, CLI reference,
development setup, examples.
```

**Time**: 10 minutes (would be 2-3 hours manually)

### Step 5: Review & Refine (Human)
- Run tests, fix any issues
- Verify error messages are clear
- Test CLI commands
- Check documentation accuracy

**Time**: 2-3 hours

**Total**: ~4 hours with AI vs. ~20 hours manually = **80% time savings!**

---

## Project Structure

```
url_validator/
├── url_validator/
│   ├── __init__.py       # Package initialization
│   ├── validator.py      # Core validator (AI-generated)
│   ├── cli.py            # CLI interface (AI-generated)
│   └── exceptions.py     # Custom exceptions
├── tests/
│   ├── test_validator.py # Validator tests (AI-generated)
│   └── test_cli.py       # CLI tests (AI-generated)
├── examples/
│   └── example_usage.py  # Usage examples
├── setup.py              # Package configuration
├── README.md             # This file (AI-generated)
├── LICENSE               # MIT license
└── .gitignore            # Git ignore file
```

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

## Learn More

This project is part of **Neural Dojo** - Module 3: AI-Powered Code Generation.

**Key Lessons**:
1. AI can generate production-quality code
2. Always review and test generated code
3. Specifications matter - clear spec = good code
4. Use AI for boilerplate, focus on business logic
5. 80% time savings is realistic!

**Next Steps**:
- Try generating your own package
- Use the patterns learned here
- Build something useful!

---

**Built with ❤️ and AI assistance (Claude Code)**

*Generated: 2025-11-23*
