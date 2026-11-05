#!/usr/bin/env python3
"""Bygger den statiske side index.html ud fra README.md.

Brug:
    python3 scripts/byg_side.py

README.md er kilden. index.html må ikke redigeres i hånden – kør scriptet efter
hver ændring i README.md og commit begge filer. Kun standardbiblioteket bruges.
"""

import html
import re
from pathlib import Path

from faelles import build_page

ROOT = Path(__file__).resolve().parent.parent
SECTION_TAGS = {
    "Kommende møder": ("kommende", "Næste"),
    "Åbne sager": ("aabne", "Åben"),
    "Afgjorte sager": ("afgjorte", "Afgjort"),
}

PAGE_CSS = """
h2 { font-size:22px; font-weight:600; color:var(--navy); margin:36px 0 6px; display:flex; align-items:center; gap:10px; }
h2 .tag { font-size:13px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; padding:2px 8px; border-radius:999px; }
.kommende h2 .tag { background:var(--navy); color:#fff; }
.aabne h2 .tag { background:var(--yellow); color:var(--navy); }
.afgjorte h2 .tag { background:var(--tint); color:var(--grey); border:1px solid var(--line); }
.table-wrap { overflow-x:auto; margin:8px 0 0; }
table { border-collapse:collapse; width:100%; font-size:16px; }
th { text-align:left; font-weight:600; color:var(--grey); border-bottom:2px solid var(--line); padding:6px 10px; white-space:nowrap; }
td { vertical-align:top; border-bottom:1px solid var(--line); padding:8px 10px; }
td:first-child { white-space:nowrap; font-variant-numeric:tabular-nums; }
.aabne td:first-child { box-shadow:inset 3px 0 0 var(--yellow); }
tbody tr.group-start:not(:first-child) td { border-top:2px solid var(--line); }
tr.repeat td { border-top:0; }
tr.repeat td.meta { color:transparent; }
tr.repeat td.meta a { visibility:hidden; }
@media (max-width:640px) {
  h2 { font-size:20px; margin-top:28px; }
  .table-wrap { overflow:visible; }
  table, tbody, tr, td { display:block; width:auto; }
  thead { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }
  tr { padding:12px 0; border-bottom:1px solid var(--line); }
  td, tbody tr.group-start:not(:first-child) td { border:0; padding:0; }
  tr.repeat td.meta { color:var(--grey); }
  tr.repeat td.meta a { visibility:visible; }
  tbody tr.group-start:not(:first-child) { border-top:1px solid var(--line); }
  td.meta { display:inline; color:var(--grey); font-size:15px; }
  td.meta + td.meta::before { content:" · "; }
  td.title { margin-top:2px; font-weight:600; }
  td.body { margin-top:2px; }
  td.labelled { margin-top:4px; color:var(--grey); font-size:15px; }
  td.labelled::before { content:attr(data-label) ": "; font-weight:600; }
  .aabne tr { padding-left:12px; box-shadow:inset 3px 0 0 var(--yellow); }
  .aabne td:first-child { box-shadow:none; }
}
"""


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2))}"'
        + (' target="_blank" rel="noopener"' if m.group(2).startswith("http") else "")
        + f">{m.group(1)}</a>",
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def cells(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


CELL_ROLES = {"Dato": "meta", "Udvalg": "meta", "Sag": "title", "Møde": "title", "Mangler": "labelled"}


def render_table(lines):
    head = cells(lines[0])
    rows = [cells(line) for line in lines[2:]]
    roles = [CELL_ROLES.get(h, "body") for h in head]
    out = ['<div class="table-wrap"><table>', "<thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    previous_key = None
    for row in rows:
        key = tuple(c for c, role in zip(row, roles) if role == "meta")
        group_class = "repeat" if key and key == previous_key else "group-start"
        previous_key = key
        out.append(
            f'<tr class="{group_class}">'
            + "".join(
                f'<td class="{role}" data-label="{html.escape(label)}">{inline(c)}</td>'
                for c, role, label in zip(row, roles, head)
            )
            + "</tr>"
        )
    out.append("</tbody></table></div>")
    return "\n".join(out)


GITHUB_ONLY_SECTIONS = {"Bidrag"}


def render(markdown):
    blocks = re.split(r"\n\s*\n", markdown.strip())
    out = []
    section_open = False
    skipping = False
    for block in blocks:
        lines = block.strip().splitlines()
        first = lines[0]
        if first.startswith("## "):
            title = first[3:].strip()
            if section_open:
                out.append("</section>")
                section_open = False
            skipping = title in GITHUB_ONLY_SECTIONS
        if skipping:
            continue
        if first.startswith("## "):
            css, label = SECTION_TAGS.get(title, ("", ""))
            out.append(f'<section class="{css}">' if css else "<section>")
            section_open = True
            tag = f' <span class="tag">{label}</span>' if label else ""
            out.append(f"<h2>{inline(title)}{tag}</h2>")
            lines = lines[1:]
            if not lines:
                continue
            first = lines[0]
        if first.startswith("# "):
            out.append(f"<h1>{inline(first[2:].strip())}</h1>")
        elif first.startswith("|") and len(lines) > 1 and re.match(r"^\|?\s*:?-", lines[1]):
            out.append(render_table(lines))
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    if section_open:
        out.append("</section>")
    return "\n".join(out)


def main():
    markdown = (ROOT / "README.md").read_text(encoding="utf-8")
    page = build_page(
        title="Skolesager i Glostrup – Nordvang/Ejby",
        description="Politiske sager, der rammer Nordvang og Ejby – fra alle udvalg i Glostrup Kommune.",
        path="",
        prefix="",
        active="",
        css=PAGE_CSS,
        content=render(markdown),
        share_description="Kommende møder, åbne og afgjorte sager fra alle udvalg i Glostrup Kommune.",
    )
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("index.html bygget fra README.md")


if __name__ == "__main__":
    main()
