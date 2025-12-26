"""
Prediction Module for Future Races
Makes probabilistic predictions for upcoming races with documented assumptions
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    from feature_engineering import get_feature_columns
except ImportError:
    from src.feature_engineering import get_feature_columns


class F1Predictor:
    """
    Predictor class for F1 race winners.
    Handles future race predictions with explicit assumptions.
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize predictor with trained model.
        
        Args:
            model_path: Path to saved model directory
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent / 'models'
        
        # Load best model
        metadata_path = model_path / 'model_metadata.pkl'
        if not metadata_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}. Train models first.")
        
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        self.best_model_name = metadata['best_model']
        self.feature_names = metadata['feature_names']
        
        # Load the best model
        model_file = model_path / f"{self.best_model_name}_best.pkl"
        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)
        
        # Load historical data for assumptions
        data_path = Path(__file__).parent.parent / 'data' / 'historical_data.csv'
        if data_path.exists():
            self.historical_data = pd.read_csv(data_path)
        else:
            self.historical_data = pd.DataFrame()
    
    def create_future_race_features(
        self,
        driver: str,
        track: str,
        qualifying_position: int,
        assumptions: Dict
    ) -> pd.DataFrame:
        """
        Create features for a future race based on assumptions.
        
        Args:
            driver: Driver abbreviation
            track: Track location name
            qualifying_position: Expected qualifying position
            assumptions: Dictionary with assumptions about driver form, etc.
            
        Returns:
            DataFrame with features for prediction
        """
        # Base features
        features = {
            'QualifyingPosition': qualifying_position,
            'Location': track
        }
        
        # Driver form assumptions (from assumptions dict or historical average)
        if driver in assumptions.get('driver_form', {}):
            form = assumptions['driver_form'][driver]
            features['PointsLast5'] = form.get('points_last_5', 50)
            features['AvgPositionLast5'] = form.get('avg_position', 5)
            features['WinsLast5'] = form.get('wins_last_5', 1)
        else:
            # Use historical average if available
            driver_data = self.historical_data[
                self.historical_data['Abbreviation'] == driver
            ]
            if not driver_data.empty:
                features['PointsLast5'] = driver_data['Points'].tail(5).sum()
                features['AvgPositionLast5'] = driver_data['Position'].tail(5).mean()
                features['WinsLast5'] = driver_data['Won'].tail(5).sum()
            else:
                features['PointsLast5'] = 30
                features['AvgPositionLast5'] = 8
                features['WinsLast5'] = 0
        
        # Track-specific performance
        track_data = self.historical_data[
            (self.historical_data['Abbreviation'] == driver) &
            (self.historical_data['Location'] == track)
        ]
        if not track_data.empty:
            features['AvgPositionAtTrack'] = track_data['Position'].mean()
            features['BestPositionAtTrack'] = track_data['Position'].min()
            features['WinsAtTrack'] = track_data['Won'].sum()
        else:
            features['AvgPositionAtTrack'] = 10
            features['BestPositionAtTrack'] = 5
            features['WinsAtTrack'] = 0
        
        # Constructor strength
        if driver in assumptions.get('constructor_strength', {}):
            team_strength = assumptions['constructor_strength'][driver]
            features['TeamAvgPoints'] = team_strength.get('avg_points', 15)
            features['TeamRank'] = team_strength.get('rank', 5)
        else:
            # Use historical average
            driver_data = self.historical_data[
                self.historical_data['Abbreviation'] == driver
            ]
            if not driver_data.empty and 'TeamName' in driver_data.columns:
                team = driver_data['TeamName'].iloc[0]
                team_data = self.historical_data[
                    self.historical_data['TeamName'] == team
                ]
                if not team_data.empty:
                    features['TeamAvgPoints'] = team_data['Points'].mean()
                    # Estimate rank from points
                    all_teams = self.historical_data.groupby('TeamName')['Points'].mean()
                    features['TeamRank'] = (all_teams > features['TeamAvgPoints']).sum() + 1
                else:
                    features['TeamAvgPoints'] = 15
                    features['TeamRank'] = 5
            else:
                features['TeamAvgPoints'] = 15
                features['TeamRank'] = 5
        
        # Qualifying impact
        features['PositionChange'] = 0  # Assume no change (conservative)
        features['QualiToRaceAvg'] = 0
        
        # Season features
        if driver in assumptions.get('season_stats', {}):
            season = assumptions['season_stats'][driver]
            features['DriverChampionshipRank'] = season.get('championship_rank', 5)
            features['PointsPerRace'] = season.get('points_per_race', 10)
        else:
            driver_data = self.historical_data[
                self.historical_data['Abbreviation'] == driver
            ]
            if not driver_data.empty:
                features['PointsPerRace'] = driver_data['Points'].mean()
                # Estimate rank
                all_drivers = self.historical_data.groupby('Abbreviation')['Points'].mean()
                features['DriverChampionshipRank'] = (all_drivers > features['PointsPerRace']).sum() + 1
            else:
                features['PointsPerRace'] = 10
                features['DriverChampionshipRank'] = 10
        
        # Weather (use assumptions or historical average)
        if 'weather' in assumptions:
            weather = assumptions['weather']
            features['AvgTemperature'] = weather.get('temperature', 25)
            features['AvgHumidity'] = weather.get('humidity', 60)
            features['HadRain'] = weather.get('rain', False)
        else:
            # Use historical average for this track
            track_weather = self.historical_data[
                self.historical_data['Location'] == track
            ]
            if not track_weather.empty:
                features['AvgTemperature'] = track_weather['AvgTemperature'].mean()
                features['AvgHumidity'] = track_weather['AvgHumidity'].mean()
                features['HadRain'] = track_weather['HadRain'].mean() > 0.3
            else:
                features['AvgTemperature'] = 25
                features['AvgHumidity'] = 60
                features['HadRain'] = False
        
        # Lap time features (use assumptions or defaults)
        features['AvgLapTime'] = assumptions.get('lap_times', {}).get('avg', 90)
        features['BestLapTime'] = assumptions.get('lap_times', {}).get('best', 85)
        features['PitStops'] = assumptions.get('pit_stops', 2)
        
        # Create DataFrame
        feature_df = pd.DataFrame([features])
        
        # Select only features the model expects
        available_features = [f for f in self.feature_names if f in feature_df.columns]
        feature_df = feature_df[available_features]
        
        # Fill missing features with defaults
        for feat in self.feature_names:
            if feat not in feature_df.columns:
                feature_df[feat] = 0
        
        # Reorder columns to match training
        feature_df = feature_df[self.feature_names]
        
        return feature_df
    
    def predict_race(
        self,
        drivers: List[str],
        track: str,
        qualifying_positions: Dict[str, int],
        assumptions: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Predict win probabilities for a future race.
        
        Args:
            drivers: List of driver abbreviations
            track: Track location name
            qualifying_positions: Dict mapping driver to qualifying position
            assumptions: Optional assumptions about form, weather, etc.
            
        Returns:
            DataFrame with predictions sorted by win probability
        """
        if assumptions is None:
            assumptions = {}
        
        predictions = []
        
        for driver in drivers:
            quali_pos = qualifying_positions.get(driver, 10)
            
            # Create features
            features = self.create_future_race_features(
                driver, track, quali_pos, assumptions
            )
            
            # Predict probability
            win_prob = self.model.predict_proba(features)[0, 1]
            
            predictions.append({
                'Driver': driver,
                'Track': track,
                'QualifyingPosition': quali_pos,
                'WinProbability': win_prob
            })
        
        pred_df = pd.DataFrame(predictions)
        pred_df = pred_df.sort_values('WinProbability', ascending=False)
        pred_df['WinProbability'] = pred_df['WinProbability'] * 100  # Convert to percentage
        
        return pred_df


def predict_next_season_races(
    races: List[Dict],
    assumptions: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Predict all races for next season.
    
    Args:
        races: List of race dicts with 'track', 'drivers', 'qualifying_positions'
        assumptions: Optional assumptions dictionary
        
    Returns:
        DataFrame with predictions for all races
    """
    predictor = F1Predictor()
    
    all_predictions = []
    
    for race in races:
        track = race['track']
        drivers = race['drivers']
        quali_positions = race['qualifying_positions']
        
        race_predictions = predictor.predict_race(
            drivers, track, quali_positions, assumptions
        )
        
        all_predictions.append(race_predictions)
    
    combined = pd.concat(all_predictions, ignore_index=True)
    return combined


if __name__ == '__main__':
    # Example: Predict a future race
    print("Loading predictor...")
    predictor = F1Predictor()
    
    # Example race prediction
    drivers = ['VER', 'LEC', 'NOR', 'HAM', 'PER', 'SAI', 'RUS', 'ALO']
    track = "Monaco"
    quali_positions = {
        'VER': 1,
        'LEC': 2,
        'NOR': 3,
        'HAM': 4,
        'PER': 5,
        'SAI': 6,
        'RUS': 7,
        'ALO': 8
    }
    
    print(f"\nPredicting {track} GP...")
    predictions = predictor.predict_race(drivers, track, quali_positions)
    
    print("\n" + "="*50)
    print("PREDICTION RESULTS")
    print("="*50)
    print(predictions.head(10).to_string(index=False))
    print("\n⚠️  Note: These are probabilistic estimates based on historical patterns.")
    print("   Predictions use documented assumptions about driver form and conditions.")

