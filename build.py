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
<link rel="stylesheet" href="styles.css?v=20261026-logo">
<script>document.documentElement.classList.add('js');</script>
</head>
<body>
<div class="logo-bg" aria-hidden="true"></div>
<nav><div class="wrap nav-inner">
<a class="brand" href="index.html"><img class="brand-logo" src="logo-nav.jpg" alt="All Black Towns logo">All <span>Black</span> Towns</a>
<div class="nav-links">
<a href="index.html" class="{h}">Home</a>
<a href="towns.html" class="{t}">Towns</a>
<a href="map.html" class="{mp}">Map</a>
<a href="music.html" class="{m}">Music</a>
<a href="education.html" class="{ed}">Education</a>
<a href="about.html" class="{a}">About</a>
<a href="share.html" class="{sh}">Share a Town</a>
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
<a class="brand" href="index.html"><img class="brand-logo" src="logo-nav.jpg" alt="All Black Towns logo">All <span>Black</span> Towns</a>
<p style="margin-top:12px">A creative universe built on the true history of America's Black towns -<br>one town, one song, one story at a time.</p>
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
                    ed="active" if active == "ed" else "",
                    a="active" if active == "a" else "",
                    sh="active" if active == "sh" else "")
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
<div class="kicker">A creative universe built on true history &middot; {len(towns)} towns &middot; {len(towns)} original songs</div>
<h1>Every Black town<br>has a <em>song.</em></h1>
<p class="lede">From Boley to Blackdom, Rosewood to Seneca Village - All Black Towns is a creative universe built on the true history of America's Black towns and neighborhoods. Every town is real, and every story really happened - told first in song, and growing into film, story, and study.</p>
<a class="btn" href="towns.html">Explore the towns</a>
<a class="btn ghost" href="music.html">Hear the music</a>
<div class="stats">
<div class="stat"><div class="num">{len(towns)}</div><div class="lbl">Towns honored</div></div>
<div class="stat"><div class="num">{len(towns)}</div><div class="lbl">Original songs</div></div>
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
<p class="section-sub">{len(towns)} original songs and counting - each written for a specific town, carrying its history in the lyrics. Human-written words, composed with AI instruments, sung so the names are never forgotten.</p>
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
<section class="block alt"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">Know a town that is not here?</h2>
<p class="section-sub">Some Black towns were never written into the record, and the record that exists is incomplete. If you know one, through records or through your family's telling, send it in. Every submission is researched, and you will get an honest answer about what we find.</p>
<p><a class="btn" href="share.html">Share a town</a></p>
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
music_data = json.dumps([{"song": t["song"], "town": t["town"], "state": t["state"],
                          "about": t["about"]} for t in sorted(towns, key=lambda x: x["song"].lower())])
music_state_opts = "\n".join(f'<option value="{esc(s)}">{esc(s)}</option>' for s in states)

