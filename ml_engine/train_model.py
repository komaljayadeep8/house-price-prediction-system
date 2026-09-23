"""
ML Engine: House Price Prediction System
Trains and evaluates multiple regression models on Housing dataset with feature engineering.
Produces serialized models and JSON metrics for the web application.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

def prepare_data(data_path='data/Housing.csv'):
    df = pd.read_csv(data_path)
    print(f"Loaded raw dataset with shape: {df.shape}")

    # Check for missing values
    missing = df.isnull().sum().to_dict()
    print(f"Missing values: {missing}")

    # Enrich with realistic metropolitan location categories correlated with prefarea
    # Preferred: Downtown Central, Tech Park Cyber City, Riverside Bay
    # Standard: Suburban North, West Greens, East Expressway
    np.random.seed(42)
    pref_locations = ['Downtown Central', 'Tech Park Cyber City', 'Riverside Bay']
    std_locations = ['Suburban North', 'West Greens', 'East Expressway']

    locations = []
    for idx, row in df.iterrows():
        if row['prefarea'] == 'yes':
            loc = pref_locations[idx % len(pref_locations)]
        else:
            loc = std_locations[idx % len(std_locations)]
        locations.append(loc)

    df['location'] = locations

    # Save cleaned data copy
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/housing_enriched.csv', index=False)
    print("Saved enriched dataset to data/housing_enriched.csv")

    return df

def feature_engineering(df):
    data = df.copy()

    # Binary flags mapping
    binary_cols = ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea']
    for col in binary_cols:
        data[col] = (data[col] == 'yes').astype(int)

    # Ordinal mapping for furnishingstatus
    furnishing_map = {'unfurnished': 0, 'semi-furnished': 1, 'furnished': 2}
    data['furnishingstatus_code'] = data['furnishingstatus'].map(furnishing_map)

    # Domain Feature Engineering
    # 1. Total rooms
    data['total_rooms'] = data['bedrooms'] + data['bathrooms']
    # 2. Bathroom to Bedroom ratio
    data['bath_bed_ratio'] = np.round(data['bathrooms'] / np.maximum(data['bedrooms'], 1), 2)
    # 3. Comprehensive Amenity Score (0 to 7)
    data['amenity_score'] = (
        data['mainroad'] +
        data['guestroom'] +
        data['basement'] +
        data['hotwaterheating'] +
        data['airconditioning'] +
        data['prefarea'] +
        (data['parking'] > 0).astype(int)
    )

    # One-hot encode location
    location_dummies = pd.get_dummies(data['location'], prefix='loc', drop_first=False, dtype=int)
    data = pd.concat([data, location_dummies], axis=1)

    return data

def train_and_evaluate():
    raw_df = prepare_data()
    engineered_df = feature_engineering(raw_df)

    # Feature columns to use for training
    feature_cols = [
        'area', 'bedrooms', 'bathrooms', 'stories', 'parking',
        'mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea',
        'furnishingstatus_code', 'total_rooms', 'bath_bed_ratio', 'amenity_score',
        'loc_Downtown Central', 'loc_East Expressway', 'loc_Riverside Bay',
        'loc_Suburban North', 'loc_Tech Park Cyber City', 'loc_West Greens'
    ]

    X = engineered_df[feature_cols]
    y = engineered_df['price']

    # Train-test split (80-20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

    # Scaler for numeric columns
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Models to compare
    models = {
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
    }

    comparison = {}
    best_model_name = None
    best_r2 = -float('inf')
    best_model = None

    for name, model in models.items():
        # Train model
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)

        # Calculate genuine evaluation metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

        # Cross validation R2
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        cv_r2_mean = float(cv_scores.mean())

        comparison[name] = {
            'r2_score': round(float(r2), 4),
            'mae': round(float(mae), 2),
            'rmse': round(float(rmse), 2),
            'mape': round(float(mape), 2),
            'cv_r2_mean': round(cv_r2_mean, 4)
        }

        print(f"[{name}] Test R2: {r2:.4f} | MAE: Rs.{mae:,.0f} | RMSE: Rs.{rmse:,.0f} | MAPE: {mape:.2f}% | CV R2: {cv_r2_mean:.4f}")

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_model = model

    print(f"\n---> Selected Best Model: {best_model_name} (R2 = {best_r2:.4f})")

    # Feature Importance computation
    feature_importance = {}
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        for col, imp in zip(feature_cols, importances):
            feature_importance[col] = round(float(imp) * 100, 2)
    elif hasattr(best_model, 'coef_'):
        coefs = np.abs(best_model.coef_)
        total_coef = np.sum(coefs)
        for col, coef in zip(feature_cols, coefs):
            feature_importance[col] = round(float(coef / total_coef) * 100, 2)

    # Sort feature importance descending
    sorted_importance = dict(sorted(feature_importance.items(), key=lambda item: item[1], reverse=True))

    # Generate Test sample actual vs predicted points for Chart.js plotting
    y_test_pred = best_model.predict(X_test_scaled)
    test_samples = []
    # Take first 45 test samples for clear visualization
    for idx, (actual, pred) in enumerate(zip(y_test.values[:45], y_test_pred[:45])):
        test_samples.append({
            'index': idx + 1,
            'actual': round(float(actual), 0),
            'predicted': round(float(pred), 0),
            'error': round(float(pred - actual), 0),
            'error_pct': round(float((pred - actual) / actual) * 100, 2)
        })

    # Compute descriptive dataset statistics
    stats = {
        'total_samples': len(raw_df),
        'min_price': float(raw_df['price'].min()),
        'max_price': float(raw_df['price'].max()),
        'avg_price': round(float(raw_df['price'].mean()), 2),
        'median_price': float(raw_df['price'].median()),
        'min_area': float(raw_df['area'].min()),
        'max_area': float(raw_df['area'].max()),
        'avg_area': round(float(raw_df['area'].mean()), 2),
        'locations': list(raw_df['location'].unique()),
        'furnishing_distribution': raw_df['furnishingstatus'].value_counts().to_dict(),
        'bedrooms_distribution': raw_df['bedrooms'].value_counts().to_dict()
    }

    # Package full metrics
    full_metrics = {
        'best_model': best_model_name,
        'best_r2': round(float(best_r2), 4),
        'best_mae': round(float(comparison[best_model_name]['mae']), 2),
        'best_rmse': round(float(comparison[best_model_name]['rmse']), 2),
        'best_mape': round(float(comparison[best_model_name]['mape']), 2),
        'model_comparison': comparison,
        'feature_importance': sorted_importance,
        'test_samples': test_samples,
        'dataset_stats': stats
    }

    # Save artifacts
    os.makedirs('ml_engine', exist_ok=True)
    joblib.dump(best_model, 'ml_engine/model.pkl')
    joblib.dump(scaler, 'ml_engine/scaler.pkl')

    with open('ml_engine/feature_columns.json', 'w') as f:
        json.dump(feature_cols, f, indent=2)

    with open('ml_engine/model_metrics.json', 'w') as f:
        json.dump(full_metrics, f, indent=2)

    print("Model, scaler, feature columns, and metrics saved successfully to ml_engine/!")
    return full_metrics

if __name__ == '__main__':
    train_and_evaluate()
