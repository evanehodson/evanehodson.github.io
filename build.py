import markdown
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

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
all_sessions = []

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
        dt = None
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

    # --- Register session ---
    session = {
        "date": date,
        "title": title,
        "formatted_date": formatted_date,
        "duration": duration,
        "day_name": day_name,
        "project": project,
        "dt": dt
    }
    
    project_posts[project].append(session)
    all_sessions.append(session)

# Sort all sessions by date
all_sessions = sorted([s for s in all_sessions if s["dt"]], key=lambda x: x["dt"], reverse=True)

# === CALCULATE WEEKLY STATS ===
now = datetime.now()
week_start = now - timedelta(days=now.weekday())  # Monday
week_sessions = [s for s in all_sessions if s["dt"] >= week_start]

# Parse durations for weekly total
def parse_duration(dur_str):
    """Convert '2h 30m' to minutes"""
    if not dur_str:
        return 0
    total = 0
    parts = dur_str.lower().replace(',', '').split()
    for i, part in enumerate(parts):
        if 'h' in part:
            total += int(part.replace('h', '')) * 60
        elif 'm' in part:
            total += int(part.replace('m', ''))
        elif i > 0 and parts[i-1].replace('.', '').isdigit():
            # Handle "2 h 30 m" format
            if 'h' in part:
                total += int(parts[i-1]) * 60
            elif 'm' in part:
                total += int(parts[i-1])
    return total

def format_duration(minutes):
    """Convert minutes to '2h 30m' format"""
    if minutes == 0:
        return "0m"
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h"
    else:
        return f"{mins}m"

week_total_minutes = sum(parse_duration(s["duration"]) for s in week_sessions)
week_total_formatted = format_duration(week_total_minutes)

# Average session duration this week
week_avg_minutes = week_total_minutes // len(week_sessions) if week_sessions else 0
week_avg_formatted = format_duration(week_avg_minutes)

# === CALCULATE MONTHLY STATS ===
month_start = now.replace(day=1)
month_sessions = [s for s in all_sessions if s["dt"] >= month_start]
month_total_minutes = sum(parse_duration(s["duration"]) for s in month_sessions)

# === CALCULATE STREAK ===
dates_with_sessions = sorted(set(s["dt"].date() for s in all_sessions if s["dt"]), reverse=True)

current_streak = 0
if dates_with_sessions:
    current_date = now.date()
    # Check if there's a session today or yesterday (to not break streak)
    if dates_with_sessions[0] >= current_date - timedelta(days=1):
        current_streak = 1
        check_date = dates_with_sessions[0] - timedelta(days=1)
        
        for session_date in dates_with_sessions[1:]:
            if session_date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            elif session_date < check_date:
                break

# Longest streak ever
longest_streak = 0
temp_streak = 1
for i in range(len(dates_with_sessions) - 1):
    if dates_with_sessions[i] - dates_with_sessions[i+1] == timedelta(days=1):
        temp_streak += 1
        longest_streak = max(longest_streak, temp_streak)
    else:
        temp_streak = 1
longest_streak = max(longest_streak, temp_streak, current_streak)

# === BUILD CALENDAR HEATMAP ===
# Last 8 weeks
calendar_html = '<div class="calendar">\n'
calendar_html += '  <div class="calendar-labels">\n'
calendar_html += '    <span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span>\n'
calendar_html += '  </div>\n'

# Get sessions count per day
session_counts = defaultdict(int)
for s in all_sessions:
    if s["dt"]:
        session_counts[s["dt"].date()] += 1

# Generate 8 weeks of calendar
for week_offset in range(7, -1, -1):
    week_start_date = now.date() - timedelta(days=now.weekday() + week_offset * 7)
    calendar_html += '  <div class="calendar-week">\n'
    
    for day_offset in range(7):
        day_date = week_start_date + timedelta(days=day_offset)
        count = session_counts.get(day_date, 0)
        
        # Determine intensity class
        if count == 0:
            intensity = "empty"
        elif count == 1:
            intensity = "low"
        elif count == 2:
            intensity = "medium"
        else:
            intensity = "high"
        
        # Don't show future dates
        if day_date > now.date():
            calendar_html += f'    <span class="calendar-day future"></span>\n'
        else:
            calendar_html += f'    <span class="calendar-day {intensity}" title="{day_date}: {count} sessions"></span>\n'
    
    calendar_html += '  </div>\n'

