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

ROOT = Path(__file__).resolve().parent.parent
SECTION_TAGS = {
    "Kommende møder": ("kommende", "Næste"),
    "Åbne sager": ("aabne", "Åben"),
    "Afgjorte sager": ("afgjorte", "Afgjort"),
}

TEMPLATE = """<!doctype html>
<html lang="da">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Skolesager i Glostrup – Nordvang/Ejby</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta name="description" content="Politiske sager, der rammer Nordvang og Ejby – fra alle udvalg i Glostrup Kommune.">
<meta property="og:type" content="website">
<meta property="og:locale" content="da_DK">
<meta property="og:title" content="Skolesager i Glostrup – Nordvang/Ejby">
<meta property="og:description" content="Kommende møder, åbne og afgjorte sager fra alle udvalg i Glostrup Kommune.">
<meta property="og:url" content="https://duemunk.github.io/glostrup-skolesager/">
<meta property="og:image" content="https://duemunk.github.io/glostrup-skolesager/delingsbillede.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Nordvang-/Ejbyskolens logo og teksten Skolesager i Glostrup">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap">
<style>
:root { --navy:#0b1f5a; --ink:#17203a; --grey:#5b6482; --yellow:#f2a826; --line:#dcd8cc; --paper:#fff; --tint:#f6f4ee; --font:"Source Sans 3","Source Sans Pro",system-ui,sans-serif; }
html, body { margin:0; background:var(--paper); color:var(--ink); font-family:var(--font); font-size:17px; line-height:1.45; }
.page { max-width:1100px; margin:0 auto; padding:32px 16px 48px; }
header { display:flex; align-items:baseline; gap:12px; padding-bottom:10px; border-bottom:2px solid var(--yellow); margin-bottom:28px; }
header .logo { width:56px; height:auto; }
header .school { font-weight:700; line-height:1; }
h1 { font-size:32px; font-weight:700; color:var(--navy); line-height:1.15; margin:0 0 4px; }
h1 + p { color:var(--grey); margin:0 0 12px; }
h2 { font-size:22px; font-weight:600; color:var(--navy); margin:36px 0 6px; display:flex; align-items:center; gap:10px; }
h2 .tag { font-size:13px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; padding:2px 8px; border-radius:999px; }
.kommende h2 .tag { background:var(--navy); color:#fff; }
.aabne h2 .tag { background:var(--yellow); color:var(--navy); }
.afgjorte h2 .tag { background:var(--tint); color:var(--grey); border:1px solid var(--line); }
p { margin:0 0 10px; }
a { color:var(--navy); text-decoration-color:var(--yellow); text-decoration-thickness:2px; text-underline-offset:2px; }
a:hover { color:#1a4a9a; }
.table-wrap { overflow-x:auto; margin:8px 0 0; }
table { border-collapse:collapse; width:100%; font-size:16px; }
th { text-align:left; font-weight:600; color:var(--grey); border-bottom:2px solid var(--line); padding:6px 10px; white-space:nowrap; }
td { vertical-align:top; border-bottom:1px solid var(--line); padding:8px 10px; }
td:first-child { white-space:nowrap; font-variant-numeric:tabular-nums; }
.aabne td:first-child { box-shadow:inset 3px 0 0 var(--yellow); }
footer { margin-top:40px; padding-top:8px; border-top:1px solid var(--line); color:var(--grey); font-size:14px; }
@media (max-width:640px) { h1 { font-size:26px; } table { font-size:15px; } td, th { padding:6px 8px; } }
</style>
</head>
<body>
<div class="page">
<header><svg class="logo" role="img" aria-label="Nordvang-/Ejbyskolen" viewBox="0 0 89 55" xmlns="http://www.w3.org/2000/svg">
  <polygon fill="#F2A826" points="30 0 53 16 53 55 30 55"/>
  <polygon fill="#F2A826" points="0 16 24 0 24 55 0 55"/>
  <polygon fill="#32896A" transform="translate(74, 38) scale(-1, 1) translate(-74, -38)" points="59 39.3076923 74 21 89 39.3076923 89 55 59 55"/>
</svg><span class="school">Nordvang-/Ejbyskolen</span></header>
<main>
{content}
</main>
<footer>Kilde: <a href="https://dagsorden.glostrup.dk/">Åben Dagsorden, Glostrup Kommune</a> · Ikke en officiel side · <a href="https://github.com/duemunk/glostrup-skolesager">Ret eller tilføj på GitHub</a></footer>
</div>
</body>
</html>
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


def render_table(lines):
    head = cells(lines[0])
    rows = [cells(line) for line in lines[2:]]
    out = ['<div class="table-wrap"><table>', "<thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def render(markdown):
    blocks = re.split(r"\n\s*\n", markdown.strip())
    out = []
    section_open = False
    for block in blocks:
        lines = block.strip().splitlines()
        first = lines[0]
        if first.startswith("## "):
            title = first[3:].strip()
            if section_open:
                out.append("</section>")
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
    page = TEMPLATE.replace("{content}", render(markdown))
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print("index.html bygget fra README.md")


if __name__ == "__main__":
    main()
