#!/usr/bin/env python3
"""Bygger sagssiderne (sager/) og kildesiden (kilder/) ud fra data/.

Brug:
    python3 scripts/byg_sager.py

Kilder: data/sager.json (temaer, sager og deres tidslinjer) og data/links.json.
Filerne i sager/ og kilder/ må ikke redigeres i hånden – ret i data/ og kør
scriptet igen. Kun standardbiblioteket bruges.
"""

import html
import json
import shutil
from pathlib import Path

from faelles import FOOTER, build_page

ROOT = Path(__file__).resolve().parent.parent
SB = "Skolebestyrelsen"

CSS = """
.lead { max-width:65ch; }
.summary { display:flex; gap:16px; flex-wrap:wrap; color:var(--grey); font-size:15px; margin:4px 0 8px; }
section.topic { margin-top:28px; }
section.topic h2, .linkgroup h2 { font-size:15px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:var(--grey); margin:0 0 6px; }
.cases { list-style:none; margin:0; padding:0; border-top:1px solid var(--line); }
.cases li { border-bottom:1px solid var(--line); }
.case-row { display:grid; grid-template-columns:auto 1fr auto; gap:4px 12px; align-items:baseline; padding:12px 8px; text-decoration:none; color:inherit; }
.case-row:hover { background:var(--tint); }
.case-row .t { font-weight:600; color:var(--navy); }
.case-row .l { grid-column:2 / 4; }
.case-row .m { grid-column:2 / 4; color:var(--grey); font-size:14px; }
.case-row .chev { color:var(--grey); }
.pill { font-size:12px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; padding:2px 8px; border-radius:999px; white-space:nowrap; }
.pill.aaben { background:var(--yellow); color:var(--navy); }
.pill.afgjort { background:var(--tint); color:var(--grey); border:1px solid var(--line); }
.back { display:inline-block; margin-bottom:12px; font-weight:600; }
.eyebrow { color:var(--grey); font-size:14px; letter-spacing:.06em; text-transform:uppercase; margin-bottom:4px; }
.case-head { display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:6px; }
.case-head h1 { margin:0; }
.legend { display:flex; gap:16px; flex-wrap:wrap; font-size:14px; color:var(--grey); margin-top:10px; }
.legend span::before { content:""; display:inline-block; width:10px; height:10px; border-radius:50%; border:3px solid var(--navy); margin-right:6px; vertical-align:-1px; }
.legend .l-sb::before { border-color:var(--yellow); }
.legend .l-k::before { border-style:dashed; border-color:var(--grey); }
.timeline { list-style:none; margin:24px 0 0; padding:0; position:relative; max-width:760px; }
.timeline::before { content:""; position:absolute; left:7px; top:6px; bottom:6px; width:2px; background:var(--line); }
.ev { position:relative; padding:0 0 22px 30px; }
.ev::before { content:""; position:absolute; left:1px; top:6px; width:14px; height:14px; border-radius:50%; background:var(--paper); border:3px solid var(--navy); box-sizing:border-box; }
.ev.sb::before { border-color:var(--yellow); }
.ev.kommende::before { border-style:dashed; border-color:var(--grey); }
.ev .row1 { display:flex; gap:8px; flex-wrap:wrap; align-items:center; font-size:14px; color:var(--grey); }
.src { font-weight:600; padding:1px 8px; border-radius:6px; background:var(--tint); color:var(--ink); }
.ev.sb .src { background:var(--sb); color:var(--navy); }
.ev .t { font-weight:600; margin-top:3px; }
.ev .x { margin:2px 0 4px; max-width:65ch; }
.ev .links { display:flex; gap:14px; flex-wrap:wrap; font-size:15px; }
.linkgroup { margin-top:24px; max-width:760px; }
.linkgroup ul { list-style:none; margin:0; padding:0; border-top:1px solid var(--line); }
.linkgroup li { padding:10px 0; border-bottom:1px solid var(--line); }
.linkgroup .note { display:block; color:var(--grey); font-size:15px; }
@media (max-width:640px) { .case-row { padding:12px 2px; } }
"""


def e(text):
    return html.escape(str(text))


def dk(date):
    return f"{date[8:10]}-{date[5:7]}-{date[0:4]}"


def pill(status):
    return '<span class="pill aaben">Åben</span>' if status == "åben" else '<span class="pill afgjort">Afgjort</span>'


def ext(url, label):
    return f'<a href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>'


def build_footer(data):
    first, last = data["referater_fra_til"]
    note = (
        f' Skolebestyrelsens referater: <span class="num">{dk(first)}–{dk(last)}</span>'
        " (senere er ikke offentliggjort).</footer>"
    )
    return FOOTER.replace("</footer>", note)


