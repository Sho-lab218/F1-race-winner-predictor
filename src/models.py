"""
Model Training Module
Trains multiple ML models to predict race winners
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from typing import Dict, Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# Make XGBoost optional (common issue on macOS)
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError as e:
    XGBOOST_AVAILABLE = False
    print(f"Warning: XGBoost not available: {e}")
    print("Will use Logistic Regression and Random Forest only.")

try:
    from feature_engineering import create_ml_features, get_feature_columns
except ImportError:
    from src.feature_engineering import create_ml_features, get_feature_columns


def prepare_training_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    """
    Prepare data for model training.
    
    Args:
        df: DataFrame with engineered features
        
    Returns:
        X: Feature matrix
        y: Target variable (win indicator)
        feature_names: List of feature column names
    """
    # Get feature columns
    feature_cols = get_feature_columns()
    
    # Filter to available columns
    available_features = [col for col in feature_cols if col in df.columns]
    
    # Select features and target
    X = df[available_features].copy()
    y = df['Won'].copy()
    
    # Remove any remaining NaN or inf values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    
    return X, y, available_features


def train_logistic_regression(X: pd.DataFrame, y: pd.Series) -> Dict:
    """
    Train logistic regression baseline model.
    
    Args:
        X: Feature matrix
        y: Target variable
        
    Returns:
        Dictionary with model and metrics
    """
    print("\nTraining Logistic Regression...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"  Accuracy: {accuracy:.3f}")
    print(f"  ROC-AUC: {auc:.3f}")
    
    return {
        'model': model,
        'accuracy': accuracy,
        'auc': auc,
        'name': 'LogisticRegression'
    }


def train_random_forest(X: pd.DataFrame, y: pd.Series) -> Dict:
    """
    Train random forest model.
    
    Args:
        X: Feature matrix
        y: Target variable
        
    Returns:
        Dictionary with model and metrics
    """
    print("\nTraining Random Forest...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"  Accuracy: {accuracy:.3f}")
    print(f"  ROC-AUC: {auc:.3f}")
    
    return {
        'model': model,
        'accuracy': accuracy,
        'auc': auc,
        'name': 'RandomForest'
    }


def train_xgboost(X: pd.DataFrame, y: pd.Series) -> Dict:
    """
    Train XGBoost gradient boosting model.
    
    Args:
        X: Feature matrix
        y: Target variable
        
    Returns:
        Dictionary with model and metrics
    """
    if not XGBOOST_AVAILABLE:
        raise ImportError("XGBoost is not available. Install with: pip install xgboost")
    
    print("\nTraining XGBoost...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"  Accuracy: {accuracy:.3f}")
    print(f"  ROC-AUC: {auc:.3f}")
    
    return {
        'model': model,
        'accuracy': accuracy,
        'auc': auc,
        'name': 'XGBoost'
    }


def train_all_models(df: pd.DataFrame) -> Dict:
    """
    Train all models and return the best one.
    
    Args:
        df: DataFrame with engineered features
        
    Returns:
        Dictionary with all models and best model info
    """
    print("Preparing training data...")
    X, y, feature_names = prepare_training_data(df)
    
    print(f"Training on {len(X)} samples with {len(feature_names)} features")
    print(f"Win rate: {y.mean():.2%}")
    
    # Train all models
    models = {}
    models['logistic'] = train_logistic_regression(X, y)
    models['random_forest'] = train_random_forest(X, y)
    
    # Try XGBoost if available
    if XGBOOST_AVAILABLE:
        try:
            models['xgboost'] = train_xgboost(X, y)
        except Exception as e:
            print(f"\n⚠️  XGBoost training failed: {e}")
            print("   Continuing with Logistic Regression and Random Forest only.")
    else:
        print("\n⚠️  XGBoost not available. Using Logistic Regression and Random Forest only.")
    
    # Select best model by AUC
    best_model_name = max(models.keys(), key=lambda k: models[k]['auc'])
    best_model = models[best_model_name]
    
    print(f"\n✓ Best model: {best_model['name']} (AUC: {best_model['auc']:.3f})")
    
    return {
        'models': models,
        'best_model': best_model,
        'feature_names': feature_names
    }


def save_models(training_results: Dict, output_dir: Path = None):
    """
    Save trained models to disk.
    
    Args:
        training_results: Results from train_all_models
        output_dir: Directory to save models
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / 'models'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save best model
    best_model = training_results['best_model']
    model_path = output_dir / f"{best_model['name']}_best.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(best_model['model'], f)
    
    # Save all models
    for name, model_info in training_results['models'].items():
        model_path = output_dir / f"{model_info['name']}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model_info['model'], f)
    
    # Save feature names
    feature_path = output_dir / 'feature_names.pkl'
    with open(feature_path, 'wb') as f:
        pickle.dump(training_results['feature_names'], f)
    
    # Save metadata
    metadata = {
        'best_model': best_model['name'],
        'best_auc': best_model['auc'],
        'best_accuracy': best_model['accuracy'],
        'feature_names': training_results['feature_names']
    }
    metadata_path = output_dir / 'model_metadata.pkl'
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    
    print(f"\n✓ Models saved to {output_dir}")


if __name__ == '__main__':
    # Load and prepare data
    data_path = Path(__file__).parent.parent / 'data' / 'historical_data.csv'
    
    if not data_path.exists():
        print("No historical data found. Run data_collection.py first.")
    else:
        print("Loading historical data...")
        df = pd.read_csv(data_path)
        
        print("Engineering features...")
        df_features = create_ml_features(df)
        
        print("\nTraining models...")
        results = train_all_models(df_features)
        
        print("\nSaving models...")
        save_models(results)
        
        print("\n✓ Model training complete!")

