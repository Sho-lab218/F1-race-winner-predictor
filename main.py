"""
Main Script for F1 Prediction System
Runs the complete pipeline: data collection -> feature engineering -> training -> predictions
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_collection import collect_historical_data
from feature_engineering import create_ml_features
from models import train_all_models, save_models
import pandas as pd


def main():
    """
    Main pipeline execution.
    """
    print("="*60)
    print("F1 RACE WINNER PREDICTION SYSTEM")
    print("="*60)
    print("\n⚠️  This system provides PROBABILISTIC estimates, not deterministic predictions.")
    print("   All predictions are based on historical patterns and documented assumptions.\n")
    
    # Step 1: Collect data
    print("\n[1/4] Collecting historical data...")
    print("-" * 60)
    data = collect_historical_data([2021, 2022, 2023, 2024])
    
    if data.empty:
        print("❌ No data collected. Please check your internet connection and try again.")
        return
    
    print(f"✓ Collected {len(data)} race records")
    
    # Step 2: Feature engineering
    print("\n[2/4] Engineering features...")
    print("-" * 60)
    df_features = create_ml_features(data)
    print(f"✓ Created features for {len(df_features)} records")
    
    # Step 3: Train models
    print("\n[3/4] Training models...")
    print("-" * 60)
    results = train_all_models(df_features)
    
    # Step 4: Save models
    print("\n[4/4] Saving models...")
    print("-" * 60)
    save_models(results)
    
    print("\n" + "="*60)
    print("✓ PIPELINE COMPLETE")
    print("="*60)
    print(f"\nBest model: {results['best_model']['name']}")
    print(f"Accuracy: {results['best_model']['accuracy']:.3f}")
    print(f"ROC-AUC: {results['best_model']['auc']:.3f}")
    print("\nNext steps:")
    print("  - Run 'python src/predictions.py' for example predictions")
    print("  - Run 'streamlit run app.py' for interactive dashboard")


if __name__ == '__main__':
    main()

