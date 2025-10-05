# 🚀 AirGuardian - Inicio Rápido

## Opción 1: Script Automático (Recomendado)

### Windows
```bash
# Doble clic en START.bat
# O ejecutar en terminal:
START.bat
```

### Linux/Mac
```bash
chmod +x START.sh
./START.sh
```

El script automático:
1. ✅ Verifica que Python y Node.js estén instalados
2. ✅ Crea el entorno virtual de Python
3. ✅ Instala todas las dependencias
4. ✅ Inicia backend y frontend automáticamente
5. ✅ Abre tu navegador en http://localhost:5173

---

## Opción 2: Manual

### Paso 1: Backend

```bash
# Terminal 1
cd backend

# Crear y activar entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python main.py
```

✅ Backend corriendo en http://localhost:8000

### Paso 2: Frontend

```bash
# Terminal 2 (nueva ventana)
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor
npm run dev
```

✅ Frontend corriendo en http://localhost:5173

---

## 🌐 Acceder a la Aplicación

Abre tu navegador y ve a: **http://localhost:5173**

---

## 🎯 Verificar que Funciona

1. ✅ Deberías ver un mapa oscuro con marcadores de colores
2. ✅ Click en el sidebar para ver estaciones
3. ✅ Click en un marcador para abrir el panel de detalles
4. ✅ Navega por las pestañas: Current, History, Forecast
5. ✅ Click en el ícono de capas (arriba derecha) para activar TEMPO

---

## 🔧 APIs Opcionales

La aplicación funciona con datos mock sin configuración adicional.

Para usar datos reales, crea `backend/.env`:

```env
OPENWEATHER_API_KEY=tu_key_aqui
NASA_API_KEY=DEMO_KEY
```

**Obtener API Keys:**
- OpenWeatherMap: https://openweathermap.org/api (gratis)
- NASA: https://api.nasa.gov/ (usa DEMO_KEY o registra)

---

## ❓ Problemas Comunes

### Puerto 8000 ya en uso
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID [PID] /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Puerto 5173 ya en uso
Edita `frontend/vite.config.js` y cambia el puerto a 3000

### Errores de instalación
```bash
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Documentación Completa

- Ver [SETUP.md](SETUP.md) para guía detallada
- Ver [README.md](README.md) para documentación completa

---

## ✨ Características

- 🗺️ Mapa interactivo con Leaflet
- 📊 Gráficos de tendencias históricas
- 🤖 Predicciones ML de 48 horas
- 🛰️ Capa satelital TEMPO (heatmap)
- 🌙 Tema oscuro moderno
- 📱 Diseño responsive

---

## 🆘 Ayuda

¿Problemas? Revisa:
1. Logs en las terminales del backend y frontend
2. Consola del navegador (F12)
3. Que ambos servidores estén corriendo
4. Que los puertos no estén bloqueados

---

**¡Disfruta monitoreando la calidad del aire!** 🌍💨

