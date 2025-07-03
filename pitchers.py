import requests
import pandas as pd
import time
from datetime import datetime, timedelta

TEAM_ID = 135  # Padres
SEASON = 2025

def innings_to_outs(innings_str):
    if '.' not in innings_str:
        return int(float(innings_str)) * 3
    whole, frac = innings_str.split('.')
    outs = int(whole) * 3
    if frac == '1':
        outs += 1
    elif frac == '2':
        outs += 2
    return outs

# Date range: last 7 days
end_date = datetime.now()
start_date = end_date - timedelta(days=7)
start_date_str = start_date.strftime('%Y-%m-%d')
end_date_str = end_date.strftime('%Y-%m-%d')

# Fetch Padres roster
roster_url = f'https://statsapi.mlb.com/api/v1/teams/{TEAM_ID}/roster'
roster = requests.get(roster_url).json()['roster']

pitchers = []

for player in roster:
    player_id = player['person']['id']
    player_name = player['person']['fullName']
    position = player['position']['abbreviation']

    if position != 'P':
        continue  # skip non-pitchers

    # Get pitching logs
    url = f'https://statsapi.mlb.com/api/v1/people/{player_id}/stats'
    params = {
        'stats': 'gameLog',
        'group': 'pitching',
        'season': SEASON,
    }

    resp = requests.get(url, params=params).json()
    stats_list = resp.get('stats', [])
    if not stats_list:
        continue

    game_logs = stats_list[0].get('splits', [])
    if not game_logs:
        continue

    # Initialize stat totals
    outs = er = r = h = hr = hb = bb = so = w = l = 0

    for game in game_logs:
        date = game.get('date')
        if date < start_date_str or date > end_date_str:
            continue

        stat = game['stat']
        outs += innings_to_outs(stat.get('inningsPitched', '0'))
        er += int(stat.get('earnedRuns', 0))
        r += int(stat.get('runs', 0))
        h += int(stat.get('hits', 0))
        hr += int(stat.get('homeRuns', 0))
        hb += int(stat.get('hitBatsmen', 0))
        bb += int(stat.get('baseOnBalls', 0))
        so += int(stat.get('strikeOuts', 0))
        w += int(stat.get('wins', 0))
        l += int(stat.get('losses', 0))

    if outs == 0:
        continue

    ip_whole = outs // 3
    ip_frac = outs % 3
    ip = ip_whole + ip_frac / 3
    era = round((er / ip) * 9, 2) if ip > 0 else None

    pitchers.append({
        'Name': player_name,
        'ERA': era,
        'Wins': w,
        'Losses': l,
        'IP': round(ip, 1),
        'H': h,
        'R': r,
        'ER': er,
        'HR': hr,
        'HB': hb,
        'BB': bb,
        'SO': so
    })

    time.sleep(0.2)

# Create and sort DataFrame
df_pitchers = pd.DataFrame(pitchers)
df_pitchers = df_pitchers.sort_values(by='SO', ascending=False).reset_index(drop=True)

print(df_pitchers)
