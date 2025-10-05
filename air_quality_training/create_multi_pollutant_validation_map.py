import os
import sys
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from datetime import datetime

STATIONS_FILE = "data/stations_us.csv"
YEARS = [2023, 2024]
POLLUTANTS = ["PM2_5", "PM10", "NO2", "O3", "SO2"]
OUT_REAL_CSV = "models/openaq_usa_2023_2024_monthly.csv"
OUT_MAP_HTML = "multi_pollutant_validation_map.html"


def ensure_import_path():
    sys.path.append('.')


def download_reals_for_station(location_id: int, years):
    from scripts.download_s3_openaq import download_station_year, read_and_concat
    all_files = []
    for y in years:
        out_dir = f"data/raw_s3/loc{location_id}_{y}"
        files = download_station_year(location_id, y, out_dir=out_dir)
        if files:
            all_files.extend(files)
    if not all_files:
        return pd.DataFrame()
    cols = ["location_id","datetime","latitude","longitude","parameter","value","unit","city","state"]
    df = read_and_concat(all_files, columns_filter=cols)
    return df


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # normalize parameter names to model naming
    name_map = {
        'pm25': 'PM2_5',
        'pm10': 'PM10',
        'no2': 'NO2',
        'o3': 'O3',
        'so2': 'SO2'
    }
    df = df.copy()
    df['parameter'] = df['parameter'].str.lower()
    df['par_norm'] = df['parameter'].map(name_map)
    df = df[df['par_norm'].isin(POLLUTANTS)]
    # Robust datetime parsing with mixed timezones
    dt = pd.to_datetime(df['datetime'], utc=True, errors='coerce')
    # Drop rows that failed to parse
    df = df.loc[~dt.isna()].copy()
    dt = dt.loc[~dt.isna()]
    # Remove timezone (to naive) for grouping
    df['datetime'] = dt.dt.tz_convert('UTC').dt.tz_localize(None)
    df['month'] = df['datetime'].dt.to_period('M').dt.to_timestamp()
    agg = (
        df.groupby(['location_id','city','state','latitude','longitude','month','par_norm'])['value']
          .mean()
          .reset_index()
          .pivot_table(index=['location_id','city','state','latitude','longitude','month'], columns='par_norm', values='value')
          .reset_index()
    )
    return agg


def build_map(df_monthly: pd.DataFrame):
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='OpenStreetMap')

    def add_pollutant_layer(pollutant: str, color: str):
        fg = folium.FeatureGroup(name=f"{pollutant} (2023-2024)")
        for _, r in df_monthly.groupby(['location_id','city','state','latitude','longitude'])[pollutant].mean().dropna().reset_index().iterrows():
            val = float(r[pollutant])
            # scale radius by pollutant concentration
            radius = 6
            if pollutant in ['PM2_5','PM10']:
                if val < 12: radius = 6
                elif val < 35: radius = 10
                elif val < 55: radius = 14
                else: radius = 18
            else:
                radius = max(6, min(18, val * 200))
            folium.CircleMarker(
                location=[r['latitude'], r['longitude']],
                radius=radius,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.5,
                popup=folium.Popup(f"{r['city']}, {r['state']}<br>{pollutant} promedio: {val:.3f}", max_width=260)
            ).add_to(fg)
        fg.add_to(m)

    color_map = {
        'PM2_5': '#1f77b4',  # blue
        'PM10': '#ff7f0e',   # orange
        'NO2': '#2ca02c',    # green
        'O3': '#9467bd',     # purple
        'SO2': '#d62728'     # red
    }
    for pol in POLLUTANTS:
        add_pollutant_layer(pol, color_map[pol])

    # Heatmaps per pollutant
    for pol in ['PM2_5','PM10']:
        points = df_monthly[['latitude','longitude',pol]].dropna().apply(lambda r: [float(r[0]), float(r[1]), float(r[2])], axis=1).tolist()
        HeatMap(points, name=f"Heatmap {pol}", radius=18, blur=22, max_zoom=6, min_opacity=0.3).add_to(m)

    folium.LayerControl().add_to(m)

    legend = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 360px; background: white; border: 2px solid #888; z-index: 9999; padding: 12px; border-radius: 8px; font-size: 14px;">
      <h4 style="margin:0 0 8px 0;">Capas por Contaminante (2023-2024)</h4>
      <p><span style="display:inline-block;width:12px;height:12px;background:#1f77b4;margin-right:8px;"></span>PM2.5</p>
      <p><span style="display:inline-block;width:12px;height:12px;background:#ff7f0e;margin-right:8px;"></span>PM10</p>
      <p><span style="display:inline-block;width:12px;height:12px;background:#2ca02c;margin-right:8px;"></span>NO2</p>
      <p><span style="display:inline-block;width:12px;height:12px;background:#9467bd;margin-right:8px;"></span>O3</p>
      <p><span style="display:inline-block;width:12px;height:12px;background:#d62728;margin-right:8px;"></span>SO2</p>
      <hr/>
      <p style="color:#666;">Activa/Desactiva capas en el control (arriba a la derecha).</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend))

    m.save(OUT_MAP_HTML)
    return OUT_MAP_HTML


