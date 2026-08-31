# BBGM Career Oracle — Assumptions & Limitations
Last updated: 2026

This file documents the key assumptions and configurable values used throughout
the BBGM Career Oracle project. When changing any of these, note that the Python
import script AND the website's similarity algorithm may both need updating.

---

## Player Rating Scale
- **OVR (Overall) range:** 20 to 80
- **POT (Potential) range:** 20 to 80
- **IQ range:** 20 to 80
- Source: Matches the Basketball GM website's default rating scale.

---

## Career Eligibility Rules
- Only players who were **DRAFTED within the simulation window** are included.
- Only players who **RETIRED within the simulation window** are included.
- Players who existed at league start (pre-generated veterans) are **excluded**.
- Players still active when the simulation ends are **excluded**.
- Reason: We need complete career arcs to build meaningful projections.

---

## Age Ranges
- **Minimum draft age:** 18
- **Maximum draft age:** 22
- **Minimum retirement age:** 28
- **Maximum retirement age:** 38
- Note: Players can retire before 38 if their OVR drops below the threshold (see below).

---

## Development & Decline (Fake Test Data Only)
These values are used only by generate_fake_data.py to simulate realistic careers.
Real BBGM import data will replace these with actual sim results.

- **Years to reach peak after draft:** 3 to 7 years
- **Peak OVR:** 85% to 100% of POT
- **Annual OVR decline after peak:** 1.5 to 4.0 points per year
- **Retirement OVR threshold:** 28 (player retires if OVR falls below this)
- **Draft OVR range:** 20 to 60 (players are rarely elite straight out of draft)
- **Minimum POT for drafted players:** 35

---

## Positions
Valid positions: PG, SG, SF, PF, C

---

## Height Ranges by Position (in inches)
- **PG:** 70 to 76 inches  (5'10" to 6'4")
- **SG:** 74 to 78 inches  (6'2" to 6'6")
- **SF:** 76 to 80 inches  (6'4" to 6'8")
- **PF:** 78 to 83 inches  (6'6" to 6'11")
- **C:**  81 to 87 inches  (6'9" to 7'3")

---

## Similarity Algorithm Attributes (in priority order)
1. OVR at the queried age (primary anchor)
2. POT at the queried age
3. Age (must match — this is the comparison anchor)
4. Position (used as a pre-filter)
5. Height
6. IQ

---

## Projection Output
- Lines shown: 25th percentile, 50th percentile, 75th percentile, 95th percentile
- Chart type: OVR by age (x = age, y = OVR)

---

## Database Format
- Storage: players.json (hosted on GitHub at /data/players.json)
- Format: JSON array of player objects
- Each player has: id, name, position, height, draft_age, draft_ovr,
  draft_pot, iq, retire_age, peak_ovr, ovr_by_age (array of age/ovr pairs)

---

## Notes / Open Questions
- Should IQ be weighted differently than height in similarity matching? TBD.
- Should we track per-age POT, or only draft-time POT? Currently: draft-time only.
- Height is stored in inches. Display conversion to feet/inches is handled by the frontend.
