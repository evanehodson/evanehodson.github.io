import markdown
from pathlib import Path
from datetime import datetime

DRAFTS = Path("drafts")
POSTS = Path("posts")
POSTS.mkdir(exist_ok=True)

entries = []

for md in sorted(DRAFTS.glob("*.md"), reverse=True):
    html_body = markdown.markdown(md.read_text(), extensions=["extra"])
    date = md.stem

    title = html_body.split("</h1>")[0].replace("<h1>", "") if "<h1>" in html_body else date

    out = POSTS / f"{date}.html"
    out.write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="../style.css">
</head>
<body>
<a href="../index.html">← Home</a>
{html_body}
</body>
</html>
""", encoding="utf-8")

    entries.append(f'<li><a href="posts/{date}.html">{title}</a> <small>{date}</small></li>')

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
  <p class="subtitle">
    Research & Development Log — Modeling endurance performance, terrain, and fatigue.
  </p>
</header>

<section class="about">
  <p>
    This site documents ongoing research and development at <strong>Sommet Innovations</strong>.
    Entries reflect active work in progress: modeling decisions, assumptions, failures,
    and technical breakthroughs related to endurance performance prediction.
  </p>
</section>

<h2>Development Log</h2>

<ul class="post-list">
{chr(10).join(entries)}
</ul>

<footer>
  <p>
    © Sommet Innovations — Open development notes. Not polished. Not final.
  </p>
</footer>

</body>
</html>
""", encoding="utf-8")
