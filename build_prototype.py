#!/usr/bin/env python3
"""V2 chaptered renderer for the All Black Towns dossier/lesson pages, built
on the education teardown patterns: chaptered layout + sticky contents rail
with scrollspy, orientation header, progress + resume (localStorage),
click-down <details> for optional depth, per-chapter recall prompts and
prev/next links, print styles. assemble_page() is the shared template;
build() renders Sweet Auburn (the model page).
"""
import json
import os
import re

import markdown

from build_dossiers import CHROME_BOTTOM, CHROME_TOP, SRC, split_sections

SITE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SITE, "dossiers")

V2_CSS = """
.dossier h2{font-family:'Playfair Display',serif;font-size:1.55rem;margin:36px 0 12px;color:#f5efe0}
.dossier h3{font-size:1.15rem;margin:24px 0 8px;color:#e3c76a}
.dossier p{margin:0 0 14px;line-height:1.68}
.dossier ul,.dossier ol{margin:0 0 16px 24px;line-height:1.62}
.dossier li{margin-bottom:7px}
.facts{background:#1a1712;border:1px solid rgba(201,162,39,.22);border-left:5px solid #c9a227;border-radius:8px;padding:20px 24px 8px;margin:10px 0 14px;color:#f5efe0}
.facts h2{color:#e3c76a;margin-top:0}
.beta-banner{background:#1a1712;border:1px solid rgba(201,162,39,.22);border-radius:8px;padding:16px 20px;margin:0 0 26px;line-height:1.55;color:#f5efe0}
.doss-end{background:#1a1712;border:1px solid rgba(201,162,39,.22);border-radius:8px;padding:20px 24px 8px;margin:34px 0 10px;color:#f5efe0}
.backlink{display:inline-block;margin:0 0 18px;font-weight:600}
#progress-bar{position:fixed;top:0;left:0;height:3px;background:#c9a227;width:0;z-index:999}
.orient{background:#1a1712;border:1px solid #c9a227;color:#f5efe0;border-radius:10px;padding:24px 26px;margin:0 0 22px}
.orient .meta{font-size:.92rem;letter-spacing:.04em;text-transform:uppercase;color:#e3c76a;margin-bottom:10px}
.orient .eq{font-family:'Playfair Display',serif;font-size:1.3rem;line-height:1.45;margin:0 0 10px}
.orient p{line-height:1.6;margin:0 0 14px}
.orient .fork{display:flex;flex-wrap:wrap;gap:10px;margin-top:6px}
.orient .fork a,.orient .fork button{background:#c9a227;color:#0e0c09;border:0;border-radius:6px;padding:10px 16px;font-weight:700;cursor:pointer;text-decoration:none;font-size:.95rem}
.orient .fork button.ghost{background:transparent;color:#f5efe0;border:1px solid #c9a227}
#resume-chip{display:none;background:rgba(201,162,39,.14);border:1px solid rgba(201,162,39,.22);color:#f5efe0;border-radius:6px;padding:10px 14px;margin-top:14px;font-size:.95rem}
#teacher-panel{display:none;background:#1a1712;border:1px solid rgba(201,162,39,.22);border-left:5px solid #c9a227;border-radius:8px;padding:18px 22px 6px;margin:0 0 22px;line-height:1.6;color:#f5efe0}
.layout{display:grid;grid-template-columns:230px 1fr;gap:34px;align-items:start}
.rail{position:sticky;top:88px;font-size:.93rem}
.rail h4{font-size:.78rem;letter-spacing:.09em;text-transform:uppercase;color:#c9a227;margin:0 0 10px}
.rail a{display:block;padding:7px 10px 7px 12px;color:#d8cdb4;text-decoration:none;border-left:3px solid rgba(201,162,39,.22);line-height:1.35}
.rail a.active{border-left-color:#c9a227;background:rgba(201,162,39,.12);color:#f5efe0;font-weight:700}
.rail a .tick{display:inline-block;width:1.1em;color:#c9a227;font-weight:700}
.rail .rail-tools{margin-top:14px}
.rail .rail-tools button{background:none;border:1px solid #c9a227;color:#e3c76a;border-radius:6px;padding:6px 10px;cursor:pointer;font-size:.85rem}
#chapter-bar{display:none}
.chapter{scroll-margin-top:92px}
details.deep{scroll-margin-top:92px}
.chapter > h2{border-bottom:2px solid rgba(201,162,39,.22);padding-bottom:8px}
.video-embed{margin:22px 0 26px;background:#1a1712;border:1px solid rgba(201,162,39,.22);border-radius:8px;padding:14px 14px 10px}
.video-embed .video-frame{position:relative;padding-top:56.25%}
.video-embed iframe{position:absolute;inset:0;width:100%;height:100%;border:0;border-radius:4px}
.video-embed figcaption{margin-top:10px;color:#e3c76a;font-weight:600;line-height:1.45}
.recall{background:rgba(201,162,39,.10);border:1px solid rgba(201,162,39,.22);border-radius:8px;padding:14px 18px;margin:20px 0 6px;line-height:1.55;font-size:.97rem;color:#f5efe0}
.recall strong{color:#e3c76a}
.chap-nav{display:flex;justify-content:space-between;gap:12px;margin:22px 0 4px;font-weight:600}
.chap-nav a{color:#e3c76a}
details.deep{border:1px solid rgba(201,162,39,.22);border-radius:8px;background:#1a1712;margin:26px 0 10px}
details.deep > summary{font-family:'Playfair Display',serif;font-size:1.3rem;color:#f5efe0;cursor:pointer;padding:16px 20px;list-style:none}
details.deep > summary::-webkit-details-marker{display:none}
details.deep > summary::after{content:"+";float:right;color:#c9a227;font-weight:700}
details.deep[open] > summary::after{content:"\\2212"}
details.deep .deep-body{padding:0 20px 8px}
details.inline{margin:14px 0}
details.inline > summary{cursor:pointer;font-weight:700;color:#e3c76a;list-style:none}
details.inline > summary::-webkit-details-marker{display:none}
details.inline > summary::after{content:" +";color:#c9a227}
details.inline[open] > summary::after{content:" \\2212"}
.chapter[hidden]{display:none}
.cfu{border:1px solid rgba(201,162,39,.22);border-left:5px solid #c9a227;background:rgba(201,162,39,.07);border-radius:8px;padding:16px 20px 10px;margin:26px 0 8px;color:#f5efe0}
.cfu h3{font-family:'Playfair Display',serif;font-size:1.25rem;margin:0 0 6px;color:#e3c76a}
.cfu .cfu-intro{color:#d8cdb4;font-size:.95rem;margin:0 0 6px;line-height:1.55}
.cfu-q{margin:14px 0 6px}
.cfu-q .qtext{font-weight:700;margin:0 0 8px;line-height:1.5}
.cfu .opt{display:block;width:100%;text-align:left;background:rgba(245,239,224,.05);border:1px solid rgba(201,162,39,.35);color:#f5efe0;border-radius:6px;padding:9px 12px;margin:6px 0;font:inherit;font-size:.97rem;line-height:1.45;cursor:pointer}
.cfu .opt:hover{border-color:#c9a227}
.cfu .opt.picked-right{border-color:#8fbf6a;background:rgba(143,191,106,.16)}
.cfu .opt.picked-wrong{border-color:#c96a4a;background:rgba(201,106,74,.13);opacity:.8}
.cfu .opt[disabled]{cursor:default}
.cfu .feedback{font-size:.95rem;line-height:1.55;margin:8px 0 2px}
.cfu .feedback.good{color:#c4e2a6}
.cfu .feedback.try{color:#eec39b}
.cfu .done-note{margin:12px 0 6px;padding:10px 14px;border:1px dashed #c9a227;border-radius:6px;color:#e3c76a;font-size:.97rem}
.cfu-key{display:none}
.rail a.locked{opacity:.48}
.rail a .lk{float:right;font-size:.8rem}
#chapter-sheet a.locked{opacity:.55}
.chap-nav a.locked{opacity:.5}
#lock-note{background:rgba(201,162,39,.12);border:1px solid #c9a227;border-radius:8px;color:#f5efe0;padding:12px 16px;margin:0 0 18px;line-height:1.55}
#teacher-controls{display:none;background:#1a1712;border:1px solid rgba(201,162,39,.22);border-left:5px solid #c9a227;border-radius:8px;padding:16px 22px 12px;margin:0 0 22px;line-height:1.6;color:#f5efe0}
#teacher-controls h3{margin:0 0 6px;font-family:'Playfair Display',serif;color:#e3c76a}
#teacher-controls p{color:#d8cdb4;font-size:.95rem;margin:0 0 10px}
#teacher-controls .row{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
#teacher-controls label{font-size:.97rem;cursor:pointer}
#teacher-controls button{background:none;border:1px solid #c9a227;color:#e3c76a;border-radius:6px;padding:7px 14px;font:inherit;font-size:.9rem;cursor:pointer}
.timeline{border-left:2px solid #c9a227;margin:28px 0 10px 4px;padding:2px 0 2px 22px}
.timeline h3{font-family:'Playfair Display',serif;color:#e3c76a;font-size:1.25rem;margin:0 0 14px}
.tl-item{position:relative;margin:0 0 13px;line-height:1.5}
.tl-item::before{content:"";position:absolute;left:-27.5px;top:7px;width:9px;height:9px;border-radius:50%;background:#c9a227}
.tl-year{font-family:'Playfair Display',serif;font-weight:700;color:#e3c76a;margin-right:9px}
.tl-text{color:#f5efe0;font-size:.98rem}
.orient .map-link{margin-top:12px}
.orient .map-link a{color:#e3c76a;font-weight:600}
@media (max-width:900px){
  .layout{grid-template-columns:1fr}
  .rail{display:none}
  #chapter-bar{display:flex;position:sticky;top:0;z-index:60;background:#1a1712;border:1px solid rgba(201,162,39,.22);color:#f5efe0;padding:10px 14px;border-radius:6px;justify-content:space-between;align-items:center;margin-bottom:16px}
  #chapter-bar button{background:#c9a227;color:#0e0c09;border:0;border-radius:5px;padding:6px 12px;font-weight:700;cursor:pointer}
  #chapter-sheet{display:none;background:#1a1712;border:1px solid rgba(201,162,39,.22);border-radius:8px;padding:10px 16px;margin:-8px 0 16px}
  #chapter-sheet.open{display:block}
  #chapter-sheet a{display:block;padding:8px 4px;color:#d8cdb4;text-decoration:none;border-bottom:1px solid rgba(201,162,39,.22)}
}
@media print{
  #progress-bar,.rail,#chapter-bar,#chapter-sheet,.orient .fork,.recall,.chap-nav,.backlink,nav,footer{display:none !important}
  .layout{grid-template-columns:1fr}
  .chapter[hidden]{display:block !important}
  #lock-note,#teacher-controls,.cfu .feedback{display:none !important}
  .cfu-key{display:block !important}
  .cfu .opt{display:block;width:100%;background:none;border:0;color:#000;text-align:left;padding:2px 0}
}
"""

