import json, re, html, urllib.request, urllib.parse
BASE = "https://dagsorden.glostrup.dk"
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "glostrup-skolesager"}), timeout=60).read().decode("utf-8")
meetings = {}
for q in ["høringssvar", "høring", "skolebestyrelse", "skolebestyrelserne", "Nordvang", "Ejby"]:
    r = json.loads(get(f"{BASE}/rest/meeting/search?" + urllib.parse.urlencode({"query": q, "fromDate": "01/08/2024"})))
    for m in r["meetings"]:
        meetings.setdefault(m["meetingId"], m)
out = []
for mid, m in sorted(meetings.items(), key=lambda kv: kv[1]["date"]):
    h = get(f"{BASE}/fragments/meeting/{mid}/view")
    for part in re.split(r'<button[^>]*agenda-item-btn[^>]*>', h)[1:]:
        t = re.search(r'agenda-item-title">(.*?)</h3>', part, re.S)
        link = re.search(r'href="(/meeting/agendaitem/print/\d+/\d+)"', part)
        for href, text in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', part, re.S):
            text = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()
            if re.search(r"høring", text, re.I) and re.search(r"\bNO\b|NO[._ -]?EJ|Nordvang|Ejby|SB_NO", text, re.I):
                out.append({"date": m["date"][:10], "committee": m["committeeGroupName"], "status": m["status"],
                            "item": html.unescape(re.sub(r"<[^>]+>", "", t.group(1))).strip() if t else "",
                            "item_url": BASE + link.group(1) if link else "", "bilag": text,
                            "bilag_url": href if href.startswith("http") else BASE + href})
pass
for o in out: print(o["date"], "|", o["committee"], "|", o["item"], "|", o["bilag"], "|", o["bilag_url"])
