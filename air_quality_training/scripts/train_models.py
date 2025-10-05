# scripts/train_models_multi.py

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib

def train_multioutput(df_model, output_cols, test_ratio=0.2):
    # Dividir en características (X) y objetivos (y)
    X = df_model.drop(columns=output_cols)
    y = df_model[output_cols]

    split_idx = int(len(df_model) * (1 - test_ratio))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print("Tamaño train:", X_train.shape, "Tamaño test:", X_test.shape)

    # Modelo base
    base_model = RandomForestRegressor(n_estimators=100, random_state=42)
    model = MultiOutputRegressor(base_model, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    # Evaluar por cada contaminante
    results = {}
    for i, col in enumerate(output_cols):
        yt = y_test.iloc[:, i]
        yp = y_pred[:, i]
        mae = mean_absolute_error(yt, yp)

        mse = mean_squared_error(yt, yp)
        rmse = np.sqrt(mse)  # raíz del MSE

        r2 = r2_score(yt, yp)

        results[col] = {"MAE": mae, "RMSE": rmse, "R2": r2}
        print(f"Resultados para {col}: MAE = {mae:.4f}, RMSE = {rmse:.4f}, R² = {r2:.4f}")

    return model, X_test, y_test, y_pred, results

if __name__ == "__main__":
    input_file = "data/processed/station_2178_2020_model.csv"
    df = pd.read_csv(input_file, index_col="datetime", parse_dates=True)

    output_cols = ["PM2_5", "PM10", "NO2", "O3", "SO2"]
    model, X_test, y_test, y_pred, results = train_multioutput(df, output_cols, test_ratio=0.2)

    os.makedirs("models", exist_ok=True)
    model_path = "models/multi_rf_model.pkl"
    joblib.dump(model, model_path)
    print("Modelo multisalida guardado en:", model_path)

    # Guardar predicciones + valores reales
    out = pd.DataFrame(y_pred, index=y_test.index, columns=output_cols)
    for col in output_cols:
        out[f"{col}_true"] = y_test[col]
    predictions_path = "models/predictions_multi.csv"
    out.to_csv(predictions_path)
    print("Predicciones multisalida guardadas en:", predictions_path)
