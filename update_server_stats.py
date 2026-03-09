#!/usr/bin/env python3
"""
Scrapes ActivePlayer.io and cpt-hedge.com for Last War server stats.
Writes results to guides/server_stats.json.
Run weekly via GitHub Actions or manually.
"""

import json
import re
import sys
from datetime import datetime, timezone
from urllib.request import urlopen, Request

STATS_FILE = "guides/server_stats.json"


def fetch_url(url):
    """Fetch URL content as string."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (OWOW SKYNET Stats Bot)"})
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def scrape_activeplayer():
    """Scrape player stats from ActivePlayer.io."""
    html = fetch_url("https://activeplayer.io/last-war-survival/")

    stats = {}

    # Helper: find number patterns near labels
    def find_stat(pattern, text=html):
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else None

    # Monthly active players - look for patterns like "4.5M - 7.5M"
    # The page has structured data we can parse
    android_mau = find_stat(r"Android.*?Monthly Active.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")
    ios_mau = find_stat(r"iOS.*?Monthly Active.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")

    # Try alternate patterns - ActivePlayer uses various layouts
    if not android_mau:
        android_mau = find_stat(r"Monthly Active.*?Android.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")
    if not ios_mau:
        ios_mau = find_stat(r"Monthly Active.*?iOS.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")

    # Daily active
    android_dau = find_stat(r"Daily Active.*?Android.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")
    if not android_dau:
        android_dau = find_stat(r"Android.*?Daily Active.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")
    ios_dau = find_stat(r"Daily Active.*?iOS.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")
    if not ios_dau:
        ios_dau = find_stat(r"iOS.*?Daily Active.*?>([\d.]+[MK]\s*-\s*[\d.]+[MK])<")

    # Downloads
    gplay_dl = find_stat(r"Google Play.*?Downloads.*?>([\d.]+[MBK+]+)<")
    if not gplay_dl:
        gplay_dl = find_stat(r"Downloads.*?>([\d,]+[+]?)<.*?Google")
    appstore_dl = find_stat(r"App Store.*?Downloads.*?>([\d.]+[MBK+]+)<")
    if not appstore_dl:
        appstore_dl = find_stat(r"Downloads.*?>([\d.]+[MBK+]+)<.*?App Store")

    # Monthly trend - look for month/player/change rows
    trend_pattern = r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4})\s*(?:\(peak\))?\s*</.*?>([\d.]+[MK])<.*?([-+][\d.]+%)"
    trends = re.findall(trend_pattern, html, re.DOTALL)

    # Engagement
    android_eng = find_stat(r"Android.*?[Ee]ngagement.*?>([\d.]+%)<")
    if not android_eng:
        android_eng = find_stat(r"[Ee]ngagement.*?Android.*?>([\d.]+%)<")
    ios_eng = find_stat(r"iOS.*?[Ee]ngagement.*?>([\d.]+%)<")
    if not ios_eng:
        ios_eng = find_stat(r"[Ee]ngagement.*?iOS.*?>([\d.]+%)<")

    yoy = find_stat(r"[Yy]ear.over.[Yy]ear.*?>([-+][\d.]+%)<")
    vs_peak = find_stat(r"peak.*?>([\d.]+%)<")

    return {
        "mau_android": android_mau,
        "mau_ios": ios_mau,
        "dau_android": android_dau,
        "dau_ios": ios_dau,
        "dl_gplay": gplay_dl,
        "dl_appstore": appstore_dl,
        "trends": trends,
        "eng_android": android_eng,
        "eng_ios": ios_eng,
        "yoy": yoy,
        "vs_peak": vs_peak,
    }


def scrape_cpthedge():
    """Scrape server landscape from cpt-hedge.com."""
    html = fetch_url("https://cpt-hedge.com/servers")

    stats = {}

    # Total servers - look in the RSC flight data or rendered HTML
    total = re.search(r"Total Servers.*?(\d[\d,]+)", html, re.DOTALL)
    if total:
        stats["totalServers"] = total.group(1)

    # Newest server
    newest = re.search(r"Newest Server.*?((?:State)?#\d+.*?Day \d+)", html, re.DOTALL)
    if not newest:
        newest = re.search(r"(State#\d+)\s*\(Day\s*(\d+)\)", html)
    if newest:
        stats["newest"] = newest.group(1) if "Day" in newest.group(1) else f"{newest.group(1)} (Day {newest.group(2)})"

    # Oldest server
    oldest = re.search(r"Oldest Server.*?((?:State)?#\d+.*?Day \d+)", html, re.DOTALL)
    if oldest:
        stats["oldest"] = oldest.group(1)

    # Also try parsing from self.__next_f.push RSC data
    if not stats.get("totalServers"):
        rsc_total = re.search(r'"2194"|"(\d{3,5})".*?[Tt]otal', html)
        if rsc_total:
            stats["totalServers"] = rsc_total.group(1) or "2194"

    return stats


def load_existing():
    """Load existing stats file as fallback."""
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def main():
    print("Fetching ActivePlayer.io stats...")
    try:
        ap = scrape_activeplayer()
        print(f"  MAU Android: {ap.get('mau_android', 'N/A')}")
        print(f"  MAU iOS: {ap.get('mau_ios', 'N/A')}")
        print(f"  Trends found: {len(ap.get('trends', []))}")
    except Exception as e:
        print(f"  ERROR: {e}")
        ap = {}

    print("Fetching cpt-hedge.com server data...")
    try:
        ch = scrape_cpthedge()
        print(f"  Total servers: {ch.get('totalServers', 'N/A')}")
        print(f"  Newest: {ch.get('newest', 'N/A')}")
        print(f"  Oldest: {ch.get('oldest', 'N/A')}")
    except Exception as e:
        print(f"  ERROR: {e}")
        ch = {}

    # Load existing as fallback for any missing fields
    existing = load_existing()

    def val(new, fallback_path):
        """Use new value if available, otherwise keep existing."""
        if new:
            return new
        if existing:
            keys = fallback_path.split(".")
            obj = existing
            for k in keys:
                obj = obj.get(k, {}) if isinstance(obj, dict) else {}
            return obj if obj else "--"
        return "--"

    # Compute combined MAU
    combined = "--"
    if ap.get("mau_android") and ap.get("mau_ios"):
        try:
            # Parse ranges like "4.5M - 7.5M" and "3.5M - 6.1M" -> sum midpoints
            def parse_range(s):
                nums = re.findall(r"([\d.]+)([MK])", s)
                vals = []
                for n, unit in nums:
                    v = float(n) * (1_000_000 if unit == "M" else 1_000)
                    vals.append(v)
                return vals
            a_range = parse_range(ap["mau_android"])
            i_range = parse_range(ap["mau_ios"])
            if len(a_range) >= 2 and len(i_range) >= 2:
                low = (a_range[0] + i_range[0]) / 1_000_000
                high = (a_range[1] + i_range[1]) / 1_000_000
                combined = f"~{(low + high) / 2:.1f}M"
        except Exception:
            pass

    # Compute android share
    android_share = "--"
    if ap.get("dau_android") and ap.get("dau_ios"):
        try:
            def midpoint(s):
                nums = re.findall(r"([\d.]+)([MK])", s)
                vals = [float(n) * (1_000_000 if u == "M" else 1_000) for n, u in nums]
                return sum(vals) / len(vals) if vals else 0
            a_mid = midpoint(ap["dau_android"])
            i_mid = midpoint(ap["dau_ios"])
            if i_mid > 0:
                ratio = a_mid / i_mid
                android_share = f"{ratio:.1f}x more"
        except Exception:
            pass

    # Build trends
    trend_list = []
    if ap.get("trends"):
        for month, players, change in ap["trends"][:4]:
            direction = "up" if change.startswith("+") else "down"
            trend_list.append({"month": month, "players": players, "change": change, "direction": direction})

    # Build total downloads
    dl_total = "--"
    if ap.get("dl_gplay") and ap.get("dl_appstore"):
        dl_total = f"~{ap['dl_gplay']} + {ap['dl_appstore']}"
        # Try to sum
        try:
            def parse_dl(s):
                m = re.search(r"([\d.]+)([MBK])", s)
                if m:
                    return float(m.group(1)) * (1_000_000 if m.group(2) == "M" else 1)
                return 0
            t = parse_dl(ap["dl_gplay"]) + parse_dl(ap["dl_appstore"])
            dl_total = f"~{t / 1_000_000:.0f}M+"
        except Exception:
            pass

    # Assemble final JSON
    result = {
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "sources": {
            "playerStats": "https://activeplayer.io/last-war-survival/",
            "serverData": "https://cpt-hedge.com/servers",
        },
        "monthlyActivePlayers": {
            "combined": combined if combined != "--" else val(None, "monthlyActivePlayers.combined"),
            "android": ap.get("mau_android") or val(None, "monthlyActivePlayers.android"),
            "ios": ap.get("mau_ios") or val(None, "monthlyActivePlayers.ios"),
        },
        "dailyActivePlayers": {
            "android": ap.get("dau_android") or val(None, "dailyActivePlayers.android"),
            "ios": ap.get("dau_ios") or val(None, "dailyActivePlayers.ios"),
            "androidShare": android_share if android_share != "--" else val(None, "dailyActivePlayers.androidShare"),
        },
        "downloads": {
            "googlePlay": ap.get("dl_gplay") or val(None, "downloads.googlePlay"),
            "appStore": ap.get("dl_appstore") or val(None, "downloads.appStore"),
            "total": dl_total if dl_total != "--" else val(None, "downloads.total"),
        },
        "monthlyTrend": trend_list if trend_list else (existing or {}).get("monthlyTrend", []),
        "serverLandscape": {
            "totalServers": ch.get("totalServers") or val(None, "serverLandscape.totalServers"),
            "newest": ch.get("newest") or val(None, "serverLandscape.newest"),
            "oldest": ch.get("oldest") or val(None, "serverLandscape.oldest"),
        },
        "engagement": {
            "androidRate": ap.get("eng_android") or val(None, "engagement.androidRate"),
            "iosRate": ap.get("eng_ios") or val(None, "engagement.iosRate"),
            "yoyGrowth": ap.get("yoy") or val(None, "engagement.yoyGrowth"),
            "vsPeak": ap.get("vs_peak") or val(None, "engagement.vsPeak"),
        },
    }

    with open(STATS_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nWrote {STATS_FILE} (updated {result['lastUpdated']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
