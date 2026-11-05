"""Fælles sidehoved, faneblade, typografi og sidefod for alle sider.

Bruges af byg_side.py (forsiden) og byg_sager.py (sager og kilder). Farver og
skrift følger Nordvang-/Ejbyskolens visuelle identitet.
"""

import html

BASE_URL = "https://duemunk.github.io/nordvang-ejby/"

TABS = [("", "Overblik"), ("sager/", "Sager"), ("kilder/", "Kilder og links")]

BASE_CSS = """
:root { --navy:#0b1f5a; --ink:#17203a; --grey:#5b6482; --yellow:#f2a826; --line:#dcd8cc; --paper:#fff; --tint:#f6f4ee; --sb:#e7ecf8; --font:"Source Sans 3","Source Sans Pro",system-ui,sans-serif; }
html, body { margin:0; background:var(--paper); color:var(--ink); font-family:var(--font); font-size:17px; line-height:1.45; }
.page { max-width:1100px; margin:0 auto; padding:32px 16px 48px; }
header { display:flex; align-items:baseline; gap:12px; padding-bottom:10px; border-bottom:2px solid var(--yellow); }
header .logo { width:56px; height:auto; }
header .school { font-weight:700; line-height:1; }
nav.tabs { display:flex; gap:24px; flex-wrap:wrap; margin:6px 0 24px; }
nav.tabs a { color:var(--grey); font-weight:600; text-decoration:none; padding:10px 0; border-bottom:3px solid transparent; }
nav.tabs a:hover { color:var(--navy); }
nav.tabs a[aria-current="page"] { color:var(--navy); border-bottom-color:var(--yellow); }
h1 { font-size:32px; font-weight:700; color:var(--navy); line-height:1.15; margin:0 0 4px; text-wrap:balance; }
h1 + p { color:var(--grey); margin:0 0 12px; }
p { margin:0 0 10px; }
a { color:var(--navy); text-decoration-color:var(--yellow); text-decoration-thickness:2px; text-underline-offset:2px; }
a:hover { color:#1a4a9a; }
a:focus-visible { outline:2px solid var(--yellow); outline-offset:2px; border-radius:4px; }
.num { font-variant-numeric:tabular-nums; }
footer { margin-top:40px; padding-top:8px; border-top:1px solid var(--line); color:var(--grey); font-size:14px; }
@media (max-width:640px) {
  .page { padding:20px 16px 40px; }
  header .logo { width:44px; }
  nav.tabs { gap:20px; margin-bottom:18px; }
  h1 { font-size:26px; }
}
"""

LOGO = """<svg class="logo" role="img" aria-label="Nordvang-/Ejbyskolen" viewBox="0 0 89 55" xmlns="http://www.w3.org/2000/svg">
  <polygon fill="#F2A826" points="30 0 53 16 53 55 30 55"/>
  <polygon fill="#F2A826" points="0 16 24 0 24 55 0 55"/>
  <polygon fill="#32896A" transform="translate(74, 38) scale(-1, 1) translate(-74, -38)" points="59 39.3076923 74 21 89 39.3076923 89 55 59 55"/>
</svg>"""


def build_head(title, description, path, prefix, share_description=None):
    title_e, description_e = html.escape(title), html.escape(description)
    share_e = html.escape(share_description or description)
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_e}</title>
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<meta name="description" content="{description_e}">
<meta property="og:type" content="website">
<meta property="og:locale" content="da_DK">
<meta property="og:title" content="{title_e}">
<meta property="og:description" content="{share_e}">
<meta property="og:url" content="{BASE_URL}{path}">
<meta property="og:image" content="{BASE_URL}delingsbillede.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Nordvang-/Ejbyskolens logo og teksten Skolesager i Glostrup">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap">"""


def build_header(active, prefix):
    links = "".join(
        f'<a href="{(prefix + href) or "./"}"' + (' aria-current="page"' if href == active else "") + f">{label}</a>"
        for href, label in TABS
    )
    return f'<header>{LOGO}<span class="school">Nordvang-/Ejbyskolen</span></header>\n<nav class="tabs" aria-label="Sider">{links}</nav>'


FOOTER = (
    '<footer>Kilde: <a href="https://dagsorden.glostrup.dk/">Åben Dagsorden, Glostrup Kommune</a>'
    " · Ikke en officiel side · "
    '<a href="https://github.com/duemunk/nordvang-ejby">Ret eller tilføj på GitHub</a></footer>'
)


def build_page(title, description, path, prefix, active, css, content, footer=FOOTER, share_description=None):
    return f"""<!doctype html>
<html lang="da">
<head>
{build_head(title, description, path, prefix, share_description)}
<style>{BASE_CSS}{css}</style>
</head>
<body>
<div class="page">
{build_header(active, prefix)}
<main>
{content}
</main>
{footer}
</div>
</body>
</html>
"""
