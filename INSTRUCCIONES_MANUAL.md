# 🚀 Instrucciones para Iniciar AirGuardian MANUALMENTE

## 📋 Requisitos Previos
- Python 3.9 o superior instalado
- Node.js 18 o superior instalado

---

## 🐍 PASO 1: Iniciar el Backend

### 1.1 Abrir Terminal/PowerShell
- Presiona `Win + R`
- Escribe `powershell` y presiona Enter

### 1.2 Navegar a la carpeta del backend
```powershell
cd C:\Users\Usuario\Desktop\web-earth\backend
```

### 1.3 Activar el entorno virtual
```powershell
.\venv\Scripts\Activate.ps1
```

**Si te da error de permisos en PowerShell**, usa Command Prompt (cmd) en su lugar:
```cmd
venv\Scripts\activate.bat
```

### 1.4 Iniciar el servidor FastAPI
```powershell
python main.py
```

### ✅ Verificación del Backend
Deberías ver algo como esto:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Abre en el navegador:** http://localhost:8000

Deberías ver:
```json
{"message": "AirGuardian API", "version": "1.0.0"}
```

✅ **¡Backend funcionando! NO CIERRES ESTA TERMINAL.**

---

## ⚛️ PASO 2: Iniciar el Frontend

### 2.1 Abrir OTRA Terminal/PowerShell
- Presiona `Win + R`
- Escribe `powershell` y presiona Enter
- (Necesitas una terminal separada, no cierres la del backend)

### 2.2 Navegar a la carpeta del frontend
```powershell
cd C:\Users\Usuario\Desktop\web-earth\frontend
```

### 2.3 Iniciar el servidor de desarrollo Vite
```powershell
npm run dev
```

### ✅ Verificación del Frontend
Deberías ver algo como esto:
```
  VITE v4.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

**Abre en el navegador:** http://localhost:5173

✅ **¡Frontend funcionando! NO CIERRES ESTA TERMINAL.**

---

## 🌐 PASO 3: Usar la Aplicación

Abre tu navegador en: **http://localhost:5173**

Deberías ver:
- ✅ El mapa de AirGuardian
- ✅ Estaciones de monitoreo
- ✅ NO deberías ver errores en la consola

---

## 🛑 Para Detener los Servidores

1. **Backend**: Ve a la terminal del backend y presiona `Ctrl + C`
2. **Frontend**: Ve a la terminal del frontend y presiona `Ctrl + C`

---

## 🐛 Solución de Problemas Comunes

### Error: "No se puede activar el entorno virtual"

**En PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Luego intenta activar nuevamente.

**O usa Command Prompt (cmd) en su lugar:**
```cmd
cd C:\Users\Usuario\Desktop\web-earth\backend
venv\Scripts\activate.bat
python main.py
```

---

### Error: "ModuleNotFoundError" al iniciar el backend

Instala las dependencias:
```powershell
cd C:\Users\Usuario\Desktop\web-earth\backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

---

### Error: "node_modules not found" al iniciar el frontend

Instala las dependencias:
```powershell
cd C:\Users\Usuario\Desktop\web-earth\frontend
npm install
npm run dev
```

---

### El puerto 8000 ya está en uso

Busca qué proceso está usando el puerto:
```powershell
netstat -ano | findstr :8000
```

Mata el proceso (reemplaza XXXX con el PID que encontraste):
```powershell
taskkill /PID XXXX /F
```

---

### El puerto 5173 ya está en uso

Vite automáticamente usará el siguiente puerto disponible (5174, 5175, etc.)
Revisa el mensaje en la terminal para ver qué puerto está usando.

---

## 📝 Resumen Rápido

**Terminal 1 (Backend):**
```powershell
cd C:\Users\Usuario\Desktop\web-earth\backend
.\venv\Scripts\Activate.ps1
python main.py
```

**Terminal 2 (Frontend):**
```powershell
cd C:\Users\Usuario\Desktop\web-earth\frontend
npm run dev
```

**Navegador:**
```
http://localhost:5173
```

---

## ✅ Cambios Aplicados

✅ Arreglado error de importación circular en `predict_api.py`
✅ Arreglado error de Leaflet en `index.html`
✅ Arreglado URL de API en `TempoHeatmap.jsx`

¡Todo debería funcionar ahora! 🎉

