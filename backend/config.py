PEAK_AGE = 30

LAG_COLS = [
    "age",
    "years_from_peak",
    "decline_rate",
    "gp",
    "player_height",
    "player_weight",
    "reb",
    "ast",
    "net_rating",
    "oreb_pct",
    "dreb_pct",
    "usg_pct",
    "ts_pct",
    "ast_pct",
    "pts",
]

FEATURES = (
    [f"lag_{col}" for col in LAG_COLS]
    + [f"lag1_{col}" for col in LAG_COLS]
    + [f"lag2_{col}" for col in LAG_COLS]
)

MAX_TOKENS = 300
MAX_DAILY_CALLS = 10
