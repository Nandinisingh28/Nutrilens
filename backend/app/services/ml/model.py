"""
Health Score Machine Learning Model
"""
import os
import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from dataclasses import dataclass

from app.services.ml.dataset_generator import generate_training_data

logger = logging.getLogger(__name__)


@dataclass
class HealthScoreResult:
    """Result from health score prediction"""
    score: float
    risk_labels: List[str]
    confidence: float
    feature_importance: Dict[str, float]


class HealthScoreModel:
    """
    Machine learning model for predicting health scores.
    Uses Random Forest for robust predictions.
    """
    
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'trained_model.pkl')
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'training_data.csv')
    
    FEATURES = [
        'protein_per_100g',
        'sugar_per_100g',
        'fat_per_100g',
        'fiber_per_100g',
        'calories_per_100g',
        'sodium_per_100g',
        'has_artificial_sweetener',
        'has_preservatives',
        'has_trans_fat',
        'ingredient_risk_count',
    ]
    
    def __init__(self):
        self.model: Optional[RandomForestRegressor] = None
        self.is_trained = False
        self._load_or_train()
    
    def _load_or_train(self):
        """Load existing model or train a new one"""
        if os.path.exists(self.MODEL_PATH):
            try:
                loaded = joblib.load(self.MODEL_PATH)
                # Check feature count matches (stale model detection)
                if hasattr(loaded, 'n_features_in_') and loaded.n_features_in_ != len(self.FEATURES):
                    logger.warning(
                        f"Stale model detected ({loaded.n_features_in_} features vs {len(self.FEATURES)} expected). Retraining.")
                    os.remove(self.MODEL_PATH)
                else:
                    self.model = loaded
                    self.is_trained = True
                    return
            except Exception:
                pass
        
        # Train new model
        self.train()
    
    def train(self, data_path: str = None):
        """
        Train the health score model
        
        Args:
            data_path: Path to training data CSV
        """
        # Load or generate data
        df = None
        if data_path and os.path.exists(data_path):
            df = pd.read_csv(data_path)
        elif os.path.exists(self.DATA_PATH):
            df = pd.read_csv(self.DATA_PATH)
        
        # Check if loaded CSV has all required feature columns
        if df is not None and not all(f in df.columns for f in self.FEATURES):
            missing = [f for f in self.FEATURES if f not in df.columns]
            logger.warning(f"Stale training data missing columns {missing}. Regenerating.")
            df = None
        
        if df is None:
            # Generate fresh training data
            os.makedirs(os.path.dirname(self.DATA_PATH), exist_ok=True)
            df = generate_training_data(self.DATA_PATH, n_samples=3000)
        
        # Prepare features and target
        X = df[self.FEATURES].fillna(0)
        y = df['health_score']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model trained - MSE: {mse:.2f}, R2: {r2:.3f}")
        
        # Save model
        os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
        joblib.dump(self.model, self.MODEL_PATH)
        
        self.is_trained = True
    
    def predict(
        self,
        nutrition: Dict,
        ingredient_flags: Dict = None
    ) -> HealthScoreResult:
        """
        Predict health score for given nutrition values
        
        Args:
            nutrition: Dictionary with nutrition values per 100g
            ingredient_flags: Dictionary with ingredient flags
            
        Returns:
            HealthScoreResult with score and analysis
        """
        if not self.is_trained:
            self.train()
        
        # Prepare features
        features = self._prepare_features(nutrition, ingredient_flags)
        
        # Get prediction
        score = self.model.predict([features])[0]
        score = max(0, min(100, score))  # Clamp to 0-100
        
        # Get confidence from tree variance
        predictions = np.array([tree.predict([features])[0] for tree in self.model.estimators_])
        confidence = 1 - (np.std(predictions) / 100)
        confidence = max(0.5, min(1.0, confidence))
        
        # Get feature importance
        importance = dict(zip(self.FEATURES, self.model.feature_importances_))
        
        # Generate risk labels
        risk_labels = self._generate_risk_labels(nutrition, ingredient_flags)
        
        return HealthScoreResult(
            score=round(score, 1),
            risk_labels=risk_labels,
            confidence=round(confidence, 2),
            feature_importance=importance
        )
    
    def _prepare_features(
        self,
        nutrition: Dict,
        ingredient_flags: Dict = None
    ) -> List[float]:
        """Prepare feature vector from nutrition data"""
        
        if ingredient_flags is None:
            ingredient_flags = {}
        
        features = [
            nutrition.get('protein_per_100g') or nutrition.get('protein') or 0,
            nutrition.get('sugar_per_100g') or nutrition.get('sugar') or 0,
            nutrition.get('fat_per_100g') or nutrition.get('fat') or 0,
            nutrition.get('fiber_per_100g') or nutrition.get('fiber') or 0,
            nutrition.get('calories_per_100g') or nutrition.get('calories') or 0,
            nutrition.get('sodium_per_100g') or nutrition.get('sodium') or 0,
            1 if ingredient_flags.get('has_artificial_sweetener') else 0,
            1 if ingredient_flags.get('has_preservatives') else 0,
            1 if ingredient_flags.get('has_trans_fat') else 0,
            ingredient_flags.get('ingredient_risk_count', 0) or 0,
        ]
        
        return features
    
    def _generate_risk_labels(
        self,
        nutrition: Dict,
        ingredient_flags: Dict = None
    ) -> List[str]:
        """Generate risk labels based on nutrition analysis"""
        
        if ingredient_flags is None:
            ingredient_flags = {}
        
        risks = []
        
        sugar = nutrition.get('sugar_per_100g') or nutrition.get('sugar') or 0
        fat = nutrition.get('fat_per_100g') or nutrition.get('fat') or 0
        fiber = nutrition.get('fiber_per_100g') or nutrition.get('fiber') or 0
        calories = nutrition.get('calories_per_100g') or nutrition.get('calories') or 0
        sodium = nutrition.get('sodium_per_100g') or nutrition.get('sodium') or 0
        
        if sugar > 20:
            risks.append('HIGH_SUGAR')
        
        if fat > 18:
            risks.append('HIGH_FAT')
        
        if fiber < 2:
            risks.append('LOW_FIBER')
        
        if calories > 450:
            risks.append('HIGH_CALORIE')
        
        if sodium > 600:
            risks.append('HIGH_SODIUM')
        
        if ingredient_flags.get('has_trans_fat'):
            risks.append('TRANS_FAT')
        
        if ingredient_flags.get('has_artificial_sweetener'):
            risks.append('ARTIFICIAL_SWEETENER')
        
        if ingredient_flags.get('has_preservatives'):
            risks.append('PRESERVATIVES')
        
        return risks
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from trained model"""
        if not self.is_trained:
            return {}
        
        return dict(zip(self.FEATURES, self.model.feature_importances_))


# Singleton instance
_model_instance: Optional[HealthScoreModel] = None


def get_health_model() -> HealthScoreModel:
    """Get or create the health score model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = HealthScoreModel()
    return _model_instance
