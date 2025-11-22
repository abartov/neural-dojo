# Module 5 Examples: Building with AI Coding Assistants

This directory contains **workflow demonstrations** for using AI coding assistants effectively.

Unlike other modules with code examples, Module 5 focuses on **how to use the tools themselves**. These are documented workflows, configuration templates, and prompt patterns.

---

## 📁 Contents

### Workflow Demonstrations

1. **[workflow_01_feature_development.md](workflow_01_feature_development.md)**
   - Building a complete feature using multiple AI tools
   - Shows Claude Code → Copilot → Cursor workflow
   - Real example: Adding authentication to a REST API

2. **[workflow_02_debugging_production.md](workflow_02_debugging_production.md)**
   - Debugging a production bug systematically with AI
   - Uses Claude Code for analysis, Copilot for fixes
   - Real example: Fixing intermittent 500 errors

3. **[workflow_03_code_review.md](workflow_03_code_review.md)**
   - Using AI for comprehensive code review
   - Claude Code for architecture, Copilot for tests
   - Real example: Reviewing a pull request

4. **[workflow_04_refactoring.md](workflow_04_refactoring.md)**
   - Large-scale refactoring with AI assistance
   - Multi-tool workflow for safety
   - Real example: Migrating from REST to GraphQL

5. **[workflow_05_learning_codebase.md](workflow_05_learning_codebase.md)**
   - Onboarding to a new codebase with AI
   - Using Cursor + ChatGPT/Gemini for exploration
   - Real example: Understanding a Django project

### Configuration Templates

- **[config_claude_code.md](config_claude_code.md)** - Claude Code best practices
- **[config_copilot.md](config_copilot.md)** - Copilot settings and shortcuts
- **[config_cursor.md](config_cursor.md)** - Cursor IDE configuration
- **[config_aider.md](config_aider.md)** - Aider.ai setup and commands

### Prompt Patterns

- **[prompt_patterns.md](prompt_patterns.md)** - Reusable prompt templates for common tasks

---

## 🚀 Quick Start

### 1. Read a Workflow
Start with **workflow_01_feature_development.md** to see a complete end-to-end example.

### 2. Configure Your Tools
Check the config files for your preferred tools to optimize settings.

### 3. Use Prompt Patterns
Copy patterns from **prompt_patterns.md** and adapt to your needs.

---

## 💡 How to Use These Workflows

These are **templates**, not scripts. You'll need to:

1. **Adapt to your project**: Change the example code/context to your actual codebase
2. **Modify prompts**: Adjust for your specific requirements
3. **Iterate**: First try rarely perfect - refine based on results
4. **Measure**: Track time saved, quality improvements

---

## 📊 Expected Outcomes

After following these workflows, you should:

- **30-50% faster** on feature development (boilerplate, tests)
- **20-30% faster** on debugging (systematic approach, AI suggestions)
- **50%+ faster** on code review (automated checks, AI insights)
- **70%+ faster** on documentation (generation, consistency)
- **Reduced cognitive load** (AI handles tedious tasks)

---

## 🎯 Success Criteria

You've mastered AI-assisted development when you can:

- [ ] Choose the right tool for each task automatically
- [ ] Write effective prompts without thinking
- [ ] Review AI suggestions critically and quickly
- [ ] Combine multiple tools in your workflow
- [ ] Measure and improve your productivity
- [ ] Teach others your workflow

---

## ⚠️ Important Notes

**Always Review AI Code**:
- Check for security vulnerabilities (SQL injection, XSS, etc.)
- Verify business logic correctness
- Test edge cases
- Ensure performance is acceptable

**Privacy Considerations**:
- Don't paste proprietary code to cloud AI tools without permission
- Use local models (Ollama) for sensitive code if needed
- Review your company's AI tool policy
- Consider data retention policies of each tool

---

## 📚 Related Resources

- **Module 5 Theory**: `/docs/curriculum/notes/module_05_ai_tools.md`
- **Module 1**: AI-Native Development overview
- **Module 2**: Prompt Engineering fundamentals
- **Module 3**: Code Generation patterns
- **Module 4**: AI-Assisted Debugging

---

**Happy coding with AI! 🥋🧠⚡**
