import os
import csv
import json

def load_team_user_map(map_path='team_user_map.json'):
    with open(map_path, encoding='utf-8') as f:
        mapping = json.load(f)
    team_to_user = {}
    for entry in mapping:
        user = entry['user']
        for team in entry['teams']:
            team_to_user[team] = user
    return team_to_user

def check_team_mappings(csv_root='csv', map_path='team_user_map.json'):
    team_to_user = load_team_user_map(map_path)
    unmapped = set()
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
                    for row in reader:
                        if row and row[0].strip():
                            team = row[0].strip()
                            if team not in team_to_user:
                                unmapped.add((year_dir, team))
    if unmapped:
        print("Teams with no user mapping:")
        for year, team in sorted(unmapped):
            print(f"{year}: {team}")
    else:
        print("All teams are mapped to a user.")

if __name__ == '__main__':
    check_team_mappings()
