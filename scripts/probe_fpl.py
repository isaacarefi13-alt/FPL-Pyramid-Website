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
MATCH_BASE = "https://draft.premierleague.com/api/league/{id}/element-status?event=1"
MATCH_CANDIDATES = [
    "https://draft.premierleague.com/api/league/{id}/matches",
    "https://draft.premierleague.com/api/league/{id}/matches?event=1",
]


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
            for url_template in MATCH_CANDIDATES:
                url = url_template.format(id=league_id)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 FPL-Pyramid-Diagnostics/0.4", "Accept": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=20) as match_response:
                        match_data = json.load(match_response)
                    if isinstance(match_data, dict):
                        print(f"  match endpoint {url.split('/api/')[-1]}: HTTP 200; keys={sorted(match_data)}")
                        for key, val in match_data.items():
                            if isinstance(val, list):
                                print(f"    {key}: {len(val)} items; first fields={sorted(val[0]) if val and isinstance(val[0], dict) else []}")
                    else:
                        print(f"  match endpoint {url.split('/api/')[-1]}: HTTP 200; type={type(match_data).__name__}")
                except urllib.error.HTTPError as error:
                    print(f"  match endpoint {url.split('/api/')[-1]}: HTTP {error.code}")
                except (urllib.error.URLError, ValueError, TimeoutError) as error:
                    print(f"  match endpoint error: {type(error).__name__}: {error}")
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
