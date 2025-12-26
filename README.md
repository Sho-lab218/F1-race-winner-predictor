# 🏎️ F1 Race Winner Prediction System

A full-stack machine learning application that predicts Formula 1 race winners using probabilistic models. Built with React, FastAPI, and the official FastF1 API.


## 🎯 Overview

This system provides **probabilistic estimates** of win likelihoods based on historical patterns, driver performance, track characteristics, and race conditions. It does not claim to perfectly predict future races, but rather estimates probabilities based on historical data.

### Features

- ✅ **Modern Web UI** - React + TypeScript frontend with Tailwind CSS
- ✅ **REST API** - FastAPI backend with automatic documentation
- ✅ **ML Pipeline** - Multiple models (Logistic Regression, Random Forest, XGBoost)
- ✅ **FastF1 Integration** - Uses official F1 data API
- ✅ **Real-time Predictions** - Interactive dashboard with probability charts
- ✅ **Track-Specific Analysis** - Considers historical performance at each track

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │  ← Modern UI (TypeScript, Tailwind, Vite)
│  (Port 5173)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│  ← REST API (Python, FastAPI)
│  (Port 8000)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ML Models      │  ← Trained Models (XGBoost, Random Forest)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastF1 API     │  ← Official F1 Data Source
└─────────────────┘
```

## 📸 Screenshots

![Main Interface](screenshots/main-interface.png)
*Race configuration and prediction interface*

![Prediction Results](screenshots/prediction-results.png)
*Podium visualization with win probabilities*

![Probability Chart](screenshots/probability-chart.png)
*Win probability distribution for all drivers*

![Driver Rankings](screenshots/driver-rankings.png)
*Complete driver rankings table*

## 📸 Screenshots

![Main Interface](screenshots/main-interface.png)
*Race configuration and prediction interface*

![Prediction Results](screenshots/prediction-results.png)
*Podium visualization with win probabilities*

![Probability Chart](screenshots/probability-chart.png)
*Win probability distribution for all drivers*

![Driver Rankings](screenshots/driver-rankings.png)
*Complete driver rankings table*

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- pip and npm

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd F1
   ```

2. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Collect data and train models**
   ```bash
   # Collect historical F1 data (uses FastF1 API)
   python src/data_collection.py
   
   # Train ML models
   python main.py
   ```

5. **Start the application**

   **Terminal 1 - Backend:**
   ```bash
   python -m uvicorn api.app:app --reload
   ```

   **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Open in browser**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
F1/
├── api/                    # FastAPI backend
│   └── app.py             # REST API server
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── App.tsx        # Main app
│   └── package.json
├── src/                    # ML pipeline
│   ├── data_collection.py # FastF1 API integration
│   ├── feature_engineering.py
│   ├── models.py          # Model training
│   └── predictions.py    # Prediction logic
├── screenshots/            # Application screenshots
├── main.py                # Training pipeline
├── requirements.txt       # Python dependencies
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **FastF1** - Official F1 data API
- **Scikit-learn** - ML algorithms
- **XGBoost** - Gradient boosting (optional)
- **Pandas/NumPy** - Data processing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization

## 📊 How It Works

1. **Data Collection** - Uses FastF1 API to fetch historical race data
2. **Feature Engineering** - Creates 20+ features (driver form, track performance, etc.)
3. **Model Training** - Trains multiple models and selects the best
4. **Predictions** - Generates win probabilities for future races
5. **API** - Exposes predictions via REST API
6. **Frontend** - Interactive UI for making predictions

## 🔧 API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /api/predict` - Get race predictions
- `GET /api/tracks` - List available tracks
- `GET /api/drivers` - List common drivers
- `GET /docs` - Interactive API documentation

## 🚀 Alternative Startup Methods

### Using Startup Scripts

**Backend:**
```bash
./start_api.sh
```

**Frontend:**
```bash
./start_frontend.sh
```

### Example Predictions (CLI)

```bash
python example_predictions.py
```

## ⚠️ Important Notes

- **Probabilistic Predictions**: All predictions are probability estimates, not certainties
- **Assumptions Documented**: Future race inputs are explicitly estimated
- **FastF1 API Required**: First data collection needs internet connection
- **Models Must Be Trained**: Run `python main.py` before using the API

## 🐛 Troubleshooting

### Backend Connection Issues

**"API Disconnected" in frontend:**
- Make sure backend is running: `python -m uvicorn api.app:app --reload`
- Check backend health: `curl http://localhost:8000/health`
- Verify backend is on port 8000

**Port 8000 already in use:**
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

### XGBoost Installation (Optional)

XGBoost is optional - the app works with Logistic Regression and Random Forest. If you want XGBoost:

**macOS:**
```bash
brew install libomp
pip install --upgrade --force-reinstall xgboost
```

**Linux:**
```bash
sudo apt-get install libomp-dev
pip install xgboost
```

### Model Training Errors

**"Models not found":**
- Run `python main.py` to train models first
- Make sure you've collected data: `python src/data_collection.py`

**"No historical data found":**
- Run `python src/data_collection.py` to collect data
- First run takes 10-15 minutes (downloads from FastF1 API)

### Frontend Build Issues

**Module not found:**
```bash
cd frontend
npm install
```

**Port conflicts:**
- Frontend defaults to port 5173
- Change in `frontend/vite.config.ts` if needed


