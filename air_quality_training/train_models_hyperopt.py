# scripts/train_models_hyperopt_satellite.py

import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

def hyperparameter_search_multi(df_model, output_cols, param_grid, n_splits=5):
    """
    Realiza GridSearchCV con TimeSeriesSplit para modelo multisalida.
    Incluye la variable satelital como feature.
    """
    # X serán las características (todas excepto las columnas objetivo)
    X = df_model.drop(columns=output_cols)
    y = df_model[output_cols]

    print(f"Características usadas para el modelo: {list(X.columns)}")

    # Time series splits
    tscv = TimeSeriesSplit(n_splits=n_splits)

    # Modelo base
    base = RandomForestRegressor(random_state=42)
    multi = MultiOutputRegressor(base, n_jobs=-1)

    # Definir GridSearchCV con cross-validation temporal
    grid = GridSearchCV(
        estimator=multi,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=2,
        refit=True
    )

    print("Iniciando búsqueda de hiperparámetros con TimeSeriesSplit...")
    grid.fit(X, y)

    print("Mejores parámetros:", grid.best_params_)
    print("Mejor puntaje (neg MSE):", grid.best_score_)

    best_model = grid.best_estimator_
    return best_model, grid

def evaluate_multi_model(model, X_test, y_test, output_cols):
    """
    Evalúa el modelo multisalida en el conjunto de prueba.
    """
    y_pred = model.predict(X_test)
    results = {}
    for i, col in enumerate(output_cols):
        yt = y_test.iloc[:, i]
        yp = y_pred[:, i]
        mae = mean_absolute_error(yt, yp)
        mse = mean_squared_error(yt, yp)
        rmse = np.sqrt(mse)
        r2 = r2_score(yt, yp)
        results[col] = {"MAE": mae, "RMSE": rmse, "R2": r2}
        print(f"{col}: MAE = {mae:.4f}, RMSE = {rmse:.4f}, R² = {r2:.4f}")
    return results, y_pred


if __name__ == "__main__":
    # 🔹 Cargar el dataset que incluye la columna satelital
    input_csv = "data/processed/station_2178_2020_model_sat.csv"
    df = pd.read_csv(input_csv, index_col="datetime", parse_dates=True)

    # Definir columnas objetivo (lo que el modelo predice)
    output_cols = ["PM2_5", "PM10", "NO2", "O3", "SO2"]

    # Verificar si existe la columna satelital
    if "pm25_satellite" not in df.columns:
        raise ValueError("❌ La columna 'pm25_satellite' no se encontró en el dataset procesado.")
    else:
        print("✅ Columna satelital detectada e incluida en el entrenamiento.")

    # 🔹 Definir el grid de búsqueda (puedes ampliarlo luego)
    param_grid = {
        "estimator__n_estimators": [50, 100],
        "estimator__max_depth": [5, 10, None],
        "estimator__min_samples_split": [2, 5]
    }

    # Entrenamiento con optimización
    best_model, grid = hyperparameter_search_multi(df, output_cols, param_grid, n_splits=5)

    # Dividir en train/test (último 20 % como test)
    split_idx = int(len(df) * 0.8)
    X = df.drop(columns=output_cols)
    y = df[output_cols]
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print("Evaluando modelo afinado en test final:")
    results, y_pred = evaluate_multi_model(best_model, X_test, y_test, output_cols)

    # Guardar modelo y resultados
    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, "models/best_multi_rf_model_satellite.pkl")
    print("🌍 Modelo óptimo (con datos satelitales) guardado en models/best_multi_rf_model_satellite.pkl")

    out_df = pd.DataFrame(y_pred, index=y_test.index, columns=output_cols)
    for col in output_cols:
        out_df[f"{col}_true"] = y_test[col].values
    out_df.to_csv("models/predictions_multi_hyperopt_satellite.csv")
    print("📈 Predicciones (con satélite) guardadas en models/predictions_multi_hyperopt_satellite.csv")