V2_JS = """
<script>
(function(){
  var KEY = '__KEY__';
  var CFU = window.ABT_CFU || null;
  var state = {done: []};
  try {
    var stored = JSON.parse(localStorage.getItem(KEY));
    if (stored) { for (var k in stored) state[k] = stored[k]; }
  } catch(e) {}
  if (!state.done) state.done = [];
  if (CFU) {
    if (!state.cfu) state.cfu = {};
    state.teacherUnlock = !!state.teacherUnlock;
    if (!('current' in state)) state.current = null;
  }
  var chapters = Array.prototype.slice.call(document.querySelectorAll('.chapter'));
  var railLinks = {};
  document.querySelectorAll('.rail a[data-ch]').forEach(function(a){ railLinks[a.getAttribute('data-ch')] = a; });
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(state)); } catch(e) {} }
  function paintTicks(){
    chapters.forEach(function(ch){
      var a = railLinks[ch.id];
      if (a) { var t = a.querySelector('.tick'); if (t) t.textContent = state.done.indexOf(ch.id) >= 0 ? '\\u2713' : ''; }
    });
  }
  function cfuPassed(cid){
    if (!CFU) return false;
    var c = CFU.chapters[cid];
    if (!c) return true;
    var got = state.cfu[cid] || [];
    return c.questions.every(function(q, i){ return got[i] === true; });
  }
  function isUnlocked(i){
    if (!CFU) return true;
    if (state.teacherUnlock) return true;
    if (i <= 0) return true;
    return cfuPassed(chapters[i - 1].id);
  }
  function chapterIndex(el){ return chapters.indexOf(el); }
  var note = document.getElementById('lock-note');
  function hideNote(){ if (note) note.style.display = 'none'; }
  function showNote(target){
    if (!note) return;
    var label = target.getAttribute('data-label') || target.id;
    note.innerHTML = '<strong>' + label + ' is locked for now.</strong> Answer the check for understanding questions at the end of the previous chapter to unlock it.';
    note.style.display = 'block';
    note.scrollIntoView({behavior: 'smooth', block: 'center'});
  }
  function paintLocks(){
    if (!CFU) return;
    document.querySelectorAll('a[href^="#"]').forEach(function(a){
      var t = document.querySelector(a.getAttribute('href'));
      if (t && t.classList.contains('chapter')) {
        var locked = !isUnlocked(chapterIndex(t));
        a.classList.toggle('locked', locked);
        if (a.hasAttribute('data-ch')) {
          var lk = a.querySelector('.lk');
          if (locked && !lk) { lk = document.createElement('span'); lk.className = 'lk'; lk.textContent = '\\uD83D\\uDD12'; a.appendChild(lk); }
          if (!locked && lk) lk.remove();
        }
      }
    });
  }
  function setActive(id){
    chapters.forEach(function(ch){
      var a = railLinks[ch.id];
      if (a) a.classList.toggle('active', ch.id === id);
    });
    var sheetLabel = document.getElementById('chapter-bar-label');
    var target = document.getElementById(id);
    if (sheetLabel && target) sheetLabel.textContent = target.getAttribute('data-label');
  }
  function showChapter(id, scroll){
    var target = document.getElementById(id);
    if (!target) return;
    chapters.forEach(function(ch){
      if (ch.id === id) {
        ch.removeAttribute('hidden');
        if (ch.tagName === 'DETAILS') ch.open = true;
      } else {
        ch.setAttribute('hidden', '');
      }
    });
    document.querySelectorAll('.chap-nav[data-for]').forEach(function(n){
      if (n.getAttribute('data-for') === id) n.removeAttribute('hidden');
      else n.setAttribute('hidden', '');
    });
    state.current = id; save();
    setActive(id);
    hideNote();
    if (scroll !== false) {
      var layout = document.querySelector('.layout');
      if (layout) {
        var y = layout.getBoundingClientRect().top + window.pageYOffset - 84;
        window.scrollTo(0, Math.max(0, y));
      }
    }
  }
  var chip = document.getElementById('resume-chip');
  if (chip && CFU) {
    var passedCount = chapters.filter(function(c){ return cfuPassed(c.id); }).length;
    var nextU = null;
    chapters.forEach(function(c, i){ if (!nextU && isUnlocked(i) && !cfuPassed(c.id)) nextU = c; });
    if (passedCount > 0 && nextU) {
      chip.style.display = 'block';
      chip.innerHTML = 'Welcome back. You left off at <strong>' + nextU.getAttribute('data-label') + '</strong>. <a href="#' + nextU.id + '">Continue there \\u2192</a>';
    }
  } else if (chip && state.done.length) {
    var next = chapters.filter(function(c){ return state.done.indexOf(c.id) < 0; })[0];
    if (next) {
      var label = next.getAttribute('data-label');
      chip.style.display = 'block';
      chip.innerHTML = 'Welcome back. You left off at <strong>' + label + '</strong>. <a href="#' + next.id + '">Continue there \\u2192</a>';
    }
  }
  if (CFU) {
    chapters.forEach(function(ch){
      if (cfuPassed(ch.id) && state.done.indexOf(ch.id) < 0) state.done.push(ch.id);
    });
    save();
  }
  paintTicks();
  paintLocks();
  var bar = document.getElementById('progress-bar');
  if (!CFU) {
    var active = null;
    var spy = new IntersectionObserver(function(entries){
      entries.forEach(function(en){
        if (en.isIntersecting) {
          if (active && railLinks[active]) railLinks[active].classList.remove('active');
          active = en.target.id;
          if (railLinks[active]) railLinks[active].classList.add('active');
          var sheetLabel = document.getElementById('chapter-bar-label');
          if (sheetLabel) sheetLabel.textContent = en.target.getAttribute('data-label');
        }
        var rect = en.target.getBoundingClientRect();
        if (rect.bottom < window.innerHeight * 0.55 && state.done.indexOf(en.target.id) < 0) {
          state.done.push(en.target.id); save(); paintTicks();
        }
      });
    }, {rootMargin: '-30% 0px -55% 0px'});
    chapters.forEach(function(ch){ spy.observe(ch); });
  }
  window.addEventListener('scroll', function(){
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    if (bar && max > 0) bar.style.width = (h.scrollTop / max * 100) + '%';
  }, {passive: true});
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click', function(ev){
      var t = document.querySelector(a.getAttribute('href'));
      var sheet = document.getElementById('chapter-sheet');
      if (sheet) sheet.classList.remove('open');
      if (CFU && t && t.classList.contains('chapter')) {
        ev.preventDefault();
        if (isUnlocked(chapterIndex(t))) showChapter(t.id);
        else showNote(t);
        return;
      }
      if (t && t.tagName === 'DETAILS') t.open = true;
    });
  });
  var tp = document.getElementById('teacher-panel');
  var tc = document.getElementById('teacher-controls');
  var tbtn = document.getElementById('teach-btn');
  if (tbtn && (tp || tc)) tbtn.addEventListener('click', function(){
    var opened = null;
    [tp, tc].forEach(function(el){
      if (!el) return;
      el.style.display = el.style.display === 'block' ? 'none' : 'block';
      if (el.style.display === 'block') opened = el;
    });
    if (opened) opened.scrollIntoView({behavior:'smooth', block:'start'});
  });
  var ex = document.getElementById('expand-all');
  if (ex) ex.addEventListener('click', function(){
    var dets = document.querySelectorAll('details');
    var anyClosed = Array.prototype.some.call(dets, function(d){ return !d.open; });
    dets.forEach(function(d){ d.open = anyClosed; });
    ex.textContent = anyClosed ? 'Collapse all sections' : 'Expand all sections';
  });
  var sheetBtn = document.getElementById('chapter-sheet-btn');
  var sheet = document.getElementById('chapter-sheet');
  if (sheetBtn && sheet) sheetBtn.addEventListener('click', function(){ sheet.classList.toggle('open'); });
  if (CFU) {
    function markCorrect(qEl, cid, qi){
      var q = CFU.chapters[cid].questions[qi];
      qEl.querySelectorAll('.opt').forEach(function(b){
        b.disabled = true;
        if (+b.getAttribute('data-o') === q.answer) b.classList.add('picked-right');
      });
      var fb = qEl.querySelector('.feedback');
      fb.hidden = false; fb.className = 'feedback good'; fb.textContent = q.explain;
    }
    function refreshDone(block, cid){
      var dn = block.querySelector('.done-note');
      if (!dn) return;
      if (cfuPassed(cid)) {
        var idx = -1;
        chapters.forEach(function(c, i){ if (c.id === cid) idx = i; });
        dn.hidden = false;
        dn.textContent = (idx === chapters.length - 1)
          ? 'Chapter complete. That was the final chapter of this dossier.'
          : 'Chapter complete. The next chapter is now unlocked.';
      } else {
        dn.hidden = true;
      }
    }
    document.querySelectorAll('.cfu').forEach(function(block){
      var cid = block.getAttribute('data-chapter');
      var got = state.cfu[cid] || [];
      block.querySelectorAll('.cfu-q').forEach(function(qEl){
        var qi = +qEl.getAttribute('data-q');
        if (got[qi]) markCorrect(qEl, cid, qi);
      });
      refreshDone(block, cid);
    });
    document.querySelectorAll('.cfu .opt').forEach(function(btn){
      btn.addEventListener('click', function(){
        var qEl = btn.closest('.cfu-q');
        var block = btn.closest('.cfu');
        var cid = block.getAttribute('data-chapter');
        var qi = +qEl.getAttribute('data-q');
        var oi = +btn.getAttribute('data-o');
        var q = CFU.chapters[cid].questions[qi];
        if (!state.cfu[cid]) state.cfu[cid] = [];
        if (state.cfu[cid][qi]) return;
        var fb = qEl.querySelector('.feedback');
        if (oi === q.answer) {
          state.cfu[cid][qi] = true;
          if (cfuPassed(cid) && state.done.indexOf(cid) < 0) state.done.push(cid);
          save();
          markCorrect(qEl, cid, qi);
          paintTicks(); paintLocks();
          refreshDone(block, cid);
        } else {
          btn.classList.add('picked-wrong');
          btn.disabled = true;
          fb.hidden = false; fb.className = 'feedback try';
          fb.textContent = 'Not quite. Re-read this chapter and try again: the answer is in the text above.';
        }
      });
    });
    var uc = document.getElementById('unlock-all');
    if (uc) {
      uc.checked = !!state.teacherUnlock;
      uc.addEventListener('change', function(){ state.teacherUnlock = uc.checked; save(); paintLocks(); });
    }
    var rp = document.getElementById('reset-progress');
    if (rp) rp.addEventListener('click', function(){
      if (window.confirm('Reset all reading progress and check-for-understanding answers on this device?')) {
        try { localStorage.removeItem(KEY); } catch(e) {}
        location.reload();
      }
    });
    var startId = null;
    if (state.current) {
      var cur = document.getElementById(state.current);
      if (cur && isUnlocked(chapterIndex(cur))) startId = state.current;
    }
    if (!startId) {
      var firstOpen = null;
      chapters.forEach(function(c, i){ if (!firstOpen && isUnlocked(i) && !cfuPassed(c.id)) firstOpen = c; });
      startId = firstOpen ? firstOpen.id : chapters[chapters.length - 1].id;
    }
    showChapter(startId, false);
  }
  var hiddenBeforePrint = [];
  window.addEventListener('beforeprint', function(){
    document.querySelectorAll('details').forEach(function(d){ d.open = true; });
    if (CFU) {
      hiddenBeforePrint = [];
      chapters.forEach(function(ch){
        if (ch.hasAttribute('hidden')) { hiddenBeforePrint.push(ch.id); ch.removeAttribute('hidden'); }
      });
      document.querySelectorAll('.chap-nav[data-for]').forEach(function(n){ n.removeAttribute('hidden'); });
    }
  });
  window.addEventListener('afterprint', function(){
    if (CFU) {
      hiddenBeforePrint.forEach(function(id){
        var el = document.getElementById(id);
        if (el && id !== state.current) el.setAttribute('hidden', '');
      });
      document.querySelectorAll('.chap-nav[data-for]').forEach(function(n){
        if (n.getAttribute('data-for') !== state.current) n.setAttribute('hidden', '');
      });
    }
  });
})();
</script>
"""

