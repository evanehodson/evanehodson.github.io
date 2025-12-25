import markdown
from pathlib import Path
from collections import defaultdict

# === FOLDERS ===
DRAFTS = Path("drafts")
POSTS = Path("posts")
POSTS.mkdir(exist_ok=True)

# === HARD-CODED PROJECT DEFINITIONS ===
PROJECTS = {
    "GradeSense": {
        "title": "GradeSense",
        "summary": "A terrain-aware ultramarathon pacing and finishing-time prediction model that integrates gradient, fitness, and fatigue dynamics.",
    }
}

# === COLLECT POSTS BY PROJECT ===
project_posts = defaultdict(list)

for md in sorted(DRAFTS.glob("*.md"), reverse=True):
    text = md.read_text()
    lines = text.splitlines()

    # --- Extract project tag ---
    project = None
    for line in lines[:5]:
        if line.lower().startswith("tags:"):
            project = line.split(":", 1)[1].strip()
            break

    # Skip posts that aren't assigned to a known project
    if project not in PROJECTS:
        continue

    # --- Convert markdown to HTML ---
    html_body = markdown.markdown(text, extensions=["extra"])
    date = md.stem
    title = (
        html_body.split("</h1>")[0].replace("<h1>", "")
        if "<h1>" in html_body
        else date
    )

    # --- Write per-post HTML ---
    out = POSTS / f"{date}.html"
    out.write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title} — Sommet Innovations</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>

<header>
  <a href="../index.html">← Development Log</a>
</header>

<article>
{html_body}
</article>

<footer>
  <p>Sommet Innovations · Development Log · {date}</p>
</footer>

</body>
</html>
""", encoding="utf-8")

    # --- Register post under project ---
    project_posts[project].append((date, title))

# === BUILD INDEX.HTML ===
sections_html = ""

for key, meta in PROJECTS.items():
    posts = sorted(project_posts.get(key, []), reverse=True)

    sections_html += f"""
<section class="project">
  <h2>{meta['title']}</h2>
  <p class="summary">{meta['summary']}</p>

  <ul class="post-list">
"""
    for date, title in posts:
        sections_html += f'    <li><a href="posts/{date}.html">{title}</a> <small>{date}</small></li>\n'

    sections_html += """
  </ul>
</section>
"""

Path("index.html").write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Sommet Innovations — Development Log</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>

<header>
  <h1>Sommet Innovations</h1>
</header>

<section class="about">
  <p>
    This site documents ongoing research and development at <strong>Sommet Innovations</strong>.
  </p>
</section>

{sections_html}

</body>
</html>
""", encoding="utf-8")
