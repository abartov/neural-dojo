#!/usr/bin/env python3
"""
Module 3: CLI Tool Generation

Demonstrates generating command-line interfaces with argparse.

KEY INSIGHT: AI can create user-friendly CLIs with proper help, validation, and subcommands!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_cli(specification: str) -> str:
    """Generate CLI tool from specification."""
    prompt = f"""
You are an expert at building command-line tools.

{specification}

Requirements:
- Use argparse for argument parsing
- Include helpful --help text for all commands
- Add input validation
- Use proper exit codes (0 success, 1 error)
- Add --verbose flag for detailed output
- Include version command (--version)
- Use type hints and docstrings
- Add error handling with clear messages
- Make it user-friendly

Return ONLY the code, no explanations.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def main():
    """Demonstrate CLI generation."""
    print("=" * 60)
    print("MODULE 3: CLI TOOL GENERATION")
    print("=" * 60)

    # Example: File processing CLI
    print("\n📝 Example: File Processing CLI")
    print("-" * 60)

    spec = """
Generate a CLI tool for processing text files: file_processor.py

Commands:
1. count <file>
   - Count lines, words, characters in file
   - Options:
     --lines-only: Only show line count
     --words-only: Only show word count
     --chars-only: Only show character count
   - Handle file not found
   - Handle encoding errors

2. search <file> <pattern>
   - Search for pattern in file (case-insensitive)
   - Show matching lines with line numbers
   - Options:
     --case-sensitive: Make search case-sensitive
     --count: Just show count of matches
     --context N: Show N lines before/after match
   - Use regex for pattern

3. replace <file> <old> <new>
   - Replace text in file
   - Options:
     --output FILE: Write to different file (default: overwrite)
     --backup: Create .bak backup before replacing
     --dry-run: Show changes without applying
   - Confirm before overwriting (unless --yes flag)

4. stats <file> [<file> ...]
   - Show statistics for one or more files:
     - File size
     - Line count
     - Word count
     - Most common words (top 10)
   - Options:
     --format {text,json,csv}: Output format

Global Options:
- --verbose, -v: Show detailed output
- --quiet, -q: Suppress non-error output
- --version: Show version (1.0.0)

Error Handling:
- File not found → clear error message, exit 1
- Permission denied → clear error message, exit 1
- Invalid pattern → show regex error, exit 1
- Conflicting options → show help, exit 1

Help:
- Each command should have detailed help
- Show examples in help text
- Make error messages actionable
"""

    print("Specification:")
    print(spec)

    print("\n🤖 Generating CLI tool...")
    cli_code = generate_cli(spec)

    print("\n✨ Generated CLI Tool:")
    print(cli_code)

    # Usage examples
    print("\n\n📖 USAGE EXAMPLES:")
    print("=" * 60)
    print("After saving to file_processor.py, you can use it like this:")
    print("")
    print("# Count lines/words/chars")
    print("$ python file_processor.py count document.txt")
    print("Lines: 42")
    print("Words: 385")
    print("Characters: 2,156")
    print("")
    print("# Count only lines")
    print("$ python file_processor.py count --lines-only document.txt")
    print("Lines: 42")
    print("")
    print("# Search for pattern")
    print("$ python file_processor.py search document.txt 'error'")
    print("12: Error in processing data")
    print("27: Handle error case properly")
    print("")
    print("# Search with context")
    print("$ python file_processor.py search document.txt 'error' --context 1")
    print("11: # Process data")
    print("12: Error in processing data  ← match")
    print("13: return None")
    print("")
    print("# Replace text (dry run)")
    print("$ python file_processor.py replace document.txt 'old' 'new' --dry-run")
    print("Would replace 3 occurrences:")
    print("12: Error in old processing → Error in new processing")
    print("")
    print("# Get statistics")
    print("$ python file_processor.py stats *.txt")
    print("File: doc1.txt")
    print("  Size: 2.1 KB")
    print("  Lines: 42")
    print("  Words: 385")
    print("")
    print("# Get stats in JSON")
    print("$ python file_processor.py stats doc.txt --format json")
    print('{"file": "doc.txt", "size": 2156, "lines": 42, "words": 385}')

    # Lessons learned
    print("\n\n💡 LESSONS LEARNED:")
    print("=" * 60)
    print("1. Specify ALL commands and options upfront:")
    print("   - What each command does")
    print("   - All flags and arguments")
    print("   - Default behaviors")
    print("")
    print("2. Request good UX explicitly:")
    print("   - Helpful error messages")
    print("   - Confirmation prompts")
    print("   - Progress indicators")
    print("   - Clear help text")
    print("")
    print("3. Include examples in help:")
    print("   - Shows users how to use tool")
    print("   - Reduces support questions")
    print("   - Demonstrates common patterns")
    print("")
    print("4. Exit codes matter:")
    print("   - 0 = success (for scripting)")
    print("   - 1 = error")
    print("   - Enables chaining commands")
    print("")
    print("5. AI generates production-ready CLIs:")
    print("   - Proper argument parsing")
    print("   - Input validation")
    print("   - Error handling")
    print("   - Saves 3-4 hours of boilerplate!")
    print("")
    print("📦 NEXT STEPS:")
    print("   1. Save to file_processor.py")
    print("   2. chmod +x file_processor.py")
    print("   3. Try it: python file_processor.py --help")
    print("   4. Test each command")
    print("   5. Add to your toolkit!")


if __name__ == "__main__":
    main()
