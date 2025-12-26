"""
FastAPI Backend for F1 Prediction System
Provides REST API endpoints for predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from predictions import F1Predictor
import uvicorn

app = FastAPI(
    title="F1 Race Winner Prediction API",
    description="Probabilistic ML predictions for Formula 1 race winners",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5176", "http://localhost:3000"],  # Vite ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize predictor (lazy loading)
_predictor = None

def get_predictor():
    """Lazy load predictor to avoid errors if models don't exist yet"""
    global _predictor
    if _predictor is None:
        try:
            _predictor = F1Predictor()
        except FileNotFoundError as e:
            raise HTTPException(
                status_code=503,
                detail="Models not trained yet. Please run 'python main.py' first."
            )
    return _predictor


# Request/Response models
class QualifyingPosition(BaseModel):
    driver: str
    position: int


class RacePredictionRequest(BaseModel):
    track: str
    drivers: List[str]
    qualifying_positions: Dict[str, int]
    assumptions: Optional[Dict] = None


class PredictionResult(BaseModel):
    driver: str
    track: str
    qualifying_position: int
    win_probability: float


class RacePredictionResponse(BaseModel):
    predictions: List[PredictionResult]
    message: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: Optional[str] = None


# API Endpoints
@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "message": "F1 Race Winner Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/api/predict",
            "tracks": "/api/tracks",
            "drivers": "/api/drivers"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        predictor = get_predictor()
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            model_name=predictor.best_model_name
        )
    except HTTPException:
        return HealthResponse(
            status="unhealthy",
            model_loaded=False
        )


@app.post("/api/predict", response_model=RacePredictionResponse)
async def predict_race(request: RacePredictionRequest):
    """
    Predict win probabilities for a race.
    
    Args:
        request: Race prediction request with track, drivers, and qualifying positions
        
    Returns:
        Predictions sorted by win probability
    """
    try:
        predictor = get_predictor()
        
        predictions = predictor.predict_race(
            drivers=request.drivers,
            track=request.track,
            qualifying_positions=request.qualifying_positions,
            assumptions=request.assumptions
        )
        
        # Convert to response format
        results = [
            PredictionResult(
                driver=row['Driver'],
                track=row['Track'],
                qualifying_position=int(row['QualifyingPosition']),
                win_probability=round(row['WinProbability'], 2)
            )
            for _, row in predictions.iterrows()
        ]
        
        return RacePredictionResponse(
            predictions=results,
            message="Predictions are probabilistic estimates based on historical patterns"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tracks", response_model=List[str])
async def get_tracks():
    """Get list of available F1 tracks"""
    return [
        "Bahrain", "Jeddah", "Melbourne", "Baku", "Miami", "Monaco",
        "Barcelona", "Montreal", "Silverstone", "Spielberg", "Budapest",
        "Spa-Francorchamps", "Zandvoort", "Monza", "Singapore", "Suzuka",
        "Qatar", "Austin", "Mexico City", "São Paulo", "Las Vegas", "Abu Dhabi"
    ]


@app.get("/api/drivers", response_model=List[str])
async def get_drivers():
    """Get list of common F1 drivers"""
    return [
        'VER', 'PER', 'LEC', 'SAI', 'HAM', 'RUS', 'NOR', 'PIA',
        'ALO', 'STR', 'OCO', 'GAS', 'ALB', 'SAR', 'BOT', 'ZHO',
        'TSU', 'RIC', 'HUL', 'MAG'
    ]


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

