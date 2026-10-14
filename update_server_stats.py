#!/usr/bin/env python3
"""
Daily data refresh for the Server Dashboard + Event Calendar (run by GitHub Actions).

Sources
  - cpt-hedge.com/servers : every server's creation date, current season / week and the
    real start timestamp of each season (the list ships inside one of the page's JS chunks).
  - activeplayer.io       : player-count estimates (refreshed by them ~monthly).

Writes
  guides/server_stats.json    - global player stats + server landscape (dashboard "Global" panel)
  guides/server_seasons.json  - per-server creation + season starts + typical season lengths
                                (dashboard + calendar compute season/day from this, any server)
  guides/lastwar_calendar.ics - Server #2013 calendar with REAL season dates
                                (events + weekly schedule from guides/calendar_data.json)

A failed source never wipes good data: the previous file values are kept.
"""

import html as htmllib
import json
import re
import statistics
import sys
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen

STATS_FILE = "guides/server_stats.json"
SEASONS_FILE = "guides/server_seasons.json"
CAL_DATA_FILE = "guides/calendar_data.json"
ICS_FILE = "guides/lastwar_calendar.ics"
TRACKED_SERVER = "2013"
RESET_UTC_HOUR = 2          # cpt-hedge day boundary (server reset 02:00 UTC)
DAY_MS = 86_400_000
UA = {"User-Agent": "Mozilla/5.0 (RGBB SKYNET stats bot; +https://extremesecrecy.github.io/lastwar-research-trees/)"}


def fetch(url):
    with urlopen(Request(url, headers=UA), timeout=45) as r:
        return r.read().decode("utf-8", errors="ignore")


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


# ───────────────────────── ActivePlayer ─────────────────────────
def page_text(raw):
    """HTML -> ' | '-joined visible text lines (stable to parse, layout-agnostic)."""
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    t = htmllib.unescape(re.sub(r"<[^>]+>", "\n", t))
    return " | ".join(l.strip() for l in t.split("\n") if l.strip())


def scrape_activeplayer():
    j = page_text(fetch("https://activeplayer.io/last-war-survival/"))
    out = {}

    def block(store):
        m = re.search(store + r" Player Statistics \| Current Players \| (.*?) \| Daily Active Users \| (.*?) \| "
                      r"Monthly Active Users \| (.*?) \| Downloads \| (.*?) \|", j)
        return m.groups() if m else None

    gp, ap = block("Google Play"), block("App Store")
    if not gp or not ap:
        raise ValueError("platform blocks not found (page layout changed?)")
    out["current"] = {"android": gp[0], "ios": ap[0]}
    out["dau"] = {"android": gp[1], "ios": ap[1]}
    out["mau"] = {"android": gp[2], "ios": ap[2]}
    out["dl"] = {"googlePlay": gp[3], "appStore": ap[3]}

    m = re.search(r"approximately ([\d.]+[MK]) monthly active users across both", j)
    out["mau_combined"] = m.group(1) if m else None
    m = re.search(r"Google Play Engagement \| ([\d.]+%) \| App Store Engagement \| ([\d.]+%)", j)
    out["eng"] = m.groups() if m else (None, None)
    m = re.search(r"Peak player count was ([\d.]+[MK]) in (\w+ \d{4}), current count is ([\d.]+%) of that peak", j)
    out["peak"] = m.groups() if m else None
    m = re.search(r"Growth Metrics \| ([+\-−]?[\d.]+%) \| Avg Monthly Growth", j)
    out["avg_growth"] = m.group(1) if m else None
    m = re.search(r"(?:Store data last refreshed|Data last updated): ([A-Z][a-z]+ \d{1,2}, \d{4})", j)
    out["as_of"] = m.group(1) if m else None

    trends = []
    m = re.search(r"Monthly Player Trends \| Google Play \| Month \| Estimated Players \| Change \| % Change \| Data Points \| (.*)", j)
    if m:
        for mo, players, _chg, pct in re.findall(
                r"((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{4}) \| "
                r"([\d.]+[MK]) \| ([+\-][\d.,]+[MK]?|-) \| ([+\-][\d.]+%|-)", m.group(1))[:4]:
            trends.append({"month": mo, "players": players, "change": pct,
                           "direction": "up" if pct.startswith("+") else "down"})
    out["trends"] = trends
    return out


