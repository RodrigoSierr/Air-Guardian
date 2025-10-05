"""
Machine Learning model for air quality prediction
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import pickle
import os

class AirQualityPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = "model/aqi_model.pkl"
        self.scaler_path = "model/scaler.pkl"
        
    def create_features(self, df):
        """Create features from raw data"""
        df = df.copy()
        
        # Time-based features
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['month'] = pd.to_datetime(df['timestamp']).dt.month
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Cyclical encoding for time features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Lag features (previous values)
        lag_columns = ['pm25', 'pm10', 'no2', 'o3', 'aqi']
        for col in lag_columns:
            if col in df.columns:
                df[f'{col}_lag_1h'] = df[col].shift(1)
                df[f'{col}_lag_3h'] = df[col].shift(3)
                df[f'{col}_lag_6h'] = df[col].shift(6)
                df[f'{col}_lag_24h'] = df[col].shift(24)
        
        # Rolling statistics
        if 'pm25' in df.columns:
            df['pm25_rolling_mean_6h'] = df['pm25'].rolling(window=6, min_periods=1).mean()
            df['pm25_rolling_std_6h'] = df['pm25'].rolling(window=6, min_periods=1).std()
            df['pm25_rolling_mean_24h'] = df['pm25'].rolling(window=24, min_periods=1).mean()
        
        return df
    
    def generate_synthetic_data(self, n_samples=10000):
        """Generate synthetic training data"""
        np.random.seed(42)
        
        timestamps = [datetime.now() - timedelta(hours=i) for i in range(n_samples)]
        
        data = {
            'timestamp': timestamps,
            'pm25': np.random.gamma(shape=2, scale=20, size=n_samples) + 10,
            'pm10': np.random.gamma(shape=2, scale=30, size=n_samples) + 15,
            'no2': np.random.gamma(shape=2, scale=15, size=n_samples) + 5,
            'o3': np.random.gamma(shape=2, scale=20, size=n_samples) + 10,
            'temperature': np.random.normal(20, 8, n_samples),
            'humidity': np.random.uniform(30, 90, n_samples),
            'wind_speed': np.random.gamma(shape=2, scale=3, size=n_samples),
            'pressure': np.random.normal(1013, 10, n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Calculate AQI from PM2.5
        def calculate_aqi(pm25):
            if pm25 <= 12.0:
                return (50 / 12.0) * pm25
            elif pm25 <= 35.4:
                return 50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1)
            elif pm25 <= 55.4:
                return 100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5)
            elif pm25 <= 150.4:
                return 150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5)
            elif pm25 <= 250.4:
                return 200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5)
            else:
                return 300 + ((500 - 300) / (500.4 - 250.5)) * (pm25 - 250.5)
        
        df['aqi'] = df['pm25'].apply(calculate_aqi)
        
        # Add some temporal patterns
        hours = pd.to_datetime(df['timestamp']).dt.hour
        df['pm25'] += 20 * np.sin(2 * np.pi * hours / 24)  # Daily pattern
        df['aqi'] = df['pm25'].apply(calculate_aqi)
        
        return df
    
    def train(self, df=None):
        """Train the prediction model"""
        if df is None:
            print("Generating synthetic training data...")
            df = self.generate_synthetic_data()
        
        print(f"Training with {len(df)} samples...")
        
        # Create features
        df = self.create_features(df)
        
        # Drop rows with NaN values (from lag features)
        df = df.dropna()
        
        # Select features for training
        feature_cols = [
            'hour_sin', 'hour_cos', 'month_sin', 'month_cos', 'is_weekend',
            'pm25', 'pm10', 'no2', 'o3',
            'temperature', 'humidity', 'wind_speed', 'pressure',
            'pm25_lag_1h', 'pm25_lag_3h', 'pm25_lag_6h', 'pm25_lag_24h',
            'pm25_rolling_mean_6h', 'pm25_rolling_std_6h', 'pm25_rolling_mean_24h'
        ]
        
        # Filter out features that don't exist in the dataframe
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        X = df[feature_cols]
        y = df['aqi']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print("Training Random Forest model...")
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training R² score: {train_score:.4f}")
        print(f"Testing R² score: {test_score:.4f}")
        
        # Save model
        self.save_model()
        
        return test_score
    
    def save_model(self):
        """Save trained model to disk"""
        os.makedirs("model", exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(self.scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            print("Model loaded successfully")
            return True
        except FileNotFoundError:
            print("Model not found. Training new model...")
            self.train()
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict(self, features):
        """Make prediction"""
        if self.model is None:
            self.load_model()
        
        features_scaled = self.scaler.transform(features)
        predictions = self.model.predict(features_scaled)
        
        return predictions
    
    def predict_future(self, current_data, hours_ahead=48):
        """Predict AQI for future timestamps"""
        if self.model is None:
            self.load_model()
        
        predictions = []
        last_timestamp = datetime.fromisoformat(current_data['timestamp'])
        
        # Simple prediction: use current values and project forward
        for hour in range(1, hours_ahead + 1):
            future_time = last_timestamp + timedelta(hours=hour)
            
            # Create feature vector
            hour_val = future_time.hour
            month_val = future_time.month
            day_of_week = future_time.weekday()
            
            # Mock feature values (in real scenario, use weather forecasts)
            features = {
                'hour_sin': np.sin(2 * np.pi * hour_val / 24),
                'hour_cos': np.cos(2 * np.pi * hour_val / 24),
                'month_sin': np.sin(2 * np.pi * month_val / 12),
                'month_cos': np.cos(2 * np.pi * month_val / 12),
                'is_weekend': 1 if day_of_week >= 5 else 0,
                'pm25': current_data.get('pm25', 30),
                'pm10': current_data.get('pm10', 45),
                'no2': current_data.get('no2', 40),
                'o3': current_data.get('o3', 50),
                'temperature': current_data.get('temperature', 20),
                'humidity': current_data.get('humidity', 60),
                'wind_speed': current_data.get('wind_speed', 5),
                'pressure': current_data.get('pressure', 1013),
                'pm25_lag_1h': current_data.get('pm25', 30),
                'pm25_lag_3h': current_data.get('pm25', 30),
                'pm25_lag_6h': current_data.get('pm25', 30),
                'pm25_lag_24h': current_data.get('pm25', 30),
                'pm25_rolling_mean_6h': current_data.get('pm25', 30),
                'pm25_rolling_std_6h': 5.0,
                'pm25_rolling_mean_24h': current_data.get('pm25', 30),
            }
            
            # Convert to DataFrame
            df_features = pd.DataFrame([features])
            
            # Predict
            aqi_pred = self.predict(df_features)[0]
            
            # Add some uncertainty
            confidence = max(0.5, 1.0 - (hour / hours_ahead) * 0.5)
            
            predictions.append({
                'timestamp': future_time.isoformat(),
                'aqi': int(max(0, min(500, aqi_pred))),
                'confidence': round(confidence, 2)
            })
        
        return predictions

if __name__ == "__main__":
    # Train model on startup
    predictor = AirQualityPredictor()
    predictor.train()

