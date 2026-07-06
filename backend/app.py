import os
from sqlalchemy import create_engine
import joblib
import pandas as pd
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import MAX_DAILY_CALLS, MAX_TOKENS, PEAK_AGE, LAG_COLS, FEATURES
from google import genai
from google.genai import types

load_dotenv()

# Global variables to hold the model and dataset
model = None
explainer = None
df = None
df_actuals = None
api_cache = {}
daily_counter = 0


# Helper function to get player data
def get_player_data(player_name: str):
    data = df[df["player_name"].str.lower() == player_name.lower()]
    if data.empty:
        raise HTTPException(status_code=404, detail=f"Player '{player_name}' not found")
    return data


# get last 3 seasons for lag features
def get_last_3_seasons(player_data):
    seasons = player_data.sort_values("season").tail(3)
    lag0 = seasons.iloc[-1]
    lag1 = seasons.iloc[-2] if len(seasons) >= 2 else lag0
    lag2 = seasons.iloc[-3] if len(seasons) >= 3 else lag1
    return lag0, lag1, lag2


# build input features
def build_input_features(lag0, lag1, lag2):
    input_features = {}
    for col in LAG_COLS:
        input_features[f"lag_{col}"] = lag0[col]
        input_features[f"lag1_{col}"] = lag1[col]
        input_features[f"lag2_{col}"] = lag2[col]
    return input_features


# Helper function to create a summary row
def summary_row(row):
    return {
        "age": int(row["age"]),
        "reb": round(float(row["reb"]), 1),
        "ast": round(float(row["ast"]), 1),
        "usg_pct": round(float(row["usg_pct"]), 3),
        "ts_pct": round(float(row["ts_pct"]), 3),
        "net_rating": round(float(row["net_rating"]), 3),
        "gp": int(row["gp"]),
    }


# Helper function to create a summary row for actual stats
def actual_summary_row(row):
    return {
        "age": int(row["actual_age"]),
        "reb": round(float(row["actual_rpg"]), 1),
        "ast": round(float(row["actual_apg"]), 1),
        "usg_pct": round(float(row["actual_usg_pct"]), 3),
        "ts_pct": round(float(row["actual_ts_pct"]), 3),
        "net_rating": round(float(row["actual_net_rating"]), 3),
        "gp": int(row["actual_gp"]),
    }


# Helper function to get prediction data
def get_prediction_data(player_name: str):
    player_data = get_player_data(player_name)

    # get last 3 seasons for lag features
    lag0, lag1, lag2 = get_last_3_seasons(player_data)

    # build input features
    input_features = build_input_features(lag0, lag1, lag2)

    input_df = pd.DataFrame([input_features])[FEATURES]
    predicted_ppg = model.predict(input_df)[0]

    shap_results = pd.Series(explainer(input_df)[0].values, index=FEATURES)
    shap_results = shap_results.drop(["lag_pts", "lag1_pts", "lag2_pts"])
    order = shap_results.abs().sort_values(ascending=False).index
    shap_results = shap_results.loc[order[:3]]

    # lookup actual 2025-26 stats
    actual_row = df_actuals[
        df_actuals["player_name"].str.lower() == player_name.lower()
    ]
    actual_season_stats = {}
    if not actual_row.empty:
        actual_season_stats = actual_summary_row(actual_row.iloc[0])

    actual_ppg = (
        round(float(actual_row.iloc[0]["actual_ppg"]), 1)
        if not actual_row.empty
        else None
    )
    return {
        "player": lag0["player_name"],
        "team": lag0["team_abbreviation"],
        "last_season": lag0["season"],
        "last_season_ppg": round(float(lag0["pts"]), 1),
        "predicted_ppg": round(float(predicted_ppg), 1),
        "actual_ppg": actual_ppg,
        "last_season_stats": summary_row(lag0),
        "last_season_stats_1": summary_row(lag1),
        "last_season_stats_2": summary_row(lag2),
        "actual_stats": actual_season_stats,
        "top_shap_values": shap_results.round(2).to_dict(),
    }


