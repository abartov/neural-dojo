#!/usr/bin/env python3
"""
Content Quality Auditor for Neural Dojo

Checks modules against the quality standards defined in CONTENT_STANDARDS.md.
Helps identify modules that need improvement and tracks quality progress.

Usage:
    python scripts/audit_content_quality.py                 # Audit all modules
    python scripts/audit_content_quality.py --module 36     # Audit specific module
    python scripts/audit_content_quality.py --summary       # Show summary only
    python scripts/audit_content_quality.py --json          # Output as JSON
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
NOTES_DIR = PROJECT_ROOT / "docs" / "curriculum" / "notes"

# Quality thresholds
MIN_LINES = 800  # Minimum lines for a quality module
MIN_DID_YOU_KNOW = 3  # Minimum "Did You Know?" sections
MIN_WORDS = 5000  # Minimum word count
MAX_CODE_BLOCK_LINES = 50  # Max lines before needing explanation break
MIN_PROSE_BEFORE_CODE = 50  # Minimum characters before code block


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class QualityCheck:
    """Result of a single quality check."""
    name: str
    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    details: Optional[str] = None


@dataclass
class ModuleAudit:
    """Complete audit results for a module."""
    module_id: str
    module_name: str
    file_path: Path
    checks: list[QualityCheck] = field(default_factory=list)
    overall_score: float = 0.0
    quality_level: str = "needs_improvement"  # good, acceptable, needs_improvement

    def add_check(self, check: QualityCheck):
        self.checks.append(check)

    def calculate_overall(self):
        if not self.checks:
            self.overall_score = 0.0
            self.quality_level = "needs_improvement"
            return

        self.overall_score = sum(c.score for c in self.checks) / len(self.checks)

        if self.overall_score >= 0.8:
            self.quality_level = "good"
        elif self.overall_score >= 0.6:
            self.quality_level = "acceptable"
        else:
            self.quality_level = "needs_improvement"


# ============================================================================
# Quality Checks
# ============================================================================

def check_line_count(content: str) -> QualityCheck:
    """Check if module has sufficient content length."""
    lines = len(content.splitlines())
    score = min(1.0, lines / MIN_LINES)
    passed = lines >= MIN_LINES

    return QualityCheck(
        name="Line Count",
        passed=passed,
        score=score,
        message=f"{lines} lines (target: {MIN_LINES}+)",
        details=f"Module has {lines} lines. Good modules have {MIN_LINES}+ lines."
    )


def check_word_count(content: str) -> QualityCheck:
    """Check if module has sufficient word count."""
    # Remove code blocks for word count
    no_code = re.sub(r'```[\s\S]*?```', '', content)
    words = len(no_code.split())
    score = min(1.0, words / MIN_WORDS)
    passed = words >= MIN_WORDS

    return QualityCheck(
        name="Word Count",
        passed=passed,
        score=score,
        message=f"{words} words (target: {MIN_WORDS}+)",
        details=f"Module has {words} words (excluding code). Target is {MIN_WORDS}+."
    )


def check_did_you_know(content: str) -> QualityCheck:
    """Check for 'Did You Know?' sections."""
    # Match various formats
    patterns = [
        r'\*\*Did You Know\?\*\*',
        r'> \*\*Did You Know\?\*\*',
        r'### Did You Know',
        r'## Did You Know',
        r'Did You Know\?'
    ]

    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, content, re.IGNORECASE))

    # Dedupe by dividing (patterns might overlap)
    count = max(1, count // 2) if count > 0 else 0

    score = min(1.0, count / MIN_DID_YOU_KNOW)
    passed = count >= MIN_DID_YOU_KNOW

    return QualityCheck(
        name="Did You Know Sections",
        passed=passed,
        score=score,
        message=f"{count} sections (target: {MIN_DID_YOU_KNOW}+)",
        details=f"Found {count} 'Did You Know?' sections. Good modules have {MIN_DID_YOU_KNOW}+."
    )


def check_opening_hook(content: str) -> QualityCheck:
    """Check if module opens with an engaging hook (not just headers)."""
    # Get content after the metadata and first header
    lines = content.splitlines()

    # Find first real content (after headers and metadata)
    content_start = 0
    in_metadata = False
    for i, line in enumerate(lines):
        if line.strip() == '---':
            in_metadata = not in_metadata
            continue
        if in_metadata:
            continue
        if line.startswith('#'):
            content_start = i + 1
            continue
        if line.strip() and not line.startswith('*') and not line.startswith('-'):
            content_start = i
            break

    # Get first paragraph
    first_para = ""
    for line in lines[content_start:content_start + 20]:
        if line.strip() == "":
            if first_para:
                break
        elif not line.startswith('#') and not line.startswith('---'):
            first_para += line + " "

    first_para = first_para.strip()

    # Check for story indicators
    story_indicators = [
        r'\d{4}',  # Year (dates in stories)
        r'\d+:\d+ [AP]M',  # Time
        r'engineer|developer|researcher|team|company',  # Characters
        r'when|while|after|before',  # Narrative words
        r'discovered|realized|found|noticed',  # Discovery verbs
        r'"[^"]+"',  # Quoted speech
    ]

    story_score = 0
    for pattern in story_indicators:
        if re.search(pattern, first_para, re.IGNORECASE):
            story_score += 1

    # Normalize score
    score = min(1.0, story_score / 3)
    passed = story_score >= 2

    return QualityCheck(
        name="Opening Hook",
        passed=passed,
        score=score,
        message="Story-based opening" if passed else "Technical opening",
        details=f"Opening paragraph has {story_score}/6 story indicators. "
                f"Good modules open with relatable scenarios or war stories."
    )


def check_analogies(content: str) -> QualityCheck:
    """Check for use of analogies and metaphors."""
    analogy_indicators = [
        r'like a',
        r'think of it as',
        r'imagine',
        r'similar to',
        r'just like',
        r'analogous to',
        r'metaphor',
        r'compare it to',
        r'it\'s like',
        r'picture',
    ]

    count = 0
    for pattern in analogy_indicators:
        count += len(re.findall(pattern, content, re.IGNORECASE))

    # Good modules have 5+ analogies
    score = min(1.0, count / 5)
    passed = count >= 3

    return QualityCheck(
        name="Analogies",
        passed=passed,
        score=score,
        message=f"{count} analogies found",
        details=f"Found {count} analogy indicators. Good modules use 5+ analogies "
                f"to explain complex concepts."
    )


def check_researcher_names(content: str) -> QualityCheck:
    """Check if researcher names are mentioned in stories."""
    # Common ML researcher name patterns
    name_patterns = [
        r'[A-Z][a-z]+ et al\.',
        r'[A-Z][a-z]+ and [A-Z][a-z]+',
        r'[A-Z][a-z]+ [A-Z][a-z]+',  # Full names
        r'researcher[s]? at',
        r'team at',
        r'invented by',
        r'proposed by',
        r'discovered by',
        r'developed by',
    ]

    # Known researchers
    known_researchers = [
        'Hinton', 'LeCun', 'Bengio', 'Sutskever', 'Karpathy', 'Ng',
        'Vaswani', 'Goodfellow', 'Turing', 'McCarthy', 'Minsky',
        'Schmidhuber', 'Hochreiter', 'Graves', 'Mikolov', 'Devlin',
        'Radford', 'Brown', 'Bai', 'Askell', 'Anthropic', 'OpenAI', 'Google'
    ]

    name_count = 0
    for name in known_researchers:
        if name.lower() in content.lower():
            name_count += 1

    pattern_count = 0
    for pattern in name_patterns:
        pattern_count += len(re.findall(pattern, content))

    total = name_count + (pattern_count // 2)
    score = min(1.0, total / 5)
    passed = total >= 3

    return QualityCheck(
        name="Researcher Names",
        passed=passed,
        score=score,
        message=f"{total} researcher references",
        details=f"Found {name_count} known researchers and {pattern_count} attribution patterns. "
                f"Good modules attribute discoveries to specific people."
    )


def check_code_explanations(content: str) -> QualityCheck:
    """Check if code blocks have prose explanations before them."""
    # Find all code blocks
    code_blocks = list(re.finditer(r'```[\s\S]*?```', content))

    if not code_blocks:
        return QualityCheck(
            name="Code Explanations",
            passed=True,
            score=1.0,
            message="No code blocks to check",
            details="Module has no code blocks."
        )

    blocks_with_prose = 0
    for match in code_blocks:
        # Get 500 chars before the code block
        start = max(0, match.start() - 500)
        before_text = content[start:match.start()]

        # Remove other code blocks and headers from before_text
        before_text = re.sub(r'```[\s\S]*?```', '', before_text)
        before_text = re.sub(r'^#+.*$', '', before_text, flags=re.MULTILINE)

        # Count prose characters (excluding whitespace)
        prose_chars = len(re.sub(r'\s', '', before_text))

        if prose_chars >= MIN_PROSE_BEFORE_CODE:
            blocks_with_prose += 1

    ratio = blocks_with_prose / len(code_blocks) if code_blocks else 1.0
    score = ratio
    passed = ratio >= 0.7

    return QualityCheck(
        name="Code Explanations",
        passed=passed,
        score=score,
        message=f"{blocks_with_prose}/{len(code_blocks)} blocks have prose",
        details=f"{blocks_with_prose} of {len(code_blocks)} code blocks have sufficient "
                f"explanatory prose before them. Target: 70%+."
    )


def check_key_takeaways(content: str) -> QualityCheck:
    """Check for Key Takeaways section."""
    has_takeaways = bool(re.search(
        r'(Key Takeaways|Takeaways|Summary|What You Learned)',
        content,
        re.IGNORECASE
    ))

    return QualityCheck(
        name="Key Takeaways",
        passed=has_takeaways,
        score=1.0 if has_takeaways else 0.0,
        message="Has takeaways section" if has_takeaways else "Missing takeaways",
        details="Good modules end with a clear summary of key points."
    )


def check_practical_exercises(content: str) -> QualityCheck:
    """Check for hands-on exercises section."""
    exercise_indicators = [
        r'Hands-On',
        r'Exercise',
        r'Practice',
        r'Try It',
        r'Your Turn',
        r'TODO:',
        r'Implement',
    ]

    count = 0
    for pattern in exercise_indicators:
        if re.search(pattern, content, re.IGNORECASE):
            count += 1

    score = min(1.0, count / 3)
    passed = count >= 2

    return QualityCheck(
        name="Practical Exercises",
        passed=passed,
        score=score,
        message=f"{count} exercise indicators",
        details=f"Found {count} exercise/practice indicators. Good modules have "
                f"hands-on exercises for active learning."
    )


def check_real_numbers(content: str) -> QualityCheck:
    """Check for real statistics and numbers."""
    # Patterns for real numbers/statistics
    number_patterns = [
        r'\$[\d,]+[KMB]?',  # Dollar amounts
        r'\d+%',  # Percentages
        r'\d+x',  # Multipliers
        r'\d{4}',  # Years
        r'\d+,\d{3}',  # Large numbers with commas
        r'cited \d+',  # Citation counts
        r'\d+ times',  # Frequency
    ]

    count = 0
    for pattern in number_patterns:
        count += len(re.findall(pattern, content))

    score = min(1.0, count / 15)
    passed = count >= 10

    return QualityCheck(
        name="Real Numbers",
        passed=passed,
        score=score,
        message=f"{count} statistics/numbers",
        details=f"Found {count} real numbers and statistics. Good modules make "
                f"content credible with specific data points."
    )


# ============================================================================
# Audit Functions
# ============================================================================

def audit_module(file_path: Path) -> ModuleAudit:
    """Run all quality checks on a module."""
    content = file_path.read_text()

    # Extract module info from filename
    filename = file_path.stem
    match = re.match(r'module_(\d+(?:\.\d+)?)', filename)
    module_id = match.group(1) if match else filename

    # Extract title from content
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    module_name = title_match.group(1) if title_match else filename

    audit = ModuleAudit(
        module_id=module_id,
        module_name=module_name,
        file_path=file_path
    )

    # Run all checks
    checks = [
        check_line_count(content),
        check_word_count(content),
        check_did_you_know(content),
        check_opening_hook(content),
        check_analogies(content),
        check_researcher_names(content),
        check_code_explanations(content),
        check_key_takeaways(content),
        check_practical_exercises(content),
        check_real_numbers(content),
    ]

    for check in checks:
        audit.add_check(check)

    audit.calculate_overall()
    return audit


def find_module_files(module_filter: Optional[str] = None) -> list[Path]:
    """Find module files, optionally filtered by ID."""
    if module_filter:
        # Try different patterns
        patterns = [
            f"module_{module_filter}_*.md",
            f"module_{module_filter.zfill(2)}_*.md",
            f"module_0{module_filter}_*.md",
            f"*{module_filter}*.md",  # Broader match as fallback
        ]
        for pattern in patterns:
            matches = list(NOTES_DIR.glob(pattern))
            # Filter to only actual module files (not deep_dive, etc.)
            matches = [m for m in matches if m.name.startswith("module_")]
            if matches:
                return matches
        return []

    return sorted(NOTES_DIR.glob("module_*.md"))


# ============================================================================
# Output Functions
# ============================================================================

def print_audit_result(audit: ModuleAudit, verbose: bool = True):
    """Print audit results for a module."""
    # Quality level emoji
    level_emoji = {
        "good": "🟢",
        "acceptable": "🟡",
        "needs_improvement": "🔴"
    }

    emoji = level_emoji.get(audit.quality_level, "❓")
    score_pct = int(audit.overall_score * 100)

    print(f"\n{emoji} Module {audit.module_id}: {audit.module_name}")
    print(f"   Score: {score_pct}% ({audit.quality_level})")
    print(f"   File: {audit.file_path.name}")

    if verbose:
        print("\n   Checks:")
        for check in audit.checks:
            status = "✅" if check.passed else "❌"
            print(f"   {status} {check.name}: {check.message}")


def print_summary(audits: list[ModuleAudit]):
    """Print summary of all audits."""
    good = sum(1 for a in audits if a.quality_level == "good")
    acceptable = sum(1 for a in audits if a.quality_level == "acceptable")
    needs_work = sum(1 for a in audits if a.quality_level == "needs_improvement")

    print("\n" + "=" * 60)
    print("  Content Quality Audit Summary")
    print("=" * 60)

    print(f"\n📊 Overall: {len(audits)} modules audited")
    print(f"   🟢 Good: {good} ({good/len(audits)*100:.0f}%)")
    print(f"   🟡 Acceptable: {acceptable} ({acceptable/len(audits)*100:.0f}%)")
    print(f"   🔴 Needs Improvement: {needs_work} ({needs_work/len(audits)*100:.0f}%)")

    if needs_work > 0:
        print("\n📝 Modules Needing Improvement:")
        for audit in audits:
            if audit.quality_level == "needs_improvement":
                score_pct = int(audit.overall_score * 100)
                print(f"   🔴 Module {audit.module_id} ({score_pct}%): {audit.module_name}")

    # Average score
    avg_score = sum(a.overall_score for a in audits) / len(audits)
    print(f"\n📈 Average Quality Score: {avg_score*100:.0f}%")


def output_json(audits: list[ModuleAudit]):
    """Output audit results as JSON."""
    data = {
        "summary": {
            "total": len(audits),
            "good": sum(1 for a in audits if a.quality_level == "good"),
            "acceptable": sum(1 for a in audits if a.quality_level == "acceptable"),
            "needs_improvement": sum(1 for a in audits if a.quality_level == "needs_improvement"),
            "average_score": sum(a.overall_score for a in audits) / len(audits)
        },
        "modules": [
            {
                "module_id": a.module_id,
                "module_name": a.module_name,
                "file": str(a.file_path.name),
                "score": a.overall_score,
                "quality_level": a.quality_level,
                "checks": [
                    {
                        "name": c.name,
                        "passed": c.passed,
                        "score": c.score,
                        "message": c.message
                    }
                    for c in a.checks
                ]
            }
            for a in audits
        ]
    }
    print(json.dumps(data, indent=2))


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Audit content quality of Neural Dojo modules"
    )
    parser.add_argument(
        "--module", "-m",
        help="Audit specific module by ID (e.g., 36, 01.4)"
    )
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Show summary only (no individual results)"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed check results"
    )

    args = parser.parse_args()

    # Find modules to audit
    files = find_module_files(args.module)

    if not files:
        print(f"❌ No modules found" + (f" matching '{args.module}'" if args.module else ""))
        sys.exit(1)

    # Run audits
    audits = [audit_module(f) for f in files]

    # Output results
    if args.json:
        output_json(audits)
    elif args.summary:
        print_summary(audits)
    else:
        for audit in audits:
            print_audit_result(audit, verbose=args.verbose)
        print_summary(audits)


if __name__ == "__main__":
    main()
