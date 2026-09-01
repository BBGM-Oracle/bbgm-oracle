# BBGM Career Oracle — Assumptions & Design Decisions

This file documents the key assumptions and decisions made during the build.
It is updated as each phase is completed.

---

## Data & Simulation

- **Simulation length:** 20 years per BBGM export. This was chosen over 10 years to capture more complete careers.
- **Complete careers only:** A player record is only imported if the player was *drafted* AND *retired* within the simulation window. Players who were pre-generated at league start (i.e., already in the league when the sim begins) are discarded. Players who are still active when the sim ends are also discarded. This is a hard data integrity rule — including incomplete careers would corrupt the projection model.
- **OVR/POT/IQ scale:** All ratings use BBGM's native 20–80 scale.
- **IQ calculation:** IQ is computed as the average of a player's offensive IQ (`oiq`) and defensive IQ (`diq`) from the BBGM export.
- **Draft age range:** 18–22. Players drafted outside this range are excluded as outliers.
- **Retirement age range:** 28–38. Players retiring outside this range are excluded as outliers.
- **Two `players.json` files exist in the repo:** The correct target is `data/players.json`. The root-level `players.json` is a leftover artifact and should be ignored.

---

## Player Attributes & Similarity

- **Similarity attribute priority order:** Position (filter first) → Age (the anchor — match historical players at the same age) → OVR → POT → Height → IQ. Start small; expand attribute set as database grows.
- **Age is the anchor:** The similarity engine finds historical players at the same age as the user's input player, then scores by other attributes. Do not over-engineer the attribute set early.
- **Position matching:** BBGM sometimes lists multiple positions for a player (e.g., "PG-SG"). Only the **first position listed** is used for similarity matching. Multi-position support may be added in a future phase.
- **Height storage:** Height is stored in the database as total inches (e.g., 6'4" = 76 inches). The frontend accepts feet and inches separately and converts to inches before matching.

---

## Database Schema

Each player record in `data/players.json` contains:

| Field        | Type             | Description                                      |
|-------------|-----------------|--------------------------------------------------|
| `id`         | integer          | Auto-incremented unique ID                       |
| `name`       | string           | Player name from BBGM export                    |
| `position`   | string           | First position listed (PG, SG, SF, PF, C)       |
| `height`     | integer          | Height in total inches                           |
| `draft_age`  | integer          | Player's age when drafted                        |
| `draft_ovr`  | integer          | OVR rating at time of draft                      |
| `draft_pot`  | integer          | POT rating at time of draft                      |
| `iq`         | float            | Average of oiq and diq at time of draft          |
| `retire_age` | integer          | Player's age when retired                        |
| `peak_ovr`   | integer          | Highest OVR rating reached during career         |
| `ovr_by_age` | array of objects | `[{"age": 19, "ovr": 48}, ...]` — full trajectory |

---

## Frontend

- **User inputs:** OVR, POT, age, position, height (feet + inches separately), IQ.
- **Height input:** Two separate number fields — one for feet, one for inches — each with its unit label displayed next to it. Tab order moves naturally from feet to inches.
- **Projection output (Phase 5):** OVR-by-age graph with four percentile lines: 25th, 50th, 75th, and 95th.
- **Phase 4 behavior:** After submitting the form, a "coming soon" message is displayed along with a summary of the entered values. The actual projection engine is Phase 5.

---

## Import Script (`import_bbgm.py`)

- Handles both `gameAttributes` formats found in BBGM exports (list format and dict format).
- Determines the simulation start season automatically from `gameAttributes`.
- Appends new players to `data/players.json` with auto-incremented IDs (no duplicates overwritten).
- Skips players who do not meet the complete-career criteria described above.

---

## Hosting & Workflow

- **Hosting:** GitHub Pages (free tier). The live site is at `https://bbgm-oracle.github.io/bbgm-oracle/`.
- **GitHub username:** BBGM-Oracle
- **Local development path:** `C:\Users\travi\OneDrive\Desktop\Website\bbgm-oracle\`
- **Update workflow:** Python scripts run locally via Command Prompt. Output files are uploaded manually to GitHub via the web interface.
- **Browser for testing:** Firefox.
- **Local HTML tool note:** The separate local tool (`bbgm-career-oracle.html`) requires a Python local server to function due to browser file security restrictions. Run `python -m http.server 8000` in its directory and open `http://localhost:8000`.

---

## Build Phases

| Phase | Description                              | Status      |
|-------|------------------------------------------|-------------|
| 1     | GitHub setup                             | ✅ Complete |
| 2     | Database schema + fake test data script  | ✅ Complete |
| 3     | Python BBGM import script                | ✅ Complete |
| 4     | Frontend input form                      | ✅ Complete |
| 5     | Similarity algorithm + Chart.js projection | 🔲 Next    |
| 6     | Integration & testing                    | 🔲 Pending  |
| 7     | Admin update workflow                    | 🔲 Pending  |

---

*Last updated: Phase 4 complete*
