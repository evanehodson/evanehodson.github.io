import markdown
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# === FOLDERS ===
DRAFTS = Path("drafts")
POSTS = Path("posts")
POSTS.mkdir(exist_ok=True)

# === HARD-CODED PROJECT DEFINITIONS ===
PROJECTS = {
    "GradeSense": {
        "title": "GradeSense",
        "summary": "Terrain-aware ultramarathon pacing and finishing-time prediction model.",
        "emoji": "⛰️",
        "category": "ML"
    }
}

# === COLLECT POSTS BY PROJECT ===
project_posts = defaultdict(list)
total_sessions = 0

for md in sorted(DRAFTS.glob("*.md"), reverse=True):
    text = md.read_text()
    lines = text.splitlines()

    # --- Extract metadata ---
    project = None
    duration = None
    
    for line in lines[:10]:
        if line.lower().startswith("tags:"):
            project = line.split(":", 1)[1].strip()
        if line.lower().startswith("duration:"):
            duration = line.split(":", 1)[1].strip()

    # Skip posts that aren't assigned to a known project
    if project not in PROJECTS:
        continue

    total_sessions += 1

    # --- Convert markdown to HTML ---
    html_body = markdown.markdown(text, extensions=["extra"])
    date = md.stem
    
    # Parse title
    title = (
        html_body.split("</h1>")[0].replace("<h1>", "")
        if "<h1>" in html_body
        else date
    )
    
    # Format date nicely
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y").upper()
        day_name = dt.strftime("%A")
    except:
        formatted_date = date
        day_name = ""

    # --- Write per-post HTML ---
    out = POSTS / f"{date}.html"
    out.write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title} — Dev Log</title>
  <link rel="stylesheet" href="../style.css">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<header>
  <a href="../index.html">← Back to Log</a>
</header>

<article>
  <header>
    <small>{formatted_date} • {day_name}</small>
    <h1>{title}</h1>
    {f'<p class="duration">Duration: {duration}</p>' if duration else ''}
  </header>
  
  <div class="session-content">
{html_body}
  </div>
</article>

<footer>
  <p>Session logged: {formatted_date}</p>
</footer>

</body>
</html>
""", encoding="utf-8")

    # --- Register post under project ---
    project_posts[project].append({
        "date": date,
        "title": title,
        "formatted_date": formatted_date,
        "duration": duration,
        "day_name": day_name
    })

# === CALCULATE STATS ===
# Count posts per month for activity
monthly_activity = defaultdict(int)
for project in project_posts.values():
    for post in project:
        try:
            dt = datetime.strptime(post["date"], "%Y-%m-%d")
            month_key = dt.strftime("%Y-%m")
            monthly_activity[month_key] += 1
        except:
            pass

recent_months = sorted(monthly_activity.items(), reverse=True)[:3]

# === BUILD INDEX.HTML ===
stats_html = f"""
<div class="stats">
  <div class="stat">
    <div class="stat-value">{total_sessions}</div>
    <div class="stat-label">Total Sessions</div>
  </div>
  <div class="stat">
    <div class="stat-value">{len(project_posts)}</div>
    <div class="stat-label">Active Projects</div>
  </div>
  <div class="stat">
    <div class="stat-value">{monthly_activity.get(datetime.now().strftime('%Y-%m'), 0)}</div>
    <div class="stat-label">This Month</div>
  </div>
</div>
"""

# Recent activity
recent_activity = []
for project_name, posts in project_posts.items():
    for post in posts:
        recent_activity.append({
            "project": project_name,
            "post": post
        })

recent_activity = sorted(recent_activity, key=lambda x: x["post"]["date"], reverse=True)[:10]

recent_html = """
<section class="recent-sessions">
  <h2>Recent Sessions</h2>
  <ul class="post-list">
"""

for item in recent_activity:
    post = item["post"]
    project = item["project"]
    emoji = PROJECTS[project].get("emoji", "📝")
    
    recent_html += f"""    <li>
      <small>{post['formatted_date']}</small>
      <a href="posts/{post['date']}.html">
        <span class="project-tag">{emoji} {project}</span>
        {post['title']}
      </a>
    </li>
"""

recent_html += """
  </ul>
</section>
"""

# Projects section
projects_html = ""
for key, meta in PROJECTS.items():
    posts = sorted(project_posts.get(key, []), key=lambda x: x["date"], reverse=True)
    
    if not posts:
        continue
    
    emoji = meta.get("emoji", "📝")
    
    projects_html += f"""
<section class="project">
  <h2>{emoji} {meta['title']}</h2>
  <p class="summary">{meta['summary']}</p>
  <div class="project-stats">
    <span>{len(posts)} sessions logged</span>
  </div>

  <ul class="post-list">
"""
    for post in posts:
        projects_html += f"""    <li>
      <small>{post['formatted_date']}</small>
      <a href="posts/{post['date']}.html">{post['title']}</a>
    </li>
"""

    projects_html += """
  </ul>
</section>
"""

Path("index.html").write_text(f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Development Log — Sommet Innovations</title>
  <link rel="stylesheet" href="style.css">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<header>
  <h1>Development Log</h1>
  <p>Sommet Innovations</p>
</header>

{stats_html}

{recent_html}

{projects_html}

<footer>
  <p>Keep building. Keep logging.</p>
</footer>

</body>
</html>
""", encoding="utf-8")

print(f"[OK] Built {total_sessions} sessions across {len(project_posts)} projects")