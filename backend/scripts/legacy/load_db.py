import os
import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "csv")


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


def load_lookup(conn):
    # read csv/player_lookup.csv with pandas, TRUNCATE the lookup
    df = pd.read_csv(os.path.join(CSV_DIR, "player_lookup.csv"))
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE lookup;")
        for row in df.itertuples():
            cur.execute(
                """
                INSERT INTO lookup (player_id, player_name) VALUES (%s, %s)
                """,
                (row.player_id, row.player_name),
            )


def load_allseason(conn):
    #  read csv/all_seasons.csv, TRUNCATE allseason, loop + INSERT.
    df = pd.read_csv(os.path.join(CSV_DIR, "all_seasons.csv"))

    missing_id_count = df["player_id"].isna().sum()
    if missing_id_count > 0:
        print(f"Skipping {missing_id_count} rows with no player_id")
        df = df[df["player_id"].notna()]

    df["player_id"] = df["player_id"].astype(int)
    # draft_round/draft_number can be the string "Undrafted", and so can
    # draft_year -- coerce it to a real number (or NaN) before the NaN->None pass
    df["draft_year"] = pd.to_numeric(df["draft_year"], errors="coerce")
    df = df.replace({np.nan: None})  # Replace NaN with real None for SQL insertion

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE allseason;")
        for rows in df.itertuples():
            cur.execute(
                """
                INSERT INTO allseason (
                    player_id, player_name, age, player_height, player_weight, college,
                    draft_year, draft_round, draft_number, gp, pts, reb, ast,
                    net_rating, oreb_pct, dreb_pct, usg_pct, ts_pct,
                    ast_pct, season, team_abbreviation, country
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    rows.player_id,
                    rows.player_name,
                    rows.age,
                    rows.player_height,
                    rows.player_weight,
                    rows.college,
                    rows.draft_year,
                    rows.draft_round,
                    rows.draft_number,
                    rows.gp,
                    rows.pts,
                    rows.reb,
                    rows.ast,
                    rows.net_rating,
                    rows.oreb_pct,
                    rows.dreb_pct,
                    rows.usg_pct,
                    rows.ts_pct,
                    rows.ast_pct,
                    rows.season,
                    rows.team_abbreviation,
                    rows.country,
                ),
            )


def load_actuals(conn):
    df = pd.read_csv(os.path.join(CSV_DIR, "actuals.csv"))

    missing_id_count = df["player_id"].isna().sum()
    if missing_id_count > 0:
        print(f"Skipping {missing_id_count} rows with no player_id")
        df = df[df["player_id"].notna()]

    df["player_id"] = df["player_id"].astype(int)
    df = df.replace({np.nan: None})

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE actuals;")
        for rows in df.itertuples():
            cur.execute(
                """INSERT INTO actuals (player_id, player_name, actual_age, actual_ppg, actual_rpg, actual_usg_pct, actual_ts_pct, actual_net_rating, actual_gp, actual_apg) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    rows.player_id,
                    rows.player_name,
                    rows.actual_age,
                    rows.actual_ppg,
                    rows.actual_rpg,
                    rows.actual_usg_pct,
                    rows.actual_ts_pct,
                    rows.actual_net_rating,
                    rows.actual_gp,
                    rows.actual_apg,
                ),
            )


def load_predictions(conn):
    # read csv/predictions.csv, TRUNCATE predictions, loop + INSERT.
    df = pd.read_csv(os.path.join(CSV_DIR, "predictions.csv"))
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE predictions;")
        for rows in df.itertuples():
            cur.execute(
                """INSERT INTO predictions (player_name, predicted_ppg,season) VALUES (%s, %s, %s)""",
                (
                    rows.player_name,
                    rows.predicted_ppg,
                    rows.season,
                ),
            )


if __name__ == "__main__":
    conn = get_connection()

    load_lookup(conn)
    load_allseason(conn)
    load_actuals(conn)
    load_predictions(conn)

    conn.commit()
    conn.close()
    print("Done loading all tables.")
