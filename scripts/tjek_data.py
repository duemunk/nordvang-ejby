#!/usr/bin/env python3
"""Tjekker data/sager.json, data/principper.json og data/links.json, før siderne bygges.

Brug:
    python3 scripts/tjek_data.py

Skriver hver fejl på dansk med sag og felt, og afslutter med kode 1, hvis der er fejl.
Kører også automatisk på GitHub ved hvert push og hver pull request.
"""

import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUSES = {"åben", "afgjort"}
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def is_date(value):
    try:
        datetime.date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))


def is_url(value):
    return isinstance(value, str) and value.startswith("https://")


def load(name, errors):
    path = ROOT / "data" / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        errors.append(f"data/{name}, linje {error.lineno}, kolonne {error.colno}: ugyldig JSON ({error.msg}). Tjek kommaer og anførselstegn.")
        return None


def validate_cases(data, errors):
    first_last = data.get("referater_fra_til")
    if not (isinstance(first_last, list) and len(first_last) == 2 and all(is_date(d) for d in first_last)):
        errors.append('"referater_fra_til" skal være to datoer som ["ÅÅÅÅ-MM-DD", "ÅÅÅÅ-MM-DD"].')
    if not is_date(data.get("opdateret")):
        errors.append('"opdateret" skal være en dato som "ÅÅÅÅ-MM-DD".')
    slugs = {topic.get("slug") for topic in data.get("temaer", [])}
    seen_ids = set()
    for index, case in enumerate(data.get("sager", []), start=1):
        case_id = case.get("id") or f"sag nr. {index}"
        where = f"Sag {case_id}"
        if not isinstance(case.get("id"), str) or not ID_PATTERN.match(case["id"]):
            errors.append(f'{where}: "id" må kun indeholde små bogstaver, tal og bindestreg.')
        elif case["id"] in seen_ids:
            errors.append(f'{where}: "id" findes allerede.')
        seen_ids.add(case.get("id"))
        if case.get("status") not in STATUSES:
            errors.append(f'{where}: "status" er "{case.get("status")}", men skal være "åben" eller "afgjort".')
        if case.get("topic") not in slugs:
            errors.append(f'{where}: "topic" er "{case.get("topic")}", men skal være et af: {", ".join(sorted(slugs))}.')
        for field in ("t", "lead"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                errors.append(f'{where}: "{field}" mangler.')
        events = case.get("events")
        if not isinstance(events, list) or not events:
            errors.append(f'{where}: "events" skal være en liste med mindst én hændelse.')
            continue
        for number, event in enumerate(events, start=1):
            at = f"{where}, hændelse {number}"
            if not is_date(event.get("d")):
                errors.append(f'{at}: "d" er "{event.get("d")}", men skal være en dato som "ÅÅÅÅ-MM-DD".')
            for field in ("src", "kind", "t", "x"):
                if not isinstance(event.get(field), str) or not event[field].strip():
                    errors.append(f'{at}: "{field}" mangler.')
            links = event.get("links")
            if not isinstance(links, list) or not links:
                errors.append(f'{at}: "links" skal have mindst ét link som ["Tekst", "https://…"].')
                continue
            for link in links:
                if not (isinstance(link, list) and len(link) == 2 and isinstance(link[0], str) and is_url(link[1])):
                    errors.append(f'{at}: linket {json.dumps(link, ensure_ascii=False)} skal være ["Tekst", "https://…"].')


def validate_links(groups, errors):
    for group in groups:
        name = group.get("group", "?")
        for link in group.get("links", []):
            if not isinstance(link.get("title"), str) or not is_url(link.get("url")):
                errors.append(f'data/links.json, gruppe "{name}": hvert link skal have "title" og en "url", der starter med https://.')


PRINCIPLE_STATUSES = {"vedtaget", "under arbejde", "gældende", "udkast", "mangler"}


def validate_principles(data, errors):
    if not is_url(data.get("mappe")):
        errors.append('data/principper.json: "mappe" skal være et link, der starter med https://.')
    for link in data.get("krav", []):
        if not (isinstance(link, list) and len(link) == 2 and isinstance(link[0], str) and is_url(link[1])):
            errors.append('data/principper.json: hvert link i "krav" skal være ["tekst", "https://…"].')
    for principle in data.get("principper", []):
        name = principle.get("t", "?")
        if not isinstance(principle.get("t"), str) or not isinstance(principle.get("x"), str):
            errors.append(f'data/principper.json, "{name}": skal have "t" og "x".')
        if principle.get("status") not in PRINCIPLE_STATUSES:
            errors.append(f'data/principper.json, "{name}": "status" skal være en af {", ".join(sorted(PRINCIPLE_STATUSES))}.')
        if principle.get("dato") is not None and not is_date(principle.get("dato")):
            errors.append(f'data/principper.json, "{name}": "dato" skal være ÅÅÅÅ-MM-DD eller null.')
        for link in principle.get("grundlag", []):
            if not (isinstance(link, list) and len(link) == 2 and isinstance(link[0], str) and is_url(link[1])):
                errors.append(f'data/principper.json, "{name}": hvert link i "grundlag" skal være ["tekst", "https://…"].')
        if principle.get("status") == "udkast" and principle.get("links"):
            errors.append(f'data/principper.json, "{name}": udkast må ikke have links.')
        for link in principle.get("links", []):
            if not (isinstance(link, list) and len(link) == 2 and isinstance(link[0], str) and is_url(link[1])):
                errors.append(f'data/principper.json, "{name}": hvert link skal være ["tekst", "https://…"].')


def main():
    errors = []
    cases = load("sager.json", errors)
    links = load("links.json", errors)
    principles = load("principper.json", errors)
    if cases is not None:
        validate_cases(cases, errors)
    if links is not None:
        validate_links(links, errors)
    if principles is not None:
        validate_principles(principles, errors)
    if errors:
        print(f"{len(errors)} fejl i data:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Data er i orden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