ESSENTIAL_QUESTION = ("How did one Atlanta street become \"the richest Negro street in the world,\" "
                      "and why did the forces that concentrated its wealth later scatter it?")

RECALL = ('<div class="recall"><strong>Quick recall.</strong> Before you move on, say it back without '
          'scrolling up: which people, places, or decisions from this chapter matter most, and why? '
          'Then glance back and check yourself.</div>')


def md2html(text):
    return markdown.markdown(text)


def video_embed_html(video_id, title):
    """Responsive 16:9 YouTube embed block for a chapter video, captioned
    as a 'Watch:' line. Used for the educational chapter videos hosted on
    the All Black Towns YouTube channel (unlisted) and embedded on site."""
    return ('<figure class="video-embed"><div class="video-frame">'
            '<iframe src="https://www.youtube.com/embed/%s" title="%s" '
            'loading="lazy" allow="accelerometer; autoplay; clipboard-write; '
            'encrypted-media; gyroscope; picture-in-picture; web-share" '
            'allowfullscreen></iframe></div>'
            '<figcaption>Watch: %s</figcaption></figure>'
            % (video_id, title, title))


def inject_after_first_h2(html, block):
    """Insert block right after the chapter's first </h2> heading."""
    return html.replace("</h2>", "</h2>\n" + block, 1)


