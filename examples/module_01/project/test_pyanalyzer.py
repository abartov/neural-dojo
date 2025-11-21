"""
Test suite for Python File Analyzer

Tests all major functionality:
- Single file analysis
- Directory analysis
- Error handling
- Output formatting
- Edge cases

Run with: pytest test_pyanalyzer.py -v
"""

import pytest
import tempfile
import json
from pathlib import Path
from pyanalyzer import (
    analyze_file,
    analyze_directory,
    format_pretty_output,
    format_json_output,
    CodeMetrics,
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_analyze_simple_file(temp_dir):
    """Test analyzing a simple Python file."""
    code = """
def hello():
    print("Hello")

def world():
    print("World")
"""
    file_path = temp_dir / "simple.py"
    file_path.write_text(code)

    metrics = analyze_file(file_path)

    assert metrics.functions == 2
    assert metrics.classes == 0
    assert metrics.lines == 4  # def hello():, print("Hello"), def world():, print("World")
    assert metrics.complexity == 0


def test_analyze_with_classes(temp_dir):
    """Test analyzing file with classes."""
    code = """
class MyClass:
    def __init__(self):
        self.value = 0

    def method(self):
        return self.value

class AnotherClass:
    pass
"""
    file_path = temp_dir / "classes.py"
    file_path.write_text(code)

    metrics = analyze_file(file_path)

    assert metrics.classes == 2
    assert metrics.functions == 2  # __init__ and method


def test_analyze_with_complexity(temp_dir):
    """Test complexity counting (if/while/for)."""
    code = """
def complex_function(x):
    if x > 0:
        for i in range(10):
            if i % 2 == 0:
                print(i)

    while x < 100:
        x += 1

    return x
"""
    file_path = temp_dir / "complex.py"
    file_path.write_text(code)

    metrics = analyze_file(file_path)

    assert metrics.functions == 1
    assert metrics.complexity == 4  # 2 ifs + 1 for + 1 while


def test_analyze_with_comments(temp_dir):
    """Test that comments are excluded from line count."""
    code = """
# This is a comment
def func():
    # Another comment
    x = 1  # Inline comment
    return x

# More comments
"""
    file_path = temp_dir / "comments.py"
    file_path.write_text(code)

    metrics = analyze_file(file_path)

    # Should count: def func():, x = 1 (with inline comment), return x
    # Should NOT count: comment-only lines (2 comment lines excluded)
    assert metrics.lines == 3  # def func():, x = 1, return x
    assert metrics.functions == 1


def test_analyze_async_functions(temp_dir):
    """Test counting async functions."""
    code = """
async def async_func():
    return 42

async def another_async():
    pass
"""
    file_path = temp_dir / "async.py"
    file_path.write_text(code)

    metrics = analyze_file(file_path)

    assert metrics.functions == 2  # Both async functions counted


def test_file_not_found():
    """Test handling of non-existent file."""
    with pytest.raises(FileNotFoundError):
        analyze_file(Path("/nonexistent/file.py"))


def test_invalid_python(temp_dir):
    """Test handling of invalid Python syntax."""
    code = """
def broken function():
    this is not valid python
"""
    file_path = temp_dir / "broken.py"
    file_path.write_text(code)

    with pytest.raises(SyntaxError):
        analyze_file(file_path)


def test_empty_file(temp_dir):
    """Test analyzing empty file."""
    file_path = temp_dir / "empty.py"
    file_path.write_text("")

    metrics = analyze_file(file_path)

    assert metrics.functions == 0
    assert metrics.classes == 0
    assert metrics.lines == 0
    assert metrics.complexity == 0


def test_directory_analysis(temp_dir):
    """Test analyzing directory recursively."""
    # Create multiple files
    file1 = temp_dir / "file1.py"
    file1.write_text("""
def func1():
    pass

class Class1:
    pass
""")

    file2 = temp_dir / "file2.py"
    file2.write_text("""
def func2():
    pass

def func3():
    pass
""")

    # Create subdirectory
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    file3 = subdir / "file3.py"
    file3.write_text("""
class Class2:
    def method(self):
        pass
""")

    metrics = analyze_directory(temp_dir)

    assert metrics.functions == 4  # func1, func2, func3, method
    assert metrics.classes == 2  # Class1, Class2


def test_directory_with_broken_file(temp_dir, capsys):
    """Test that directory analysis skips broken files."""
    # Good file
    good_file = temp_dir / "good.py"
    good_file.write_text("def good(): pass")

    # Broken file
    bad_file = temp_dir / "bad.py"
    bad_file.write_text("def broken( syntax")

    metrics = analyze_directory(temp_dir)

    # Should have metrics from good file
    assert metrics.functions == 1

    # Should print warning for bad file
    captured = capsys.readouterr()
    assert "Skipping" in captured.err
    assert "bad.py" in captured.err


def test_empty_directory(temp_dir, capsys):
    """Test analyzing directory with no Python files."""
    metrics = analyze_directory(temp_dir)

    assert metrics.functions == 0
    assert metrics.classes == 0
    assert metrics.lines == 0
    assert metrics.complexity == 0

    captured = capsys.readouterr()
    assert "No Python files found" in captured.err


def test_pretty_output_format(temp_dir):
    """Test pretty output formatting."""
    metrics = CodeMetrics(functions=5, classes=2, lines=100, complexity=15)
    output = format_pretty_output(temp_dir / "test.py", metrics, is_directory=False)

    assert "Python File Analyzer" in output
    assert "test.py" in output
    assert "Functions:  5" in output
    assert "Classes:    2" in output
    assert "Lines:      100" in output
    assert "Complexity: 15" in output


def test_json_output_format(temp_dir):
    """Test JSON output formatting."""
    metrics = CodeMetrics(functions=3, classes=1, lines=50, complexity=8)
    output = format_json_output(temp_dir / "test.py", metrics, is_directory=False)

    data = json.loads(output)
    assert data["type"] == "file"
    assert "test.py" in data["path"]
    assert data["metrics"]["functions"] == 3
    assert data["metrics"]["classes"] == 1
    assert data["metrics"]["lines"] == 50
    assert data["metrics"]["complexity"] == 8


def test_json_output_directory(temp_dir):
    """Test JSON output for directory."""
    metrics = CodeMetrics(functions=10, classes=3, lines=200, complexity=25)
    output = format_json_output(temp_dir, metrics, is_directory=True)

    data = json.loads(output)
    assert data["type"] == "directory"
    assert data["metrics"]["functions"] == 10


def test_analyze_real_file():
    """Test analyzing the analyzer itself (meta!)."""
    # Analyze pyanalyzer.py
    this_dir = Path(__file__).parent
    analyzer_file = this_dir / "pyanalyzer.py"

    if analyzer_file.exists():
        metrics = analyze_file(analyzer_file)

        # pyanalyzer.py should have multiple functions and classes
        assert metrics.functions > 5
        assert metrics.classes > 0
        assert metrics.lines > 100


def test_nested_complexity(temp_dir):
    """Test nested control structures."""
    code = """
def nested():
    for i in range(10):
        if i > 5:
            while True:
                if i == 7:
                    break
"""
    file_path = temp_dir / "nested.py"
    file_path.write_text(code)

    metrics = analyze_file(file_path)

    assert metrics.complexity == 4  # 1 for, 2 ifs, 1 while


def test_metrics_dataclass():
    """Test CodeMetrics dataclass."""
    metrics = CodeMetrics(functions=1, classes=2, lines=3, complexity=4)

    assert metrics.functions == 1
    assert metrics.classes == 2
    assert metrics.lines == 3
    assert metrics.complexity == 4

    # Test to_dict
    data = metrics.to_dict()
    assert data["functions"] == 1
    assert data["classes"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=pyanalyzer", "--cov-report=term-missing"])
