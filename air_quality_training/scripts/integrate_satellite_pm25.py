import os
import pandas as pd
import xarray as xr
import numpy as np

# === CONFIGURACIÓN ===
satellite_file = r"C:\Users\gabit\OneDrive\Escritorio\TrainingModel\sdei\sdei-global-annual-gwr-pm2-5-modis-misr-seawifs-viirs-aod-v5-gl-04-2022-netcdf.nc"
input_file = r"data\processed\station_2178_2020_model.csv"
output_file = r"data\processed\station_2178_2020_model_sat.csv"

# Coordenadas reales del sensor 2178 (Del Norte, Albuquerque)
station_lat = 35.1353
station_lon = -106.5847

def get_pm25_from_coords(ds, lat, lon):
    lat_idx = np.abs(ds["lat"].values - lat).argmin()
    lon_idx = np.abs(ds["lon"].values - lon).argmin()
    return float(ds["GWRPM25"].values[lat_idx, lon_idx])

print(f"Leyendo archivo satelital: {os.path.basename(satellite_file)}")
ds = xr.open_dataset(satellite_file)
print("Variables disponibles:", list(ds.variables.keys()))

print(f"Leyendo dataset local: {input_file}")
df = pd.read_csv(input_file)

# Asignamos la misma coordenada a todas las filas
df["latitude"] = station_lat
df["longitude"] = station_lon

# Extraemos valor satelital solo una vez
pm25_sat_value = get_pm25_from_coords(ds, station_lat, station_lon)
print(f"PM2.5 satelital en lat={station_lat}, lon={station_lon}: {pm25_sat_value:.2f}")

# Añadimos columna fija (puede usarse como feature externo)
df["pm25_satellite"] = pm25_sat_value

# Guardamos dataset combinado
df.to_csv(output_file, index=False)
print(f"\n✅ Dataset actualizado con valor satelital guardado en: {output_file}")
print(df[["datetime", "pm25_satellite"]].head())
