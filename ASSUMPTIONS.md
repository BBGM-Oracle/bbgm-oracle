# BBGM Career Oracle — Assumptions & Design Decisions

## Project Overview
A web tool that compiles simulated basketball player careers from basketball-gm.com and projects OVR trajectories using similarity matching. Users enter player attributes and receive a projection graph showing 25th, 50th, 75th, and 95th percentile OVR curves by age.

- **Live site:** https://bbgm-oracle.github.io/bbgm-oracle/
- **Repo:** https://github.com/BBGM-Oracle/bbgm-oracle

---

## Database Integrity Rules

### Complete-Career-Only Filter (Non-Negotiable)
Only players with complete careers are valid entries. A player is valid if and only if:
- They were drafted within the simulation (`draft.round > 0`)
- They are retired (`retiredYear` is not null)
- They have ratings data
- They have a birth year

**Discarded:**
- Pre-generated players present at league start (`draft.round = 0`)
- Players still active when the simulation ends (`retiredYear = null`)

---

## Similarity Algorithm

### Attributes (Priority Order)
| Priority | Attribute | Role        | Weight |
|----------|-----------|-------------|--------|
| 1        | Position  | Hard filter | —      |
| 2        | OVR       | Scored      | 30%    |
| 3        | POT       | Scored      | 25%    |
| 4        | Age       | Scored      | 25%    |
| 5        | IQ        | Scored      | 10%    |
| 6        | Height    | Scored      | 10%    |

**Age is the anchor** — historical players are matched at the same age as the queried player.

### Parameters
- TOP_N = 20 (similar players used for projection)
- Minimum 5-player threshold before displaying a warning to the user
- Queried player is not plotted on the output graph

### Multi-Position Support (Deferred)
Only the first listed position is used. Full multi-position support (e.g. "PG-SG") is deferred until the database is larger.

---

## BBGM Export Quirks
- No `gameAttributes` block in Players-only exports
- Top-level `pos` is always null — use `ratings[0].pos` instead
- `draft.age` is always null — calculate as `draft.year - born.year`
- Active players have `retiredYear: null`
- Pre-generated players have `draft.round = 0`

---

## Database Schema
**File:** `data/players.json`

| Field       | Description                                      |
|-------------|--------------------------------------------------|
| id          | Auto-incrementing integer (internal DB key)      |
| name        | Full player name                                 |
| position    | Position string from ratings[0].pos              |
| height      | Total inches (converted from BBGM hgt 0–100)     |
| draft_age   | draft.year − born.year                           |
| draft_ovr   | OVR at time of draft (first rating entry)        |
| draft_pot   | POT at time of draft (first rating entry)        |
| iq          | IQ at time of draft (first rating entry)         |
| retire_age  | retiredYear − born.year                          |
| peak_ovr    | Highest OVR achieved across entire career        |
| ovr_by_age  | Dictionary of {age: ovr} across career           |

**Height formula:** `round(66 + (hgt / 100) * 24)` → maps 0–100 to ~66–90 inches

---

## Supported Positions
All nine BBGM positions: **PG, SG, G, GF, SF, F, PF, FC, C**
(Listed in this order in the UI dropdown)

---

## Import Workflow (Phase 7)

### Tools
| File                     | Location        | Purpose                                          |
|--------------------------|-----------------|--------------------------------------------------|
| `import_bbgm.py`         | Local only       | Main import script                               |
| `run_import.bat`         | Local only       | Double-click launcher for the import script      |
| `data/imports_log.json`  | Local only       | Tracks imported player IDs per simulation        |
| `data/players.json`      | GitHub + Local   | The database — upload to GitHub after each import|

### Standard Import Steps
1. Run a BBGM simulation and download the JSON export
2. Move the export file into the `exports/` folder (never delete these — they are the source of truth)
3. Double-click `run_import.bat`
4. Follow the on-screen prompts
5. Upload the updated `data/players.json` to GitHub

### Multi-Simulation Deduplication
- Each simulation is given a user-defined name (e.g. "Sim_1", "Sim_2")
- Player uniqueness is determined by `(simulation_name, bbgm_pid)`
- Re-importing the same simulation at a later year adds only new retirees — no duplicates
- Different simulations with overlapping BBGM pids are treated as separate players

### First-Time Setup (runs automatically, one time only)
When `imports_log.json` doesn't exist, the script:
1. Asks the user to name their existing simulation
2. Scans all files in `exports/` to register already-imported player IDs
3. Creates `imports_log.json` automatically

### Files to NEVER Upload to GitHub
- `import_bbgm.py`
- `run_import.bat`
- `data/imports_log.json`
- Anything in the `exports/` folder

---

## Tech Stack
- **Frontend:** HTML/CSS/JavaScript, Chart.js v4 (CDN) — all in `index.html`
- **Data pipeline:** Python 3.x scripts, run locally on Windows via Command Prompt or .bat file
- **Hosting:** GitHub Pages (free static hosting)
- **Data source:** basketball-gm.com JSON simulation exports

---

## Known Deferred Issues

### Age-37 Curve Convergence
All four percentile curves converge near age 37 due to insufficient player data at high ages.
- **Proposed fix:** Enforce a minimum players-per-age threshold (3–5 players) before plotting that age point
- **Status:** Deferred to a future phase

---

## Phase Completion Log
| Phase | Description                                              | Status |
|-------|----------------------------------------------------------|--------|
| 1     | GitHub setup and Pages hosting                           | ✓      |
| 2     | Database schema + fake data generation script            | ✓      |
| 3     | `import_bbgm.py` built and tested                        | ✓      |
| 4     | Frontend form built with dark theme                      | ✓      |
| 5     | Similarity algorithm + Chart.js projection graph         | ✓      |
| 6     | Live site testing + position dropdown fix (9 positions)  | ✓      |
| 7     | Multi-simulation support, deduplication, .bat launcher   | ✓      |
