#!/usr/bin/env python3
"""
Documentation Generator for Neural Dojo

Usage:
    python -m tools.docs_generator --index        # Generate MODULE_INDEX.md
    python -m tools.docs_generator --html         # Generate HTML to docs/_site/
    python -m tools.docs_generator --all          # Generate everything
    python -m tools.docs_generator --serve        # Generate and serve locally
    python -m tools.docs_generator --clean        # Clean generated files
"""

import argparse
import http.server
import shutil
import socketserver
from pathlib import Path

try:
    import markdown

    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: 'markdown' package not installed. Run: pip install markdown")

from .config import PathConfig, get_default_config
from .parsers import CurriculumData, Module, generate_module_index, parse_curriculum
from .templates import html_template, nav_bar, progress_stats_html


def md_to_html(md_content: str) -> str:
    """Convert markdown to HTML."""
    if not MARKDOWN_AVAILABLE:
        return f"<pre>{md_content}</pre>"

    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    return md.convert(md_content)


def generate_index_file(config: PathConfig) -> bool:
    """
    Generate MODULE_INDEX.md from MASTER_CURRICULUM.md.

    Args:
        config: Path configuration

    Returns:
        True if successful
    """
    print(f"Parsing {config.master_curriculum}...")

    if not config.master_curriculum.exists():
        print(f"ERROR: {config.master_curriculum} not found")
        return False

    curriculum = parse_curriculum(config.master_curriculum)

    print(f"Found {len(curriculum.phases)} phases")
    for phase in curriculum.phases:
        module_count = len(phase.modules)
        complete_count = sum(1 for m in phase.modules if m.status == "complete")
        print(f"  Phase {phase.number}: {complete_count}/{module_count} complete")

    index_content = generate_module_index(curriculum)

    config.module_index.write_text(index_content)
    print(f"Generated {config.module_index}")

    return True


def md_path_to_html_url(md_path: str) -> str:
    """Convert a markdown path to HTML URL in the modules directory."""
    filename = md_path.split("/")[-1]
    html_filename = filename.replace(".md", ".html")
    return f"../modules/{html_filename}"


def generate_module_card_html(module: Module) -> str:
    """Generate HTML card for a single module."""
    status_colors = {
        "complete": "#059669",
        "theory_only": "#7c3aed",
        "in_progress": "#d97706",
        "pending": "#6b7280",
    }
    status_labels = {
        "complete": "🟢 Complete",
        "theory_only": "📝 Theory Only",
        "in_progress": "🟡 In Progress",
        "pending": "⚪ Pending",
    }

    status_color = status_colors.get(module.status, "#6b7280")
    status_label = status_labels.get(module.status, "⚪ Pending")
    heureka = " 🔮" if module.is_heureka else ""

    html_parts = [
        f'<div class="module-card" style="border-left: 4px solid {status_color};">',
        f'<h4>Module {module.number}: {module.title}{heureka}</h4>',
        f'<span class="status-badge" style="background: {status_color};">{status_label}</span>',
    ]

    # Module details
    details = []
    if module.duration:
        details.append(f"<strong>Duration:</strong> {module.duration}")
    if module.prerequisites:
        details.append(f"<strong>Prerequisites:</strong> {module.prerequisites}")

    # Theory files
    if module.theory_files:
        theory_links = []
        for t in module.theory_files:
            html_url = md_path_to_html_url(t["path"])
            theory_links.append(f'<a href="{html_url}">{t["name"]}</a>')
        details.append(f"<strong>Theory:</strong> {', '.join(theory_links)}")

    if details:
        html_parts.append(f'<p class="module-details">{" | ".join(details)}</p>')

    # Learning objectives
    if module.learning_objectives:
        html_parts.append("<p><strong>Objectives:</strong></p><ul>")
        for obj in module.learning_objectives[:3]:
            html_parts.append(f"<li>{obj}</li>")
        if len(module.learning_objectives) > 3:
            html_parts.append(f"<li><em>... and {len(module.learning_objectives) - 3} more</em></li>")
        html_parts.append("</ul>")

    html_parts.append("</div>")
    return "\n".join(html_parts)


def generate_phase_html(phase, curriculum: CurriculumData) -> str:
    """Generate HTML for a single phase."""
    complete_count = sum(1 for m in phase.modules if m.status == "complete")
    total = len(phase.modules)

    html_parts = [
        f"<h2>Phase {phase.number}: {phase.title}</h2>",
        f"<p><strong>Weeks {phase.weeks}</strong> | {complete_count}/{total} complete</p>",
        '<div class="modules-grid">',
    ]

    for module in phase.modules:
        html_parts.append(generate_module_card_html(module))

    html_parts.append("</div>")
    return "\n".join(html_parts)


