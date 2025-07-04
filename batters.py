import requests
import pandas as pd
import time
from collections import defaultdict
from datetime import datetime, timedelta
from sqlalchemy import create_engine

TEAM_ID = 135  # Padres
SEASON = 2025

# Calculate dates for last 7 days
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Step 1: Get active roster
roster_url = f'https://statsapi.mlb.com/api/v1/teams/{TEAM_ID}/roster'
roster = requests.get(roster_url).json()['roster']

batters = []

for player in roster:
    player_id = player['person']['id']
    player_name = player['person']['fullName']
    position = player['position']['abbreviation']
    
    if position == 'P':  # Skip pitchers
        continue

    # Step 2: Get game logs (hitting) for player in last 7 days
    url = f'https://statsapi.mlb.com/api/v1/people/{player_id}/stats'
    params = {
        'stats': 'gameLog',
        'group': 'hitting',
        'season': SEASON,
    }

    resp = requests.get(url, params=params).json()
    game_logs = resp.get('stats', [{}])[0].get('splits', [])

    totals = defaultdict(int)
    ab_total = 0

    for game in game_logs:
        game_date = game.get('date')
        if game_date >= start_date_str and game_date <= end_date_str:
            stat = game['stat']
            totals['Hits'] += stat.get('hits', 0)
            totals['Runs'] += stat.get('runs', 0)
            totals['RBI'] += stat.get('rbi', 0)
            ab_total += stat.get('atBats', 0)

    hits = totals['Hits']
    runs = totals['Runs']
    rbi = totals['RBI']
    avg = round(hits / ab_total, 3) if ab_total > 0 else None

    if ab_total > 0:  # Only include if player appeared in last 7 days
        batters.append({
            'Name': player_name,
            'Hits': hits,
            'Runs': runs,
            'RBI': rbi,
            'AB': ab_total,
            'AVG': avg,
            'H+R+RBI': hits + runs + rbi
        })

    time.sleep(0.2)  # Be gentle on API

# Step 3: Create DataFrame and sort
df_batters = pd.DataFrame(batters)
df_batters = df_batters.sort_values(by='H+R+RBI', ascending=False).reset_index(drop=True)

print(df_batters)
