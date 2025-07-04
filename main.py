from sqlalchemy import create_engine
from batters import df_batters
from pitchers import df_pitchers

# Connect to Postgres
engine = create_engine('postgresql://localhost:5432/mlb_stats')

def clear_today_data():
    with engine.connect() as conn:
        conn.execute("DELETE FROM batters WHERE stat_date = CURRENT_DATE;")
        conn.execute("DELETE FROM pitchers WHERE stat_date = CURRENT_DATE;")
        # Optionally reset sequences if you want
        # conn.execute("ALTER SEQUENCE batters_id_seq RESTART WITH 1;")
        # conn.execute("ALTER SEQUENCE pitchers_id_seq RESTART WITH 1;")

def push_data():
    # Rename columns if needed (example shown for batters)
    batters_renamed = df_batters.rename(columns={
        "Name": "name", "Hits": "hits", "Runs": "runs", "RBI": "rbi",
        "AB": "ab", "AVG": "avg", "H+R+RBI": "h_r_rbi"
    })

    pitchers_renamed = df_pitchers.rename(columns={
        "Name": "name", "ERA": "era", "Wins": "wins", "Losses": "losses",
        "IP": "ip", "H": "h", "R": "r", "ER": "er", "HR": "hr",
        "HB": "hb", "BB": "bb", "SO": "so"
    })

    batters_renamed.to_sql('batters', engine, if_exists='append', index=False)
    pitchers_renamed.to_sql('pitchers', engine, if_exists='append', index=False)

if __name__ == "__main__":
    clear_today_data()
    push_data()
    print("Data for batters and pitchers pushed successfully.")
