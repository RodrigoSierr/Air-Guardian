"""
Script maestro para descargar, procesar y predecir contaminación en múltiples estaciones OpenAQ (EE. UU.)
Formato listo para visualización en mapa.
"""
import os
import pandas as pd
import numpy as np
import xarray as xr
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Configuración
STATIONS_FILE = "data/stations_us.csv"
YEAR = 2020
CONTAMINANTS = ["pm25", "pm10", "no2", "o3", "so2"]
SATELLITE_FILE = "sdei/sdei-global-annual-gwr-pm2-5-modis-misr-seawifs-viirs-aod-v5-gl-04-2022-netcdf.nc"

# Crear directorios necesarios
os.makedirs("data/raw_s3", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("models", exist_ok=True)

def get_pm25_satellite_value(lat, lon, satellite_file):
    """Obtiene el valor de PM2.5 satelital para las coordenadas dadas"""
    try:
        ds = xr.open_dataset(satellite_file)
        lat_idx = np.abs(ds["lat"].values - lat).argmin()
        lon_idx = np.abs(ds["lon"].values - lon).argmin()
        return float(ds["GWRPM25"].values[lat_idx, lon_idx])
    except Exception as e:
        print(f"Error obteniendo datos satelitales para lat={lat}, lon={lon}: {e}")
        return np.nan

def process_station(location_id, latitude, longitude, city, state):
    """Procesa una estación individual: descarga, procesa, entrena y predice"""
    try:
        print(f"\n[PROCESANDO] Estación {location_id} - {city}, {state}")
        
        # 1. Descargar datos
        import sys
        sys.path.append('.')
        from scripts.download_s3_openaq import download_station_year, read_and_concat
        raw_dir = f"data/raw_s3/loc{location_id}_{YEAR}"
        downloaded = download_station_year(location_id, YEAR, out_dir=raw_dir)
        
        if not downloaded:
            print(f"[ERROR] No se pudieron descargar datos para estación {location_id}")
            return None
            
        # Leer y concatenar archivos
        cols = ["location_id", "sensors_id", "location", "datetime", "latitude", "longitude", "parameter", "value", "unit"]
        df_raw = read_and_concat(downloaded, columns_filter=cols)
        df_raw = df_raw[df_raw["parameter"].isin(CONTAMINANTS)]
        
        if len(df_raw) == 0:
            print(f"[ERROR] No hay datos de contaminantes para estación {location_id}")
            return None
            
        # Guardar datos procesados
        processed_csv = f"data/processed/station_{location_id}_{YEAR}.csv"
        df_raw.to_csv(processed_csv, index=False)
        
        # 2. Preprocesar para modelo
        from scripts.preprocess_data import preprocess_for_model
        model_csv = f"data/processed/station_{location_id}_{YEAR}_model.csv"
        preprocess_for_model(processed_csv, model_csv, lags=3)
        
        # 3. Integrar valor satelital
        pm25_sat_value = get_pm25_satellite_value(latitude, longitude, SATELLITE_FILE)
        df_model = pd.read_csv(model_csv, index_col="datetime", parse_dates=True)
        df_model["latitude"] = latitude
        df_model["longitude"] = longitude
        df_model["pm25_satellite"] = pm25_sat_value
        
        # Guardar con datos satelitales
        sat_csv = f"data/processed/station_{location_id}_{YEAR}_model_sat.csv"
        df_model.to_csv(sat_csv)
        
        # 4. Entrenar modelo y predecir
        from train_models_hyperopt import hyperparameter_search_multi, evaluate_multi_model
        output_cols = ["PM2_5", "PM10", "NO2", "O3", "SO2"]
        
        # Verificar que tenemos las columnas necesarias
        missing_cols = [col for col in output_cols if col not in df_model.columns]
        if missing_cols:
            print(f"[ERROR] Faltan columnas {missing_cols} en estación {location_id}")
            return None
        
        # Parámetros simplificados para procesamiento rápido
        param_grid = {
            "estimator__n_estimators": [50],
            "estimator__max_depth": [5],
            "estimator__min_samples_split": [2]
        }
        
        # Entrenar modelo
        best_model, _ = hyperparameter_search_multi(df_model, output_cols, param_grid, n_splits=3)
        
        # Dividir datos para evaluación
        split_idx = int(len(df_model) * 0.8)
        X = df_model.drop(columns=output_cols)
        y = df_model[output_cols]
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        # Evaluar modelo
        _, y_pred = evaluate_multi_model(best_model, X_test, y_test, output_cols)
        
        # Crear DataFrame de resultados
        out_df = pd.DataFrame(y_pred, index=y_test.index, columns=output_cols)
        for col in output_cols:
            out_df[f"{col}_true"] = y_test[col].values
        
        # Agregar metadatos
        out_df["latitude"] = latitude
        out_df["longitude"] = longitude
        out_df["pm25_satellite"] = pm25_sat_value
        out_df["location_id"] = location_id
        out_df["city"] = city
        out_df["state"] = state
        
        print(f"[OK] Estación {location_id} procesada exitosamente - {len(out_df)} predicciones")
        return out_df
        
    except Exception as e:
        print(f"[ERROR] Error procesando estación {location_id}: {e}")
        return None

def main():
    """Función principal que procesa todas las estaciones"""
    print("[INICIANDO] Procesamiento de estaciones de EE.UU.")
    print(f"[CONFIG] Estaciones a procesar: {STATIONS_FILE}")
    print(f"[CONFIG] Año: {YEAR}")
    print(f"[CONFIG] Contaminantes: {CONTAMINANTS}")
    
    # Leer estaciones
    stations = pd.read_csv(STATIONS_FILE)
    print(f"[INFO] Total de estaciones: {len(stations)}")
    
    all_results = []
    successful_stations = 0
    
    for _, row in tqdm(stations.iterrows(), total=len(stations), desc="Procesando estaciones"):
        location_id = row["location_id"]
        latitude = row["latitude"]
        longitude = row["longitude"]
        city = row["city"]
        state = row["state"]
        
        result = process_station(location_id, latitude, longitude, city, state)
        if result is not None:
            all_results.append(result)
            successful_stations += 1
    
    if all_results:
        # Concatenar todos los resultados
        final_df = pd.concat(all_results, ignore_index=True)
        final_df.to_csv("models/predictions_us_map.csv", index=False)
        
        print(f"\n[COMPLETADO] Proceso finalizado!")
        print(f"[RESULTADO] Estaciones procesadas exitosamente: {successful_stations}/{len(stations)}")
        print(f"[RESULTADO] Total de predicciones: {len(final_df)}")
        print(f"[ARCHIVO] Generado: models/predictions_us_map.csv")
        print(f"[COLUMNAS] {list(final_df.columns)}")
        
        # Mostrar resumen por estación
        print(f"\n[RESUMEN] Por estación:")
        station_summary = final_df.groupby(['location_id', 'city', 'state']).size().reset_index(name='predicciones')
        print(station_summary.to_string(index=False))
        
    else:
        print("[ERROR] No se pudo procesar ninguna estación")

if __name__ == "__main__":
    main()