# Helper function to build the prompt for the AI
def prompt_builder(explain_data):
    return (
        f"{explain_data['player']} was predicted to score {explain_data['predicted_ppg']} points per game, "
        f"but actually scored {explain_data['actual_ppg']} points per game. "
        f"The prediction was based on these past 3 seasons: {explain_data['last_season_stats']}, "
        f"{explain_data['last_season_stats_1']}, {explain_data['last_season_stats_2']}. "
        f"Here are the top 3 factors that influenced the prediction: {explain_data['top_shap_values']}. "
        f"Here is what actually happened this season: {explain_data['actual_stats']}. "
        "Analyze this NBA player prediction using the SHAP values and the player's last three seasons of "
        "statistics. Provide the explanation in exactly two sections: "
        "## Why the model made this prediction "
        "Using the top SHAP factors and the last 3 seasons of stats, explain why the model predicted "
        f"{explain_data['predicted_ppg']} points per game. "
        "## What actually happened "
        "Using the actual stats provided, explain how the real performance compared to the prediction. "
        "Format each section as 2-3 markdown bullet points, each starting with '- ' and no longer than one "
        "short sentence. Never reference raw column names like lag_usg_pct, lag2_ast, or ts_pct — always use "
        "the plain stat name a basketball fan would recognize, like usage rate, assists, or true shooting "
        "percentage. "
        "Keep the explanation concise and easy for a basketball fan to understand. "
        "Do not invent additional seasons, stats, or projections beyond what is given."
    )


# Load the model and dataset during application startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, df, df_actuals, explainer
    model = joblib.load("nba_model.pkl")
    explainer = joblib.load("nba_explainer.pkl")

    # open connection and read into pandas DataFrames
    engine = create_engine(os.getenv("DATABASE_URL"))
    df = pd.read_sql("SELECT * FROM allseason", engine)
    df_actuals = pd.read_sql("SELECT * FROM actuals", engine)
    engine.dispose()

    df = df.sort_values(by=["player_name", "season"])

    # compute age curve columns so they're ready for prediction
    df["years_from_peak"] = df["age"] - PEAK_AGE
    df["decline_rate"] = df["years_from_peak"].apply(
        lambda x: -(x**2) if x < 0 else x**2
    )
    yield


# Initialize the FastAPI application
app = FastAPI(
    title="NBA Player Performance Prediction", version="1.0.0", lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        os.getenv("CORS_ORIGIN", "http://localhost:5173"),
        "https://jwiggins973.github.io",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


# Define API endpoints
@app.get("/")
def health_check():
    return {"message": "NBA Player Performance Prediction API is running."}


# Get a list of all players
@app.get("/players")
def get_players():
    players = sorted(df["player_name"].dropna().unique().tolist())
    return {"players": players}


# GET Player History
@app.get("/history/{player_name}")
def history(player_name: str):
    player_data = get_player_data(player_name)

    seasons = player_data[["season", "pts"]].dropna()
    result = []
    for row in seasons.itertuples():
        result.append({"season": row.season, "ppg": round(float(row.pts), 1)})

    return {"history": result}


# Get predicted ppg
@app.get("/predict/{player_name}")
def predict(player_name: str):
    return get_prediction_data(player_name)


# explain a prediction
@app.get("/explain/{player_name}")
def explain(player_name: str):
    explain_data = get_prediction_data(player_name)
    if explain_data["actual_ppg"] is None:
        raise HTTPException(
            status_code=404,
            detail="No actual performance data available for this player.",
        )

    global daily_counter
    if player_name in api_cache:
        return {"explanation": api_cache[player_name]}

    else:

        if daily_counter >= MAX_DAILY_CALLS:
            raise HTTPException(
                status_code=429,
                detail="Daily API call limit exceeded.",
            )

        else:
            if os.getenv("GEMINI_API_KEY") is None:
                return {"explanation": "GEMINI_API_KEY is not set."}
            else:
                # write gemini prompt
                prompt = prompt_builder(explain_data)
                # Call the Gemini API
                client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=MAX_TOKENS,
                        thinking_config=types.ThinkingConfig(thinking_budget=0),
                    ),
                )
                api_cache[player_name] = response.text
                daily_counter += 1
                return {"explanation": response.text}
