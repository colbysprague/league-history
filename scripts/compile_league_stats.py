import os
import csv
import json

def load_team_user_map(map_path='../team_user_map.json'):
    with open(map_path, encoding='utf-8') as f:
        mapping = json.load(f)
    team_to_user = {}
    for entry in mapping:
        user = entry['user']
        for team in entry['teams']:
            team_to_user[team] = user
    return team_to_user

def parse_record(record):
    # Expects format like '10-3-1' (wins-losses-ties)
    parts = record.strip().split('-')
    if len(parts) == 3:
        return tuple(int(x) for x in parts)
    elif len(parts) == 2:
        return int(parts[0]), int(parts[1]), 0
    else:
        return 0, 0, 0

def compile_league_stats(csv_root='csv', map_path='../team_user_map.json', output_csv='cumulative_stats.csv'):
    team_to_user = load_team_user_map(map_path)
    user_stats = {}
    for year_dir in sorted(os.listdir(csv_root)):
        year_path = os.path.join(csv_root, year_dir)
        if os.path.isdir(year_path):
            teams_csv = os.path.join(year_path, 'teams.csv')
            if os.path.isfile(teams_csv):
                with open(teams_csv, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # Try to find relevant columns
                    colnames = [c.lower() for c in reader.fieldnames]
                    team_col = next((c for c in reader.fieldnames if c.lower() in ['team', 'team name', 'name']), reader.fieldnames[0])
                    record_col = next((c for c in reader.fieldnames if 'record' in c.lower()), None)
                    pf_col = next((c for c in reader.fieldnames if 'points for' in c.lower() or 'pf' == c.lower() or 'points scored' in c.lower()), None)
                    pa_col = next((c for c in reader.fieldnames if 'points against' in c.lower() or 'pa' == c.lower()), None)
                    for row in reader:
                        team = row.get(team_col, '').strip()
                        user = team_to_user.get(team)
                        if not user:
                            continue  # skip unmapped teams
                        record = row.get(record_col, '').strip() if record_col else ''
                        wins, losses, ties = parse_record(record)
                        def parse_float(val):
                            if not val:
                                return 0.0
                            try:
                                return float(str(val).replace(',', ''))
                            except Exception:
                                return 0.0
                        pf = parse_float(row.get(pf_col, 0)) if pf_col and row.get(pf_col) else 0.0
                        pa = parse_float(row.get(pa_col, 0)) if pa_col and row.get(pa_col) else 0.0
                        if user not in user_stats:
                            user_stats[user] = {'wins': 0, 'losses': 0, 'ties': 0, 'pf': 0.0, 'pa': 0.0}
                        user_stats[user]['wins'] += wins
                        user_stats[user]['losses'] += losses
                        user_stats[user]['ties'] += ties
                        user_stats[user]['pf'] += pf
                        user_stats[user]['pa'] += pa
    # Prepare and sort output rows by points for (desc)
    rows = []
    for user, stats in user_stats.items():
        games_played = stats['wins'] + stats['losses'] + stats['ties']
        rows.append([
            user,
            stats['wins'],
            stats['losses'],
            stats['ties'],
            games_played,
            round(stats['pf'], 2),
            round(stats['pa'], 2)
        ])
    rows.sort(key=lambda r: r[5], reverse=True)  # sort by points for (index 5)
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['User', 'Wins', 'Losses', 'Ties', 'Games Played', 'Points For', 'Points Against'])
        for row in rows:
            writer.writerow(row)
    print(f"Cumulative stats written to {output_csv}")

if __name__ == '__main__':
    compile_league_stats()
