# scripts/read_earthdata_pm25.py
import xarray as xr

def get_pm25_from_netcdf(file_path, lat, lon):
    """Lee un archivo NetCDF de Earthdata (PM2.5) y obtiene el valor más cercano a una lat/lon."""
    ds = xr.open_dataset(file_path)
    print("Variables disponibles:", list(ds.variables.keys()))
    print("Dimensiones:", ds.dims)

    # Verificamos el nombre de la variable (puede ser 'GWRPM25' o similar)
    var_name = None
    for name in ds.variables.keys():
        if 'pm' in name.lower() or 'gwr' in name.lower():
            var_name = name
            break

    if var_name is None:
        raise ValueError("No se encontró variable PM2.5 en el archivo.")

    # Selecciona el punto más cercano a las coordenadas dadas
    pm25_value = ds[var_name].sel(lat=lat, lon=lon, method='nearest').values.item()
    print(f"PM2.5 en lat={lat}, lon={lon}: {pm25_value}")
    return pm25_value

if __name__ == "__main__":
    # Ruta al archivo .nc descargado
    file_path = r"C:\Users\gabit\OneDrive\Escritorio\TrainingModel\sdei\sdei-global-annual-gwr-pm2-5-modis-misr-seawifs-viirs-aod-v5-gl-04-2022-netcdf.nc"


    # Coordenadas de ejemplo: Arequipa y Lima
    coords = {
        "Arequipa": (-16.3989, -71.535),
        "Lima": (-12.0464, -77.0428)
    }

    for city, (lat, lon) in coords.items():
        try:
            print(f"\n--- {city.upper()} ---")
            get_pm25_from_netcdf(file_path, lat, lon)
        except Exception as e:
            print(f"Error en {city}: {e}")