def rng(s):
    """'1.5M - 2.5M' -> (1.5e6, 2.5e6)"""
    v = [float(n) * {"M": 1e6, "K": 1e3, "B": 1e9}.get(u, 1)
         for n, u in re.findall(r"([\d.]+)\s*([MKB]?)", (s or "").replace(",", ""))]
    return v


def fmt_m(x):
    return f"{x / 1e6:.1f}M" if x >= 1e6 else f"{x / 1e3:.0f}K"


# ───────────────────────── cpt-hedge ─────────────────────────
def scrape_cpthedge_servers():
    """Return the raw server list cpt-hedge bundles into its /servers page JS."""
    page = fetch("https://cpt-hedge.com/servers")
    chunks = sorted(set(re.findall(r'/_next/static/chunks/[^"\'?]+\.js', page)))
    for path in chunks:
        js = fetch("https://cpt-hedge.com" + path)
        i = js.find('[{"id":"')
        if i >= 0 and '"seasonStartTimestamps"' in js:
            data, _ = json.JSONDecoder().raw_decode(js[i:])
            if len(data) > 100:
                return data
    raise ValueError("server list chunk not found (site changed?)")


def game_day_index(ms):
    """Days since epoch on the game calendar (day flips at RESET_UTC_HOUR UTC)."""
    return (int(ms) - RESET_UTC_HOUR * 3_600_000) // DAY_MS


def build_seasons(servers, now_ms):
    gaps = {}
    for d in servers:
        t = d.get("seasonStartTimestamps") or {}
        prev = int(d["timestamp"])
        for k in range(1, 10):
            v = t.get(f"s{k}")
            if not v:
                break
            gaps.setdefault(k, []).append((int(v) - prev) / DAY_MS)
            prev = int(v)
    cadence = {str(k): round(statistics.median(v)) for k, v in sorted(gaps.items()) if len(v) >= 20}

    compact = {}
    for d in servers:
        sid = d["id"]
        compact[sid] = {
            "c": int(d["timestamp"]),
            "s": {k[1:]: int(v) for k, v in (d.get("seasonStartTimestamps") or {}).items()},
            "cs": d.get("currentSeason"), "ps": bool(d.get("isPostSeason")), "wk": d.get("currentWeek"),
            "r": d.get("region") or [],
        }
    today = game_day_index(now_ms)
    ages = {sid: today - game_day_index(v["c"]) + 1 for sid, v in compact.items()}
    numeric = [s for s in compact if s.isdigit()]
    newest = max(numeric, key=int)
    oldest = max(compact, key=lambda s: ages[s])
    landscape = {
        "totalServers": f"{len(compact):,}",
        "newest": f"#{newest} (Day {ages[newest]})",
        "oldest": f"#{oldest} (Day {ages[oldest]})",
    }
    seasons = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "https://cpt-hedge.com/servers",
        "sourceUpdatedAt": max(int(d.get("updatedAt") or 0) for d in servers),
        "resetUtcHour": RESET_UTC_HOUR,
        "cadenceDays": cadence,   # "k": median days from season k-1 start (or creation) to season k start
        "servers": compact,
    }
    return seasons, landscape


def season_starts(entry, cadence, upto=8):
    """Game-day index of each season start: real where known, else estimated from cadence.
    Returns {season: (dayIndex, estimated_bool)}; season 0 = server creation."""
    out = {0: (game_day_index(entry["c"]), False)}
    for k in range(1, upto + 1):
        real = entry["s"].get(str(k))
        if real:
            out[k] = (game_day_index(real), False)
        else:
            out[k] = (out[k - 1][0] + int(cadence.get(str(k), cadence.get(str(k - 1), 112))), True)
    return out


