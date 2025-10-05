import os
import json
import pandas as pd

def preprocess_openaq_pm25(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        js = json.load(f)
    results = js.get("results", [])
    if not results:
        print("No 'results' in JSON.")
        return
    df = pd.json_normalize(results)

    print("Available columns:", df.columns.tolist())

    desired = []
    for c in ["date.utc", "location", "parameter", "value", "unit",
              "coordinates.latitude", "coordinates.longitude"]:
        if c in df.columns:
            desired.append(c)
        else:
            print("Column missing:", c)

    df2 = df[desired].copy()

    rename_map = {}
    if "coordinates.latitude" in df2.columns:
        rename_map["coordinates.latitude"] = "latitude"
    if "coordinates.longitude" in df2.columns:
        rename_map["coordinates.longitude"] = "longitude"
    if "value" in df2.columns:
        rename_map["value"] = "pm25"

    df2 = df2.rename(columns=rename_map)

    if "date.utc" in df2.columns:
        df2["date.utc"] = pd.to_datetime(df2["date.utc"])

    os.makedirs("../data/processed", exist_ok=True)
    outfname = "../data/processed/openaq_pm25_processed.csv"
    df2.to_csv(outfname, index=False)
    print("Processed file saved:", outfname)

if __name__ == "__main__":
    # Ajusta esta ruta al nombre del archivo JSON descargado
    json_path = "../data/raw/openaq_pm25_2024-09-01_2024-10-04.json"
    preprocess_openaq_pm25(json_path)