def simple_projection_from_2020(predictions_csv: str, df_monthly_real: pd.DataFrame, annual_trend: float = 0.03) -> pd.DataFrame:
    # If we have 2020 data in predictions file, build a naive projection to 2023-2024
    if not os.path.exists(predictions_csv):
        return pd.DataFrame()
    dfp = pd.read_csv(predictions_csv)
    if 'PM10' not in dfp.columns and 'PM2_5' in dfp.columns:
        dfp['PM10'] = dfp['PM2_5'] * 1.6
    if 'datetime' in dfp.columns:
        dfp['datetime'] = pd.to_datetime(dfp['datetime'], errors='coerce')
    else:
        # assume 2020 hourly
        dfp['datetime'] = pd.date_range(start='2020-01-01', periods=len(dfp), freq='H')
    base = (
        dfp[dfp['datetime'].dt.year == 2020]
        .groupby(['location_id','city','state','latitude','longitude'])[POLLUTANTS]
        .mean().reset_index()
    )
    months = pd.period_range('2023-01', '2024-12', freq='M').to_timestamp()
    rows = []
    for idx, month in enumerate(months):
        factor = 1 + annual_trend * ( (month.year - 2020) + (month.month-1)/12 )
        g = base.copy()
        g['month'] = month
        for pol in POLLUTANTS:
            if pol in g.columns:
                g[pol] = g[pol] * factor
        rows.append(g)
    proj = pd.concat(rows, ignore_index=True)
    # Harmonize with real monthly
    cols = ['location_id','city','state','latitude','longitude','month'] + POLLUTANTS
    proj = proj[cols]
    return proj


def add_validation_to_map(map_html: str, real_df: pd.DataFrame, proj_df: pd.DataFrame):
    # Compute errors for PM2.5 and PM10 monthly mean across 2023-2024
    if proj_df.empty:
        return
    real_avg = real_df.groupby(['location_id','city','state','latitude','longitude'])[ ['PM2_5','PM10'] ].mean()
    proj_avg = proj_df.groupby(['location_id','city','state','latitude','longitude'])[ ['PM2_5','PM10'] ].mean()
    comp = real_avg.join(proj_avg, lsuffix='_real', rsuffix='_proj', how='inner').reset_index()
    comp['PM2_5_diff'] = comp['PM2_5_proj'] - comp['PM2_5_real']
    comp['PM10_diff'] = comp['PM10_proj'] - comp['PM10_real']

    # Separate validation map
    val = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles='OpenStreetMap')
    fg = folium.FeatureGroup(name='Validación: Proyección - Real (positivo = sobreestima)')
    for _, r in comp.iterrows():
        diff = float(r['PM2_5_diff'])
        color = '#d73027' if diff > 0 else '#1a9850'
        radius = min(18, max(6, abs(diff)))
        folium.CircleMarker(
            location=[r['latitude'], r['longitude']],
            radius=radius,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.6,
            popup=folium.Popup(f"{r['city']}, {r['state']}<br>Δ PM2.5 (proj-real): {diff:.2f}", max_width=260)
        ).add_to(fg)
    fg.add_to(val)
    folium.LayerControl().add_to(val)
    val.save('validation_projection_vs_real.html')


def main():
    ensure_import_path()
    print('[INICIANDO] Descarga OpenAQ 2023-2024 y mapa multi-contaminante')
    stations = pd.read_csv(STATIONS_FILE)

    monthly_list = []
    ok = 0
    for _, s in stations.iterrows():
        try:
            df = download_reals_for_station(int(s['location_id']), YEARS)
            if df.empty:
                continue
            agg = aggregate_monthly(df)
            if not agg.empty:
                monthly_list.append(agg)
                ok += 1
        except Exception as e:
            print(f"[WARN] Estación {s['location_id']} falló: {e}")
    if not monthly_list:
        print('[ERROR] No se descargaron datos reales')
        return
    monthly = pd.concat(monthly_list, ignore_index=True)
    os.makedirs(os.path.dirname(OUT_REAL_CSV), exist_ok=True)
    monthly.to_csv(OUT_REAL_CSV, index=False)
    print(f"[OK] Guardado real mensual: {OUT_REAL_CSV} ({len(monthly)} filas, {ok} estaciones)")

    # Build map
    map_path = build_map(monthly)
    print(f"[OK] Mapa guardado: {map_path}")

    # Validation: compare with naive projection from 2020 predictions
    proj = simple_projection_from_2020('models/predictions_us_map.csv', monthly)
    if not proj.empty:
        add_validation_to_map(map_path, monthly, proj)
        print('[OK] Validación guardada: validation_projection_vs_real.html')
    else:
        print('[INFO] Sin proyección disponible para validación')


if __name__ == '__main__':
    main()
