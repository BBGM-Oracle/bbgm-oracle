import json
import sys
import os
from pathlib import Path


def infer_starting_season(players):
    earliest = None
    for player in players:
        for rating in player.get('ratings', []):
            s = rating.get('season')
            if isinstance(s, int) and (earliest is None or s < earliest):
                earliest = s
    return earliest


def infer_current_season(players):
    latest = None
    for player in players:
        for rating in player.get('ratings', []):
            s = rating.get('season')
            if isinstance(s, int) and (latest is None or s > latest):
                latest = s
    return latest


def import_bbgm(bbgm_export_path, players_json_path):

    print("")
    print("Loading BBGM export: " + bbgm_export_path)
    try:
        with open(bbgm_export_path, 'r', encoding='utf-8') as f:
            bbgm_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: File not found: " + bbgm_export_path)
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: This file does not look like a valid BBGM export.")
        sys.exit(1)

    raw_players = bbgm_data.get('players', [])
    print("Players found in export: " + str(len(raw_players)))

    starting_season = infer_starting_season(raw_players)
    current_season  = infer_current_season(raw_players)

    if starting_season is None:
        print("ERROR: Could not detect simulation start year from ratings data.")
        sys.exit(1)

    print("Simulation detected: " + str(starting_season) + " to " + str(current_season))

    if os.path.exists(players_json_path):
        with open(players_json_path, 'r', encoding='utf-8') as f:
            existing_players = json.load(f)
        print("Existing database: " + str(len(existing_players)) + " players")
    else:
        existing_players = []
        print("No existing database found - creating a new one.")

    next_id = max((p['id'] for p in existing_players), default=0) + 1

    imported            = []
    skipped_preexisting = 0
    skipped_active      = 0
    skipped_no_ratings  = 0

    for player in raw_players:
        draft        = player.get('draft', {})
        draft_year   = draft.get('year', 0)
        retired_year = player.get('retiredYear')

        if not isinstance(draft_year, int) or draft_year < starting_season:
            skipped_preexisting += 1
            continue

        if retired_year is None:
            skipped_active += 1
            continue

        ratings = player.get('ratings', [])
        if not ratings:
            skipped_no_ratings += 1
            continue

        born_year  = player.get('born', {}).get('year', 0)
        ovr_by_age = []

        for r in ratings:
            season = r.get('season')
            ovr    = r.get('ovr')
            if isinstance(season, int) and isinstance(ovr, (int, float)) and born_year:
                age = season - born_year
                if 16 <= age <= 50:
                    ovr_by_age.append({'age': age, 'ovr': int(ovr)})

        if not ovr_by_age:
            skipped_no_ratings += 1
            continue

        ovr_by_age.sort(key=lambda x: x['age'])

        draft_rating = next(
            (r for r in ratings if r.get('season') == draft_year),
            ratings[0]
        )

        draft_age = draft_year - born_year if born_year else 0
        draft_ovr = draft.get('ovr') or draft_rating.get('ovr', 0)
        draft_pot = draft.get('pot') or draft_rating.get('pot', 0)

        oiq = draft_rating.get('oiq', 50)
        diq = draft_rating.get('diq', 50)
        iq  = round((oiq + diq) / 2)

        peak_ovr   = max(r['ovr'] for r in ovr_by_age)
        retire_age = int(retired_year) - born_year if born_year else 0
        position   = draft_rating.get('pos') or player.get('pos') or 'SF'
        height     = player.get('hgt', 72)

        first = player.get('firstName', '')
        last  = player.get('lastName', '')
        name  = (first + ' ' + last).strip() or 'Unknown Player'

        new_player = {
            'id':         next_id,
            'name':       name,
            'position':   position,
            'height':     int(height),
            'draft_age':  int(draft_age),
            'draft_ovr':  int(draft_ovr),
            'draft_pot':  int(draft_pot),
            'iq':         int(iq),
            'retire_age': int(retire_age),
            'peak_ovr':   int(peak_ovr),
            'ovr_by_age': ovr_by_age
        }

        imported.append(new_player)
        next_id += 1

    all_players = existing_players + imported
    os.makedirs(os.path.dirname(players_json_path), exist_ok=True)

    with open(players_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_players, f, indent=2)

    print("")
    print("=" * 46)
    print("            IMPORT COMPLETE")
    print("=" * 46)
    print("  Players imported:           " + str(len(imported)))
    print("  Skipped (pre-sim players):  " + str(skipped_preexisting))
    print("  Skipped (still active):     " + str(skipped_active))
    print("  Skipped (no ratings):       " + str(skipped_no_ratings))
    print("  Total in database now:      " + str(len(all_players)))
    print("=" * 46)
    print("")
    print("  Saved to: " + players_json_path)
    print("")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("")
        print("USAGE:")
        print("  python import_bbgm.py <path_to_bbgm_export.json>")
        print("")
        print("EXAMPLE:")
        print('  python import_bbgm.py "C:\\Users\\travi\\Downloads\\BBGM_League_3.json"')
        print("")
        sys.exit(1)

    bbgm_export_path  = sys.argv[1]
    script_dir        = Path(__file__).parent
    players_json_path = str(script_dir / 'data' / 'players.json')

    import_bbgm(bbgm_export_path, players_json_path)
