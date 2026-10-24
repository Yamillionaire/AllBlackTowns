#!/usr/bin/env python3
"""Build the All Black Towns v1 static site."""
import json, re, html

SITE = "/home/hatch/workspace/allblacktowns-site"
towns = json.load(open(f"{SITE}/towns.json"))
duptext = open("/home/hatch/workspace/goals/blacktown-project/files/suno-duplicates-map.md").read()
canonicals = re.findall(r'^### (.+)$', duptext, re.M)
singles = re.findall(r'^- (.+?) \([A-Z][^)]*\)$', duptext, re.M)
songs = canonicals + singles

states = sorted(set(t["state"] for t in towns if t["state"]))
with_about = [t for t in towns if t["about"]]
featured = [t for t in with_about if t["town"] in
            ("Overtown", "Boley", "Blackdom", "Nicodemus", "Rosewood", "Seneca Village")]
if len(featured) < 6:
    featured += [t for t in with_about if t not in featured][:6 - len(featured)]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - All Black Towns</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
<script>document.documentElement.classList.add('js');</script>
</head>
<body>
<nav><div class="wrap nav-inner">
<a class="brand" href="index.html">All <span>Black</span> Towns</a>
<div class="nav-links">
<a href="index.html" class="{h}">Home</a>
<a href="towns.html" class="{t}">Towns</a>
<a href="map.html" class="{mp}">Map</a>
<a href="music.html" class="{m}">Music</a>
<a href="about.html" class="{a}">About</a>
</div></div></nav>
"""

FOOT = """
<section class="block alt newsletter" id="newsletter"><div class="wrap">
<div class="rule" style="margin:0 auto 26px"></div>
<h2>Hear every town's song first.</h2>
<p>Join the list for new releases, town histories, and the stories behind the music. One email when it matters - never noise.</p>
<form class="nl-form" action="https://formsubmit.co/REPLACE_WITH_YOUR_EMAIL" method="POST">
<input type="email" name="email" placeholder="Your email address" required>
<input type="hidden" name="_subject" value="New All Black Towns subscriber">
<button class="btn" type="submit">Join the list</button>
</form>
<p class="nl-note">Free forever. Unsubscribe anytime.</p>
</div></section>
<footer><div class="wrap">
<a class="brand" href="index.html">All <span>Black</span> Towns</a>
<p style="margin-top:12px">A music project honoring the historic Black towns of America -<br>one town, one song, one story at a time.</p>
<p style="margin-top:14px; opacity:.6">&copy; 2026 All Black Towns. All rights reserved.</p>
</div></footer>

