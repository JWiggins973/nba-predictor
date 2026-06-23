import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from config import FEATURES


def export_all(model, df, df_for_forecast, x_test, y_test, shap_values):

    y_pred = model.predict(x_test)

    # 1. metrics.csv
    score = model.score(x_test, y_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    pd.DataFrame(
        {
            "metric": ["R2", "MAE", "RMSE"],
            "value": [round(score, 4), round(mae, 4), round(rmse, 4)],
        }
    ).to_csv("csv/metrics.csv", index=False)
    print("Saved csv/metrics.csv")

    # 2. shap_values.csv
    pd.DataFrame(
        {
            "feature": x_test.columns,
            "mean_shap_value": np.abs(shap_values.values).mean(axis=0).round(4),
        }
    ).sort_values("mean_shap_value", ascending=False).to_csv(
        "csv/shap_values.csv", index=False
    )
    print("Saved csv/shap_values.csv")

    # 3. predictions.csv — 2025-26 forecast using true latest season per player
    latest = (
        df_for_forecast.sort_values("season")
        .groupby("player_name")
        .last()
        .reset_index()
    )
    latest = latest.dropna(subset=FEATURES)
    latest["predicted_ppg"] = model.predict(latest[FEATURES]).round(1)
    latest["season"] = "2025-26"

    latest[["player_name", "season", "predicted_ppg"]].to_csv(
        "csv/predictions.csv", index=False
    )
    print(f"Saved csv/predictions.csv — {len(latest)} players forecast for 2025-26")
