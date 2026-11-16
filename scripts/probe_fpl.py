#!/usr/bin/env python3
"""Read-only verification of three FPL Draft league IDs and standings.

Never modifies site data. Fails if an endpoint is inaccessible or a league
does not contain the expected 10 managers.
"""
import json
import urllib.error
import urllib.request

LEAGUES = {"FPL1": 28811, "FPL2": 16233, "FPL3": 26756}
BASE = "https://draft.premierleague.com/api/league/{id}/details"

def main():
    errors = []
    for division, league_id in LEAGUES.items():
        request = urllib.request.Request(BASE.format(id=league_id), headers={
            "User-Agent": "Mozilla/5.0 FPL-Pyramid-Diagnostics/0.3",
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                data = json.load(response)
            league = data.get("league", {})
            entries = data.get("league_entries", [])
            standings = data.get("standings", [])
            print(f"{division} league {league_id}: name={league.get('name')!r}; entries={len(entries)}; standings={len(standings)}")
            print(f"  league keys={sorted(league)}")
            print(f"  entry fields={sorted(entries[0]) if entries else []}")
            print(f"  standing fields={sorted(standings[0]) if standings else []}")
            if len(entries) != 10 or len(standings) != 10:
                errors.append(f"{division}: expected 10 entries and standings, got {len(entries)} and {len(standings)}")
        except (urllib.error.URLError, ValueError, TimeoutError) as error:
            errors.append(f"{division}: {type(error).__name__}: {error}")
    if errors:
        for error in errors:
            print("ERROR: " + error)
        raise SystemExit(1)
    print("PASS: all three leagues returned 10 entries and 10 standings. Match history still needs separate verification.")

if __name__ == "__main__":
    main()
