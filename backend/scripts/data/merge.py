import pandas as pd
from clean_names import clean_name

allseasons_df = pd.read_csv("csv/all_seasons_cleaned.csv")
lookup_df = pd.read_csv("csv/player_lookup.csv")

# exact match, same as your very first merge.py
merged = pd.merge(allseasons_df, lookup_df, on="player_name", how="left")

matched = merged[merged["player_id"].notna()]
unmatched = merged[merged["player_id"].isna()].copy()

# build match_key on the leftover unmatched rows, and on lookup_df
unmatched["match_key"] = unmatched["player_name"].apply(clean_name)
lookup_df["match_key"] = lookup_df["player_name"].apply(clean_name)

# find which match_keys are safe to use (unique — no collision)
key_counts = lookup_df["match_key"].value_counts()
safe_keys = key_counts[key_counts == 1].index
safe_lookup_df = lookup_df[lookup_df["match_key"].isin(safe_keys)]

# drop the old all-NaN player_id column, then re-merge the leftovers
# on match_key, against only the safe subset of lookup_df
unmatched = unmatched.drop(columns=["player_id"])
fallback = pd.merge(
    unmatched, safe_lookup_df[["match_key", "player_id"]], on="match_key", how="left"
)

# fix some of the remaining unmatched players manually (these are all just typos or suffixes, so we can just hardcode them)
manual_ids = {
    "Enes Kanter": 202683,
    "RJ Nembhard Jr.": 1630612,
    "Jeenathan Williams": 1631466,
}

for player_name, player_id in manual_ids.items():
    fallback.loc[fallback["player_name"] == player_name, "player_id"] = player_id

# stitch both passes back together
final = pd.concat([matched, fallback], ignore_index=True)
print("still unmatched after both passes:", final["player_id"].isna().sum())
final.to_csv("csv/all_seasons_with_player_id.csv", index=False)
