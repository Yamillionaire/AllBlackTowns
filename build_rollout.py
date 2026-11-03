#!/usr/bin/env python3
"""Roll the v2 chaptered template (build_prototype.assemble_page) to the four
sample-extract pages and the Sweet Auburn lesson plan page."""
import os
import re

from build_dossiers import SRC, split_sections
from build_prototype import (assemble_page, inject_after_first_h2, md2html,
                             video_embed_html)

SITE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SITE, "dossiers")


def slugify(h):
    return re.sub(r"[^a-z0-9]+", "-", h.lower()).strip("-")


def write(slug, out):
    path = os.path.join(OUT, slug + ".html")
    open(path, "w").write(out)
    print("wrote", path, len(out), "bytes")


EXTRACTS = [
    ("boley", "boley-dossier-pilot.md", "Boley, Oklahoma"),
    ("nicodemus", "nicodemus-dossier-pilot.md", "Nicodemus, Kansas"),
    ("eatonville", "eatonville-dossier-pilot.md", "Eatonville, Florida"),
    ("rosewood", "rosewood-dossier-pilot.md", "Rosewood, Florida"),
]

for slug, fname, place in EXTRACTS:
    title, sections = split_sections(open(os.path.join(SRC, fname)).read())
    name = title.replace("Town Dossier: ", "")
    sec = dict(sections)
    keep_heads = [h for h, _ in sections if h in ("Header", "Key Facts Box") or h.startswith("1.")]
    rest = [h for h, _ in sections if h not in ("Header", "Key Facts Box") and not h.startswith("1.")]

    words = sum(len(sec[h].split()) for h in keep_heads)
    minutes = max(1, round(words / 200))

    chapters = []
    chapters.append(("intro", "Introduction", "Introduction",
                     md2html("## Introduction\n\n" + sec["Header"]), "open", False))
    founding = [h for h in keep_heads if h.startswith("1.")][0]
    chapters.append(("ch1", founding, founding,
                     md2html("## %s\n\n%s" % (founding, sec[founding])), "open", True))
    contents = "".join("<li>%s</li>" % h for h in rest)
    full_html = ("<h2>Inside the full dossier</h2><ul>%s</ul>"
                 "<p>The complete dossier, with the full timeline, the turning point, the town today, "
                 "the song's lyrics annotated line by line, and primary sources, is part of the "
                 "All Black Towns Pilot Collection. Membership opens soon - "
                 '<a href="../education.html#newsletter">join the list</a> to hear about it first.</p>') % contents
    chapters.append(("full", "Inside the full dossier", "Inside the full dossier", full_html, "open", False))

    facts_html = '<div class="facts">%s</div>' % md2html("## Key Facts Box\n\n" + sec["Key Facts Box"])
    banner = ("<strong>Beta sample extract.</strong> The opening of the %s dossier: its header, "
              "key facts, and founding story. The full dossier is part of the Pilot Collection." % name)
    orient = (
        '<div class="orient"><div class="meta">About %d min read &middot; Sample extract &middot; Free beta sample</div>'
        '<p>This is the opening of the %s dossier: where the town came from, its key facts, and its founding story. '
        'The complete dossier, with the full timeline, the turning point, the town today, and the song with its '
        'lyrics annotated, is part of the Pilot Collection.</p>'
        '<div class="fork"><a href="#ch1">Start reading</a>'
        '<button type="button" class="ghost" onclick="window.print()">Print / save PDF</button></div>'
        '<div id="resume-chip"></div></div>'
    ) % (minutes, name)

    out = assemble_page(name + " - Town Dossier (Sample Extract)",
                        "Sample extract of the %s town dossier." % place,
                        banner, orient, None, facts_html, chapters, "", "abt-v2-" + slug)
    write(slug, out)

# Lesson plan
title, sections = split_sections(open(os.path.join(SRC, "sweet-auburn-lesson-plan-pilot.md")).read())
lname = title.replace("Lesson Plan: ", "").replace("Town Dossier: ", "")
lname = lname if "Lesson Plan" in lname else lname + " - Lesson Plan"
sec = dict(sections)
eq_text = sec["Essential Question"].strip()

chapters = [("intro", "Introduction", "Introduction",
             md2html("## Introduction\n\n" + sec["Header"]), "open", False)]
for h, _ in sections:
    if h in ("Header", "Essential Question"):
        continue
    ch_html = md2html("## %s\n\n%s" % (h, sec[h]))
    if slugify(h) == "background-brief":
        # The Background Brief is where the lesson teaches the dossier's
        # chapter stories; it opens with the Chapter 1 founding story, so
        # the chapter videos sit at the very top in story order (Chapter 1,
        # then 2, then 3, then 4, then 5, then 6). Each injection lands
        # directly under the heading, so they are applied in reverse story
        # order.
        ch_html = inject_after_first_h2(ch_html, video_embed_html(
            "TUjl_nB8gLo",
            "The Town Today: Sweet Auburn, Chapter 6 (Educational Version)"))
        ch_html = inject_after_first_h2(ch_html, video_embed_html(
            "7L6tapDlsV8",
            "Survival, Decline, or Destruction: Sweet Auburn, Chapter 5 (Educational Version)"))
        ch_html = inject_after_first_h2(ch_html, video_embed_html(
            "1q5OVtwsM9c",
            "The Turning Point: Sweet Auburn, Chapter 4 (Educational Version)"))
        ch_html = inject_after_first_h2(ch_html, video_embed_html(
            "cZe_ARWH76A",
            "Peak Years: Sweet Auburn, Chapter 3 (Educational Version)"))
        ch_html = inject_after_first_h2(ch_html, video_embed_html(
            "opr7v_0n-w4",
            "Building the Town: Sweet Auburn, Chapter 2 (Educational Version)"))
        ch_html = inject_after_first_h2(ch_html, video_embed_html(
            "YYkamPbVW_Q",
            "Founding: Sweet Auburn, Chapter 1 (Educational Version)"))
    chapters.append((slugify(h), h, h, ch_html, "open", False))

banner = ("<strong>Free beta sample.</strong> The pilot lesson plan for the All Black Towns curriculum, "
          "built on the <a href=\"sweet-auburn.html\"><strong>Sweet Auburn dossier</strong></a>. "
          "It opens with the song, moves into the documents, and closes with discussion and a hands-on task.")
orient = (
    '<div class="orient"><div class="meta">Pilot lesson plan &middot; Grades 9-12 &middot; Two 50-minute periods &middot; Free beta sample</div>'
    '<p class="eq">%s</p>'
    '<p>Built entirely from the Sweet Auburn dossier. Every part of the plan is a chapter below: the background '
    'brief, vocabulary, the song opening, the primary source activity, lyric analysis, discussion, the performance '
    'task, and assessment, with standards alignment and adaptation notes at the end.</p>'
    '<div class="fork"><a href="#background-brief">Start the plan</a>'
    '<a href="sweet-auburn.html">Open the dossier</a>'
    '<button type="button" class="ghost" onclick="window.print()">Print / save PDF</button></div>'
    '<div id="resume-chip"></div></div>'
) % eq_text

out = assemble_page(lname, "The Sweet Auburn pilot lesson plan.",
                    banner, orient, None, None, chapters, "", "abt-v2-sweet-auburn-lesson")
write("sweet-auburn-lesson", out)
print("done")
