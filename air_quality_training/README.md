# Modelo Predictivo de Contaminación del Aire
## Datos Satelitales + Estaciones Reales (OpenAQ + NASA EarthData)

Este proyecto construye un modelo predictivo para estimar y proyectar niveles de contaminación atmosférica (PM2.5, PM10, NO₂, O₃, SO₂) usando datos de sensores urbanos y satelitales.

## Estructura del Proyecto

```
├── data/
│   ├── raw/              # Datos crudos
│   ├── raw_s3/           # Datos descargados de OpenAQ S3
│   └── processed/        # Datos procesados
├── models/              # Modelos entrenados y predicciones
├── notebooks/          # Jupyter notebooks
├── scripts/           # Scripts de Python
│   ├── download_data.py
│   ├── preprocess_data.py
│   ├── train_models.py
│   └── predict_us_stations.py
└── sdei/              # Datos satelitales de NASA
```

## Requisitos

```bash
pip install -r requirements.txt
```

## Uso

1. Descargar datos de OpenAQ:
```bash
python scripts/download_data.py
```

2. Preprocesar datos:
```bash
python scripts/preprocess_data.py
```

3. Entrenar modelo:
```bash
python scripts/train_models_hyperopt.py
```

4. Generar predicciones para múltiples estaciones:
```bash
python scripts/predict_us_stations.py
```

## Licencia

MIT