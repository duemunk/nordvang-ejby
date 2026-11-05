# Glostrup – skolesager

- Svar og skriv på dansk.
- `README.md` er kilden. `index.html` bygges med `python3 scripts/byg_side.py` og redigeres aldrig i hånden.
- Sagssiderne (`sager/`) og kildesiden (`kilder/`) bygges fra `data/sager.json` og `data/links.json` med `python3 scripts/byg_sager.py`. Fælles sidehoved, faneblade og typografi ligger i `scripts/faelles.py`.
- Opdatering af oversigten: brug skillen `opdater-skolesager` (`.claude/skills/opdater-skolesager/SKILL.md`).
- Typografi og farver følger Nordvang-/Ejbyskolens visuelle identitet: Source Sans 3, navy `#0b1f5a`, gul `#f2a826`, grøn `#32896A` i logoet. Ret dem kun i `scripts/faelles.py`.
- Delingsbilledet `delingsbillede.png` (1200 × 630) tegnes fra `scripts/delingsbillede.html` med headless Chrome: `--headless=new --window-size=1200,630 --screenshot=delingsbillede.png`.
- Hjemmeskærmsikonerne i `ikoner/` tegnes fra `scripts/ikon.html` med headless Chrome i 180, 192 og 512 px (`?w=64`), og den maskable i 512 px med `?w=50`. `manifest.webmanifest` peger på dem.
