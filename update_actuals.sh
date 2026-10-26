#!/bin/zsh
set -e
cd /Users/jw/nba-predictor/backend
source ../venv/bin/activate

# local database: URL comes from backend/.env
python3 scripts/data/fetch_actual.py

# Aiven: URL comes from a separate file, so it overrides .env for this run
set -a
source .env.aiven
set +a
python3 scripts/data/fetch_actual.py
