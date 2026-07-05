import time
from datetime import datetime
import os

import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerbiostats


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


def fetch_bio_stats(season):
    for attempt in range(3):
        try:
            bio_stats = leaguedashplayerbiostats.LeagueDashPlayerBioStats(
                season=season,
                per_mode_simple="PerGame",
                timeout=60,
                proxy=os.getenv("NBA_PROXY_URL"),
            )
            break
        except Exception as e:
            print(f"Bio stats request failed (attempt {attempt + 1}): {e}")
            if attempt == 2:
                raise
            time.sleep(5)
    return bio_stats


if is_in_season():
    current_season = get_current_season_yr()
    previous_season = get_previous_season_yr()

    # check if previous yr in actual so can append
    df1 = pd.read_csv("csv/all_seasons.csv")
    if previous_season in df1["season"].values:
        print("Actuals for the previous season already exist.")
    else:
        # append to  all_seasons.csv
        bio_stats = fetch_bio_stats(previous_season)
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
        print(
            f"Appended {len(df_bio)} players for {previous_season} to all_seasons.csv"
        )

    print("Fetching " + current_season + " actuals...")
    stats = fetch_bio_stats(current_season)
    df = stats.get_data_frames()[0]

    # keep only what we need
    df = df[
        [
            "PLAYER_ID",
            "PLAYER_NAME",
            "AGE",
            "PTS",
            "REB",
            "AST",
            "USG_PCT",
            "TS_PCT",
            "NET_RATING",
            "GP",
        ]
    ].copy()
    df["player_id"] = df["PLAYER_ID"]
    df["actual_age"] = df["AGE"]
    df["actual_ppg"] = df["PTS"].round(1)
    df["actual_rpg"] = df["REB"].round(1)
    df["actual_apg"] = df["AST"].round(1)
    df["actual_usg_pct"] = df["USG_PCT"].round(3)
    df["actual_ts_pct"] = df["TS_PCT"].round(3)
    df["actual_net_rating"] = df["NET_RATING"].round(3)
    df["actual_gp"] = df["GP"]

    # clean up
    df = df.rename(columns={"PLAYER_NAME": "player_name"})
    df = df[
        [
            "player_id",
            "player_name",
            "actual_age",
            "actual_ppg",
            "actual_rpg",
            "actual_apg",
            "actual_usg_pct",
            "actual_ts_pct",
            "actual_net_rating",
            "actual_gp",
        ]
    ]

    # save
    df.to_csv("csv/actuals.csv", index=False)
    print(f"Saved {len(df)} players to csv/actuals.csv")
else:
    print("Not in a season to fetch actuals.")
