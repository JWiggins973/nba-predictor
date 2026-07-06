import os
import sys
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

backend_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, backend_dir)

import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from config import PEAK_AGE, LAG_COLS, FEATURES
from exports import export_all

# Load the data
engine = create_engine(os.getenv("DATABASE_URL"))
df = pd.read_sql("SELECT * FROM allseason", engine)
engine.dispose()

# drop ts_pct outliers
df = df[(df["ts_pct"] > 0.0) & (df["ts_pct"] <= 1.0)]

# sort by player name and season
df = df.sort_values(by=["player_name", "season"]).reset_index(drop=True)

# predict next season
df["next_pts"] = df.groupby("player_name")["pts"].shift(-1)

# age curve
df["years_from_peak"] = df["age"] - PEAK_AGE
df["decline_rate"] = df["years_from_peak"].apply(lambda x: -(x**2) if x < 0 else x**2)

# lag features
for col in LAG_COLS:
    df[f"lag_{col}"] = df.groupby("player_name")[col].shift(0)
    df[f"lag1_{col}"] = df.groupby("player_name")[col].shift(1)
    df[f"lag2_{col}"] = df.groupby("player_name")[col].shift(2)

# save full df before dropna for forecasting
df_for_forecast = df.copy()

# drop rows with missing values
df = df.dropna(subset=FEATURES + ["next_pts"])
print(f"Rows after lag: {len(df)}")

# time-based train/test split
train = df[df["season"] < "2019-20"]
test = df[df["season"] >= "2019-20"]

x_train = train[FEATURES]
y_train = train["next_pts"]
x_test = test[FEATURES]
y_test = test["next_pts"]

print(f"Training Rows: {len(x_train)}")
print(f"Testing Rows: {len(x_test)}")

# train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(x_train, y_train)

# SHAP
explainer = shap.TreeExplainer(model)
shap_values = explainer(x_test)

shap.summary_plot(shap_values, x_test, plot_type="bar", show=False)
plt.title("SHAP Feature Importance")
plt.tight_layout()
plt.savefig("shap_summary_plot.png")

# evaluate
score = model.score(x_test, y_test)
print(f"R²: {score:.4f}")
print("Model trained!")

# save model
joblib.dump(model, "nba_model.pkl")
print("Model saved to nba_model.pkl")
joblib.dump(explainer, "nba_explainer.pkl")
print("Explainer saved to nba_explainer.pkl")

# export all files
export_all(model, df, df_for_forecast, x_test, y_test, shap_values)
