# 🏀 NBA Player Performance Predictor

Predicts next-season points per game (PPG) for NBA players, now with an LLM-powered explanation of each prediction.

<sub>*I originally built this to learn how to train a model and use FastAPI, but I actually want it to be functional and reusable going forward, so I'll be periodically updating it.*</sub>

## 🔗 Live Links
- **Frontend:** https://jwiggins973.github.io/nba-predictor/
- **API:** https://nba-predictor-fu6x.onrender.com
- **Tableau Dashboard:** https://public.tableau.com/views/NBA_Predictor/Dashboard1

## 🛠 Stack
- **ML:** Python, Scikit-learn, SHAP, Pandas
- **Backend:** FastAPI
- **LLM:** Anthropic Claude API (Haiku)
- **Frontend:** React, Vite, Recharts
- **BI:** Tableau Public
- **Deployment:** Docker, GitHub Container Registry, Render, GitHub Pages
- **CI/CD:** GitHub Actions

## ⚙️ How It Works
1. Random Forest model trained on 12,000+ NBA player seasons (1996-2024)
2. 3-season rolling window lag features fed into the model
3. SHAP values explain which features drove each prediction
4. FastAPI serves predictions via REST API
5. Once a player's actual next-season stats are in, Claude explains the gap between predicted and actual PPG in plain language
6. React frontend displays results with career scoring chart
7. Tableau dashboard visualizes predicted vs actual PPG with SHAP feature importance
8. A daily GitHub Actions cron job (during the NBA season) pulls fresh stats and updates the dataset automatically

## 💻 Run Locally
```bash
# Backend
cd backend
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your-key-here" > .env  # needed for the /explain endpoint
uvicorn app:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 🐳 Docker
```bash
docker pull ghcr.io/jwiggins973/nba-predictor-backend:latest
docker run -p 8000:8000 ghcr.io/jwiggins973/nba-predictor-backend:latest
```

## 🧪 Tests
```bash
# Backend (after Run Locally setup)
cd backend
pytest test_app.py

# End-to-end
cd e2e
npm install
npx playwright install --with-deps
npx playwright test
```

## 📊 Model Performance
- R²: 0.83
- MAE: 2.22 PPG
- RMSE: 2.91 PPG
- Train: 1996-2024 | Test: 2024-25 | Forecast: 2025-26

## 📌 Coming soon
- Backfill `player_id` onto historical data and migrate CSVs to SQLite
- Phase 2: per-game player stat prediction model