def event_day_index(evt, starts):
    s = evt["season"]
    return starts[s][0] + max(int(evt["day"]), 1) - 1


# ───────────────────────── ICS (Server #2013) ─────────────────────────
def build_ics(cal, starts, reset_hour=18):
    """Same layout as build_calendar.py's ICS, but dated from REAL season starts."""
    epoch = datetime(1970, 1, 1)
    d_of = lambda idx: epoch + timedelta(days=idx)
    created = d_of(starts[0][0])
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//RGBB SKYNET//Last War Calendar//EN",
         "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:Last War - Server #2013 Events",
         "X-WR-TIMEZONE:UTC"]
    uid = 0
    dow_map = {0: "SU", 1: "MO", 2: "TU", 3: "WE", 4: "TH", 5: "FR", 6: "SA"}
    for sch in cal["weekly"]:
        if sch["vp"] == 0:
            continue
        first = created + timedelta(days=((sch["dow"] - 1) % 7 - created.weekday()) % 7)
        todo = "\\n".join("DO: " + t for t in sch["whatToDo"])
        save = "\\n".join("SAVE: " + t for t in sch["whatToSave"])
        uid += 1
        L += ["BEGIN:VEVENT", f"UID:rgbb-weekly-{uid}@lastwar",
              f"DTSTART:{first:%Y%m%d}T{reset_hour:02d}0000", "DURATION:PT2H",
              f"RRULE:FREQ=WEEKLY;BYDAY={dow_map[sch['dow']]}",
              f"SUMMARY:{sch['vsDuel']} ({sch['vp']}VP {chr(9733) * sch['vp']})",
              f"DESCRIPTION:Arms Race: {sch['armsRace']}\\nVS Duel: {sch['vsDuel']}\\nVP: {sch['vp']}\\n\\n{todo}\\n\\n{save}",
              "END:VEVENT"]
    for evt in cal["timeline"]:
        s = evt["season"]
        day = d_of(event_day_index(evt, starts))
        est = starts[s][1]
        uid += 1
        prefix = f"S{s}: " if s > 0 and not evt["name"].startswith(f"S{s}:") else ""
        summary = prefix + evt["name"] + (" (est. date)" if est else "")
        desc = (evt.get("details") or "").replace("\n", "\\n")
        if est:
            desc += "\\n\\nDate ESTIMATED - Season %d start not announced yet; updates automatically daily." % s
        L += ["BEGIN:VEVENT", f"UID:rgbb-event-{uid}@lastwar", f"DTSTART;VALUE=DATE:{day:%Y%m%d}",
              f"SUMMARY:{summary}", f"DESCRIPTION:{desc}", f"CATEGORIES:{evt['type'].upper()}"]
        if evt["type"] == "hero":
            L += ["BEGIN:VALARM", "TRIGGER:-P1D", "ACTION:DISPLAY", f"DESCRIPTION:Tomorrow: {summary}", "END:VALARM"]
        L.append("END:VEVENT")
    L.append("END:VCALENDAR")
    return "\r\n".join(L) + "\r\n"


