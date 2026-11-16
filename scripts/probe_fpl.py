#!/usr/bin/env python3
"""Read-only availability and schema check for unofficial FPL Draft league endpoints.

No personal data or responses are persisted; only status, structure and counts are logged.
"""
import json
import urllib.error
import urllib.request

LEAGUES = {"FPL1": 148874, "FPL2": 82799, "FPL3": 215819}
BASE = "https://draft.premierleague.com/api/league/{league_id}/details"

def main():
    failures = 0
    for division, league_id in LEAGUES.items():
        url = BASE.format(league_id=league_id)
        request = urllib.request.Request(url, headers={
            "User-Agent": "FPL-Pyramid-Sync/0.1 (read-only diagnostics)",
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read(2_000_000)
                data = json.loads(body)
                if not isinstance(data, dict):
                    raise ValueError("Expected JSON object")
                print(f"{division} ({league_id}): HTTP {response.status}; keys={sorted(data.keys())}")
                for key in ("league", "league_entries", "standings", "matches"):
                    value = data.get(key)
                    if isinstance(value, list):
                        print(f"  {key}: {len(value)} items")
                    elif isinstance(value, dict):
                        print(f"  {key}: object keys={sorted(value.keys())}")
        except (urllib.error.URLError, ValueError, TimeoutError) as error:
            failures += 1
            print(f"{division} ({league_id}): failed: {type(error).__name__}: {error}")
    if failures:
        raise SystemExit(f"{failures} of {len(LEAGUES)} league feeds failed")
    print("All league detail feeds returned JSON. Match-history parsing is NOT validated.")

if __name__ == "__main__":
    main()
