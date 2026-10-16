"""Build a 30-day SVG from public GitHub Events API data (not a contribution calendar)."""
import datetime as dt
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

user = 'AlexBerchtold'
token = os.environ.get('GH_TOKEN', '')
headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'AlexBerchtold-profile'}
if token:
    headers['Authorization'] = f'Bearer {token}'
today = dt.datetime.now(dt.timezone.utc).date()
dates = [today - dt.timedelta(days=i) for i in range(29, -1, -1)]
counts = {d.isoformat(): 0 for d in dates}
for page in range(1, 4):
    req = Request(f'https://api.github.com/users/{user}/events/public?per_page=100&page={page}', headers=headers)
    with urlopen(req, timeout=25) as response:
        events = json.load(response)
    if not events:
        break
    for event in events:
        date = event.get('created_at', '')[:10]
        if date in counts:
            counts[date] += 1
    if len(events) < 100:
        break

width, height = 800, 160
bars = []
max_count = max(counts.values(), default=0)
for i, date in enumerate(dates):
    value = counts[date.isoformat()]
    bar_height = round(value / max_count * 85) if max_count else 0
    x = 26 + i * 25
    y = 124 - bar_height
    color = '#3b82f6' if value else '#30363d'
    bars.append(f'<rect x="{x}" y="{y}" width="16" height="{max(2, bar_height)}" rx="3" fill="{color}"/><title>{date.isoformat()}: {value} eventos públicos</title>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Eventos públicos recientes en GitHub, últimos 30 días">
<rect width="100%" height="100%" rx="12" fill="#0d1117"/>
<text x="24" y="27" font-family="Arial,sans-serif" font-size="15" font-weight="bold" fill="#f0f6fc">Actividad pública reciente</text>
<text x="24" y="47" font-family="Arial,sans-serif" font-size="11" fill="#8b949e">Eventos públicos registrados por GitHub · últimos 30 días · no equivale al calendario de contribuciones</text>
{''.join(bars)}
<text x="24" y="146" font-family="Arial,sans-serif" font-size="11" fill="#8b949e">{dates[0].isoformat()}</text>
<text x="775" y="146" text-anchor="end" font-family="Arial,sans-serif" font-size="11" fill="#8b949e">{today.isoformat()}</text>
</svg>'''
Path('dist').mkdir(exist_ok=True)
Path('dist/public-activity.svg').write_text(svg, encoding='utf-8')
