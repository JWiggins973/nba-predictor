# 🏀 NBA Player Performance Predictor

Predicts next-season points per game (PPG) for NBA players using a Random Forest model with SHAP explainability.

## 🔗 Live Links
- **Frontend:** https://jwiggins973.github.io/nba-predictor/
- **API:** https://nba-predictor-fu6x.onrender.com
- **Tableau Dashboard:** https://public.tableau.com/views/NBA_Predictor/Dashboard1

## 🐳 Docker
```bash
docker pull ghcr.io/jwiggins973/nba-predictor-backend:latest
docker run -p 8000:8000 ghcr.io/jwiggins973/nba-predictor-backend:latest
```

## 🛠 Stack
- **ML:** Python, Scikit-learn, SHAP, Pandas
- **Backend:** FastAPI
- **Frontend:** React, Vite, Recharts
- **BI:** Tableau Public
- **Deployment:** Docker, GitHub Container Registry, Render, GitHub Pages
- **CI/CD:** GitHub Actions

## ⚙️ How It Works
1. Random Forest model trained on 12,000+ NBA player seasons (1996-2024)
2. 3-season rolling window lag features fed into the model
3. SHAP values explain which features drove each prediction
4. FastAPI serves predictions via REST API
5. React frontend displays results with career scoring chart
6. Tableau dashboard visualizes predicted vs actual PPG with SHAP feature importance

## 💻 Run Locally
```bash
# Backend
pip install -r requirements.txt
uvicorn app:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📊 Model Performance
- R²: 0.83
- MAE: 2.22 PPG
- RMSE: 2.91 PPG
- Train: 1996-2024 | Test: 2024-25 | Forecast: 2025-26
