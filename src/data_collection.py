"""
Data Collection Module for F1 Race Data
Uses FastF1 API to fetch historical race data
"""

import fastf1
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Enable caching for faster data retrieval
CACHE_DIR = Path(__file__).parent.parent / 'data' / 'cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache(str(CACHE_DIR))


def get_season_data(year: int) -> pd.DataFrame:
    """
    Collect all race data for a given season.
    
    Args:
        year: Season year (e.g., 2023)
        
    Returns:
        DataFrame with race results, qualifying, and session data
    """
    print(f"Fetching data for {year} season...")
    
    schedule = fastf1.get_event_schedule(year)
    all_races = []
    
    for idx, event in schedule.iterrows():
        if event['EventFormat'] == 'conventional':
            try:
                race_data = get_race_data(year, event['RoundNumber'], event['Location'])
                if race_data is not None:
                    all_races.append(race_data)
                    print(f"  ✓ {event['Location']} - Round {event['RoundNumber']}")
            except Exception as e:
                print(f"  ✗ {event['Location']} - Error: {str(e)}")
                continue
    
    if not all_races:
        return pd.DataFrame()
    
    return pd.concat(all_races, ignore_index=True)


def get_race_data(year: int, round_num: int, location: str) -> Optional[pd.DataFrame]:
    """
    Get comprehensive data for a single race.
    
    Args:
        year: Season year
        round_num: Round number
        location: Race location name
        
    Returns:
        DataFrame with race results and features
    """
    try:
        # Load race session
        race = fastf1.get_session(year, round_num, 'R')
        race.load()
        
        # Load qualifying session
        quali = fastf1.get_session(year, round_num, 'Q')
        quali.load()
        
        # Get race results
        results = race.results[['Abbreviation', 'Position', 'Points', 'Status']].copy()
        results['Year'] = year
        results['Round'] = round_num
        results['Location'] = location
        results['TrackName'] = race.event['Location']
        
        # Get qualifying positions
        quali_results = quali.results[['Abbreviation', 'Position']].copy()
        quali_results.rename(columns={'Position': 'QualifyingPosition'}, inplace=True)
        
        # Merge qualifying with race results
        results = results.merge(quali_results, on='Abbreviation', how='left')
        
        # Get weather data
        weather_data = race.weather_data
        if not weather_data.empty:
            avg_temp = weather_data['AirTemp'].mean()
            avg_humidity = weather_data['Humidity'].mean()
            avg_rainfall = weather_data['Rainfall'].sum() > 0
        else:
            avg_temp = np.nan
            avg_humidity = np.nan
            avg_rainfall = False
        
        results['AvgTemperature'] = avg_temp
        results['AvgHumidity'] = avg_humidity
        results['HadRain'] = avg_rainfall
        
        # Get lap data for each driver
        lap_features = []
        for driver in results['Abbreviation'].unique():
            try:
                driver_laps = race.laps.pick_driver(driver)
                if not driver_laps.empty:
                    lap_features.append({
                        'Abbreviation': driver,
                        'AvgLapTime': driver_laps['LapTime'].mean().total_seconds(),
                        'BestLapTime': driver_laps['LapTime'].min().total_seconds(),
                        'TotalLaps': len(driver_laps),
                        'PitStops': driver_laps['PitOutTime'].notna().sum()
                    })
            except:
                continue
        
        if lap_features:
            lap_df = pd.DataFrame(lap_features)
            results = results.merge(lap_df, on='Abbreviation', how='left')
        
        # Add win indicator
        results['Won'] = (results['Position'] == 1).astype(int)
        
        # Add constructor info (if available)
        try:
            constructor_info = race.results[['Abbreviation', 'TeamName']].copy()
            results = results.merge(constructor_info, on='Abbreviation', how='left')
        except:
            results['TeamName'] = 'Unknown'
        
        return results
        
    except Exception as e:
        print(f"    Error loading race data: {str(e)}")
        return None


def collect_historical_data(years: List[int] = [2018, 2019, 2020, 2021, 2022, 2023, 2024]) -> pd.DataFrame:
    """
    Collect historical data for multiple seasons.
    
    Args:
        years: List of years to collect data for
        
    Returns:
        Combined DataFrame with all historical data
    """
    all_data = []
    
    for year in years:
        try:
            season_data = get_season_data(year)
            if not season_data.empty:
                all_data.append(season_data)
        except Exception as e:
            print(f"Error collecting {year} data: {str(e)}")
            continue
    
    if not all_data:
        return pd.DataFrame()
    
    combined = pd.concat(all_data, ignore_index=True)
    
    # Save to CSV
    output_path = Path(__file__).parent.parent / 'data' / 'historical_data.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_path, index=False)
    print(f"\n✓ Saved {len(combined)} records to {output_path}")
    
    return combined


if __name__ == '__main__':
    # Collect data for recent seasons
    print("Starting F1 data collection...")
    data = collect_historical_data([2021, 2022, 2023, 2024])
    print(f"\nCollected {len(data)} race records")
    print(f"\nSample data:")
    print(data.head())

