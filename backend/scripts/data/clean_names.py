import pandas as pd
import unicodedata


# strip accents from a string
def strip_accents(name):
    text = unicodedata.normalize("NFD", name)
    stripped = ""
    for c in text:
        if not unicodedata.combining(c):
            stripped += c
    return stripped


# Clean a name by removing accents and non-alphanumeric characters
def clean_name(name):
    text = strip_accents(name)
    cleaned = ""
    for c in text:
        if c.isalnum() or c.isspace():
            cleaned += c
    return " ".join(cleaned.split())


# Function to check if a name has accents
def has_accent(name):
    text = strip_accents(name)
    if text != name:
        return True
    return False


# Clean player names in the dataset
df = pd.read_csv("csv/all_seasons.csv")
df["cleaned_name"] = df["player_name"].apply(clean_name)

# Find collisions in the cleaned names
groups = df.groupby("cleaned_name")["player_name"].unique()
# Find all groups with more than one player naming convention
collisions = groups[groups.apply(len) > 1]

# Map every "wrong" spelling in a collision group to the one we want to keep
rename_map = {}
for name, players in collisions.items():
    accent_name = None
    correct_name = None
    # check if any player has an accent
    for player in players:

        if has_accent(player):
            # use the accent version
            accent_name = player

    if accent_name is None:
        for p in players:
            if "." not in p:
                correct_name = p

    if accent_name is not None:
        correct_name = accent_name

    # Every spelling in this group besides the chosen one maps to it
    for player in players:
        if player != correct_name:
            rename_map[player] = correct_name

# Apply the corrections, drop the helper column, and save the result
df["player_name"] = df["player_name"].replace(rename_map)
df = df.drop(columns=["cleaned_name"])
df.to_csv("csv/all_seasons_cleaned.csv", index=False)
