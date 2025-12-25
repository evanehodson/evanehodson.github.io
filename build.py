import markdown
from pathlib import Path
from collections import defaultdict

DRAFTS = Path("drafts")
POSTS = Path("posts")
POSTS.mkdir(exist_ok=True)

# Group posts by project
projects = defaultdict(list)

for md in sorted(DRAFTS.glob("*.md"), reverse=True):
    text = md.read_text()
    lines = text.splitlines()

    # Extract project tag
    project = None
    for line in lines[:5]:
        if line.lower().startswith("tags:"):
            project = line.split(":", 1)[1].strip()
            break

    html_body = markdown.markdown(text, extensions=["extra"])
    date = md.stem
    title = html_body.split("</h1>")[0].replace("<h1>", "") if "<h1>" in html_body else date

    # Save post HTML
    out = POSTS / f"{date}.html"
    out.write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title} — Sommet Innovations</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
<header><a href="../index.html">← Development Log</a></header>
<article>
{html_body}
</article>
<footer><p>Sommet Innovations · Development Log · {date}</p></footer>
</body>
</html>
""", encoding="utf-8")

    # Add to projects dict
    projects[project].append((date, title))

# === Generate index.html grouped by project ===
index_entries = ""
for project, posts_list in sorted(projects.items()):
    index_entries += f"<h2>{project}</h2>\n<ul>\n"
    for date, title in sorted(posts_list, reverse=True):
        index_entries += f'<li><a href="posts/{date}.html">{title}</a> <small>{date}</small></li>\n'
    index_entries += "</ul>\n"

Path("index.html").write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Sommet Innovations — Development Log</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<header><h1>Sommet Innovations</h1></header>
<section class="about">
  <p>This site documents ongoing research and development at <strong>Sommet Innovations</strong>.</p>
</section>
{index_entries}
</body>
</html>
""", encoding="utf-8")
