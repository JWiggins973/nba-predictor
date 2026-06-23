from datetime import datetime

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashplayerbiostats


# fetch season year
def get_current_season_yr():
    if datetime.now().month >= 10:
        # If the current month is October or later, we're in the middle of the season
        return str(datetime.now().year) + "-" + str(datetime.now().year + 1)[-2:]
    else:
        return str(datetime.now().year - 1) + "-" + str(datetime.now().year)[-2:]


# Check if we are in the a season to pull data
def is_in_season():
    if datetime.now().month >= 10 or datetime.now().month <= 6:
        return True
    else:
        return False


def get_previous_season_yr():
    current = get_current_season_yr()
    return (
        str(int(current.split("-")[0]) - 1) + "-" + str(int(current.split("-")[0][-2:]))
    )


if is_in_season():
    current_season = get_current_season_yr()
    previous_season = get_previous_season_yr()

    # check if previous yr in actual so can append
    df1 = pd.read_csv("csv/all_seasons.csv")
    if previous_season in df1["season"].values:
        print("Actuals for the previous season already exist.")
    else:
        # append to  all_seasons.csv
        bio_stats = leaguedashplayerbiostats.LeagueDashPlayerBioStats(
            season=previous_season, per_mode_simple="PerGame"
        )
        df_bio = bio_stats.get_data_frames()[0]

        # convert height from feet-inches string (e.g. "6-6") to centimeters
        height_parts = df_bio["PLAYER_HEIGHT"].str.split("-")
        feet = height_parts.str[0].astype(int)
        inches = height_parts.str[1].astype(int)
        df_bio["PLAYER_HEIGHT"] = (feet * 12 + inches) * 2.54

        # convert weight from pounds to kilograms
        df_bio["PLAYER_WEIGHT"] = df_bio["PLAYER_WEIGHT"].astype(float) * 0.453592

        # rename columns to match all_seasons.csv's schema (every nba_api
        # column name is just the uppercase version of our column name)
        df_bio.columns = df_bio.columns.str.lower()
        df_bio["season"] = previous_season
        df_bio = df_bio[df1.columns]

        # append and save
        df1 = pd.concat([df1, df_bio], ignore_index=True)
        df1.to_csv("csv/all_seasons.csv", index=False)
        print(f"Appended {len(df_bio)} players for {previous_season} to all_seasons.csv")

    print("Fetching " + current_season + " actuals...")
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season=current_season)
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
else:
    print("Not in a season to fetch actuals.")