def build_overview(data):
    cases = data["sager"]
    open_count = sum(1 for c in cases if c["status"] == "åben")
    out = [
        "<h1>Sager efter tema</h1>",
        '<p class="lead">Sager, der rammer Nordvang/Ejby – fra skolebestyrelsen og Glostrup Kommunes udvalg. '
        "Vælg en sag for at se hele forløbet.</p>",
        f'<div class="summary num"><span>{len(cases)} sager</span><span>{open_count} åbne</span>'
        f'<span>Opdateret {dk(data["opdateret"])}</span></div>',
    ]
    for topic in data["temaer"]:
        topic_cases = [c for c in cases if c["topic"] == topic["slug"]]
        if not topic_cases:
            continue
        topic_cases.sort(key=lambda c: c["last"], reverse=True)
        topic_cases.sort(key=lambda c: c["status"] != "åben")
        out.append(f'<section class="topic" aria-labelledby="t-{topic["slug"]}"><h2 id="t-{topic["slug"]}">{e(topic["name"])}</h2><ul class="cases">')
        for c in topic_cases:
            out.append(
                f'<li><a class="case-row" href="{c["id"]}.html">{pill(c["status"])}<span class="t">{e(c["t"])}</span>'
                f'<span class="chev" aria-hidden="true">›</span><span class="l">{e(c["lead"])}</span>'
                f'<span class="m num">Senest {dk(c["last"])} · {len(c["events"])} møder · {" og ".join(c["sources"])}</span></a></li>'
            )
        out.append("</ul></section>")
    return "\n".join(out)


def build_case(case, topic_names):
    out = [
        '<a class="back" href="./">‹ Alle sager</a>',
        f'<div class="eyebrow">{e(topic_names[case["topic"]])}</div>',
        f'<div class="case-head"><h1>{e(case["t"])}</h1>{pill(case["status"])}</div>',
        f'<p class="lead">{e(case["lead"])}</p>',
        '<div class="legend"><span class="l-sb">Skolebestyrelsen</span><span>Kommunen</span><span class="l-k">Kommende</span></div>',
        '<ol class="timeline">',
    ]
    for event in case["events"]:
        classes = " ".join(c for c in ["ev", "sb" if event["src"] == SB else "", "kommende" if event["kind"] == "Kommende" else ""] if c)
        links = "".join(ext(url, label) for label, url in event["links"])
        out.append(
            f'<li class="{classes}"><div class="row1"><span class="num">{dk(event["d"])}</span>'
            f'<span class="src">{e(event["src"])}</span><span>{e(event["kind"])}</span></div>'
            f'<div class="t">{e(event["t"])}</div><p class="x">{e(event["x"])}</p><div class="links">{links}</div></li>'
        )
    out.append("</ol>")
    return "\n".join(out)


def build_sources(links):
    out = ["<h1>Kilder og links</h1>", '<p class="lead">Hvor oplysningerne kommer fra, og hvor du selv kan følge med.</p>']
    for group in links:
        out.append(f'<section class="linkgroup"><h2>{e(group["group"])}</h2><ul>')
        for link in group["links"]:
            note = f'<span class="note">{e(link["note"])}</span>' if link.get("note") else ""
            out.append(f"<li>{ext(link['url'], link['title'])}{note}</li>")
        out.append("</ul></section>")
    return "\n".join(out)


def main():
    data = json.loads((ROOT / "data" / "sager.json").read_text(encoding="utf-8"))
    links = json.loads((ROOT / "data" / "links.json").read_text(encoding="utf-8"))
    topic_names = {t["slug"]: t["name"] for t in data["temaer"]}
    for case in data["sager"]:
        case["events"].sort(key=lambda event: event["d"], reverse=True)
        past = [event["d"] for event in case["events"] if event["kind"] != "Kommende"]
        case["last"] = past[0] if past else case["events"][0]["d"]
        case["sources"] = sorted({SB if event["src"] == SB else "Kommunen" for event in case["events"]})
    footer = build_footer(data)

    sager_dir = ROOT / "sager"
    shutil.rmtree(sager_dir, ignore_errors=True)
    sager_dir.mkdir()
    (sager_dir / "index.html").write_text(
        build_page("Sager efter tema – Nordvang/Ejby", "Sager om Nordvang/Ejby fra skolebestyrelsen og Glostrup Kommune, samlet efter tema.",
                   "sager/", "../", "sager/", CSS, build_overview(data), footer),
        encoding="utf-8",
    )
    for case in data["sager"]:
        (sager_dir / f"{case['id']}.html").write_text(
            build_page(f"{case['t']} – Nordvang/Ejby", case["lead"], f"sager/{case['id']}.html", "../", "sager/",
                       CSS, build_case(case, topic_names), footer),
            encoding="utf-8",
        )

    kilder_dir = ROOT / "kilder"
    kilder_dir.mkdir(exist_ok=True)
    (kilder_dir / "index.html").write_text(
        build_page("Kilder og links – Nordvang/Ejby", "Kilder og nyttige links om skolerne i Glostrup og Nordvang-/Ejbyskolen.",
                   "kilder/", "../", "kilder/", CSS, build_sources(links)),
        encoding="utf-8",
    )
    print(f"sager/ ({len(data['sager'])} sager) og kilder/ bygget fra data/")


if __name__ == "__main__":
    main()
