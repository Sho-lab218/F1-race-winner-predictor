"""
Feature Engineering Module
Creates ML-ready features from raw F1 data
"""

import pandas as pd
import numpy as np
from typing import Dict, List
from pathlib import Path


def calculate_driver_form(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Calculate rolling driver form (recent performance).
    
    Args:
        df: DataFrame with race results
        window: Number of recent races to consider
        
    Returns:
        DataFrame with form features
    """
    df = df.sort_values(['Abbreviation', 'Year', 'Round'])
    
    # Points in last N races
    df['PointsLast5'] = df.groupby('Abbreviation')['Points'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).sum()
    )
    
    # Average position in last N races
    df['AvgPositionLast5'] = df.groupby('Abbreviation')['Position'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).mean()
    )
    
    # Wins in last N races
    df['WinsLast5'] = df.groupby('Abbreviation')['Won'].transform(
        lambda x: x.shift(1).rolling(window=window, min_periods=1).sum()
    )
    
    return df


def calculate_track_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate driver performance at specific tracks.
    
    Args:
        df: DataFrame with race results
        
    Returns:
        DataFrame with track-specific features
    """
    # Average position at this track
    track_avg = df.groupby(['Abbreviation', 'Location'])['Position'].mean().reset_index()
    track_avg.rename(columns={'Position': 'AvgPositionAtTrack'}, inplace=True)
    df = df.merge(track_avg, on=['Abbreviation', 'Location'], how='left')
    
    # Best position at this track
    track_best = df.groupby(['Abbreviation', 'Location'])['Position'].min().reset_index()
    track_best.rename(columns={'Position': 'BestPositionAtTrack'}, inplace=True)
    df = df.merge(track_best, on=['Abbreviation', 'Location'], how='left')
    
    # Wins at this track
    track_wins = df.groupby(['Abbreviation', 'Location'])['Won'].sum().reset_index()
    track_wins.rename(columns={'Won': 'WinsAtTrack'}, inplace=True)
    df = df.merge(track_wins, on=['Abbreviation', 'Location'], how='left')
    
    return df


def calculate_constructor_strength(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate constructor/team strength metrics.
    
    Args:
        df: DataFrame with race results
        
    Returns:
        DataFrame with constructor features
    """
    # Team average points per race
    team_points = df.groupby(['TeamName', 'Year'])['Points'].mean().reset_index()
    team_points.rename(columns={'Points': 'TeamAvgPoints'}, inplace=True)
    df = df.merge(team_points, on=['TeamName', 'Year'], how='left')
    
    # Team championship position (estimate from average points)
    df['TeamRank'] = df.groupby('Year')['TeamAvgPoints'].rank(ascending=False, method='dense')
    
    return df


def calculate_qualifying_impact(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate qualifying position impact on race result.
    
    Args:
        df: DataFrame with race results
        
    Returns:
        DataFrame with qualifying-related features
    """
    # Position change (qualifying to race)
    df['PositionChange'] = df['QualifyingPosition'] - df['Position']
    
    # Qualifying position (lower is better)
    df['QualifyingPosition'] = df['QualifyingPosition'].fillna(20)  # Default to last
    
    # Historical qualifying-to-race conversion at this track
    quali_race = df.groupby(['Abbreviation', 'Location']).agg({
        'QualifyingPosition': 'mean',
        'Position': 'mean'
    }).reset_index()
    quali_race['QualiToRaceAvg'] = quali_race['QualifyingPosition'] - quali_race['Position']
    quali_race = quali_race[['Abbreviation', 'Location', 'QualiToRaceAvg']]
    df = df.merge(quali_race, on=['Abbreviation', 'Location'], how='left')
    
    return df


def calculate_season_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate season-level features.
    
    Args:
        df: DataFrame with race results
        
    Returns:
        DataFrame with season features
    """
    # Driver championship position (estimate from points)
    df['DriverChampionshipPoints'] = df.groupby(['Abbreviation', 'Year'])['Points'].cumsum()
    df['DriverChampionshipRank'] = df.groupby('Year')['DriverChampionshipPoints'].rank(
        ascending=False, method='dense'
    )
    
    # Points per race average
    df['PointsPerRace'] = df.groupby(['Abbreviation', 'Year'])['Points'].transform('mean')
    
    return df


def create_ml_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create all ML-ready features from raw race data.
    
    Args:
        df: Raw race results DataFrame
        
    Returns:
        DataFrame with engineered features
    """
    print("Engineering features...")
    
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Fill missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    # Calculate all feature groups
    df = calculate_driver_form(df)
    df = calculate_track_performance(df)
    df = calculate_constructor_strength(df)
    df = calculate_qualifying_impact(df)
    df = calculate_season_features(df)
    
    # Fill any remaining NaN values
    df = df.fillna(0)
    
    print(f"✓ Created features for {len(df)} records")
    
    return df


def get_feature_columns() -> List[str]:
    """
    Get list of feature column names for model training.
    
    Returns:
        List of feature column names
    """
    return [
        'QualifyingPosition',
        'PointsLast5',
        'AvgPositionLast5',
        'WinsLast5',
        'AvgPositionAtTrack',
        'BestPositionAtTrack',
        'WinsAtTrack',
        'TeamAvgPoints',
        'TeamRank',
        'PositionChange',
        'QualiToRaceAvg',
        'DriverChampionshipRank',
        'PointsPerRace',
        'AvgTemperature',
        'AvgHumidity',
        'HadRain',
        'AvgLapTime',
        'BestLapTime',
        'PitStops'
    ]


if __name__ == '__main__':
    # Test feature engineering
    data_path = Path(__file__).parent.parent / 'data' / 'historical_data.csv'
    
    if data_path.exists():
        df = pd.read_csv(data_path)
        df_features = create_ml_features(df)
        print(f"\nFeature columns: {len(get_feature_columns())}")
        print(f"\nSample features:")
        print(df_features[['Abbreviation', 'Location', 'Won'] + get_feature_columns()[:5]].head())
    else:
        print("No historical data found. Run data_collection.py first.")

