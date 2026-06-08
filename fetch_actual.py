import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

# fetch 2025-26 actuals
print("Fetching 2025-26 actuals...")
stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2025-26")
df = stats.get_data_frames()[0]

# keep only what we need
df = df[["PLAYER_NAME", "GP", "PTS", "REB", "AST"]].copy()

# convert totals to per game
df["actual_ppg"] = (df["PTS"] / df["GP"]).round(1)
df["actual_rpg"] = (df["REB"] / df["GP"]).round(1)
df["actual_apg"] = (df["AST"] / df["GP"]).round(1)

# clean up
df = df.rename(columns={"PLAYER_NAME": "player_name"})
df = df[["player_name", "actual_ppg", "actual_rpg", "actual_apg"]]

# save
df.to_csv("csv/actuals.csv", index=False)
print(f"Saved {len(df)} players to csv/actuals.csv")
