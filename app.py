import os
import joblib
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import PEAK_AGE, LAG_COLS, FEATURES

# Global variables to hold the model and dataset
model = None
df = None
df_actuals = None


# Helper function to get player data
def get_player_data(player_name: str):
    data = df[df["player_name"].str.lower() == player_name.lower()]
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
    return data


# Load the model and dataset during application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, df, df_actuals
    model = joblib.load("nba_model.pkl")
    df = pd.read_csv("csv/all_seasons.csv")
    df = df.sort_values(by=["player_name", "season"])

    # compute age curve columns so they're ready for prediction
    df["years_from_peak"] = df["age"] - PEAK_AGE
    df["decline_rate"] = df["years_from_peak"] ** 2
    df_actuals = pd.read_csv("csv/actuals.csv")
    yield


app = FastAPI(
    title="NBA Player Performance Prediction", version="1.0.0", lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN", "http://localhost:5173")],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# Define API endpoints
@app.get("/")
def health_check():
    return {"message": "NBA Player Performance Prediction API is running."}


@app.get("/players")
def get_players():
    players = sorted(df["player_name"].dropna().unique().tolist())
    return {"players": players}


@app.get("/history/{player_name}")
def history(player_name: str):
    player_data = get_player_data(player_name)

    seasons = player_data[["season", "pts"]].dropna()
    result = []
    for row in seasons.itertuples():
        result.append({"season": row.season, "ppg": round(float(row.pts), 1)})

    return {"history": result}


@app.get("/predict/{player_name}")
def predict(player_name: str):
    player_data = get_player_data(player_name)

    # get last 3 seasons for lag features
    seasons = player_data.sort_values("season").tail(3)
    lag0 = seasons.iloc[-1]
    lag1 = seasons.iloc[-2] if len(seasons) >= 2 else lag0
    lag2 = seasons.iloc[-3] if len(seasons) >= 3 else lag1

    # build input features
    input_features = {}
    for col in LAG_COLS:
        input_features[f"lag_{col}"] = lag0[col]
        input_features[f"lag1_{col}"] = lag1[col]
        input_features[f"lag2_{col}"] = lag2[col]

    input_df = pd.DataFrame([input_features])[FEATURES]
    predicted_ppg = model.predict(input_df)[0]

    # lookup actual 2025-26 stats
    actual_row = df_actuals[
        df_actuals["player_name"].str.lower() == player_name.lower()
    ]
    actual_ppg = (
        round(float(actual_row.iloc[0]["actual_ppg"]), 1)
        if not actual_row.empty
        else None
    )

    # return prediction and last season stats
    return {
        "player": lag0["player_name"],
        "team": lag0["team_abbreviation"],
        "last_season": lag0["season"],
        "last_season_ppg": round(float(lag0["pts"]), 1),
        "predicted_ppg": round(float(predicted_ppg), 1),
        "actual_ppg": actual_ppg,
        "last_season_stats": {
            "age": int(lag0["age"]),
            "reb": round(float(lag0["reb"]), 1),
            "ast": round(float(lag0["ast"]), 1),
            "usg_pct": round(float(lag0["usg_pct"]), 3),
            "ts_pct": round(float(lag0["ts_pct"]), 3),
        },
    }
