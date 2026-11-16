#!/usr/bin/env python3
"""Read-only discovery of FPL Draft entry metadata and possible league IDs.

Entry URLs are not league IDs. Never write standings from this diagnostic.
"""
import json
import urllib.error
import urllib.request

ENTRIES = {"FPL1": 148874, "FPL2": 82799, "FPL3": 215819}
BASE = "https://draft.premierleague.com/api"
PATHS = ["/entry/{id}/public", "/entry/{id}", "/entry/{id}/history"]

def fetch(path):
    request = urllib.request.Request(BASE + path, headers={
        "User-Agent": "Mozilla/5.0 FPL-Pyramid-Diagnostics/0.2",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.status, json.load(response)

def summarize(value, prefix="", depth=0):
    if depth > 3:
        return
    if isinstance(value, dict):
        for key, child in value.items():
            k = str(key).lower()
            if any(word in k for word in ("league", "entry", "event", "season")):
                if isinstance(child, (str, int, float, bool)) or child is None:
                    print(f"    {prefix}{key}={child}")
                elif isinstance(child, list):
                    print(f"    {prefix}{key}: list ({len(child)} items)")
                elif isinstance(child, dict):
                    print(f"    {prefix}{key}: object keys={sorted(child)}")
            if isinstance(child, dict):
                summarize(child, prefix + str(key) + ".", depth + 1)

def main():
    for division, entry_id in ENTRIES.items():
        print(f"\\n{division} entry {entry_id}:")
        for pattern in PATHS:
            path = pattern.format(id=entry_id)
            try:
                status, data = fetch(path)
                if not isinstance(data, dict):
                    print(f"  {path}: HTTP {status}; unexpected JSON type")
                    continue
                print(f"  {path}: HTTP {status}; keys={sorted(data)}")
                summarize(data)
                if path.endswith("/public"):
                    leagues = data.get("entry", {}).get("league_set", [])
                    for league in leagues:
                        if isinstance(league, dict):
                            print("    league_set item: " + json.dumps({k: v for k, v in league.items() if k in ("id", "league", "league_id", "name", "entry", "entry_id", "scoring", "variety")}, sort_keys=True))
                        else:
                            print("    league_set item: " + repr(league))
            except urllib.error.HTTPError as error:
                print(f"  {path}: HTTP {error.code}")
            except (urllib.error.URLError, ValueError, TimeoutError) as error:
                print(f"  {path}: {type(error).__name__}: {error}")
    print("\\nDiagnostic only. A successful entry lookup does not establish a correct league ID.")

if __name__ == "__main__":
    main()
