# 🏀 NBA Player Performance Predictor

Predicts a player's next-season points per game (PPG), with an AI-written explanation of each prediction.

<sub>*I built this to learn how to train a model and use FastAPI. I want it to stay useful, so I'll keep updating it.*</sub>

## 🔗 Live Links
- **Frontend:** https://jwiggins973.github.io/nba-predictor/
- **API:** https://nba-predictor-fu6x.onrender.com
- **Tableau Dashboard:** https://public.tableau.com/views/NBA_Predictor/Dashboard1

## 🛠 Stack
- **ML:** Python, Scikit-learn, SHAP, Pandas
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL (Aiven)
- **LLM:** Google Gemini
- **Frontend:** React, Vite, Recharts
- **Deployment:** Docker, GitHub Container Registry, Render, GitHub Pages
- **CI/CD:** GitHub Actions

## ⚙️ How It Works
- A Random Forest model is trained on 12,000+ NBA player seasons (1996-2024) from PostgreSQL
- Each player's last 3 seasons are used as the model's inputs
- SHAP values show which stats drove each prediction
- FastAPI serves the predictions and the React frontend displays them
- Once a player's actual stats are in, Gemini explains the gap between predicted and actual PPG
- A local script (`update_actuals.sh`) runs weekly to pull fresh stats from the NBA API into the database
- Once a season the script also retrains the model, and I commit the new model files to redeploy

## 💻 Run Locally
```bash
# Backend
cd backend
pip install -r requirements.txt
echo "GEMINI_API_KEY=your-key-here" > .env
echo "DATABASE_URL=your-postgres-url-here" >> .env
uvicorn app:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

After the first setup, `./dev.sh` from the repo root starts both. Press Ctrl+C twice to stop.

## 🐳 Docker
```bash
docker run -p 8000:8000 --env-file backend/.env ghcr.io/jwiggins973/nba-predictor-backend:latest
```

## 🧪 Tests
```bash
cd backend && pytest test_app.py      # backend
cd e2e && npm install && npx playwright install --with-deps && npx playwright test   # end-to-end
```

## 📊 Model Performance
- R²: 0.83
- MAE: 2.29 PPG
- RMSE: 2.94 PPG

## 📌 Coming soon
- Query Postgres per request instead of loading full tables at startup
- A second model that predicts per-game player stats
