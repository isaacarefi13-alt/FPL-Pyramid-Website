# The FPL Pyramid — League HQ

A responsive, self-contained fantasy Premier League history website based on the Google Drive spreadsheet **Fantasy Premier League**.

## Open

Open `index.html` in a browser. The page uses static `data.js` so it also works via `file://` without a server. The CSS references Google Fonts, but has system-font fallbacks.

## Publish

Upload `index.html`, `styles.css`, `app.js` and `data.js` together to any static host (Netlify, Vercel, GitHub Pages). Do **not** upload `build.py` unless you want the data preparation source.

## Data and limitations

- Source: https://docs.google.com/spreadsheets/d/1mAR28FMRYDPSqXlthuV2MgzVM8iEnCJT5RjPOyGZjpI/edit
- Snapshot collected November 16, 2026.
- Includes completed season tables from 2017/18 to 2025/26, plus the 2026/27 prefilled team roster entries. The 2026/27 standings are NOT computed in the source sheet.
- Current source includes some repeated teams/managers across FPL2 and FPL3, not resolved by this website.
- Includes numeric all-time records, FPL Cup group snapshots, trophy winners and an initial subset of 18 recorded derby rivalries. Cup results are incomplete without brackets.
- Historical total rows and formula errors may be inconsistent. This site does not automatically refresh, nor does it provide a private Google Drive authentication flow.
- `data.json` holds the identical dataset in standard JSON for re-use.

No changes were made to the original Google Sheet.

## Automatic sync prototype (November 2026)

This package now includes a **conservative automated importer** for FPL Draft league IDs FPL1 `148874`, FPL2 `82799`, and FPL3 `215819`. It has **not yet been verified against those live league responses**: outbound requests to draft.premierleague.com were inaccessible from the build environment. The supplied website therefore continues to show its historical snapshot; it must not be described as already live.

### Operation

- `python sync.py` requests the public `/api/league/{id}/details`, `/standings`, and `/matches` endpoints and stores successful raw responses in SQLite (`pyramid.sqlite3`). Endpoint availability and payload shapes are **unverified**, and may require changing the importer.
- Only matches with explicit `finished` / `is_finished` / `final` markers, valid gameweek and both numeric scores are saved as verified results. **If the actual API uses a different completion flag or match endpoint, adapt `extract_matches` after inspecting the responses.**
- `python export_live.py` builds `live-data.json` and `live-data.js`. If no valid finished matches are available, it leaves the historical snapshot unchanged. The website loads `live-data.js` after `data.js`.
- All-time and derby statistics are calculated from the historic snapshot plus saved completed matches, using manager names from league details. **Review name normalization, historical baseline and gameweek score conventions before trusting the computed totals.** In particular, historic manager aliases and incomplete source data require reconciliation.
- The GitHub Actions workflow `.github/workflows/update.yml` runs every three hours when published to a GitHub repository with Actions enabled and write permissions. This workflow **does not deploy the site by itself**; GitHub Pages must be configured separately.
- The workflow commits SQLite and generated website data to the repository. Use a **private repository** if the archive should not be publicly downloadable, and host the website separately. Do not put private credentials into this repository.

### FPL Cup manual edit → automatic website update

The simplest option is to maintain a separate **publishable Cup-only Google Sheet tab** with columns `group,rank,manager,w,d,l,sf,pts` (one row per manager). In Google Sheets, publish that tab as CSV, and set the GitHub Actions repository secret `FPL_CUP_CSV_URL` to its published CSV link. **Do not publish the full spreadsheet if it contains private information.** The website refreshes the Cup during scheduled exports. The original spreadsheet's Cup tab may need a separate clean export range with those column headers.

### Before declaring this production-ready

1. Run `python sync.py` on a machine/network that can reach `draft.premierleague.com` and inspect `sync_log` plus `raw_fetches` to verify actual response shapes and whether match scores are final.
2. Validate league entry-to-manager identity mappings, especially promotions/relegations and name changes, against the existing archive.
3. Verify match counts and computed standings for one completed gameweek in each division against the official site.
4. Confirm the Cup CSV export is correctly structured and that it updates without publishing other spreadsheet data.
5. Set up a GitHub repository and static site hosting. The included workflow is a starting point, not a completed deployment.

This is a **working integration scaffold, not a proven live sync**. FPL Draft endpoints are unofficial and may change.