<script>
(function(){
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var els = document.querySelectorAll('[data-rv]');
  if (RM || !('IntersectionObserver' in window)) { els.forEach(function(e){ e.classList.add('in'); }); }
  else {
    var io = new IntersectionObserver(function(es){ es.forEach(function(en){ if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, {threshold: .12});
    els.forEach(function(e){ io.observe(e); });
  }
  function countUp(el){
    var target = parseInt(el.textContent, 10); if (isNaN(target)) return;
    if (RM) { el.textContent = target; return; }
    var t0 = null;
    function step(ts){ if (!t0) t0 = ts; var pr = Math.min((ts - t0) / 1300, 1); el.textContent = Math.round(target * (1 - Math.pow(1 - pr, 3))); if (pr < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  var nums = document.querySelectorAll('.stat .num');
  if ('IntersectionObserver' in window && !RM) {
    var io2 = new IntersectionObserver(function(es){ es.forEach(function(en){ if (en.isIntersecting) { countUp(en.target); io2.unobserve(en.target); } }); }, {threshold: .4});
    nums.forEach(function(n){ io2.observe(n); });
  }
})();
</script>
</body></html>
"""

def page(active, title, desc, body):
    h = HEAD.format(title=title, desc=desc,
                    h="active" if active == "h" else "",
                    t="active" if active == "t" else "",
                    mp="active" if active == "mp" else "",
                    m="active" if active == "m" else "",
                    a="active" if active == "a" else "")
    body = (body.replace('<h2 class="section-title">', '<h2 class="section-title" data-rv>')
                .replace('<p class="section-sub">', '<p class="section-sub" data-rv>')
                .replace('<div class="quote">', '<div class="quote" data-rv>')
                .replace('<div class="stats">', '<div class="stats" data-rv>'))
    return h + body + FOOT

def esc(s):
    return html.escape(s or "")

# ---------- INDEX ----------
cards = "\n".join(
    f'<div class="town-card"><h3>{esc(t["town"])}</h3>'
    f'<div class="state">{esc(t["state"])}</div>'
    f'<p>{esc(t["about"][:220])}{"…" if len(t["about"]) > 220 else ""}</p></div>'
    for t in featured)

index_body = f"""
<header class="hero"><div class="wrap">
<div class="kicker">A music project &middot; {len(towns)} towns &middot; {len(songs)} original songs</div>
<h1>Every Black town<br>has a <em>song.</em></h1>
<p class="lede">From Boley to Blackdom, Rosewood to Seneca Village - All Black Towns is a growing musical archive honoring the historic Black towns and neighborhoods of America, one town and one story at a time.</p>
<a class="btn" href="towns.html">Explore the towns</a>
<a class="btn ghost" href="music.html">Hear the music</a>
<div class="stats">
<div class="stat"><div class="num">{len(towns)}</div><div class="lbl">Towns honored</div></div>
<div class="stat"><div class="num">{len(songs)}</div><div class="lbl">Original songs</div></div>
<div class="stat"><div class="num">50</div><div class="lbl">States &amp; territories</div></div>
</div></div></header>

<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">Towns they tried to erase.</h2>
<p class="section-sub">Thriving Black municipalities, districts, and settlements - built from nothing after Emancipation, many destroyed by violence, policy, or "progress." Each one gets its name sung back into history.</p>
<div class="town-grid">{cards}</div>
<p style="margin-top:34px"><a class="btn ghost" style="margin-left:0" href="towns.html">See all {len(towns)} towns</a></p>
</div></section>

<section class="block alt"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">The music</h2>
<p class="section-sub">{len(songs)} original songs and counting - each written for a specific town, carrying its history in the lyrics. Human-written words, composed with AI instruments, sung so the names are never forgotten.</p>
<a class="btn ghost" style="margin-left:0" href="music.html">Browse the catalog</a>
</div></section>
"""

# ---------- TOWNS ----------
state_opts = "\n".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in states)
town_data = json.dumps([{"town": t["town"], "state": t["state"],
                         "song": t["song"], "about": t["about"]} for t in towns])

towns_body = f"""
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">The towns</h2>
<p class="section-sub">{len(towns)} historic Black towns, districts, and settlements - each with its own song. Search by name or filter by state.</p>
<div class="tools">
<input id="q" type="text" placeholder="Search towns…" oninput="filterTowns()">
<select id="st" onchange="filterTowns()"><option value="">All states</option>{state_opts}</select>
</div>
<div class="count-note" id="count"></div>
<div class="town-grid" id="grid"></div>
</div></section>
<script>
const TOWNS = {town_data};
const grid = document.getElementById('grid');
const count = document.getElementById('count');
function card(t, i) {{
  const about = t.about ? `<p>${{t.about.substring(0, 240)}}${{t.about.length > 240 ? '…' : ''}}</p>` : '';
  return `<div class="town-card" style="--i:${{Math.min(i || 0, 10)}}"><h3>${{t.town}}</h3><div class="state">${{t.state}}</div>${{about}}<div class="song">♪ ${{t.song}}</div></div>`;
}}
function filterTowns() {{
  const q = document.getElementById('q').value.toLowerCase();
  const st = document.getElementById('st').value;
  const list = TOWNS.filter(t =>
    (!q || t.town.toLowerCase().includes(q) || t.song.toLowerCase().includes(q)) &&
    (!st || t.state === st));
  grid.innerHTML = list.map((t, i) => card(t, i)).join('');
  grid.classList.add('anim');
  count.textContent = `Showing ${{list.length}} of ${{TOWNS.length}} towns`;
}}
filterTowns();
</script>
"""

# ---------- MUSIC ----------
song_rows = "\n".join(
    f'<div class="song-row" data-rv><span class="t">{esc(s)}</span></div>' for s in sorted(songs))

music_body = f"""
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">The music</h2>
<p class="section-sub">{len(songs)} original songs - one per town. Every lyric is human-written from historical research; the music is composed with AI instruments. The catalog keeps growing.</p>
<div class="song-list">{song_rows}</div>
</div></section>

<section class="block alt"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">How it's made</h2>
<div class="prose">
<p><strong>Research first.</strong> Each song starts with the real history of a Black town - its founding, its people, what it built, and what happened to it.</p>
<p><strong>Human words.</strong> The lyrics are written by hand from that research, carrying names, dates, and details the history books left out.</p>
<p><strong>New instruments.</strong> The music is composed with AI tools - a new instrument for an old mission: making sure these names are sung, remembered, and never erased.</p>
</div></div></section>
"""

# ---------- ABOUT ----------
about_body = """
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">About the project</h2>
<div class="prose">
<p>After Emancipation, Black Americans built <strong>hundreds of their own towns</strong> - municipalities, districts, and settlements across the country, founded on the belief that freedom should come with land, self-rule, and a future.</p>
<p>Many thrived. Boley, Oklahoma. Nicodemus, Kansas. Blackdom, New Mexico. Mound Bayou, Mississippi. Then came the violence, the policy, the highways, the "urban renewal" - and town after town was destroyed, dispersed, or paved over.</p>
<div class="quote">"They tried to bury the towns. We're singing their names back."</div>
<p><strong>All Black Towns</strong> is a music project to honor every one of them - one town, one song, one story at a time. Each song carries the town's real history in its lyrics, so the names live in melody even where the buildings are gone.</p>
<p>The project is also a living archive: the lyrics are documented, the research is sourced, and the catalog grows as more towns are found and more songs are written.</p>
<p>This is history you can hear.</p>
</div></div></section>
"""

# ---------- MAP ----------
map_body = ""
try:
    coords = json.load(open(f"{SITE}/town-coords.json"))
    pins = []
    for t in towns:
        k = f"{t['town']}|{t['state']}"
        if k in coords:
            pins.append({"town": t["town"], "state": t["state"], "song": t["song"],
                         "about": (t["about"] or "")[:180], "lat": coords[k][0], "lon": coords[k][1]})
    pin_data = json.dumps(pins)
    map_body = f"""
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css">
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">The map</h2>
<p class="section-sub">{len(pins)} of {len(towns)} towns are placed on the map. Each pin marks a town's location; for settlements that no longer exist, the pin marks where the town stood. Tap a pin for the town and its song. Every town, mapped or not, is in the <a href="towns.html">full list</a>.</p>
<div id="townmap" class="townmap" data-rv></div>
<p class="map-note">Map data &copy; OpenStreetMap contributors. Locations are town-level approximations for a historical archive, not surveyed boundaries.</p>
</div></section>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script>
const PINS = {pin_data};
const map = L.map('townmap').setView([38.5, -96.5], 4);
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }}).addTo(map);
const cluster = L.markerClusterGroup();
const dot = L.divIcon({{ className: 'town-dot-wrap', html: '<span class="town-dot"></span>', iconSize: [16, 16], iconAnchor: [8, 8] }});
PINS.forEach(p => {{
  const m = L.marker([p.lat, p.lon], {{ icon: dot }});
  const about = p.about ? `<p>${{p.about}}...</p>` : '';
  m.bindPopup(`<div class="pop"><h3>${{p.town}}</h3><div class="pstate">${{p.state}}</div>${{about}}<div class="psong">\u266a ${{p.song}}</div></div>`);
  cluster.addLayer(m);
}});
map.addLayer(cluster);
</script>
"""
except FileNotFoundError:
    print("town-coords.json missing: map page skipped")

pages = {
    "index.html": page("h", "Home",
        "All Black Towns - a music project honoring historic Black towns, one song per town.", index_body),
    "towns.html": page("t", "Towns",
        "Explore the historic Black towns honored by the All Black Towns music project.", towns_body),
    "music.html": page("m", "Music",
        "The All Black Towns song catalog - original songs honoring historic Black towns.", music_body),
    "about.html": page("a", "About",
        "About All Black Towns - a music project honoring historic Black towns of America.", about_body),
}
if map_body:
    pages["map.html"] = page("mp", "Map",
        "An interactive map of the historic Black towns honored by All Black Towns.", map_body)
for name, content in pages.items():
    open(f"{SITE}/{name}", "w").write(content)
    print(f"Wrote {name} ({len(content)//1024} KB)")
