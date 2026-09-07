# BBGM Career Oracle — Assumptions & Design Decisions

This file documents every design decision and assumption baked into the project.
Update it whenever a decision changes.

---

## Data Integrity

- **Complete careers only.** A player is valid only if they were drafted AND retired
  within the simulation window. Pre-generated players present at league start are
  excluded. Players still active when a simulation ends are excluded.
- **Simulation length: 20 years.** Chosen to maximise the number of complete careers
  captured per export.
- **OVR/POT/IQ scale: 20–80.** Matches BBGM's native attribute scale.
- **Draft age range: 18–22.** Players drafted outside this range are excluded.
- **Retirement age range: 28–38.** Expected range; no hard filter applied.
- **IQ is averaged.** Computed as the mean of `oiq` (offensive IQ) and `diq` (defensive IQ).
- **Two `players.json` files exist in the repo.** The root-level file is ignored.
  The correct file is always `data/players.json`.

---

## Database Schema

Each player record in `data/players.json` contains:

| Field        | Type             | Description                                      |
|--------------|------------------|--------------------------------------------------|
| `id`         | integer          | Auto-incremented unique ID                       |
| `name`       | string           | Player name from BBGM export                     |
| `position`   | string           | PG / SG / SF / PF / C                           |
| `height`     | integer          | Height in total inches                           |
| `draft_age`  | integer          | Age at time of draft                             |
| `draft_ovr`  | integer          | OVR rating in draft year                         |
| `draft_pot`  | integer          | POT rating in draft year                         |
| `iq`         | float            | Average of oiq and diq at draft                  |
| `retire_age` | integer          | Age at retirement                                |
| `peak_ovr`   | integer          | Highest OVR reached during career                |
| `ovr_by_age` | array of objects | `[ { "age": 18, "ovr": 45 }, … ]` one per season|

---

## Similarity Algorithm

- **Step 1 — Position filter.** Only players matching the queried position are considered.
  Position is treated as a hard filter, not a scored attribute.
- **Step 2 — Weighted distance scoring.** Each attribute is normalised to [0, 1]
  within its expected range, then a weighted absolute difference is computed.
  Lower score = more similar.

### Attribute weights

| Attribute | Weight | Normalisation range |
|-----------|--------|---------------------|
| OVR       | 30%    | 20 – 80             |
| POT       | 25%    | 20 – 80             |
| Age       | 25%    | 18 – 22             |
| IQ        | 10%    | 20 – 80             |
| Height    | 10%    | 60 – 90 inches      |

- **Top N = 20.** The 20 most-similar players (lowest distance scores) are used
  to build each projection.
- **Minimum threshold = 5.** If fewer than 5 similar players are found, a warning
  is displayed to the user indicating the projection may not be reliable.
  If 0 players are found for a position, a separate "no data" message is shown.

---

## Projection Output

- **Chart type:** Line chart (Chart.js v4).
- **X-axis:** Age (e.g., 18 → 38). One data point per season per player.
- **Y-axis:** OVR rating, fixed range 20–80.
- **Four percentile curves:** 25th, 50th (median), 75th, and 95th.
- **Percentile method:** Linear interpolation across sorted values at each age.
  `null` is emitted for any age where no similar players have data (Chart.js spans the gap).
- **The user's own player is not plotted on the chart.** The graph shows only
  the historical distribution of similar players.

---

## Frontend Form — Input Constraints

| Field      | Min    | Max    | Notes                              |
|------------|--------|--------|------------------------------------|
| OVR        | 20     | 80     |                                    |
| POT        | 20     | 80     | Must be ≥ OVR                      |
| Draft Age  | 18     | 22     |                                    |
| IQ         | 20     | 80     |                                    |
| Height     | 5'0"   | 7'6"   | Stored as total inches internally  |
| Position   | PG–C   | —      | Dropdown; hard filter in algorithm |

---

## Hosting & Infrastructure

- **Hosting:** GitHub Pages (free tier), static site only — no server-side code.
- **GitHub organisation:** BBGM-Oracle
- **Live URL:** https://bbgm-oracle.github.io/bbgm-oracle/
- **Data file:** `data/players.json` — loaded via `fetch()` at page load.
- **No build step.** The site is pure HTML/CSS/JavaScript — no npm, no bundler.
- **Chart library:** Chart.js v4, loaded from CDN.

---

## Import Script (`import_bbgm.py`)

- Handles both `gameAttributes` formats: list of objects and plain dict.
- Determines simulation start season automatically.
- Filters for complete careers (drafted + retired within the window).
- Computes IQ as the mean of `oiq` and `diq` from the draft year.
- Builds `ovr_by_age` trajectories from season-by-season ratings.
- Appends to `data/players.json` with auto-incremented IDs (no duplicates within a run;
  re-running the same export will add duplicate records — avoid importing the same file twice).

---

## Build Phases

| Phase | Description                             | Status      |
|-------|-----------------------------------------|-------------|
| 1     | GitHub setup                            | ✅ Complete |
| 2     | Database schema + fake data script      | ✅ Complete |
| 3     | Python BBGM import script               | ✅ Complete |
| 4     | Frontend form                           | ✅ Complete |
| 5     | Similarity algorithm + Chart.js graph   | ✅ Complete |
| 6     | Integration & testing                   | ⬜ Upcoming |
| 7     | Admin update workflow                   | ⬜ Upcoming |

---

*Last updated: Phase 5 complete.*

## Phase 6 Notes

- BBGM assigns 9 distinct positions: PG, SG, G, GF, SF, F, PF, FC, C. The position 
  dropdown was updated in Phase 6 to include all 9. Earlier versions only included the 
  5 "pure" positions, leaving ~47% of the database unmatchable.

- At high ages (e.g., 37+), percentile curves converge because very few matched players 
  have data at those ages. A fix (minimum players-per-age threshold before plotting) has 
  been deferred. To implement: filter out any age from the chart data where fewer than N 
  players (suggested: 3–5) have an OVR value, so lines end naturally rather than converging.