TEACHER_CONTROLS = (
    '<div id="teacher-controls"><h3>Teacher controls</h3>'
    '<p>For classroom use on this device. Unlocking opens every chapter for this reader; '
    'resetting clears the saved progress and check-for-understanding answers stored on this device.</p>'
    '<div class="row"><label><input type="checkbox" id="unlock-all"> Unlock all chapters (teacher)</label>'
    '<button type="button" id="reset-progress">Reset progress</button></div></div>')


def load_cfu_data():
    p = os.path.join(SITE, "cfu-data.json")
    if os.path.exists(p):
        return json.load(open(p))
    return {}


def render_timeline(cfu):
    items = "".join(
        '<div class="tl-item"><span class="tl-year">%s</span><span class="tl-text">%s</span></div>'
        % (e["year"], e["label"]) for e in cfu.get("timeline", []))
    return ('<div class="timeline"><h3>Timeline: the story at a glance</h3>%s</div>' % items)


def render_cfu(cid, chdata):
    blocks = []
    key_items = []
    for i, q in enumerate(chdata["questions"]):
        opts = "".join(
            '<button type="button" class="opt" data-o="%d">%s</button>' % (j, o)
            for j, o in enumerate(q["options"]))
        blocks.append(
            '<div class="cfu-q" data-q="%d"><p class="qtext">%s</p>%s'
            '<p class="feedback" hidden></p></div>' % (i, q["q"], opts))
        key_items.append('<li><strong>%s</strong> Correct answer: %s. %s</li>'
                         % (q["q"], q["options"][q["answer"]], q["explain"]))
    return ('<div class="cfu" data-chapter="%s"><h3>Check for understanding</h3>'
            '<p class="cfu-intro">Answer every question correctly to unlock the next chapter. '
            'A wrong answer is fine: re-read the chapter and try again.</p>%s'
            '<div class="done-note" hidden></div>'
            '<div class="cfu-key"><h4>Answer key</h4><ol>%s</ol></div></div>'
            % (cid, "".join(blocks), "".join(key_items)))


