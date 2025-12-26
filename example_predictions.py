"""
Example: Making predictions for future F1 races
Demonstrates how to use the prediction system with documented assumptions
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from predictions import F1Predictor


def example_single_race():
    """Example: Predict a single future race"""
    print("="*60)
    print("EXAMPLE: Predicting Monaco GP 2025")
    print("="*60)
    
    # Initialize predictor
    predictor = F1Predictor()
    
    # Define race parameters
    drivers = ['VER', 'LEC', 'NOR', 'HAM', 'PER', 'SAI', 'RUS', 'ALO']
    track = "Monaco"
    
    # Expected qualifying positions (user assumption)
    qualifying_positions = {
        'VER': 1,  # Verstappen on pole
        'LEC': 2,  # Leclerc (home track advantage)
        'NOR': 3,
        'HAM': 4,
        'PER': 5,
        'SAI': 6,
        'RUS': 7,
        'ALO': 8
    }
    
    # Optional: Define explicit assumptions
    assumptions = {
        'driver_form': {
            'VER': {
                'points_last_5': 120,  # Strong recent form
                'avg_position': 1.5,
                'wins_last_5': 4
            },
            'LEC': {
                'points_last_5': 80,
                'avg_position': 3.0,
                'wins_last_5': 1
            }
        },
        'weather': {
            'temperature': 22,  # Monaco typical weather
            'humidity': 65,
            'rain': False
        }
    }
    
    # Make prediction
    predictions = predictor.predict_race(
        drivers, track, qualifying_positions, assumptions
    )
    
    # Display results
    print(f"\n🏁 {track} Grand Prix - Predicted Win Probabilities")
    print("-" * 60)
    print(f"{'Driver':<10} {'Qualifying':<12} {'Win Probability':<15}")
    print("-" * 60)
    
    for _, row in predictions.iterrows():
        print(f"{row['Driver']:<10} P{int(row['QualifyingPosition']):<11} {row['WinProbability']:.2f}%")
    
    print("\n⚠️  Note: These are probabilistic estimates based on:")
    print("   - Historical performance patterns")
    print("   - Track-specific statistics")
    print("   - Documented assumptions about driver form")
    print("   - Expected qualifying positions")


def example_season_predictions():
    """Example: Predict multiple races for next season"""
    print("\n" + "="*60)
    print("EXAMPLE: Predicting 2025 Season (Sample Races)")
    print("="*60)
    
    predictor = F1Predictor()
    
    # Define sample races for next season
    races = [
        {
            'track': 'Bahrain',
            'drivers': ['VER', 'LEC', 'NOR', 'HAM', 'PER', 'SAI'],
            'qualifying_positions': {'VER': 1, 'LEC': 2, 'NOR': 3, 'HAM': 4, 'PER': 5, 'SAI': 6}
        },
        {
            'track': 'Monaco',
            'drivers': ['VER', 'LEC', 'NOR', 'HAM', 'PER', 'SAI'],
            'qualifying_positions': {'VER': 2, 'LEC': 1, 'NOR': 3, 'HAM': 5, 'PER': 4, 'SAI': 6}
        },
        {
            'track': 'Silverstone',
            'drivers': ['VER', 'LEC', 'NOR', 'HAM', 'PER', 'SAI'],
            'qualifying_positions': {'VER': 1, 'NOR': 2, 'HAM': 3, 'LEC': 4, 'PER': 5, 'SAI': 6}
        }
    ]
    
    # Make predictions for all races
    all_predictions = []
    
    for race in races:
        predictions = predictor.predict_race(
            race['drivers'],
            race['track'],
            race['qualifying_positions']
        )
        
        # Get top prediction
        top_pred = predictions.iloc[0]
        all_predictions.append({
            'Race': f"{race['track']} GP",
            'Predicted Winner': top_pred['Driver'],
            'Win Probability': f"{top_pred['WinProbability']:.1f}%"
        })
    
    # Display summary
    print("\n📊 Season Prediction Summary")
    print("-" * 60)
    print(f"{'Race':<20} {'Predicted Winner':<20} {'Win Probability':<15}")
    print("-" * 60)
    
    for pred in all_predictions:
        print(f"{pred['Race']:<20} {pred['Predicted Winner']:<20} {pred['Win Probability']:<15}")
    
    print("\n⚠️  Important: These predictions use assumptions about:")
    print("   - Driver form (based on recent seasons)")
    print("   - Constructor strength (trending from last season)")
    print("   - Track-specific performance (historical averages)")
    print("   - Weather conditions (typical for each location)")


if __name__ == '__main__':
    # Run examples
    try:
        example_single_race()
        example_season_predictions()
        
        print("\n" + "="*60)
        print("✓ Examples complete!")
        print("="*60)
        print("\nTo make your own predictions:")
        print("  1. Import F1Predictor from src.predictions")
        print("  2. Define drivers, track, and qualifying positions")
        print("  3. Optionally provide assumptions dictionary")
        print("  4. Call predictor.predict_race()")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease run 'python main.py' first to train the models.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

