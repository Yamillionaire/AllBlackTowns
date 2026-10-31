#!/usr/bin/env python3
"""Build the four FULL pilot dossiers as v2 chaptered pages at the
canonical dossiers/<slug>.html. Per the user's 2026-10-27 direction, all
five pilot dossiers are FREE public samples of the education beta;
future towns' dossiers go behind the paywall once that route is set."""
import os
import re

from build_dossiers import SRC, split_sections
from build_prototype import (article_ld, assemble_page, inject_after_first_h2,
                             load_cfu_data, md2html, video_embed_html)

CFU_DATA = load_cfu_data()

SITE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SITE, "dossiers")

TOWNS = [
    ("boley", "boley-dossier-pilot.md", "Boley, Oklahoma"),
    ("nicodemus", "nicodemus-dossier-pilot.md", "Nicodemus, Kansas"),
    ("eatonville", "eatonville-dossier-pilot.md", "Eatonville, Florida"),
    ("rosewood", "rosewood-dossier-pilot.md", "Rosewood, Florida"),
]

ANNOTATION_MARKERS = [
    ("<p>Lyric annotation", "Lyric annotations, line by line"),
    ("<p>Annotation of the song itself", "Song annotation, claim by claim"),
]

for slug, fname, place in TOWNS:
    title, sections = split_sections(open(os.path.join(SRC, fname)).read())
    name = title.replace("Town Dossier: ", "")
    sec = dict(sections)
    order = [h for h, _ in sections]
    words = sum(len(b.split()) for _, b in sections)
    minutes = max(1, round(words / 200))

    chapters = [("intro", "Introduction", "Introduction",
                 md2html("## Introduction\n\n" + sec["Header"]), "open", False)]
    facts_html = '<div class="facts">%s</div>' % md2html("## Key Facts Box\n\n" + sec["Key Facts Box"])

    for h in [x for x in order if re.match(r"^\d+\.", x)]:
        n = h.split(".")[0]
        html = md2html("## %s\n\n%s" % (h, sec[h]))
        kind = "open"
        if h.startswith("7."):
            for needle, summary in ANNOTATION_MARKERS:
                if needle in html:
                    head, tail = html.split(needle, 1)
                    html = head + ('<details class="inline"><summary>%s</summary>' % summary) + needle + tail + "</details>"
                    break
        if slug == "rosewood" and h.startswith("1."):
            # Chapter 1 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "6r-q8tZsEGU",
                "Founding: Rosewood, Chapter 1 (Educational Version)"))
        if slug == "rosewood" and h.startswith("2."):
            # Chapter 2 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "Jqe9b0-F91s",
                "Building the Town: Rosewood, Chapter 2 (Educational Version)"))
        if slug == "rosewood" and h.startswith("3."):
            # Chapter 3 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "BXNHpRvKSnE",
                "Peak Years: Rosewood, Chapter 3 (Educational Version)"))
        if slug == "rosewood" and h.startswith("4."):
            # Chapter 4 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "PMAkZFX8zBw",
                "The Turning Point: Rosewood, Chapter 4 (Educational Version)"))
        if slug == "rosewood" and h.startswith("5."):
            # Chapter 5 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "Ijhn3a-7RBg",
                "Survival, Decline, or Destruction: Rosewood, Chapter 5 (Educational Version)"))
        if h.startswith(("8.", "9.")):
            kind = "details"
        recall = kind == "open" and n not in ("7",)
        chapters.append(("ch" + n, h, h, html, kind, recall))

    banner = ("<strong>Free beta sample.</strong> This is the complete %s dossier, "
              "one of the five pilot dossiers published free as samples for the "
              "All Black Towns curriculum beta." % name)
    orient = (
        '<div class="orient"><div class="meta">About %d min read &middot; %d chapters &middot; Free beta sample</div>'
        '<p>This dossier follows %s in order: how it was founded, how it was built, its peak years, '
        'the turning point, and the town today, ending with its song and the primary sources behind '
        'the record. Work through it one chapter at a time: a short check for understanding at the end of '
        'each chapter unlocks the next, and the contents rail maps where you are.</p>'
        '<div class="fork"><a href="#intro">Start reading</a>'
        '<button type="button" id="teach-btn">Teach this town</button>'
        '<button type="button" class="ghost" onclick="window.print()">Print / save PDF</button></div>'
        '<p class="map-link"><a href="../map.html">Find %s on the map</a></p>'
        '<div id="resume-chip"></div></div>'
    ) % (minutes, len(chapters), name, name.split(",")[0])

    extra = ('<div class="doss-end"><p><strong>The five free samples:</strong> this dossier is one of '
             'the five pilot dossiers published free during the curriculum beta. '
             'Read the others on the <a href="../education.html">Education page</a>.</p></div>')
    d_title = name + " - Town Dossier"
    d_desc = "The complete %s town dossier: %s." % (name, place)
    out = assemble_page(d_title, d_desc,
                        banner, orient, None, facts_html, chapters, extra, "abt-v2-%s-full" % slug,
                        cfu=CFU_DATA.get(slug), ld=article_ld(d_title, d_desc, slug))
    path = os.path.join(OUT, slug + ".html")
    open(path, "w").write(out)
    print("wrote", path, len(out), "bytes | chapters:", len(chapters), "| minutes:", minutes)
print("done")