def article_ld(title, desc, slug):
    """The Article JSON-LD block for a pilot dossier page (GEO, 2026-10-28).
    Headline and description are the page's own title and meta description;
    hand-applied to the built pages first, kept in the template so rebuilds
    reproduce it. Ends with a newline for the {ld} slot in CHROME_TOP."""
    return ('<script type="application/ld+json">\n'
            + json.dumps({
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title + " - All Black Towns",
                "description": desc,
                "url": "https://www.allblacktowns.com/dossiers/%s.html" % slug,
            }, indent=2, ensure_ascii=False) + '\n</script>\n')


def assemble_page(title, desc, banner, orient, teacher, facts_html, chapters, extra, key, chrome_top=None, cfu=None, ld=""):
    """chapters: list of (id, label, heading, html, kind, recall_bool).
    html for open chapters includes its own <h2>; for details chapters the
    h2 is stripped and the heading becomes the summary."""
    rail_items = "".join(
        '<a href="#%s" data-ch="%s"><span class="tick"></span>%s</a>' % (cid, cid, label)
        for cid, label, _, _, _, _ in chapters)
    sheet_items = "".join(
        '<a href="#%s">%s</a>' % (cid, label) for cid, label, _, _, _, _ in chapters)
    has_details = any(kind == "details" or "<details" in html for _, _, _, html, kind, _ in chapters)

    parts = []
    for i, (cid, label, heading, html, kind, recall) in enumerate(chapters):
        nxt = chapters[i + 1] if i + 1 < len(chapters) else None
        prv = chapters[i - 1] if i > 0 else None
        nav = '<div class="chap-nav"%s>' % (' data-for="%s"' % cid if kind == "details" else "")
        nav += ('<a href="#%s">&larr; %s</a>' % (prv[0], prv[1])) if prv else "<span></span>"
        nav += ('<a href="#%s">Next: %s &rarr;</a>' % (nxt[0], nxt[1])) if nxt else "<span></span>"
        nav += "</div>"
        rec = RECALL if recall else ""
        tl = render_timeline(cfu) if cfu and cfu.get("timelineChapter") == cid else ""
        cq = render_cfu(cid, cfu["chapters"][cid]) if cfu and cid in cfu.get("chapters", {}) else ""
        if kind == "details":
            inner = re.sub(r"<h2>.*?</h2>", "", html, count=1, flags=re.S)
            parts.append(
                '<details class="deep chapter" id="%s" data-label="%s"><summary>%s</summary>'
                '<div class="deep-body">%s%s%s</div></details>%s' % (cid, label, heading, inner, tl, cq, nav))
        else:
            parts.append(
                '<section class="chapter" id="%s" data-label="%s">%s%s%s%s%s</section>'
                % (cid, label, html, tl, rec, cq, nav))
    chapters_html = "\n".join(parts)

    rail = '<aside class="rail"><h4>Chapters</h4>%s' % rail_items
    if has_details:
        rail += '<div class="rail-tools"><button type="button" id="expand-all">Expand all sections</button></div>'
    rail += "</aside>"
    chapter_bar = ('<div id="chapter-bar"><span id="chapter-bar-label">%s</span>'
                   '<button type="button" id="chapter-sheet-btn">Contents</button></div>'
                   '<div id="chapter-sheet">%s</div>') % (chapters[0][1], sheet_items)

    out = (chrome_top or CHROME_TOP).format(title=title, desc=desc, css=V2_CSS, ld=ld)
    out += '<div id="progress-bar"></div>\n'
    out += '<h2 class="section-title">%s</h2>\n' % title
    out += '<div class="beta-banner">%s</div>\n' % banner
    out += orient + "\n"
    if teacher:
        out += teacher + "\n"
    if cfu:
        out += TEACHER_CONTROLS + "\n"
    if facts_html:
        out += facts_html + "\n"
    if cfu:
        out += '<div id="lock-note" style="display:none"></div>\n'
    out += chapter_bar + "\n"
    out += '<div class="layout">%s<div class="dossier">%s</div></div>\n' % (rail, chapters_html)
    out += extra
    js = V2_JS.replace("__KEY__", key)
    if cfu:
        payload = {"chapters": {}}
        for cid, chd in cfu.get("chapters", {}).items():
            payload["chapters"][cid] = {"questions": [
                {"answer": q["answer"], "explain": q["explain"]} for q in chd["questions"]]}
        js = ('<script>window.ABT_CFU = %s;</script>\n' % json.dumps(payload)) + js
    out += CHROME_BOTTOM.replace("</body></html>", js + "</body></html>")
    return out