calendar_html += '</div>\n'

# === WEEKLY BANNER ===
week_banner = f"""
<div class="weekly-banner">
  <div class="banner-stat">
    <div class="banner-value">{len(week_sessions)}</div>
    <div class="banner-label">Sessions This Week</div>
  </div>
  <div class="banner-stat">
    <div class="banner-value">{week_total_formatted}</div>
    <div class="banner-label">Total Time</div>
  </div>
  <div class="banner-stat">
    <div class="banner-value">{week_avg_formatted}</div>
    <div class="banner-label">Avg Per Session</div>
  </div>
</div>
"""

# === MONTHLY STATS SECTION ===
monthly_stats = f"""
<section class="monthly-stats">
  <h2>Monthly Overview — {now.strftime('%B %Y').upper()}</h2>
  
  <div class="stats-grid">
    <div class="stat-box">
      <div class="stat-value">{len(month_sessions)}</div>
      <div class="stat-label">Sessions</div>
    </div>
    <div class="stat-box">
      <div class="stat-value">{format_duration(month_total_minutes)}</div>
      <div class="stat-label">Total Time</div>
    </div>
    <div class="stat-box">
      <div class="stat-value">{current_streak}</div>
      <div class="stat-label">Current Streak</div>
    </div>
    <div class="stat-box">
      <div class="stat-value">{longest_streak}</div>
      <div class="stat-label">Longest Streak</div>
    </div>
  </div>
  
  <div class="calendar-container">
    <h3>Last 8 Weeks</h3>
    {calendar_html}
    <div class="calendar-legend">
      <span>Less</span>
      <span class="legend-box empty"></span>
      <span class="legend-box low"></span>
      <span class="legend-box medium"></span>
      <span class="legend-box high"></span>
      <span>More</span>
    </div>
  </div>
</section>
"""

# === RECENT SESSIONS ===
recent_activity = all_sessions[:10]

recent_html = """
<section class="recent-sessions">
  <h2>Recent Sessions</h2>
  <ul class="post-list">
"""

for session in recent_activity:
    emoji = PROJECTS[session["project"]].get("emoji", "📝")
    recent_html += f"""    <li>
      <small>{session['formatted_date']}</small>
      <a href="posts/{session['date']}.html">
        <span class="project-tag">{emoji} {session['project']}</span>
        {session['title']}
      </a>
    </li>
"""

recent_html += """
  </ul>
</section>
"""

# === PROJECTS SECTION ===
projects_html = ""
for key, meta in PROJECTS.items():
    posts = sorted(project_posts.get(key, []), key=lambda x: x["date"], reverse=True)
    
    if not posts:
        continue
    
    emoji = meta.get("emoji", "📝")
    project_total_minutes = sum(parse_duration(p["duration"]) for p in posts)
    
    projects_html += f"""
<section class="project">
  <h2>{emoji} {meta['title']}</h2>
  <p class="summary">{meta['summary']}</p>
  <div class="project-stats">
    <span>{len(posts)} sessions</span>
    <span>•</span>
    <span>{format_duration(project_total_minutes)} total</span>
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

# === BUILD INDEX.HTML ===
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

{week_banner}

{monthly_stats}

{recent_html}

{projects_html}

<footer>
  <p>Keep building. Keep logging.</p>
</footer>

</body>
</html>
""", encoding="utf-8")

print(f"[OK] Built {len(all_sessions)} sessions across {len(project_posts)} projects")
print(f"[OK] This week: {len(week_sessions)} sessions, {week_total_formatted}")
print(f"[OK] Current streak: {current_streak} days")