music_body = f"""
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">The music</h2>
<p class="section-sub">{len(towns)} original songs - one for every town. Search the catalog by song, town, or state. Every lyric is human-written from historical research; the music is composed with AI instruments. Streaming and downloads open with the store - join the list below to hear each song first.</p>
<div class="tools">
<input id="mq" type="text" placeholder="Search songs or towns..." oninput="filterMusic()">
<select id="mst" onchange="filterMusic()"><option value="">All states</option>{music_state_opts}</select>
</div>
<div class="count-note" id="mcount"></div>
<div class="town-grid" id="mgrid"></div>
</div></section>
<script>
const MUSIC = {music_data};
const mgrid = document.getElementById('mgrid');
const mcount = document.getElementById('mcount');
function mcard(t, i) {{
  const about = t.about ? `<p>${{t.about.substring(0, 240)}}${{t.about.length > 240 ? '...' : ''}}</p>` : '';
  return `<div class="town-card song-card" style="--i:${{Math.min(i || 0, 10)}}"><div class="disc" aria-hidden="true"></div><h3>${{t.song}}</h3><div class="state">${{t.town}} &middot; ${{t.state}}</div>${{about}}<div class="song-actions"><a class="mini-btn" href="#newsletter">Hear it first</a><a class="mini-link" href="towns.html">The town</a></div></div>`;
}}
function filterMusic() {{
  const q = document.getElementById('mq').value.toLowerCase();
  const st = document.getElementById('mst').value;
  const list = MUSIC.filter(t =>
    (!q || t.song.toLowerCase().includes(q) || t.town.toLowerCase().includes(q)) &&
    (!st || t.state === st));
  mgrid.innerHTML = list.map((t, i) => mcard(t, i)).join('');
  mgrid.classList.add('anim');
  mcount.textContent = `Showing ${{list.length}} of ${{MUSIC.length}} songs`;
}}
filterMusic();
</script>

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
<p><strong>All Black Towns</strong> is a creative universe built on true stories, honoring every one of them - one town, one song, one story at a time. Each song carries the town's real history in its lyrics, so the names live in melody even where the buildings are gone.</p>
<p>The project is also a living archive: the lyrics are documented, the research is sourced, and the catalog grows as more towns are found and more songs are written.</p>
<p>This is history you can hear.</p>
</div></div></section>

<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">About the creator</h2>
<div class="prose">
<p><strong>Yamil Little</strong> is an Atlanta-based creative director and the co-founder of The Elements of Hip Hop, the company behind HipHopolis, a superhero universe powered by the elements of hip hop. He created All Black Towns to put the names of America's historic Black towns back into the culture, as songs people can carry with them.</p>
<p>His career moves between music, media, and community work.</p>
<p>The project is personal. Little's grandparents came from Alabama, and the towns in these songs are the kind of places his own family's story runs through. All Black Towns is his way of keeping the record alive: researched from the sources, written town by town, and sung back into memory.</p>
</div></div></section>
"""

# ---------- EDUCATION ----------
education_body = """
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">Learn the towns</h2>
<p class="section-sub">The songs open the door. The curriculum walks through it - the full, sourced history of every town, built for learners, families, and classrooms.</p>
<div class="prose">
<p>Every All Black Towns song starts as research. The <strong>Town Dossiers</strong> are where that research lives in full: each one tells a town's complete story - its founding and founders, its churches, schools, and businesses, the turning point that changed everything, and what stands there today - with a timeline, a key facts box, primary sources, and the song's lyrics annotated line by line.</p>
<p><strong>Lesson plans</strong> turn each dossier into teaching: a lesson opens with the song, moves into the documents, and closes with discussion and a hands-on task. The pilot lesson, built on Sweet Auburn in Atlanta, is complete; the full curriculum grows town by town from the dossiers, toward every town on the master list.</p>
</div></div></section>

<section class="block alt"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">The pilot collection</h2>
<p class="section-sub">Five towns, five complete dossiers - the first set, finished and verified against the sources.</p>
<div class="town-grid">
<div class="town-card"><h3>Sweet Auburn</h3><div class="state">Atlanta, Georgia</div><p>The historic Black business district once called the richest Negro street in the world - and the home of the pilot lesson plan.</p></div>
<div class="town-card"><h3>Boley</h3><div class="state">Oklahoma</div><p>One of the largest and most famous all-Black towns of the West, founded in 1903 and still an incorporated town today.</p></div>
<div class="town-card"><h3>Nicodemus</h3><div class="state">Kansas</div><p>Founded in 1877 by Black settlers from Kentucky; the oldest surviving all-Black town west of the Mississippi, now a National Historic Site.</p></div>
<div class="town-card"><h3>Eatonville</h3><div class="state">Florida</div><p>Incorporated in 1887, among the first self-governing all-Black towns in America - and the hometown of Zora Neale Hurston.</p></div>
<div class="town-card"><h3>Rosewood</h3><div class="state">Florida</div><p>A thriving town destroyed by racial violence in 1923. Its dossier keeps the full record of what was lost.</p></div>
</div>
</div></section>

<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">Free to explore, deeper for members</h2>
<div class="prose">
<p>The map, the songs, and every town's story stay <strong>free for everyone</strong> - that is the discovery engine, and it is not going anywhere. The dossiers and lesson plans are the members' layer: the full record, kept growing.</p>
<p>The membership opens soon, with classroom and school licenses for teachers and institutions alongside individual memberships. Join the list and you will hear about it first.</p>
<p style="margin-top:26px"><a class="btn" href="#newsletter">Join the list</a></p>
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
    intl = []
    try:
        for e in json.load(open(f"{SITE}/international-towns.json")):
            intl.append({"town": e["town"], "country": e["country"], "about": e["about"],
                         "lat": e["lat"], "lon": e["lon"], "song": ""})
    except FileNotFoundError:
        pass
    for t in towns:
        if t["town"] == "Nanny Town":
            k = f"{t['town']}|{t['state']}"
            if k in coords:
                intl.append({"town": t["town"], "country": t["state"],
                             "about": (t["about"] or "")[:235],
                             "lat": coords[k][0], "lon": coords[k][1], "song": t["song"]})
    intl_data = json.dumps(intl)
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
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">The international Black towns map</h2>
<p class="section-sub">The story does not stop at the border. Wherever colonialism carried Black people (the Caribbean, the Virgin Islands, the Americas, and the ports of Europe), they did what they did here: fought for ground and built towns of their own. And in Africa itself, communities broke colonial control and governed themselves: freed people's towns that became capitals, maroon towns and refuges, and a town where a liberation republic was declared. Maroon republics, quilombos, palenques, Garifuna towns, and free Black settlements, each pinned where it stood or still stands. The songs have not reached these towns yet; the record starts here.</p>
<div id="worldmap" class="townmap" data-rv></div>
<p class="map-note">{len(intl)} places on this map. Entries the record supports only as a district or a territory are labeled as such: the record stays honest. Map data &copy; OpenStreetMap contributors.</p>
</div></section>
<script>
const IPINS = {intl_data};
const wmap = L.map('worldmap').setView([14, -35], 3);
L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' }}).addTo(wmap);
const icluster = L.markerClusterGroup();
const idot = L.divIcon({{ className: 'town-dot-wrap', html: '<span class="town-dot"></span>', iconSize: [16, 16], iconAnchor: [8, 8] }});
IPINS.forEach(p => {{
  const m = L.marker([p.lat, p.lon], {{ icon: idot }});
  const about = p.about ? `<p>${{p.about}}</p>` : '';
  const song = p.song ? `<div class="psong">\u266a ${{p.song}}</div>` : '';
  m.bindPopup(`<div class="pop"><h3>${{p.town}}</h3><div class="pstate">${{p.country}}</div>${{about}}${{song}}</div>`);
  icluster.addLayer(m);
}});
wmap.addLayer(icluster);
</script>
"""
except FileNotFoundError:
    print("town-coords.json missing: map page skipped")

