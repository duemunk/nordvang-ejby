# Instruktioner til GitHub Copilot

Repoet er en oversigt over politiske sager i Glostrup Kommune, der berører Nordvangskolen og afdeling Ejby. Skriv alt på dansk.

## Filer

- `README.md` er kilden til hele oversigten. Ret kun indhold her.
- `index.html` er GitHub Pages-siden. Den bygges med `python3 scripts/byg_side.py` og må aldrig redigeres i hånden.
- `scripts/hent_sager.py` henter skolerelevante punkter fra Åben Dagsorden (`https://dagsorden.glostrup.dk`).
- Den fulde arbejdsgang står i `.claude/skills/opdater-skolesager/SKILL.md`. Læs den, før du opdaterer oversigten, og følg den.

## Opdater oversigten (kort udgave)

1. Find datoen i linjen "Opdateret …" i `README.md`, og kør fra en uge før:
   `python3 scripts/hent_sager.py --fra DD/MM/ÅÅÅÅ`
2. Punkter markeret `[NY]` er ikke med endnu. Medtag dem, der påvirker skolerne – især Nordvang/Ejby: klasser og distrikter, kapacitet og bygninger, skoleveje, SFO, økonomi og takster, specialområdet, skolebestyrelser, befolkningsprognoser og byggeri i Ejby.
3. **Åben** = mødet har kun status *Dagsorden*, eller myndigheden under *Beslutningskompetence* har endnu ikke besluttet ("anbefales godkendt", "oversendes", "udsættes"). **Afgjort** = referat med beslutning fra den myndighed, der har kompetencen.
4. En sag står kun én gang, i sit seneste trin. Når en åben sag afgøres, flyttes rækken til Afgjorte sager med link til det afgørende møde.
5. Afsnit i fast rækkefølge: Kommende møder, Åbne sager, Afgjorte sager, Bidrag. Nyeste dato øverst i hver tabel.
6. Række-format: dato `DD-MM-ÅÅÅÅ` linket til mødet (`https://dagsorden.glostrup.dk/meeting/<id>`), sagstitel linket til punktet (`https://dagsorden.glostrup.dk/meeting/agendaitem/print/<a>/<b>`), "Kort" på højst ca. 20 ord med tal og enheder. Åbne sager har også kolonnen "Mangler".
7. Skriv kun fakta, der står i punktet. Alle kilder er links.
8. Opdatér datoen i "Opdateret …", kør `python3 scripts/byg_side.py`, og commit `README.md` og `index.html` sammen.

## Pull request

Titel og beskrivelse på dansk. Beskrivelsen lister de sager, der er tilføjet, flyttet eller rettet, med links til punkterne.

Kan `hent_sager.py` ikke nå `dagsorden.glostrup.dk` (firewall), så stop og skriv det i pull requesten i stedet for at gætte indhold.