def generate_curriculum_html(config: PathConfig) -> bool:
    """Generate HTML version of curriculum."""
    if not config.master_curriculum.exists():
        print(f"ERROR: {config.master_curriculum} not found")
        return False

    curriculum = parse_curriculum(config.master_curriculum)

    # Create output directories
    output_dir = config.html_output_dir / "curriculum"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate main index
    counts = curriculum.modules_by_status()
    total = sum(counts.values())
    complete = counts["complete"]

    body_html = [
        "<h1>Neural Dojo: Master Curriculum</h1>",
        f"<p><em>From Zero to AI Guru</em></p>",
        f"<p><strong>Last Updated:</strong> {curriculum.last_updated}</p>",
        progress_stats_html(complete, counts.get("theory_only", 0), counts["in_progress"], counts["pending"]),
        "<h2>Phases</h2>",
        '<div class="phases-grid">',
    ]

    for phase in curriculum.phases:
        complete_count = sum(1 for m in phase.modules if m.status == "complete")
        total_count = len(phase.modules)
        body_html.append(f'''
        <div class="phase-card">
            <h3><a href="phase{phase.number}.html">Phase {phase.number}: {phase.title}</a></h3>
            <p>Weeks {phase.weeks} | {complete_count}/{total_count} complete</p>
        </div>
        ''')

    body_html.append("</div>")

    # Navigation
    nav_items = [("index.html", "Overview")]
    for phase in curriculum.phases:
        nav_items.append((f"phase{phase.number}.html", f"Phase {phase.number}"))

    index_html = html_template(
        "Neural Dojo Curriculum",
        "Master AI, ML, LLMs, and AI-Driven Development",
        "\n".join(body_html),
        nav_bar(nav_items, "index.html"),
        "linear-gradient(135deg, #1e40af, #7c3aed)",
    )

    (output_dir / "index.html").write_text(index_html)
    print(f"Generated {output_dir / 'index.html'}")

    # Generate phase pages
    for phase in curriculum.phases:
        phase_body = generate_phase_html(phase, curriculum)
        phase_html = html_template(
            f"Phase {phase.number}: {phase.title}",
            f"Weeks {phase.weeks}",
            phase_body,
            nav_bar(nav_items, f"phase{phase.number}.html"),
            "linear-gradient(135deg, #059669, #10b981)",
        )
        (output_dir / f"phase{phase.number}.html").write_text(phase_html)
        print(f"Generated phase{phase.number}.html")

    return True


def generate_theory_html(config: PathConfig) -> bool:
    """Generate HTML for theory files."""
    if not MARKDOWN_AVAILABLE:
        print("Skipping theory HTML: markdown package not available")
        return False

    modules_dir = config.html_output_dir / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)

    # Find all theory files
    theory_files = list(config.notes_dir.glob("module*.md"))
    print(f"Found {len(theory_files)} theory files")

    for md_file in sorted(theory_files):
        content = md_file.read_text()
        html_content = md_to_html(content)

        # Extract title from first line
        lines = content.split("\n")
        title = lines[0].lstrip("# ") if lines else md_file.stem

        html = html_template(
            title,
            "Neural Dojo Theory",
            html_content,
            f'<a href="../curriculum/index.html">← Back to Curriculum</a>',
            "linear-gradient(135deg, #475569, #64748b)",
        )

        output_file = modules_dir / md_file.name.replace(".md", ".html")
        output_file.write_text(html)
        print(f"Generated {output_file.name}")

    return True


def clean_generated(config: PathConfig) -> None:
    """Clean generated files."""
    if config.html_output_dir.exists():
        shutil.rmtree(config.html_output_dir)
        print(f"Cleaned {config.html_output_dir}")

    if config.module_index.exists():
        config.module_index.unlink()
        print(f"Cleaned {config.module_index}")


def serve_docs(config: PathConfig, port: int = 8000) -> None:
    """Serve generated docs locally."""
    if not config.html_output_dir.exists():
        print("No generated docs found. Run with --all first.")
        return

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(config.html_output_dir), **kwargs)

    print(f"Serving docs at http://localhost:{port}")
    print("Press Ctrl+C to stop")

    with socketserver.TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped server")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Neural Dojo Documentation Generator")
    parser.add_argument("--index", action="store_true", help="Generate MODULE_INDEX.md")
    parser.add_argument("--html", action="store_true", help="Generate HTML documentation")
    parser.add_argument("--all", action="store_true", help="Generate everything")
    parser.add_argument("--serve", action="store_true", help="Generate and serve locally")
    parser.add_argument("--clean", action="store_true", help="Clean generated files")
    parser.add_argument("--port", type=int, default=8000, help="Port for serving (default: 8000)")

    args = parser.parse_args()
    config = get_default_config()

    if args.clean:
        clean_generated(config)
        if not (args.index or args.html or args.all or args.serve):
            return

    if args.all or args.serve:
        generate_index_file(config)
        generate_curriculum_html(config)
        generate_theory_html(config)
        if args.serve:
            serve_docs(config, args.port)
    elif args.index:
        generate_index_file(config)
    elif args.html:
        generate_curriculum_html(config)
        generate_theory_html(config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
