import pprint as pp
import os
import csv
import json

 
PLAYOFF_WINS = 'playoff_wins'
PLAYOFF_LOSSES = 'playoff_losses'
PLAYOFF_POINTS_FOR = 'playoff_points_for'
PLAYOFF_POINTS_AGAINST = 'playoff_points_against'
CHAMPIONSHIPS = 'championships'
CHAMPIONSHIP_APPEARANCES = 'championship_appearances'

def load_team_user_map(map_path='team_user_map.json'):
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


def get_user_from_team(team, team_to_user):
    # returns the user from a team name.
    # should return a user even if the team name is truncated. check that the keys in the map match the start of the team name without elipses
    for key in team_to_user:
        if key.startswith(team.replace("...", "")):
            return team_to_user[key]
    return None

def compile_league_stats(csv_root='csv', map_path='team_user_map.json', output_csv='cumulative_stats.csv'):
    team_to_user = load_team_user_map(map_path)
    user_stats = {}
    for year_dir in sorted(os.listdir(csv_root)):
        year_path = os.path.join(csv_root, year_dir)
        if os.path.isdir(year_path):
            teams_csv = os.path.join(year_path, 'matchups.csv')
            if os.path.isfile(teams_csv):
                with open(teams_csv, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        team = row.get('Team')
                        opponent = row.get('Opponent')
                        score1 = row.get('Score_2')
                        score2 = row.get('Score')

                        score1 = float(score1)
                        score2 = float(score2)

                        user1 = get_user_from_team(team, team_to_user)
                        user2 = get_user_from_team(opponent, team_to_user)

                        if user1 is None or user2 is None:
                            continue

                        # Determine winner and loser
                        if score1 >= score2:
                            winner, winner_score = user1, score1
                            loser, loser_score = user2, score2
                        else:
                            winner, winner_score = user2, score2
                            loser, loser_score = user1, score1

                        game_type = row.get('Game_Type', '')
                        if 'playoff' in game_type.lower() or 'championship' in game_type.lower():
                            for user in [winner, loser]:
                                if user not in user_stats:
                                    user_stats[user] = {
                                        PLAYOFF_WINS: 0,
                                        PLAYOFF_LOSSES: 0,
                                        PLAYOFF_POINTS_FOR: 0,
                                        PLAYOFF_POINTS_AGAINST: 0,
                                        CHAMPIONSHIPS: 0, 
                                        CHAMPIONSHIP_APPEARANCES: 0
                                    }
                            # Update winner stats
                            user_stats[winner][PLAYOFF_WINS] += 1
                            user_stats[winner][PLAYOFF_POINTS_FOR] += winner_score
                            user_stats[winner][PLAYOFF_POINTS_AGAINST] += loser_score

                            # Update loser stats
                            user_stats[loser][PLAYOFF_LOSSES] += 1
                            user_stats[loser][PLAYOFF_POINTS_FOR] += loser_score 
                            user_stats[loser][PLAYOFF_POINTS_AGAINST] += winner_score 

                            if 'championship' in game_type.lower():
                                user_stats[winner][CHAMPIONSHIPS] += 1
                                user_stats[winner][CHAMPIONSHIP_APPEARANCES] += 1
                                user_stats[loser][CHAMPIONSHIP_APPEARANCES] += 1

    return user_stats


stats = compile_league_stats()
# write stats to csv file 
# sort by playoff wins desc
sorted_stats = sorted(stats.items(), key=lambda x: x[1].get('playoff_wins', 0), reverse=True)

with open('playoff_stats.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    header = ['Player', 'Playoff Wins', 'Playoff Losses', 'Playoff Points For', 'Playoff Points Against', 'Championships', 'Championship Appearances']
    writer.writerow(header)

    for user, data in sorted_stats:
        row = [
            user,
            data.get('playoff_wins', 0),
            data.get('playoff_losses', 0),
            f"{data.get('playoff_points_for', 0.0):.2f}",
            f"{data.get('playoff_points_against', 0.0):.2f}",
            data.get('championships', 0),
            data.get(CHAMPIONSHIP_APPEARANCES, 0)
        ]
        writer.writerow(row)
pp.pprint(stats)