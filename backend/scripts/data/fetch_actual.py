import os
import time
from datetime import datetime
from sqlalchemy import create_engine, text
import numpy as np
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerbiostats

ALLSEASON_COLUMNS = [
    "player_name",
    "team_abbreviation",
    "age",
    "player_height",
    "player_weight",
    "college",
    "country",
    "draft_year",
    "draft_round",
    "draft_number",
    "gp",
    "pts",
    "reb",
    "ast",
    "net_rating",
    "oreb_pct",
    "dreb_pct",
    "usg_pct",
    "ts_pct",
    "ast_pct",
    "season",
    "player_id",
]


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

    # check if previous yr in allseason so can append
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        results = conn.execute(
            text("SELECT 1 FROM allseason WHERE season = :season LIMIT 1"),
            {"season": previous_season},
        )
        already_exists = results.first() is not None

    if already_exists:
        print("Actuals for the previous season already exist.")
    else:
        # append to allseason rows
        bio_stats = fetch_bio_stats(previous_season)
        df_bio = bio_stats.get_data_frames()[0]

        # convert height from feet-inches string (e.g. "6-6") to centimeters
        height_parts = df_bio["PLAYER_HEIGHT"].str.split("-")
        feet = height_parts.str[0].astype(int)
        inches = height_parts.str[1].astype(int)
        df_bio["PLAYER_HEIGHT"] = (feet * 12 + inches) * 2.54

        # convert weight from pounds to kilograms
        df_bio["PLAYER_WEIGHT"] = df_bio["PLAYER_WEIGHT"].astype(float) * 0.453592

        # keep only what we need
        df_bio.columns = df_bio.columns.str.lower()
        df_bio["season"] = previous_season

        df_bio["draft_year"] = pd.to_numeric(df_bio["draft_year"], errors="coerce")
        df_bio = df_bio.replace(
            {np.nan: None}
        )  # Replace NaN with real None for SQL insertion
        df_bio = df_bio[ALLSEASON_COLUMNS]

        with engine.begin() as conn:
            df_bio.to_sql("allseason", conn, if_exists="append", index=False)
        print(f"Appended {len(df_bio)} players from {previous_season}")

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
    ].rename(
        columns={
            "PLAYER_ID": "player_id",
            "PLAYER_NAME": "player_name",
            "AGE": "actual_age",
            "PTS": "actual_ppg",
            "REB": "actual_rpg",
            "AST": "actual_apg",
            "USG_PCT": "actual_usg_pct",
            "TS_PCT": "actual_ts_pct",
            "NET_RATING": "actual_net_rating",
            "GP": "actual_gp",
        }
    )

    # save to database
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE actuals;"))
        df.to_sql("actuals", conn, if_exists="append", index=False)
    engine.dispose()
    print(f"Saved {len(df)} players to actuals table in database.")
