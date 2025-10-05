# 🌍 Funcionalidades de Predicciones - AirGuardian

## 📋 Resumen

Se han integrado funcionalidades avanzadas de predicciones de calidad del aire en AirGuardian, incluyendo:

1. **Layer de Predicciones** con mapa de calor
2. **Botones de Análisis** en cada sensor
3. **Controles de Activación/Desactivación**
4. **Análisis Detallado** con gráficos interactivos

## 🚀 Instalación

### 1. Instalar Dependencias
```bash
# Ejecutar el script de instalación
python install_prediction_dependencies.py
```

### 2. Reiniciar Servicios
```bash
# Backend
cd backend
python main.py

# Frontend (en otra terminal)
cd frontend
npm start
```

## 🎯 Funcionalidades Implementadas

### 1. **Layer de Predicciones**
- **Mapa de calor** que muestra predicciones por contaminante
- **Sensores con valores** de predicción en tiempo real
- **Colores dinámicos** basados en niveles de calidad del aire
- **Controles de capas** para activar/desactivar predicciones

### 2. **Botones de Análisis por Sensor**
- **📈 Timeline**: Gráficos de evolución temporal
- **📊 Análisis de Impacto**: Comparación histórico vs predicciones
- **⏰ Línea de Tiempo Interactiva**: Escenarios futuros

### 3. **Controles de Activación/Desactivación**
- **Toggle principal** para mostrar/ocultar predicciones
- **Toggle de mapa de calor** para activar/desactivar visualización
- **Toggle de sensores** para mostrar/ocultar marcadores
- **Controles en tiempo real** con feedback visual

## 🔧 Uso del Sistema

### **Paso 1: Activar Predicciones**
1. Abre AirGuardian en tu navegador
2. Haz clic en el botón de capas (arriba a la derecha)
3. Activa la opción "Predicciones"
4. Selecciona una estación en el mapa

### **Paso 2: Ver Predicciones**
1. Las predicciones aparecerán como mapa de calor
2. Los sensores mostrarán valores de predicción
3. Haz clic en un sensor para ver detalles

### **Paso 3: Análisis Detallado**
1. Haz clic en un sensor con predicciones
2. Usa los botones de análisis:
   - **Timeline**: Evolución temporal
   - **Análisis de Impacto**: Comparación histórica
   - **Línea de Tiempo**: Escenarios futuros

## 📊 Tipos de Análisis

### **Timeline Analysis**
- Datos históricos de los últimos 30 días
- Predicciones para las próximas 48 horas
- Gráficos de evolución por contaminante

### **Impact Analysis**
- Comparación entre datos históricos (2020) y predicciones (2023-2024)
- Análisis por contaminante (PM2.5, PM10, NO₂, O₃, SO₂)
- Cálculo de cambios porcentuales

### **Interactive Timeline**
- Escenarios futuros:
  - **Tendencia Actual**: Basado en condiciones actuales
  - **Política Verde**: Implementación de políticas ambientales
  - **Crecimiento Urbano**: Aumento de urbanización
  - **Emergencia Climática**: Medidas drásticas de acción climática

## 🎨 Interfaz de Usuario

### **Controles de Capas**
- **Ground Stations**: Estaciones de monitoreo
- **TEMPO Satellite**: Datos satelitales de NASA
- **Predicciones**: Layer de predicciones (NUEVO)

### **Modal de Análisis**
- **Resumen**: Información general del análisis
- **Gráfico**: Visualización de datos
- **Datos**: Datos raw para descarga

### **Botones de Análisis**
- Diseño intuitivo con iconos
- Colores distintivos por tipo de análisis
- Información contextual en tooltips

## 🔌 API Endpoints

### **Nuevos Endpoints Agregados**

#### `GET /api/prediction-layer/{station_id}`
Obtiene datos de predicción para una estación específica.

#### `GET /api/prediction-layer/heatmap/{pollutant}`
Obtiene datos de mapa de calor para un contaminante específico.

#### `POST /api/prediction-layer/analysis`
Genera análisis detallado para una estación.

#### `GET /api/prediction-layer/toggle`
Activa/desactiva el layer de predicciones.

## 📁 Archivos Agregados

### **Backend**
- `prediction_layer_api.py` - API endpoints para predicciones
- `install_prediction_dependencies.py` - Script de instalación

### **Frontend**
- `PredictionLayer.jsx` - Componente de layer de predicciones
- `PredictionLayer.css` - Estilos para predicciones
- `AnalysisModal.jsx` - Modal de análisis detallado
- `AnalysisModal.css` - Estilos para modal de análisis

### **Modificaciones**
- `MapView.jsx` - Integración del layer de predicciones
- `LayerControl.jsx` - Toggle para predicciones
- `main.py` - Inclusión del router de predicciones

## 🚨 Solución de Problemas

### **Error: "Module not found"**
```bash
# Instalar dependencias faltantes
pip install pandas numpy scikit-learn plotly folium
```

### **Error: "CORS" en frontend**
- Verificar que el backend esté ejecutándose en puerto 8000
- Revisar configuración CORS en `main.py`

### **Error: "Prediction layer not loading"**
- Verificar que la estación esté seleccionada
- Comprobar que el layer de predicciones esté activado
- Revisar logs del backend

### **Error: "Analysis modal not opening"**
- Verificar que el análisis se haya generado correctamente
- Comprobar que los datos de la estación estén disponibles

## 🔧 Configuración Avanzada

### **Personalizar Predicciones**
Editar `prediction_layer_api.py` para modificar:
- Algoritmos de predicción
- Escenarios futuros
- Períodos de análisis

### **Personalizar Visualizaciones**
Editar `PredictionLayer.css` y `AnalysisModal.css` para:
- Colores y estilos
- Tamaños de componentes
- Animaciones

### **Agregar Nuevos Contaminantes**
Modificar los endpoints en `prediction_layer_api.py` para incluir nuevos contaminantes.

## 📈 Próximas Mejoras

1. **Integración con Datos Reales**: Conectar con APIs de calidad del aire
2. **Alertas Automáticas**: Sistema de notificaciones
3. **Exportación de Datos**: Funcionalidad de descarga
4. **Móvil**: Versión responsive optimizada
5. **Machine Learning**: Modelos predictivos más avanzados

## 📞 Soporte

Para cualquier problema o consulta:
1. Revisar los logs del backend
2. Verificar la consola del navegador
3. Comprobar que todas las dependencias estén instaladas
4. Verificar que los servicios estén ejecutándose correctamente

---

**🎉 ¡Sistema de Predicciones Integrado Exitosamente!**

*Todas las funcionalidades están listas para su uso en AirGuardian.*
