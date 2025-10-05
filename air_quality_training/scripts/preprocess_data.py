# scripts/preprocess_data.py

import os
import pandas as pd

def preprocess_for_model(input_csv, output_csv, lags=3):
    print("Leyendo:", input_csv)
    df = pd.read_csv(input_csv)

    # Convertir la columna datetime a tipo datetime (con manejo de zonas horarias)
    # Aquí uso utc=True para unificar fechas; si quieres mantener zona local, puedes quitarlo
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")

    # Establecer datetime como índice
    df = df.set_index("datetime")
    # Ordenar por índice temporal
    df = df.sort_index()

    print("Tipo de índice después de set_index:", type(df.index))
    print("Primeros índices:", df.index[:5])

    # Hacer pivot para convertir cada parámetro en columna
    df_wide = df.pivot_table(
        index=df.index,
        columns="parameter",
        values="value",
        aggfunc="first"
    )

    # Renombrar columnas a nombres más claros
    df_wide = df_wide.rename(columns={
        "pm25": "PM2_5",
        "pm10": "PM10",
        "no2": "NO2",
        "o3": "O3",
        "so2": "SO2"
    })

    # Verificar que el índice de df_wide es DatetimeIndex
    if not isinstance(df_wide.index, pd.DatetimeIndex):
        raise TypeError("El índice de df_wide no es DatetimeIndex; no se puede interpolar por tiempo.")

    # Interpolar valores faltantes en función del tiempo
    df_wide = df_wide.interpolate(method="time")

    # Crear lags (retardos) para cada variable
    for col in df_wide.columns:
        for lag in range(1, lags + 1):
            df_wide[f"{col}_lag{lag}"] = df_wide[col].shift(lag)

    # Eliminar filas que tienen NaN (por los lags iniciales)
    df_model = df_wide.dropna()

    print("Tamaño del dataset listo para modelado:", df_model.shape)

    # Guardar el CSV de salida
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_model.to_csv(output_csv)
    print("Archivo listo para modelo guardado en:", output_csv)

    return df_model

if __name__ == "__main__":
    input_csv = "data/processed/station_2178_2020.csv"
    output_csv = "data/processed/station_2178_2020_model.csv"
    df_ready = preprocess_for_model(input_csv, output_csv, lags=3)
    print(df_ready.head())