# ───────────────────────── main ─────────────────────────
def main():
    existing = load_json(STATS_FILE) or {}
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    ok = True

    print("cpt-hedge server list ...")
    seasons, landscape = None, None
    try:
        servers = scrape_cpthedge_servers()
        seasons, landscape = build_seasons(servers, now_ms)
        with open(SEASONS_FILE, "w", encoding="utf-8") as f:
            json.dump(seasons, f, separators=(",", ":"))
        tr = seasons["servers"].get(TRACKED_SERVER, {})
        print(f"  {landscape['totalServers']} servers; newest {landscape['newest']}; oldest {landscape['oldest']}")
        print(f"  #{TRACKED_SERVER}: season {tr.get('cs')} post={tr.get('ps')} week={tr.get('wk')} starts={tr.get('s')}")
        print(f"  cadence (days): {seasons['cadenceDays']}")
    except Exception as e:
        ok = False
        print(f"  ERROR: {e} -> keeping previous {SEASONS_FILE}")
        seasons = load_json(SEASONS_FILE)

    print("ActivePlayer ...")
    try:
        ap = scrape_activeplayer()
        print(f"  DAU {ap['dau']}  MAU {ap['mau']}  as of {ap['as_of']}")
    except Exception as e:
        ok = False
        print(f"  ERROR: {e} -> keeping previous player stats")
        ap = None

    result = dict(existing)
    result["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result["sources"] = {"playerStats": "https://activeplayer.io/last-war-survival/",
                         "serverData": "https://cpt-hedge.com/servers"}
    if ap:
        da, di = rng(ap["dau"]["android"]), rng(ap["dau"]["ios"])
        ma, mi = rng(ap["mau"]["android"]), rng(ap["mau"]["ios"])
        share = "--"
        if len(da) == 2 and len(di) == 2 and sum(di):
            share = f"{sum(da) / sum(di):.1f}x"
        combined = ap["mau_combined"] and "~" + ap["mau_combined"]
        if not combined and len(ma) == 2 and len(mi) == 2:
            combined = "~" + fmt_m((sum(ma) + sum(mi)) / 2)
        dl_total = "--"
        g, a = rng(ap["dl"]["googlePlay"]), rng(ap["dl"]["appStore"])
        if g and a:
            dl_total = "~" + fmt_m(g[0] + a[0]) + "+"
        result["playerStatsAsOf"] = ap["as_of"]
        result["monthlyActivePlayers"] = {"combined": combined or "--", "android": ap["mau"]["android"], "ios": ap["mau"]["ios"]}
        result["dailyActivePlayers"] = {"android": ap["dau"]["android"], "ios": ap["dau"]["ios"], "androidShare": share}
        result["currentPlayers"] = ap["current"]
        result["downloads"] = {"googlePlay": ap["dl"]["googlePlay"], "appStore": ap["dl"]["appStore"], "total": dl_total}
        if ap["trends"]:
            result["monthlyTrend"] = ap["trends"]
        pk = ap["peak"]
        result["engagement"] = {
            "androidRate": ap["eng"][0] or "--", "iosRate": ap["eng"][1] or "--",
            "avgMonthlyGrowth": ap["avg_growth"] or "--",
            "peak": f"{pk[0]} ({pk[1]})" if pk else "--",
            "pctOfPeak": pk[2] if pk else "--",
        }
    if landscape:
        result["serverLandscape"] = landscape
    if seasons and TRACKED_SERVER in seasons["servers"]:
        e = seasons["servers"][TRACKED_SERVER]
        st = season_starts(e, seasons["cadenceDays"])
        today = game_day_index(now_ms)
        cur = max(k for k in st if not st[k][1] and st[k][0] <= today)
        nxt = cur + 1
        result["trackedServer"] = {
            "id": TRACKED_SERVER, "season": cur, "seasonDay": today - st[cur][0] + 1,
            "serverDay": today - st[0][0] + 1, "postSeason": e["ps"], "week": e["wk"],
            "nextSeason": nxt, "nextSeasonStart": (datetime(1970, 1, 1) + timedelta(days=st[nxt][0])).strftime("%Y-%m-%d"),
            "nextSeasonEstimated": st[nxt][1],
        }
        print(f"  #{TRACKED_SERVER} today: {result['trackedServer']}")

        cal = load_json(CAL_DATA_FILE)
        if cal:
            with open(ICS_FILE, "w", encoding="utf-8", newline="") as f:
                f.write(build_ics(cal, st))
            print(f"  wrote {ICS_FILE} ({len(cal['timeline'])} events)")
        else:
            print(f"  {CAL_DATA_FILE} missing -> ICS not regenerated")

    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Wrote {STATS_FILE} ({result['lastUpdated']}){'' if ok else '  [some sources failed - kept previous values]'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
