#!/usr/bin/env python3
"""Henter skolerelevante punkter fra Glostrup Kommunes Åben Dagsorden.

Brug:
    python3 scripts/hent_sager.py --fra 01/10/2026
    python3 scripts/hent_sager.py --fra 01/10/2026 --til 31/12/2026 --soeg Nordvang Ejby

Udskriver ét afsnit pr. punkt med mødedato, udvalg, mødestatus (Dagsorden/Referat),
links, beslutningskompetence og de beslutninger, der står i punktet. Punkter, hvis
link allerede står i README.md, markeres "kendt"; nye markeres "NY".

Kun standardbiblioteket bruges, så scriptet kører uden installation.
"""

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://dagsorden.glostrup.dk"
DEFAULT_TERMS = [
    "Nordvang", "Ejby", "skole", "skoler", "folkeskole", "SFO", "skoledistrikt",
    "skolevej", "klasse", "elever", "kvalitetsrapport", "inklusion", "specialklasse",
    "specialundervisning", "skolebestyrelse", "undervisning", "pavillon",
]
TITLE_FILTER = re.compile(
    r"Nordvang|Ejby|skole|SFO|klasse|special|Befolkningsprognose|budget|faglokale|"
    r"timebank|C-sporet|vikar|redegørelse|datarapportering|Børne- og Ungepolitik|"
    r"Orientering fra (administrationen|formanden)|bestyrelsesmøder|pavillon",
    re.IGNORECASE,
)
BODY_FILTER = re.compile(r"Nordvang|Ejby|skole|SFO", re.IGNORECASE)
GENERIC_TITLE = re.compile(r"Orientering fra (administrationen|formanden)|bestyrelsesmøder", re.IGNORECASE)


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "nordvang-ejby"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8")


def search(term, from_date, to_date):
    query = {"query": term, "fromDate": from_date}
    if to_date:
        query["toDate"] = to_date
    data = json.loads(get(f"{BASE}/rest/meeting/search?{urllib.parse.urlencode(query)}"))
    return data.get("meetings", [])


def strip_tags(fragment):
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</p>|</li>|</tr>|</h\d>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t\xa0]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def parse_items(meeting_html):
    parts = re.split(r'<button[^>]*agenda-item-btn[^>]*>', meeting_html)[1:]
    for part in parts:
        title_match = re.search(r'agenda-item-title">(.*?)</h3>', part, re.S)
        link_match = re.search(r'href="(/meeting/agendaitem/print/\d+/\d+)"', part)
        if not title_match or not link_match:
            continue
        yield strip_tags(title_match.group(1)), BASE + link_match.group(1), strip_tags(part)


def extract(body, label, length=300):
    match = re.search(label + r"\s*:?\s*(.{0,%d})" % length, body, re.S)
    return match.group(1).split("\n")[0].strip() if match else ""


def decisions(body):
    found = re.findall(r"(Beslutning i [^\n]*? den \d{2}-\d{2}-\d{4})\s*\n?(.*?)(?=Beslutning i |Resumé|Bilag|$)", body, re.S)
    return [(head.strip(), " ".join(text.split())[:600]) for head, text in found]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fra", required=True, help="Startdato, dd/mm/åååå")
    parser.add_argument("--til", help="Slutdato, dd/mm/åååå")
    parser.add_argument("--soeg", nargs="*", default=DEFAULT_TERMS, help="Søgeord")
    args = parser.parse_args()

    readme = Path(__file__).resolve().parent.parent / "README.md"
    known = readme.read_text(encoding="utf-8") if readme.exists() else ""

    meetings = {}
    for term in args.soeg:
        for meeting in search(term, args.fra, args.til):
            meetings.setdefault(meeting["meetingId"], meeting)

    for meeting_id, meeting in sorted(meetings.items(), key=lambda kv: kv[1]["date"], reverse=True):
        meeting_html = get(f"{BASE}/fragments/meeting/{meeting_id}/view")
        meeting_link = f"{BASE}/meeting/{meeting_id}"
        date = meeting["date"][:10]
        dd_mm_yyyy = f"{date[8:10]}-{date[5:7]}-{date[0:4]}"
        for title, item_link, body in parse_items(meeting_html):
            if not TITLE_FILTER.search(title):
                continue
            if GENERIC_TITLE.search(title) and not BODY_FILTER.search(body):
                continue
            path = item_link.replace(BASE, "")
            state = "kendt" if path in known else "NY"
            print(f"## [{state}] {dd_mm_yyyy} · {meeting['committeeGroupName']} · {title}")
            print(f"- Mødestatus: {meeting['status']}")
            print(f"- Møde: {meeting_link}")
            print(f"- Punkt: {item_link}")
            competence = extract(body, "Beslutningskompetence", 80)
            if competence:
                print(f"- Beslutningskompetence: {competence}")
            for head, text in decisions(body):
                print(f"- {head}: {text}")
            summary = extract(body, "Resumé", 400)
            if summary:
                print(f"- Resumé: {summary}")
            print()


if __name__ == "__main__":
    sys.exit(main())
