import time
import pandas as pd

from nba_api.stats.static.players import get_players


def fetch_player_id():
    for attempt in range(3):
        try:
            player_id = get_players()
        except Exception as e:
            print(f"Player ID request failed (attempt {attempt + 1}): {e}")
            if attempt == 2:
                raise
            time.sleep(5)
    return player_id


player_id = fetch_player_id()

# clean up player names and create a DataFrame remove periods and suffixes from player names
player_id = [
    {
        "player_name": player["full_name"],
        "player_id": player["id"],
    }
    for player in player_id
]

df = pd.DataFrame(player_id, columns=["player_name", "player_id"])

df.to_csv("csv/player_lookup.csv", index=False)
print("Player lookup CSV file created successfully.")
print("Total players fetched:", len(df))
