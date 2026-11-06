---
name: opdater-skolesager
description: Opdater oversigten over skolesager i Glostrup Kommune (fokus Nordvang/Ejby) med nye dagsordener og referater fra Åben Dagsorden, byg den statiske side og send ændringen som pull request. Brug den, når nogen beder om at "opdatere oversigten", "tilføje nye sager", "tjekke nye referater", "flytte en sag til afgjort" eller rette en sag i README.md.
---

# Opdater skolesager

Oversigten bor i `README.md`. `index.html` (GitHub Pages-siden) bygges ud fra den med `scripts/byg_side.py` og må aldrig redigeres i hånden. Alt indhold er på dansk.

## 1. Hent nye punkter

Find datoen i linjen "Opdateret …" øverst i `README.md`. Hent punkter fra en uge før den dato og frem:

```bash
python3 scripts/hent_sager.py --fra 28/10/2026
```

Scriptet søger på tværs af alle udvalg og markerer hvert punkt `[NY]` eller `[kendt]` (linket står allerede i README). For hvert punkt får du mødestatus, møde- og punktlink, beslutningskompetence og beslutningerne.

Hvis brugeren har givet et konkret link til et møde eller punkt, så tag udgangspunkt i det.

## 2. Vurder hvert punkt

Medtag et punkt, når det påvirker skolerne – især Nordvangskolen og afdeling Ejby: klasser og distrikter, kapacitet og bygninger, skoleveje, SFO, økonomi og takster, specialområdet, skolebestyrelser, befolkningsprognoser og byggeri i Ejby, der giver flere børn. Spring rene formalia over (godkendelse af dagsorden, mødeplaner) og punkter, der kun nævner "skole" i forbifarten.

Et punkt er **åbent**, når

- mødet kun har status *Dagsorden* (forvaltningens indstilling, intet besluttet), eller
- beslutningen er "anbefales godkendt", "oversendes" eller "udsættes", og den myndighed, der står under *Beslutningskompetence*, endnu ikke har truffet beslutning, eller
- beslutningen udskyder noget konkret (finansiering, en selvstændig sag, ny behandling).

Et punkt er **afgjort**, når der er referat med beslutning fra den myndighed, der har beslutningskompetencen ("godkendt", "til orientering", vedtaget ved afstemning).

Samme sag går ofte gennem fagudvalg → Økonomiudvalget → Kommunalbestyrelsen. Den skal kun stå én gang: i det seneste trin, med link til det trin.

## 3. Ret README.md

Rækkefølgen af afsnit er fast: **Kommende møder**, **Åbne sager**, **Afgjorte sager**, **Bidrag**. I hver tabel står nyeste dato øverst.

- **Dato** `DD-MM-ÅÅÅÅ`, linket til mødet: `[04-11-2026](https://dagsorden.glostrup.dk/meeting/4445)`.
- **Udvalg** skrevet helt ud, fx "Børne- og Skoleudvalget".
- **Sag** som kort titel, linket til punktet: `[Skoleindskrivning 2026/27](https://dagsorden.glostrup.dk/meeting/agendaitem/print/89865/147849)`.
- **Kort**: én linje, højst ca. 20 ord, med tal og enheder (mio. kr., elever, klasser) og afstemningstal, hvor de findes. Nævn Nordvang/Ejby, når det er dem, det handler om.
- **Mangler** (kun i Åbne sager): hvem eller hvad sagen venter på, fx "Kommunalbestyrelsen", "Finansiering".
- Alle kilder er links. Skriv ikke fakta, du ikke har set i punktet.

Når en åben sag bliver afgjort: flyt rækken fra Åbne sager til Afgjorte sager, opdatér dato, link og Kort til det afgørende møde.

Kommende møder: tag møder med fra forsiden af [Åben Dagsorden](https://dagsorden.glostrup.dk/) ("Kommende møder"), når der ventes en beslutning i en åben sag. Fjern møder, der har været afholdt.

Opdatér til sidst datoen i "Opdateret …".

## 4. Ret sagssiderne

Siden "Sager efter tema" (`sager/`) bygges fra `data/sager.json`. Hver sag har `id`, `topic` (et af temaernes `slug`), `status` ("åben" eller "afgjort"), titel `t`, en kort `lead` og en liste `events`. Hver hændelse:

```json
{"d": "2026-11-04", "src": "Børne- og Skoleudvalget", "kind": "Anbefaling",
 "t": "Kort titel", "x": "En til to sætninger med tal og udfald.",
 "links": [["Punkt", "https://dagsorden.glostrup.dk/meeting/agendaitem/print/…"]]}
```

- `src` er "Skolebestyrelsen" eller udvalgets fulde navn. `kind` er fx Høring, Høringssvar, Anbefaling, Beslutning, Orientering, Udsat eller Kommende.
- For hvert nyt punkt fra trin 2: tilføj en hændelse til den sag, det hører til, og opdatér sagens `status` og `lead`. Hører det ikke til en sag, så opret en ny.
- Skolebestyrelsens høringssvar ligger som bilag på punkterne. `python3 scripts/hent_hoeringssvar.py` finder dem; link dem som `["Høringssvar (PDF)", "<url>"]`.
- Skolebestyrelsens referater ligger i [Drive-mappen](https://drive.google.com/drive/folders/1wy7QcmXD0iuhFbZv6E8iGdMmu9Gv28CH). Nye referater tilføjes til `data/skolebestyrelse.json` og som hændelser med `"src": "Skolebestyrelsen"` og link til referatets PDF. Opdatér `referater_fra_til`.
- Nye links til siden "Kilder og links" tilføjes i `data/links.json`.

## 5. Byg siderne

```bash
python3 scripts/tjek_data.py
python3 scripts/byg_side.py
python3 scripts/byg_sager.py
```

`tjek_data.py` finder fejl i `data/` (forkert status, tema eller datoformat, ødelagt JSON). Ret dem, før du bygger. Samme tjek kører automatisk på GitHub ved hvert push og hver pull request, og det fejler også, hvis de byggede sider ikke passer med data.

Åbn `index.html`, `sager/index.html` og en sagsside lokalt, og tjek, at de ser rigtige ud.

## 6. Send ændringen

Commit data og de byggede filer sammen (`README.md`, `index.html`, `data/`, `sager/`, `kilder/`) med en kort dansk overskrift, fx "Tilføj referat fra Børne- og Skoleudvalget 02-12-2026".

- Har du skriveadgang: lav en branch og en pull request med `gh pr create`.
- Ellers: fork repoet (`gh repo fork --remote`), push til din fork, og opret pull request mod `duemunk/nordvang-ejby`.

Skriv i pull requestens beskrivelse, hvilke sager der er tilføjet, flyttet eller rettet, med links.
