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

def print_teams_with_users(csv_root='csv', map_path='../team_user_map.json'):
    team_to_user = load_team_user_map(map_path)
    print(f"{'Year':<6} | {'Team Name':<30} | Username")
    print('-'*60)
    for year_dir in sorted(os.listdir(csv_root)):
        year_path = os.path.join(csv_root, year_dir)
        if os.path.isdir(year_path):
            teams_csv = os.path.join(year_path, 'teams.csv')
            if os.path.isfile(teams_csv):
                with open(teams_csv, newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    try:
                        header = next(reader)
                    except StopIteration:
                        continue  # skip empty files
                    # Find Username column index if present
                    username_idx = None
                    for i, col in enumerate(header):
                        if col.strip().lower() == 'username':
                            username_idx = i
                            break
                    for row in reader:
                        if row and row[0].strip():
                            team = row[0].strip()
                            if username_idx is not None and len(row) > username_idx and row[username_idx].strip():
                                user = row[username_idx].strip()
                            else:
                                user = team_to_user.get(team, '(unknown)')
                            print(f"{year_dir:<6} | {team:<30} | {user}")

if __name__ == '__main__':
    print_teams_with_users()
