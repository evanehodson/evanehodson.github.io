import markdown
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# === FOLDERS ===
DRAFTS = Path("drafts")
POSTS = Path("posts")
POSTS.mkdir(exist_ok=True)

# === PROJECT DEFINITIONS ===
PROJECTS = {
    "GradeSense": {
        "title": "GradeSense",
        "summary": "Terrain-aware ultramarathon pacing and finishing-time prediction model.",
    }
}

# === COLLECT POSTS ===
project_posts = defaultdict(list)

for md in sorted(DRAFTS.glob("*.md"), reverse=True):
    text = md.read_text(encoding="utf-8")
    lines = text.splitlines()

    project = None
    for line in lines[:10]:
        if line.lower().startswith("tags:"):
            project = line.split(":", 1)[1].strip()

    if project not in PROJECTS:
        continue

    # Remove metadata
    content_lines = [
        line for line in lines
        if not line.lower().startswith("tags:")
    ]
    clean_text = "\n".join(content_lines)

    # Markdown → HTML
    html_body = markdown.markdown(clean_text, extensions=["extra"])
    html_body = html_body.replace('src="images/', 'src="../images/')

    date = md.stem

    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y").upper()
        day_name = dt.strftime("%A")
    except:
        formatted_date = date
        day_name = ""

    title = (
        html_body.split("</h1>")[0].replace("<h1>", "")
        if "<h1>" in html_body
        else date
    )

    # === WRITE POST ===
    out = POSTS / f"{date}.html"
    out.write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title} — Devlog</title>
  <link rel="stylesheet" href="../style.css">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<header>
  <a href="../devlog.html">← Back to Devlog</a>
</header>

<article>
  <header>
    <small>{formatted_date} • {day_name}</small>
    <h1>{title}</h1>
  </header>

  <div class="post-content">
{html_body}
  </div>
</article>

<footer>
  <p>Sommet Innovations</p>
</footer>

</body>
</html>
""", encoding="utf-8")

    project_posts[project].append({
        "date": date,
        "title": title,
        "formatted_date": formatted_date,
    })

# === BUILD DEVLOG.HTML ===
projects_html = ""

for key, meta in PROJECTS.items():
    posts = sorted(project_posts[key], key=lambda x: x["date"], reverse=True)
    if not posts:
        continue

    projects_html += f"""
<section class="project">
  <h2>{meta["title"]}</h2>
  <p class="summary">{meta["summary"]}</p>

  <ul class="post-list">
"""
    for post in posts:
        projects_html += f"""
    <li>
      <small>{post["formatted_date"]}</small>
      <a href="posts/{post["date"]}.html">{post["title"]}</a>
    </li>
"""
    projects_html += """
  </ul>
</section>
"""

Path("devlog.html").write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Sommet Innovations — Devlog</title>
  <link rel="stylesheet" href="style.css">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<header>
  <h1>Sommet Innovations</h1>
  <p>Development log and research notes</p>
  <nav>
    <a href="index.html">Home</a>
    <a href="devlog.html">Devlog</a>
  </nav>
</header>

{projects_html}

<footer>
  <p>© 2026 Sommet Innovations.</p>
</footer>

</body>
</html>
""", encoding="utf-8")

print(f"[OK] Built devlog with {sum(len(v) for v in project_posts.values())} posts")