import os
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, HeatMapWithTime
from datetime import datetime, timedelta


def load_base_data():
    src = "models/predictions_us_map.csv"
    if not os.path.exists(src):
        raise FileNotFoundError("models/predictions_us_map.csv not found")
    df = pd.read_csv(src)
    # Ensure required columns
    if "PM10" not in df.columns:
        if "PM2_5" in df.columns:
            df["PM10"] = df["PM2_5"] * 1.6
        else:
            raise RuntimeError("PM10 not present and cannot derive from PM2_5")
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"]) 
    else:
        start_date = datetime(2020, 1, 1)
        df["datetime"] = [start_date + timedelta(hours=i) for i in range(len(df))]
    # Keep key columns
    keep = [c for c in ["location_id","city","state","latitude","longitude","PM10","datetime"] if c in df.columns]
    return df[keep]


def build_future_projection(df_current: pd.DataFrame, months_ahead: int = 36, annual_trend: float = 0.015) -> pd.DataFrame:
    # Aggregate current by station as baseline
    baseline = df_current.groupby(["location_id","city","state","latitude","longitude"], dropna=False).agg({
        "PM10": "mean"
    }).reset_index()
    # Build monthly future dates
    last_date = df_current["datetime"].max()
    monthly_dates = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=months_ahead, freq="MS")
    rows = []
    for month_idx, dt in enumerate(monthly_dates):
        # temporal factor based on annual trend
        months_elapsed = month_idx + 1
        temporal_factor = 1 + (annual_trend * (months_elapsed / 12.0))
        g = baseline.copy()
        g["datetime"] = dt
        g["PM10"] = g["PM10"] * temporal_factor
        rows.append(g)
    future = pd.concat(rows, ignore_index=True)
    return future


def _points_from_df(df: pd.DataFrame, value_col: str):
    return df[["latitude","longitude",value_col]].dropna().apply(lambda r: [float(r[0]), float(r[1]), float(r[2])], axis=1).tolist()


def build_dual_static_heatmap(df_current, df_future, out_html="dual_pm10_heatmap_static.html"):
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="OpenStreetMap")
    # Blue gradient for current
    blue_gradient = {0.0: '#e6f2ff', 0.25: '#99ccff', 0.5: '#4da3ff', 0.75: '#1a75ff', 1.0: '#0047b3'}
    # Red gradient for future
    red_gradient = {0.0: '#ffe6e6', 0.25: '#ff9999', 0.5: '#ff4d4d', 0.75: '#ff1a1a', 1.0: '#b30000'}

    curr_points = _points_from_df(df_current, "PM10")
    fut_points = _points_from_df(df_future, "PM10")

    curr_layer = HeatMap(curr_points, name="Actual 2020-2022 (PM10)", radius=18, blur=22, max_zoom=6, min_opacity=0.3, gradient=blue_gradient)
    fut_layer = HeatMap(fut_points, name="Impacto Futuro 2023-2025 (Sin Acción)", radius=18, blur=22, max_zoom=6, min_opacity=0.3, gradient=red_gradient)

    curr_fg = folium.FeatureGroup(name="Actual 2020-2022 (PM10)")
    curr_fg.add_child(curr_layer)
    fut_fg = folium.FeatureGroup(name="Impacto Futuro 2023-2025 (PM10)")
    fut_fg.add_child(fut_layer)

    curr_fg.add_to(m)
    fut_fg.add_to(m)
    folium.LayerControl().add_to(m)

    # Legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 320px; background: white; border: 2px solid #888; z-index: 9999; padding: 12px; border-radius: 8px; font-size: 14px;">
      <h4 style="margin: 0 0 8px 0;">Mapa de Calor PM10</h4>
      <p style="margin: 4px 0;"><span style="display:inline-block;width:14px;height:14px;background:#1a75ff;margin-right:8px;"></span>Actual 2020-2022</p>
      <p style="margin: 4px 0;"><span style="display:inline-block;width:14px;height:14px;background:#ff1a1a;margin-right:8px;"></span>Futuro 2023-2025 (Sin acción)</p>
      <p style="margin: 6px 0; color:#666;">Más intenso = mayor concentración</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(out_html)
    return out_html


def build_dual_time_heatmap(df_current, df_future, out_html="dual_pm10_heatmap_time.html"):
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="OpenStreetMap")

    # Prepare monthly buckets
    def frames_by_month(df):
        tmp = df.copy()
        tmp["datetime"] = pd.to_datetime(tmp["datetime"]) 
        tmp["bucket"] = tmp["datetime"].dt.to_period("M").dt.to_timestamp()
        frames = []
        index = []
        for ts, g in tmp.groupby("bucket"):
            pts = _points_from_df(g, "PM10")
            frames.append(pts)
            index.append(ts.strftime("%Y-%m"))
        return frames, index

    curr_frames, curr_index = frames_by_month(df_current)
    fut_frames, fut_index = frames_by_month(df_future)

    blue_gradient = {0.0: '#e6f2ff', 0.25: '#99ccff', 0.5: '#4da3ff', 0.75: '#1a75ff', 1.0: '#0047b3'}
    red_gradient = {0.0: '#ffe6e6', 0.25: '#ff9999', 0.5: '#ff4d4d', 0.75: '#ff1a1a', 1.0: '#b30000'}

    HeatMapWithTime(curr_frames, index=curr_index, radius=16, auto_play=False, name="Actual 2020-2022", gradient=blue_gradient, max_opacity=0.8).add_to(m)
    HeatMapWithTime(fut_frames, index=fut_index, radius=16, auto_play=False, name="Futuro 2023-2025", gradient=red_gradient, max_opacity=0.8).add_to(m)

    folium.LayerControl().add_to(m)

    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 340px; background: white; border: 2px solid #888; z-index: 9999; padding: 12px; border-radius: 8px; font-size: 14px;">
      <h4 style="margin: 0 0 8px 0;">Mapa de Calor con Línea de Tiempo (PM10)</h4>
      <p style="margin: 4px 0;"><span style="display:inline-block;width:14px;height:14px;background:#1a75ff;margin-right:8px;"></span>Actual 2020-2022</p>
      <p style="margin: 4px 0;"><span style="display:inline-block;width:14px;height:14px;background:#ff1a1a;margin-right:8px;"></span>Futuro 2023-2025</p>
      <p style="margin: 6px 0; color:#666;">Usa el control de capas y la barra temporal</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(out_html)
    return out_html


def main():
    print("[INICIANDO] Dual heatmaps PM10 (actual vs futuro)")
    df_current = load_base_data()
    # Current period: keep up to end of 2022
    df_current = df_current[df_current["datetime"] <= pd.Timestamp("2022-12-31")]
    # Build future projection 2023-2025 (sin acción)
    df_future = build_future_projection(df_current, months_ahead=36, annual_trend=0.015)

    # Subsample for performance if huge
    if len(df_current) > 250000:
        df_current = df_current.sample(250000, random_state=42)

    static_path = build_dual_static_heatmap(df_current, df_future)
    time_path = build_dual_time_heatmap(df_current, df_future)

    print("[OK] Mapas generados:")
    print(f"  - {static_path}")
    print(f"  - {time_path}")


if __name__ == "__main__":
    main()

