import os
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, HeatMapWithTime
from datetime import datetime, timedelta


def load_or_build_dataset():
    # Prefer multi-stations file; fallback to predictions_us_map.csv
    if os.path.exists("air_quality_multi_stations_timeline_map.html") and os.path.exists("air_quality_multi_stations_dashboard.html"):
        # Use the dataset created for multi-stations if available
        # But since it's embedded HTML, instead rely on the generator's CSV if present
        pass
    # Try combined predictions file
    src = "models/predictions_us_map.csv"
    if os.path.exists(src):
        df = pd.read_csv(src)
        # Ensure required columns
        required = {"latitude","longitude","PM10"}
        if not required.issubset(df.columns):
            # Build synthetic PM10 from available columns as fallback
            if "PM2_5" in df.columns:
                df["PM10"] = df["PM2_5"] * 1.6
            else:
                raise RuntimeError("PM10 not present and cannot derive from PM2_5")
        # Ensure datetime column exists
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
        else:
            # create hourly range
            start_date = datetime(2020,1,1)
            df = df.copy()
            df["datetime"] = [start_date + timedelta(hours=i) for i in range(len(df))]
        return df
    raise FileNotFoundError("models/predictions_us_map.csv not found")


essential_cols = ["latitude","longitude","PM10","datetime"]

def build_static_heatmap(df, out_html="pm10_heatmap_static.html"):
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="OpenStreetMap")
    heat_data = df[essential_cols].dropna()
    # values scaled for better visual; PM10 is ug/m3 typical tens range
    points = heat_data.apply(lambda r: [r["latitude"], r["longitude"], float(r["PM10"])], axis=1).tolist()
    HeatMap(points, radius=18, blur=22, max_zoom=6, min_opacity=0.3).add_to(m)
    m.save(out_html)
    return out_html


def build_time_heatmap(df, out_html="pm10_heatmap_time.html", period="M"):
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="OpenStreetMap")
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"]) 
    # aggregate by month to reduce frames
    df["time_bucket"] = df["datetime"].dt.to_period(period).dt.to_timestamp()
    frames = []
    time_index = []
    for ts, group in df.groupby("time_bucket"):
        g = group[essential_cols].dropna()
        frame = g.apply(lambda r: [r["latitude"], r["longitude"], float(r["PM10"])], axis=1).tolist()
        frames.append(frame)
        time_index.append(ts.strftime("%Y-%m"))
    HeatMapWithTime(frames, index=time_index, radius=16, auto_play=True, max_opacity=0.8).add_to(m)
    m.save(out_html)
    return out_html


def main():
    print("[INICIANDO] Construcción de mapas de calor PM10")
    df = load_or_build_dataset()
    # Keep only US if columns exist
    # If there are many rows, sample to speed up
    if len(df) > 200000:
        df = df.sample(n=200000, random_state=42)
    static_path = build_static_heatmap(df)
    time_path = build_time_heatmap(df)
    print(f"[OK] Mapas generados:\n  - {static_path}\n  - {time_path}")


if __name__ == "__main__":
    main()
