import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats

# Fetch 2023-24 actuals
print("Fetching 2024-25 stats...")
stats = leaguedashplayerstats.LeagueDashPlayerStats(season="2025-26")
df_actual = stats.get_data_frames()[0]

# Keep only what we need
df_actual = df_actual[["PLAYER_NAME", "PTS", "GP"]].copy()
df_actual.columns = ["player_name", "actual_ppg", "gp"]

# Convert total points to per game
df_actual["actual_ppg"] = (df_actual["actual_ppg"] / df_actual["gp"]).round(1)

# Load predictions, keeping only the most recent season per player
df_pred = pd.read_csv("csv/predictions.csv")
df_pred = df_pred.sort_values("season").groupby("player_name").last().reset_index()
df_pred = df_pred[["player_name", "predicted_ppg"]]
merged = df_pred.merge(df_actual, on="player_name", how="inner")

# Calculate MAE
merged["error"] = (merged["predicted_ppg"] - merged["actual_ppg"]).abs()
mae = merged["error"].mean()

print(f"\nPlayers matched: {len(merged)}")
print(f"MAE: {mae:.2f} PPG")
print("\nSample predictions vs actuals:")
print(
    merged[["player_name", "predicted_ppg", "actual_ppg", "error"]]
    .sort_values("error", ascending=False)
    .head(10)
    .to_string(index=False)
)