def build():
    title, sections = split_sections(open(os.path.join(SRC, "sweet-auburn-dossier-pilot.md")).read())
    name = title.replace("Town Dossier: ", "")
    sec = dict(sections)
    order = [h for h, _ in sections]

    words = sum(len(b.split()) for _, b in sections)
    minutes = max(1, round(words / 200))

    chapters = []
    intro_html = md2html("## Introduction\n\n" + sec["Header"])
    chapters.append(("intro", "Introduction", "Introduction", intro_html, "open", False))

    facts_html = '<div class="facts">%s</div>' % md2html("## Key Facts Box\n\n" + sec["Key Facts Box"])

    nums = [h for h in order if re.match(r"^\d+\.", h)]
    for h in nums:
        n = h.split(".")[0]
        html = md2html("## %s\n\n%s" % (h, sec[h]))
        kind = "open"
        if h.startswith("7."):
            marker = "<p>Lyric annotation"
            if marker in html:
                head, tail = html.split(marker, 1)
                tail = ('<details class="inline"><summary>Lyric annotations, line by line</summary>'
                        + marker + tail + "</details>")
                html = head + tail
            # Sing-along music video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it belongs to.
            html = inject_after_first_h2(html, video_embed_html(
                "kIq9uxD5ymk",
                "Sweet Auburn, Atlanta, Georgia (Sing-Along Music Video)"))
        if h.startswith(("8.", "9.")):
            kind = "details"
        if h.startswith("1."):
            # Chapter 1 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "YYkamPbVW_Q",
                "Founding: Sweet Auburn, Chapter 1 (Educational Version)"))
        if h.startswith("2."):
            # Chapter 2 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "opr7v_0n-w4",
                "Building the Town: Sweet Auburn, Chapter 2 (Educational Version)"))
        if h.startswith("3."):
            # Chapter 3 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "cZe_ARWH76A",
                "Peak Years: Sweet Auburn, Chapter 3 (Educational Version)"))
        if h.startswith("4."):
            # Chapter 4 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "1q5OVtwsM9c",
                "The Turning Point: Sweet Auburn, Chapter 4 (Educational Version)"))
        if h.startswith("5."):
            # Chapter 5 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "7L6tapDlsV8",
                "Survival, Decline, or Destruction: Sweet Auburn, Chapter 5 (Educational Version)"))
        if h.startswith("6."):
            # Chapter 6 educational video (All Black Towns channel, unlisted),
            # embedded at the top of the chapter it teaches.
            html = inject_after_first_h2(html, video_embed_html(
                "TUjl_nB8gLo",
                "The Town Today: Sweet Auburn, Chapter 6 (Educational Version)"))
        recall = kind == "open" and n not in ("7",)
        chapters.append(("ch" + n, h, h, html, kind, recall))

    banner = ("<strong>Free beta sample.</strong> This is the complete Sweet Auburn dossier, "
              "published as the sample for the All Black Towns curriculum beta. "
              "The pilot lesson plan built on it is here: "
              "<a href=\"sweet-auburn-lesson.html\"><strong>Sweet Auburn Lesson Plan</strong></a>.")

    orient = (
        '<div class="orient"><div class="meta">About %d min read &middot; %d chapters &middot; Free beta sample</div>'
        '<p class="eq">%s</p>'
        '<p>This dossier follows the district in order: how it was founded, how it was built, its peak years, '
        'the turning point, and the Sweet Auburn of today, ending with its song and the primary sources behind '
        'the record. Work through it one chapter at a time: a short check for understanding at the end of each '
        'chapter unlocks the next, and the contents rail maps where you are.</p>'
        '<div class="fork"><a href="#intro">Start reading</a>'
        '<button type="button" id="teach-btn">Teach this town</button>'
        '<button type="button" class="ghost" onclick="window.print()">Print / save PDF</button></div>'
        '<p class="map-link"><a href="../map.html">Find Sweet Auburn on the map</a></p>'
        '<div id="resume-chip"></div></div>'
    ) % (minutes, len(chapters), ESSENTIAL_QUESTION)

    teacher = (
        '<div id="teacher-panel"><h3 style="margin-top:0">For teachers</h3>'
        '<p><strong>Lesson:</strong> "The Richest Street in the World" &middot; <strong>Grade band:</strong> 9-12 '
        '(adaptations for 6-8 and adult self-guided learners included) &middot; <strong>Time:</strong> two class '
        'periods of about 50 minutes, or about two hours self-paced.</p>'
        '<p><strong>Essential question:</strong> %s</p>'
        '<p>The full lesson plan, with materials, the primary source activity, and the performance task, is here: '
        '<a href="sweet-auburn-lesson.html"><strong>Sweet Auburn Lesson Plan</strong></a>. '
        'Use Print / save PDF above to take this dossier into the classroom on paper.</p></div>'
    ) % ESSENTIAL_QUESTION

    extra = ('<div class="doss-end"><p><strong>Teach it:</strong> the pilot lesson plan built on this dossier '
             'is free with it - <a href="sweet-auburn-lesson.html">open the Sweet Auburn lesson plan</a>.</p></div>')

    sa_title = name + " - Town Dossier"
    sa_desc = "The complete Sweet Auburn town dossier: Sweet Auburn, Atlanta, Georgia."
    out = assemble_page(sa_title, sa_desc,
                        banner, orient, teacher, facts_html, chapters, extra,
                        "abt-proto-sweet-auburn", cfu=load_cfu_data().get("sweet-auburn"),
                        ld=article_ld(sa_title, sa_desc, "sweet-auburn"))
    path = os.path.join(OUT, "sweet-auburn-v2.html")
    open(path, "w").write(out)
    live = os.path.join(OUT, "sweet-auburn.html")
    open(live, "w").write(out)
    print("wrote", path, "and", live, len(out), "bytes | chapters:", len(chapters), "| minutes:", minutes)


if __name__ == "__main__":
    build()
