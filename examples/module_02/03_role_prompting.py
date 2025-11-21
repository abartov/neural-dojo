#!/usr/bin/env python3
"""
Module 2: Role Prompting

Demonstrates how assigning a role/persona to the AI dramatically changes
the response style, depth, and perspective.

KEY INSIGHT: Same question + different role = completely different answer!
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Claude client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def no_role_prompt():
    """
    No role assigned - generic response.
    """
    prompt = """
    Explain what a REST API is.
    """
    return prompt


def role_senior_engineer():
    """
    Role: Senior Software Engineer
    """
    prompt = """
    You are a senior software engineer with 10+ years of experience building scalable web services.

    Explain what a REST API is.
    """
    return prompt


def role_five_year_old():
    """
    Role: Explaining to a 5-year-old
    """
    prompt = """
    You are a patient teacher explaining technology concepts to a 5-year-old child.
    Use simple words, analogies, and avoid technical jargon.

    Explain what a REST API is.
    """
    return prompt


def role_comedian():
    """
    Role: Stand-up Comedian
    """
    prompt = """
    You are a stand-up comedian who explains tech concepts through humor and jokes.
    Be entertaining while still being accurate.

    Explain what a REST API is.
    """
    return prompt


def role_academic_professor():
    """
    Role: Computer Science Professor
    """
    prompt = """
    You are a distinguished computer science professor giving a formal lecture.
    Be rigorous, cite foundational concepts, and maintain academic tone.

    Explain what a REST API is.
    """
    return prompt


def run_prompt(prompt: str, label: str):
    """Execute a prompt and display results."""
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"{'='*60}")
    print(f"\nPrompt:\n{prompt}")
    print(f"\n{'-'*60}\nResponse:")

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.content[0].text
    print(result)

    return result


def demonstrate_coding_task_roles():
    """
    Show how roles affect code review feedback.
    """
    print("\n" + "💻"*30)
    print("TASK: Code Review with Different Roles")
    print("💻"*30)

    code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""

    # Role 1: Code Reviewer (Constructive)
    constructive = f"""
You are a supportive senior engineer doing a code review.
Focus on improvements while acknowledging what works well.

Review this code:
```python
{code}
```
"""

    # Role 2: Security Expert (Critical)
    security = f"""
You are a security-focused engineer. Your job is to identify
potential security vulnerabilities and edge cases.

Review this code:
```python
{code}
```
"""

    # Role 3: Performance Engineer
    performance = f"""
You are a performance optimization specialist. Focus on
efficiency, algorithmic complexity, and scalability.

Review this code:
```python
{code}
```
"""

    run_prompt(constructive, "👍 ROLE: Supportive Code Reviewer")
    run_prompt(security, "🔒 ROLE: Security Expert")
    run_prompt(performance, "⚡ ROLE: Performance Engineer")


def demonstrate_teaching_styles():
    """
    Show how teaching role changes explanation approach.
    """
    print("\n" + "📚"*30)
    print("TASK: Teaching with Different Roles")
    print("📚"*30)

    topic = "Explain recursion in programming"

    # Role 1: Visual Learner Teacher
    visual = f"""
You are a teacher who specializes in visual learning.
Use diagrams, analogies, and step-by-step visual descriptions.

{topic}
"""

    # Role 2: Hands-On Mentor
    hands_on = f"""
You are a coding bootcamp instructor who believes in learning by doing.
Provide practical examples and coding exercises.

{topic}
"""

    # Role 3: Socratic Teacher
    socratic = f"""
You are a Socratic teacher who guides students through questions
rather than giving direct answers.

{topic}
"""

    run_prompt(visual, "🎨 ROLE: Visual Learning Teacher")
    run_prompt(hands_on, "🔨 ROLE: Hands-On Mentor")
    run_prompt(socratic, "🤔 ROLE: Socratic Teacher")


def demonstrate_debugging_perspectives():
    """
    Show how role affects debugging approach.
    """
    print("\n" + "🐛"*30)
    print("TASK: Debugging with Different Perspectives")
    print("🐛"*30)

    bug_report = """
Bug: Application crashes when user submits form with special characters.
Error: UnicodeDecodeError on line 42 of form_handler.py
"""

    # Role 1: Methodical Debugger
    methodical = f"""
You are a systematic debugger who follows a structured debugging process.
Use the scientific method: hypothesis → test → iterate.

{bug_report}

Walk me through your debugging process.
"""

    # Role 2: Experienced Veteran
    veteran = f"""
You are a grizzled veteran engineer who has seen every bug imaginable.
You pattern-match to similar bugs you've solved before.

{bug_report}

What's your immediate assessment based on experience?
"""

    run_prompt(methodical, "🔬 ROLE: Methodical Debugger")
    run_prompt(veteran, "🎖️ ROLE: Experienced Veteran")


def main():
    """
    Main demonstration of role prompting.
    """
    print("\n" + "="*60)
    print("MODULE 2: ROLE PROMPTING")
    print("="*60)
    print("\nKEY INSIGHT: Same question + different role = different answer!")
    print("="*60)

    # Basic role comparison
    print("\n" + "🎭"*30)
    print("BASIC ROLE COMPARISON: Explaining REST API")
    print("🎭"*30)

    run_prompt(no_role_prompt(), "❌ NO ROLE (Generic)")
    run_prompt(role_senior_engineer(), "💼 ROLE: Senior Engineer")
    run_prompt(role_five_year_old(), "👶 ROLE: Teaching a 5-Year-Old")
    run_prompt(role_comedian(), "😂 ROLE: Stand-Up Comedian")
    run_prompt(role_academic_professor(), "🎓 ROLE: CS Professor")

    # Code review roles
    demonstrate_coding_task_roles()

    # Teaching styles
    demonstrate_teaching_styles()

    # Debugging perspectives
    demonstrate_debugging_perspectives()

    # Final insights
    print("\n" + "💡"*30)
    print("LESSONS LEARNED:")
    print("="*60)
    print("1. Roles change EVERYTHING:")
    print("   - Tone and style")
    print("   - Level of detail")
    print("   - Perspective and focus")
    print("   - Technical depth")
    print("2. Useful role categories:")
    print("   - Expertise level (junior, senior, expert)")
    print("   - Personality (supportive, critical, humorous)")
    print("   - Teaching style (visual, hands-on, theoretical)")
    print("   - Domain expert (security, performance, UX)")
    print("3. Role stacking:")
    print("   - 'You are a senior Python developer who specializes in'")
    print("     'async programming and has a passion for clean code'")
    print("4. When to use roles:")
    print("   - Code reviews (supportive vs critical)")
    print("   - Learning (match your learning style)")
    print("   - Problem-solving (different perspectives)")
    print("   - Communication (match your audience)")
    print("5. Anti-patterns:")
    print("   - Too vague: 'You are helpful' (not specific enough)")
    print("   - Too narrow: Overly constrains useful responses")
    print("   - Conflicting: 'Be concise but exhaustive'")
    print("="*60)

    print("\n🎭 Pro Tip:")
    print("   Store your favorite roles in your prompt library!")
    print("   Example: 'review_as_senior_engineer(code)'")


if __name__ == "__main__":
    main()
