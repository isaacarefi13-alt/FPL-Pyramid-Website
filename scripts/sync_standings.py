#!/usr/bin/env python3
"""Synchronize 2026/27 standings from FPL Draft, preserving historical records.

Uses the public, unofficial Draft API. Fail closed: all three leagues must
validate before either output file is changed. Does not modify all-time,
derbies, cups, or completed historical seasons.
"""
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LEAGUES = {"FPL1": 28811, "FPL2": 16233, "FPL3": 26756}
SEASON = "2026/27"

def fetch(division, league_id):
    url = f"https://draft.premierleague.com/api/league/{league_id}/details"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 FPL-Pyramid-Sync/1.0",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.load(response)
    if not isinstance(data, dict):
        raise ValueError(f"{division}: unexpected response type")
    league = data.get("league") or {}
    entries = data.get("league_entries") or []
    standings = data.get("standings") or []
    if str(league.get("name", "")).strip().upper() != division:
        raise ValueError(f"{division}: wrong league name {league.get('name')!r}")
    if len(entries) != 10 or len(standings) != 10:
        raise ValueError(f"{division}: expected 10 entries/standings, got {len(entries)}/{len(standings)}")
    by_id = {int(e["id"]): e for e in entries}
    if len(by_id) != 10:
        raise ValueError(f"{division}: duplicate entry identifiers")
    rows = []
    for st in standings:
        entry_id = int(st["league_entry"])
        if entry_id not in by_id:
            raise ValueError(f"{division}: unmatched entry {entry_id}")
        e = by_id[entry_id]
        w, d, l = (int(st[k]) for k in ("matches_won", "matches_drawn", "matches_lost"))
        played = int(st["matches_played"])
        if w + d + l != played:
            raise ValueError(f"{division}: inconsistent W-D-L for {entry_id}")
        rank = int(st["rank"])
        if not 1 <= rank <= 10:
            raise ValueError(f"{division}: invalid rank {rank}")
        sf, sa = int(st["points_for"]), int(st["points_against"])
        manager = " ".join(str(e.get(k) or "").strip() for k in ("player_first_name", "player_last_name")).strip()
        if not manager:
            raise ValueError(f"{division}: missing manager name")
        rows.append({
            "season": SEASON, "division": division, "rank": rank,
            "team": str(e.get("entry_name") or e.get("short_name") or "").strip(),
            "manager": manager, "w": w, "d": d, "l": l,
            "pts": int(st["total"]), "sf": sf, "sa": sa, "sd": sf - sa,
        })
    if len({r["rank"] for r in rows}) != 10:
        raise ValueError(f"{division}: duplicate ranks")
    return sorted(rows, key=lambda r: r["rank"])

def main():
    current = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
    rows = []
    for division, league_id in LEAGUES.items():
        league_rows = fetch(division, league_id)
        rows.extend(league_rows)
        print(f"{division}: {len(league_rows)} rows; games played range {min(x['w']+x['d']+x['l'] for x in league_rows)}-{max(x['w']+x['d']+x['l'] for x in league_rows)}")
    previous = [r for r in current["records"] if r["season"] != SEASON]
    if not previous:
        raise ValueError("Historical records missing; refusing update")
    current["records"] = rows + previous
    current.setdefault("meta", {})["live_standings"] = True
    current["meta"]["standings_source"] = "FPL Draft league details API"
    current["meta"]["standings_league_ids"] = LEAGUES
    # Keep existing 'live_matches' unset: individual match history has NOT been validated.
    current["meta"].pop("live_matches", None)
    current["meta"]["note"] = "Current 2026/27 standings are imported from FPL Draft. Historical seasons, all-time records, derbies and cup remain sourced from the existing spreadsheet snapshot."
    encoded = json.dumps(current, ensure_ascii=False, separators=(",", ":"))
    # Atomic replacements after all validation succeeds.
    for path, content in [(ROOT / "data.json", encoded), (ROOT / "data.js", "window.FPL_DATA = " + encoded + ";\n")]:
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(content, encoding="utf-8")
        os.replace(temp, path)
    print("Updated 2026/27 standings only; history/cup/derbies preserved.")

if __name__ == "__main__":
    main()
