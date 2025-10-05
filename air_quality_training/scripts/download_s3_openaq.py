import os
import gzip
import boto3
import pandas as pd
from botocore import UNSIGNED
from botocore.client import Config
from io import BytesIO

def download_station_year(location_id: int, year: int, out_dir="data/raw_s3"):
    """
    Descarga todos los archivos CSV.gz de la estación location_id para el año dado.
    Guarda los archivos comprimidos en out_dir.
    """
    # Configura cliente S3 sin firma (acceso público)
    s3 = boto3.client(
        "s3",
        region_name="us-east-1",
        config=Config(signature_version=UNSIGNED)
    )
    bucket = "openaq-data-archive"
    prefix = f"records/csv.gz/locationid={location_id}/year={year}/"

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

    os.makedirs(out_dir, exist_ok=True)
    downloaded_files = []

    for page in pages:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".csv.gz"):
                print("Descargando:", key)
                resp = s3.get_object(Bucket=bucket, Key=key)
                body = resp["Body"].read()
                fname = os.path.join(out_dir, os.path.basename(key))
                with open(fname, "wb") as f:
                    f.write(body)
                downloaded_files.append(fname)

    print("Total archivos descargados:", len(downloaded_files))
    return downloaded_files

def read_and_concat(files, columns_filter=None):
    dfs = []
    for fpath in files:
        with gzip.open(fpath, "rt", encoding="utf-8") as f:
            df = pd.read_csv(f)
            dfs.append(df)
    if not dfs:
        return pd.DataFrame()
    df_full = pd.concat(dfs, ignore_index=True)
    if columns_filter:
        existing = [c for c in columns_filter if c in df_full.columns]
        df_full = df_full[existing]
    return df_full

def process_station_data(location_id, year, contaminants=None):
    print(f"Procesando estación {location_id} año {year}")
    out_raw = f"data/raw_s3/loc{location_id}_{year}"
    downloaded = download_station_year(location_id, year, out_dir=out_raw)

    cols = [
        "location_id", "sensors_id", "location",
        "datetime", "latitude", "longitude",
        "parameter", "value", "unit"
    ]
    if contaminants:
        df = read_and_concat(downloaded, columns_filter=cols)
        df = df[df["parameter"].isin(contaminants)]
    else:
        df = read_and_concat(downloaded, columns_filter=cols)

    os.makedirs("data/processed", exist_ok=True)
    outname = f"data/processed/station_{location_id}_{year}.csv"
    df.to_csv(outname, index=False)
    print("Archivo procesado guardado en:", outname)
    return df

if __name__ == "__main__":
    location_id = 2178
    year = 2020
    contaminants = ["pm25", "pm10", "no2", "o3", "so2"]
    df = process_station_data(location_id, year, contaminants=contaminants)
    print("Filas obtenidas:", len(df))
    print(df.head(5))
