"""
Module 0: Test Environment Setup

Verifies that Python environment is configured correctly.
"""
import sys
import subprocess


def test_python_version():
    """Verify Python 3.10+"""
    version = sys.version_info
    assert version.major == 3
    assert version.minor >= 10
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")


def test_pip_works():
    """Verify pip is available"""
    result = subprocess.run(
        ["pip", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    print(f"✅ pip works: {result.stdout.strip()}")


def test_imports():
    """Verify key packages can be imported"""
    try:
        import dotenv  # noqa: F401
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed")
        print("   Run: pip install python-dotenv")
        return False

    return True


if __name__ == "__main__":
    print("🔍 Testing environment setup...\n")

    try:
        test_python_version()
        test_pip_works()
        success = test_imports()

        if success:
            print("\n✅ Environment setup complete!")
            print("   Next: Run test_claude_api.py to verify API access")
        else:
            print("\n❌ Environment setup incomplete. See errors above.")
            sys.exit(1)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
