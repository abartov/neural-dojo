"""Setup configuration for url_validator package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="url-validator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A comprehensive URL validation and parsing library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/url-validator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "cli": [
            "rich>=13.0.0",  # For colorful CLI output
        ],
    },
    entry_points={
        "console_scripts": [
            "url-validator=url_validator.cli:main",
        ],
    },
)
