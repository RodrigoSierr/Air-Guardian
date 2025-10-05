# 🚀 Guía de Configuración de AirGuardian

Esta guía te llevará paso a paso para configurar y ejecutar AirGuardian en tu máquina local.

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.9 o superior** - [Descargar](https://www.python.org/downloads/)
- **Node.js 18 o superior** - [Descargar](https://nodejs.org/)
- **Git** - [Descargar](https://git-scm.com/)

### Verificar Instalaciones

```bash
python --version  # Debe mostrar Python 3.9+
node --version    # Debe mostrar Node 18+
npm --version     # Debe mostrar npm 9+
```

## 🔑 Obtener API Keys (Opcional pero Recomendado)

### OpenWeatherMap (Recomendado)
1. Ve a https://openweathermap.org/api
2. Crea una cuenta gratuita
3. Genera una API key (gratis hasta 1000 llamadas/día)
4. Guarda tu API key

### NASA API (Opcional)
1. Ve a https://api.nasa.gov/
2. Registra tu aplicación
3. Usa `DEMO_KEY` o tu propia key
4. Guarda tu API key

**Nota:** La aplicación funcionará con datos mock si no configuras las API keys.

## 📦 Instalación

### Paso 1: Clonar o Descargar el Proyecto

Si tienes Git:
```bash
cd tu-directorio-de-trabajo
# El proyecto ya está en: C:\Users\Usuario\Desktop\web-earth
cd C:\Users\Usuario\Desktop\web-earth
```

### Paso 2: Configurar el Backend

```bash
# Navegar a la carpeta backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# En Windows (CMD):
venv\Scripts\activate.bat

# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (opcional)
# Copiar .env.example a .env y editar
# O crear manualmente:
```

Crear archivo `backend/.env`:
```
OPENWEATHER_API_KEY=tu_api_key_aqui
NASA_API_KEY=DEMO_KEY
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Paso 3: Configurar el Frontend

Abre una **nueva terminal** (mantén el backend abierto):

```bash
# Desde la raíz del proyecto
cd frontend

# Instalar dependencias (puede tardar unos minutos)
npm install

# Crear archivo .env (opcional)
```

Crear archivo `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

## ▶️ Ejecutar la Aplicación

### Terminal 1: Backend

```bash
cd backend

# Activar entorno virtual si no está activado
# Windows: .\venv\Scripts\Activate.ps1
# Linux/Mac: source venv/bin/activate

# Iniciar servidor backend
python main.py
```

Deberías ver:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**El backend está corriendo en:** http://localhost:8000

### Terminal 2: Frontend

```bash
cd frontend

# Iniciar servidor de desarrollo
npm run dev
```

Deberías ver:
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**El frontend está corriendo en:** http://localhost:5173

## 🌐 Usar la Aplicación

1. Abre tu navegador
2. Ve a http://localhost:5173
3. Deberías ver el mapa de AirGuardian con estaciones de calidad del aire
4. Haz clic en cualquier estación para ver detalles
5. Explora las pestañas: Current, History, Forecast

## ✅ Verificar que Todo Funciona

### Verificar Backend
Abre http://localhost:8000/docs en tu navegador
- Deberías ver la documentación interactiva de FastAPI
- Prueba el endpoint `/api/stations`

### Verificar Frontend
1. El mapa debe cargar con marcadores de colores
2. El sidebar debe mostrar estaciones
3. Al hacer clic en una estación, debe abrirse el panel de detalles
4. Los gráficos deben visualizarse correctamente

## 🐛 Solución de Problemas

### Error: Puerto 8000 ya en uso

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: Puerto 5173 ya en uso

```bash
# Edita frontend/vite.config.js y cambia el puerto:
server: {
  port: 3000,  // Usa otro puerto
}
```

### Error: Módulo no encontrado (Python)

```bash
# Asegúrate de que el entorno virtual está activado
cd backend
pip install -r requirements.txt --force-reinstall
```

### Error: Módulo no encontrado (Node)

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error: CORS en el navegador

Verifica que el backend tenga configurado:
```python
# En backend/main.py
allow_origins=["http://localhost:5173"]
```

### No se muestran estaciones en el mapa

1. Verifica que el backend esté corriendo
2. Abre la consola del navegador (F12)
3. Busca errores en la pestaña "Console"
4. Verifica la pestaña "Network" para ver si las llamadas API fallan

## 🔄 Entrenar el Modelo ML

El modelo se entrena automáticamente en el primer inicio. Para re-entrenar:

```bash
cd backend
python ml_model.py
```

Esto creará/actualizará los archivos en `backend/model/`

## 🐳 Alternativa: Usar Docker

Si tienes Docker instalado:

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Detener
docker-compose down
```

## 📝 Notas Adicionales

### Datos Mock vs Datos Reales

- Sin API keys: La app usa datos simulados (mock data)
- Con API keys: La app obtiene datos reales de OpenAQ y OpenWeatherMap

### Límites de API

- **OpenAQ**: Sin límite estricto para v2 API
- **OpenWeatherMap**: 1000 llamadas/día (gratis)
- **NASA**: 30 llamadas/hora con DEMO_KEY, más con key registrada

### Rendimiento

- Primera carga puede ser lenta mientras entrena el modelo ML
- Los datos se cachean para mejorar el rendimiento
- Usa datos mock locales para desarrollo rápido

## 🎉 ¡Listo!

Tu aplicación AirGuardian está corriendo. Explora las funcionalidades:

- ✅ Mapa interactivo con estaciones
- ✅ Datos en tiempo real
- ✅ Gráficos históricos
- ✅ Predicciones ML de 48 horas
- ✅ Interfaz responsive
- ✅ Tema oscuro moderno

## 🆘 Ayuda

Si tienes problemas:

1. Verifica que ambos servidores (backend y frontend) estén corriendo
2. Revisa los logs en las terminales
3. Abre las DevTools del navegador (F12) y busca errores
4. Verifica que los puertos 8000 y 5173 no estén bloqueados por firewall

---

**¡Disfruta monitoreando la calidad del aire!** 🌍💨

