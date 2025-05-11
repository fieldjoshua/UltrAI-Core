#!/usr/bin/env python3
"""
Script to automatically generate an HTML index for UltraAI actions.
This script scans the actions directory structure and generates an updated HTML index.
"""

import glob
import os
import re
from datetime import datetime

# Base directory for actions
ACTIONS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(ACTIONS_DIR, "index.html")


def get_action_status(action_dir):
    """Determine the status of an action based on file presence."""
    # Check for completion file
    if glob.glob(os.path.join(action_dir, "*-COMPLETED.md")):
        return "completed"

    # Check for progress files
    if glob.glob(os.path.join(action_dir, "*progress*.md")) or glob.glob(
        os.path.join(action_dir, "supporting_docs/*progress*.md")
    ):
        return "in-progress"

    # Check if implementation files exist
    if glob.glob(os.path.join(action_dir, "*-IMPLEMENTATION*.md")) or glob.glob(
        os.path.join(action_dir, "supporting_docs/*-IMPLEMENTATION*.md")
    ):
        return "in-progress"

    # Check for plan files
    if glob.glob(os.path.join(action_dir, "*-PLAN*.md")) or glob.glob(
        os.path.join(action_dir, "PLAN.md")
    ):
        return "planning"

    return "pending"


def get_keywords_for_action(action_dir, action_name):
    """Extract keywords from action files."""
    keywords = set([action_name.lower()])

    # Add standard keywords based on the action name
    name_parts = re.findall(r"[A-Z][a-z]*", action_name)
    for part in name_parts:
        keywords.add(part.lower())

    # Try to extract keywords from plan files
    plan_files = glob.glob(os.path.join(action_dir, "*-PLAN*.md"))
    plan_files.extend(glob.glob(os.path.join(action_dir, "PLAN.md")))
    plan_files.extend(glob.glob(os.path.join(action_dir, "supporting_docs/*-PLAN*.md")))

    for plan_file in plan_files:
        if os.path.exists(plan_file):
            try:
                with open(plan_file, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    # Extract potential keywords from headers
                    headers = re.findall(r"##\s+(.*)", content)
                    for header in headers:
                        words = re.findall(r"\b\w+\b", header)
                        for word in words:
                            if len(word) > 3 and word not in [
                                "the",
                                "and",
                                "for",
                                "this",
                                "that",
                                "with",
                            ]:
                                keywords.add(word.lower())
            except Exception as e:
                print(f"Error reading file {plan_file}: {e}")

    return " ".join(keywords)


def get_action_links(action_dir, action_name):
    """Get available links for the action."""
    links = []

    # Check for completion report
    completion_files = glob.glob(os.path.join(action_dir, "*-COMPLETED.md"))
    if completion_files:
        relative_path = os.path.relpath(completion_files[0], ACTIONS_DIR)
        links.append({"title": "Completion Report", "path": relative_path})

    # Check for plan
    plan_files = glob.glob(os.path.join(action_dir, "*-PLAN*.md"))
    plan_files.extend(glob.glob(os.path.join(action_dir, "PLAN.md")))
    if plan_files:
        relative_path = os.path.relpath(plan_files[0], ACTIONS_DIR)
        links.append({"title": "Plan", "path": relative_path})

    # Check for readme
    readme_files = glob.glob(os.path.join(action_dir, "README.md"))
    if readme_files:
        relative_path = os.path.relpath(readme_files[0], ACTIONS_DIR)
        links.append({"title": "README", "path": relative_path})

    # Check for progress
    progress_files = glob.glob(os.path.join(action_dir, "*progress*.md"))
    if progress_files:
        relative_path = os.path.relpath(progress_files[0], ACTIONS_DIR)
        links.append({"title": "Progress", "path": relative_path})

    # Check for status
    status_files = glob.glob(os.path.join(action_dir, "*status*.md"))
    if status_files:
        relative_path = os.path.relpath(status_files[0], ACTIONS_DIR)
        links.append({"title": "Status", "path": relative_path})

    # Check for implementation
    impl_files = glob.glob(os.path.join(action_dir, "*-IMPLEMENTATION*.md"))
    impl_files.extend(
        glob.glob(os.path.join(action_dir, "supporting_docs/*-IMPLEMENTATION*.md"))
    )
    if impl_files:
        relative_path = os.path.relpath(impl_files[0], ACTIONS_DIR)
        links.append({"title": "Implementation", "path": relative_path})

    # Add supporting docs if they exist
    supporting_docs_dir = os.path.join(action_dir, "supporting_docs")
    if os.path.exists(supporting_docs_dir) and os.path.isdir(supporting_docs_dir):
        relative_path = os.path.relpath(supporting_docs_dir, ACTIONS_DIR)
        links.append({"title": "Supporting Docs", "path": f"{relative_path}/"})

    # Add source code if it exists
    src_dir = os.path.join(action_dir, "src")
    if os.path.exists(src_dir) and os.path.isdir(src_dir):
        relative_path = os.path.relpath(src_dir, ACTIONS_DIR)
        links.append({"title": "Source Code", "path": f"{relative_path}/"})

    return links


def scan_actions():
    """Scan the actions directory and categorize actions."""
    actions = []

    # Get subdirectories in the actions directory
    action_dirs = [
        d
        for d in glob.glob(os.path.join(ACTIONS_DIR, "*"))
        if os.path.isdir(d) and not os.path.basename(d).startswith(".")
    ]

    for action_dir in action_dirs:
        action_name = os.path.basename(action_dir)

        # Skip the garbage folder
        if action_name.lower() == "garbage":
            continue

        status = get_action_status(action_dir)
        keywords = get_keywords_for_action(action_dir, action_name)
        links = get_action_links(action_dir, action_name)

        actions.append(
            {
                "name": action_name,
                "status": status,
                "keywords": keywords,
                "links": links,
            }
        )

    # Sort actions: completed first, then in-progress, then planning, then pending
    status_order = {"completed": 1, "in-progress": 2, "planning": 3, "pending": 4}
    actions.sort(key=lambda x: (status_order.get(x["status"], 5), x["name"]))

    return actions


def count_actions_by_status(actions):
    """Count actions by their status."""
    counts = {
        "completed": 0,
        "in-progress": 0,
        "planning": 0,
        "pending": 0,
        "total": len(actions),
    }

    for action in actions:
        status = action["status"]
        counts[status] = counts.get(status, 0) + 1

    return counts


def generate_html(actions):
    """Generate HTML content for the actions index."""
    # Count actions by status
    counts = count_actions_by_status(actions)

    # Group actions by status
    actions_by_status = {}
    for action in actions:
        status = action["status"]
        if status not in actions_by_status:
            actions_by_status[status] = []
        actions_by_status[status].append(action)

    # Generate the HTML content
    html_content = (
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UltraAI Actions Index</title>
    <style>
        :root {
            --primary-color: #0F172A;
            --secondary-color: #1E293B;
            --highlight-color: #3B82F6;
            --text-color: #E2E8F0;
            --success-color: #10B981;
            --pending-color: #F59E0B;
            --planning-color: #8B5CF6;
            --border-color: #334155;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            background-color: var(--primary-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }

        h1, h2, h3 {
            color: var(--text-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }

        h1 {
            font-size: 2.2rem;
            text-align: center;
            margin-bottom: 2rem;
        }

        h2 {
            font-size: 1.8rem;
            margin-top: 2rem;
        }

        .section {
            margin-bottom: 3rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .card {
            background-color: var(--secondary-color);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            height: 4px;
            width: 100%;
        }

        .card.completed::before {
            background-color: var(--success-color);
        }

        .card.in-progress::before {
            background-color: var(--highlight-color);
        }

        .card.planning::before {
            background-color: var(--planning-color);
        }

        .card.pending::before {
            background-color: var(--pending-color);
        }

        .card h3 {
            margin-top: 5px;
            font-size: 1.3rem;
            border-bottom: none;
            padding-bottom: 0;
        }

        .status {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status.completed {
            background-color: var(--success-color);
            color: white;
        }

        .status.in-progress {
            background-color: var(--highlight-color);
            color: white;
        }

        .status.planning {
            background-color: var(--planning-color);
            color: white;
        }

        .status.pending {
            background-color: var(--pending-color);
            color: white;
        }

        .card-links {
            margin-top: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .card-link {
            display: inline-block;
            text-decoration: none;
            color: var(--text-color);
            background-color: rgba(255, 255, 255, 0.1);
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 0.9rem;
            transition: background-color 0.2s ease;
        }

        .card-link:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }

        .search-container {
            margin-bottom: 30px;
        }

        .search-input {
            width: 100%;
            padding: 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: var(--secondary-color);
            color: var(--text-color);
            font-size: 1rem;
        }

        .search-input::placeholder {
            color: rgba(226, 232, 240, 0.6);
        }

        .empty-state {
            text-align: center;
            padding: 30px;
            background-color: var(--secondary-color);
            border-radius: 8px;
            margin-top: 20px;
        }

        .stat-bar {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin: 30px 0;
            flex-wrap: wrap;
        }

        .stat {
            background-color: var(--secondary-color);
            border-radius: 8px;
            padding: 15px 20px;
            text-align: center;
            min-width: 150px;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }

        footer {
            margin-top: 50px;
            text-align: center;
            padding: 20px;
            border-top: 1px solid var(--border-color);
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .meta-info {
            font-size: 0.8rem;
            margin-top: 15px;
            text-align: center;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <h1>UltraAI Actions Index</h1>

    <div class="search-container">
        <input type="text" class="search-input"
               placeholder="Search actions..." id="search-input">
    </div>

    <div class="stat-bar">
        <div class="stat">
            <div class="stat-value">"""
        + str(counts.get("completed", 0))
        + """</div>
            <div class="stat-label">Completed</div>
        </div>
        <div class="stat">
            <div class="stat-value">"""
        + str(counts.get("in-progress", 0))
        + """</div>
            <div class="stat-label">In Progress</div>
        </div>
        <div class="stat">
            <div class="stat-value">"""
        + str(counts.get("total", 0))
        + """</div>
            <div class="stat-label">Total Actions</div>
        </div>
    </div>
    """
    )

    # Add Completed Actions Section
    if "completed" in actions_by_status and actions_by_status["completed"]:
        html_content += """
    <div class="section" id="completed-section">
        <h2>Completed Actions</h2>
        <div class="grid">
    """
        for action in actions_by_status["completed"]:
            html_content += generate_action_card(action)
        html_content += """
        </div>
    </div>
    """

    # Add In Progress Actions Section
    if "in-progress" in actions_by_status and actions_by_status["in-progress"]:
        html_content += """
    <div class="section" id="in-progress-section">
        <h2>In Progress Actions</h2>
        <div class="grid">
    """
        for action in actions_by_status["in-progress"][
            :8
        ]:  # Limit to 8 in-progress actions in this section
            html_content += generate_action_card(action)
        html_content += """
        </div>
    </div>
    """

    # Add Planning Actions Section
    if "planning" in actions_by_status and actions_by_status["planning"]:
        html_content += """
    <div class="section" id="planning-section">
        <h2>Planning Stage Actions</h2>
        <div class="grid">
    """
        for action in actions_by_status["planning"][
            :6
        ]:  # Limit to 6 planning actions in this section
            html_content += generate_action_card(action)
        html_content += """
        </div>
    </div>
    """

    # Add All Actions Section
    html_content += """
    <div class="section" id="all-actions-section">
        <h2>All Actions</h2>
        <div class="grid" id="all-actions-grid">
    """
    for action in actions:
        html_content += generate_action_card(action)
    html_content += """
        </div>
    </div>

    <div id="no-results" class="empty-state" style="display: none;">
        <h3>No actions found matching your search</h3>
        <p>Try a different search term or browse the categories above</p>
    </div>
    """

    # Add footer
    today = datetime.now().strftime("%B %d, %Y")
    html_content += (
        """
    <footer>
        <p>UltraAI Actions Index - Last Updated: """
        + today
        + """</p>
    </footer>

    <div class="meta-info">
        <p>This file is automatically generated by update_index.py</p>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Get all action cards
            const searchInput = document.getElementById('search-input');
            const allCards = document.querySelectorAll('.card');
            const noResults = document.getElementById('no-results');

            // Search functionality
            searchInput.addEventListener('input', function() {{
                const searchTerm = this.value.toLowerCase();
                let hasResults = false;

                document.querySelectorAll('.card').forEach(card => {{
                    const cardContent = card.textContent.toLowerCase();
                    const cardKeywords = card.getAttribute('data-keywords') ||
                        '';

                    if (cardContent.includes(searchTerm) ||
                        cardKeywords.toLowerCase().includes(searchTerm)) {{
                        card.style.display = 'block';
                        hasResults = true;
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});

                // Show/hide sections based on whether they have visible cards
                document.querySelectorAll('.section')
                    .forEach(section => {{
                    // Always show all actions section
                    if (section.id === 'all-actions-section') return;

                    const hasVisibleCards = Array.from(
                        section.querySelectorAll('.card')).some(card =>
                        card.style.display !== 'none'
                    );

                    if (hasVisibleCards) {{
                        section.style.display = 'block';
                    }} else {{
                        section.style.display = 'none';
                    }}
                }});

                // Show/hide no results message
                noResults.style.display = hasResults ? 'none' : 'block';
            }});
        }});
    </script>
</body>
</html>
    """
    )

    return html_content


def generate_action_card(action):
    """Generate HTML for an action card."""
    name = action["name"]
    status = action["status"]
    keywords = action["keywords"]
    links = action["links"]

    card_html = (
        """
            <div class="card """
        + status
        + """" data-keywords=\""""
        + keywords
        + """\">
                <span class="status """
        + status
        + """">"""
        + status.replace("-", " ").title()
        + """</span>
                <h3>"""
        + name
        + """</h3>
                <div class="card-links">
    """
    )

    for link in links:
        card_html += (
            """
                    <a href=\""""
            + link["path"]
            + """\" class="card-link">"""
            + link["title"]
            + """</a>
        """
        )

    card_html += """
                </div>
            </div>
    """

    return card_html


def main():
    """Main function to scan actions and generate the HTML index."""
    print("Scanning actions...")
    actions = scan_actions()
    print(f"Found {len(actions)} actions.")

    print("Generating HTML index...")
    html_content = generate_html(actions)

    print(f"Writing HTML to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML index generated successfully.")


if __name__ == "__main__":
    main()
