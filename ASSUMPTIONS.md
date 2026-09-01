# BBGM Career Oracle — Assumptions & Design Decisions

Last updated: Phase 3 complete

---

## Project Goal

Compile a large database of simulated Basketball GM player careers,
then let users input a player's attributes to receive a projected
OVR trajectory based on historically similar players.

---

## Simulation Settings

- **Simulation length:** 20 years (chosen to maximize complete careers)
- **Source:** basketball-gm.com (Tools → Export League → Players only)
- **Export format:** JSON (Players only export — does NOT include gameAttributes)

---

## What Counts as a "Complete Career"

Only players meeting ALL of the following are added to the database:

1. **Drafted within the simulation** — players with draft years before
   the simulation's first season are pre-generated and excluded,
   because we don't have their full early-career history.

2. **Fully retired** — players with retiredYear = null are still active
   and excluded. We only want careers with a beginning and an end.

3. **Has rating data** — players with no ratings entries are excluded.

### How the simulation window is detected

Because "Players only" exports do not include gameAttributes, the
import script infers the simulation start year from the earliest
season that appears in any player's ratings array. The end year is
inferred from the latest season in any player's ratings array.

---

## Database Schema

Each player record contains:

| Field       | Type             | Description                                  |
|-------------|------------------|----------------------------------------------|
| id          | integer          | Auto-incremented unique ID                   |
| name        | string           | First + last name                            |
| position    | string           | Position at draft time (from ratings[0].pos) |
| height      | integer          | Height in inches                             |
| draft_age   | integer          | draft.year minus born.year                   |
| draft_ovr   | integer          | OVR rating at time of draft                  |
| draft_pot   | integer          | POT rating at time of draft                  |
| iq          | integer          | Average of oiq and diq at draft time         |
| retire_age  | integer          | retiredYear minus born.year                  |
| peak_ovr    | integer          | Highest OVR reached during career            |
| ovr_by_age  | array of objects | [{age, ovr}, ...] sorted by age              |

### Notes on specific fields

- **position**: The top-level `pos` field in BBGM Players-only exports
  is always null. Position is read from ratings[0].pos instead.
- **draft_age**: The `draft.age` field in BBGM exports is always null.
  Age is calculated as draft.year - born.year.
- **iq**: BBGM stores offensive IQ (oiq) and defensive IQ (diq)
  separately. We average both and round to the nearest integer.
- **OVR/POT/IQ scale**: 20–80, matching BBGM's native scale.

---

## Similarity Attributes (planned, Phase 5)

Matching priority order:

1. Position (filter first — only compare same position)
2. Age (the anchor — find historical players at the same age)
3. OVR
4. POT
5. Height
6. IQ

Start simple; add more attributes as the database grows.

---

## Projection Output (planned, Phase 5)

- OVR-by-age graph with four percentile lines: 25th, 50th, 75th, 95th
- User inputs: OVR, POT, age, position, height, IQ

---

## File Locations

| File                | Purpose                                     |
|---------------------|---------------------------------------------|
| data/players.json   | The real player database (target for imports)|
| players.json        | Root-level duplicate — ignore               |
| import_bbgm.py      | Python script to import BBGM exports        |
| generate_fake_data.py | Generates fake test players (Phase 2)     |
| index.html          | Website front page                          |

---

## Known Observations from First Real Import

- First import (League 3, 2026–2047 sim): **812 complete careers**
- 540 players skipped as pre-generated (drafted before sim start)
- 868 players skipped as still active
- Draft ages observed: 19–22
- Retirement ages observed: 26–38
- Draft OVR observed: 12–58
- Positions in dataset: C, F, FC, G, GF, PF, PG, SF, SG

---

## Import Workflow (for adding future simulations)

1. Run a 20-year BBGM simulation at basketball-gm.com
2. Export: Tools → Export League → select "Players" only
3. Save the exported JSON file to your Downloads folder
4. Open Command Prompt and navigate to the project folder:
       cd C:\Users\travi\OneDrive\Desktop\Website\bbgm-oracle
5. Run:
       python import_bbgm.py "C:\Users\travi\Downloads\your_export.json"
6. The script appends new players to data/players.json automatically
7. Upload the updated data/players.json to GitHub