# ---------- SHARE A TOWN (community intake) ----------
import urllib.parse as _up
_share_subject = _up.quote("A Black town to share")
_share_lines = [
    "Town name:",
    "State and county:",
    "",
    "What I know about it:",
    "",
    "How I know it (family story, records, photos, a place I can point to):",
    "",
    "Names, dates, churches, schools, or cemeteries that could help the search:",
    "",
    "My name:",
    "Best email to reach me:",
]
share_mailto = ("mailto:info@allblacktowns.com?subject=" + _share_subject
                + "&body=" + _up.quote("\n".join(_share_lines)))

share_body = f"""
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">Know a town we have not found?</h2>
<p class="section-sub">This record is built from what can be found. You may know a piece of it that was never written down. Send it in.</p>
<div class="prose">
<p>The official record of Black towns is incomplete, and everyone who works in this history knows why. Records were never kept, or were lost, burned, flooded, or thrown away when a town was taken. A town can be missing from every book and database and still have been real, with families, a church, a school, and a cemetery.</p>
<p>So this project listens two ways: to the written record, and to the people who carry the story. If your family comes from a Black town that is not on this site, or you know something about one that is, we want to hear it: a name, a place, a story passed down, a photograph, a headstone. Family tellings count here. They are often the only record a town ever got.</p>
</div>
</div></section>
<section class="block alt"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">What happens when you send it</h2>
<p class="section-sub">Every submission is researched before anything changes on the site.</p>
<div class="prose">
<p>We run what you send through everything we can search: the open internet, public libraries and archives, historical databases, maps, and records. Then we write back with an honest readout: what we could confirm, what we could not, and where that leaves the town.</p>
<p>If we cannot find a town in the searchable record, we will tell you exactly that: we do not know. Not finding a town in the record is not the same as your information being wrong, and we will never tell you it is. Some towns will stand on community memory, credited as such, while the search continues.</p>
</div>
</div></section>
<section class="block"><div class="wrap">
<div class="rule"></div>
<h2 class="section-title">What to send</h2>
<p class="section-sub">As much or as little as you have. Even a name and a county is a start.</p>
<div class="prose">
<p><strong>The town:</strong> its name, the state and county, and where it stood if you can point to it on a map.</p>
<p><strong>What you know:</strong> when it was founded or lived in, who lived there, what stood there: homes, a church, a school, a store, a cemetery.</p>
<p><strong>How you know it:</strong> family history, a story passed down, documents, photographs, a place you have stood. Tell us plainly; it helps us search the right way.</p>
<p><strong>How to reach you:</strong> your name and an email, so we can send the readout.</p>
</div>
<form class="share-form" id="shareForm" style="margin-top:28px">
<label>Town name <span class="req">(required)</span><input type="text" name="Town name" required></label>
<label>State and county<input type="text" name="State and county"></label>
<label>What you know about it <span class="req">(required)</span><textarea name="What they know" rows="5" required></textarea></label>
<label>How you know it: family story, records, photos, a place you can point to<textarea name="How they know it" rows="3"></textarea></label>
<label>Names, dates, churches, schools, or cemeteries that could help the search<textarea name="Leads for the search" rows="3"></textarea></label>
<label>Your name<input type="text" name="Submitter name"></label>
<label>Your email <span class="req">(required, so we can send you the readout)</span><input type="email" name="Submitter email" required></label>
<input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
<p style="margin:6px 0 18px"><button class="btn" type="submit" id="shareBtn">Send what you know</button></p>
<p class="form-note" id="shareNote">Submissions go straight to the project inbox at info@allblacktowns.com. Your email is required so the readout can come back to you; it stays between you and the project and is never published. Nothing is published from a submission without research.</p>
</form>
<script>
document.getElementById('shareForm').addEventListener('submit', async function (e) {{
  e.preventDefault();
  const btn = document.getElementById('shareBtn');
  const note = document.getElementById('shareNote');
  btn.disabled = true; btn.textContent = 'Sending...';
  const data = {{}};
  new FormData(e.target).forEach((v, k) => {{ data[k] = v; }});
  data._subject = 'A Black town to share: ' + (data['Town name'] || '');
  data._template = 'table';
  try {{
    const r = await fetch('https://formsubmit.co/ajax/info@allblacktowns.com', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json', 'Accept': 'application/json' }},
      body: JSON.stringify(data)
    }});
    if (!r.ok) throw new Error('send failed');
    e.target.innerHTML = '<div class="form-done"><h3>Thank you. It is in.</h3><p>What you sent will be researched against the internet, public libraries and archives, and historical databases. The readout comes back to the email you gave: what we could confirm, what we could not, and an honest answer either way.</p></div>';
  }} catch (err) {{
    btn.disabled = false; btn.textContent = 'Send what you know';
    note.textContent = 'The form could not send just now. Please try again, or write to us directly at info@allblacktowns.com.';
  }}
}});
</script>
</div></section>
"""

pages = {
    "index.html": page("h", "Home",
        "All Black Towns - a creative universe built on the true history of America's Black towns, told first in song.", index_body),
    "towns.html": page("t", "Towns",
        "Explore the historic Black towns honored by the All Black Towns music project.", towns_body),
    "music.html": page("m", "Music",
        "The All Black Towns song catalog - original songs honoring historic Black towns.", music_body),
    "about.html": page("a", "About",
        "About All Black Towns - a creative universe built on the true history of America's Black towns.", about_body),
    "education.html": page("ed", "Education",
        "The All Black Towns curriculum - Town Dossiers and lesson plans built on the true history of America's Black towns.", education_body),
    "share.html": page("sh", "Share a Town",
        "Know a Black town that is not on this site? Send in what you know. Every submission is researched, and family tellings count.", share_body),
}
if map_body:
    pages["map.html"] = page("mp", "Map",
        "An interactive map of the historic Black towns honored by All Black Towns.", map_body)
for name, content in pages.items():
    open(f"{SITE}/{name}", "w").write(content)
    print(f"Wrote {name} ({len(content)//1024} KB)")
