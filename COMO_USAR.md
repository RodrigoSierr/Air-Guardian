# 🎯 Cómo Usar AirGuardian

## 🚀 Inicio Rápido (La forma más fácil)

### Para Windows:

**Haz doble clic en:**
```
START.bat
```

Esto iniciará automáticamente:
- ✅ Backend (API)
- ✅ Frontend (Interfaz web)
- ✅ Abrirá el navegador

---

## 📋 Scripts Disponibles

### Windows (tu sistema):

| Script | Qué hace |
|--------|----------|
| `START.bat` | Inicia TODO (backend + frontend) automáticamente |
| `START_BACKEND.bat` | Solo inicia el backend (puerto 8000) |
| `START_FRONTEND.bat` | Solo inicia el frontend (puerto 5173) |

### Linux/Mac:

| Script | Qué hace |
|--------|----------|
| `START.sh` | Inicia TODO (backend + frontend) automáticamente |

---

## 🔧 Inicio Manual (Paso a Paso)

Si prefieres iniciar manualmente:

### 1️⃣ Abrir Terminal (PowerShell o CMD)

**Terminal 1 - Backend:**
```powershell
cd C:\Users\Usuario\Desktop\web-earth\backend
.\venv\Scripts\python.exe main.py
```

### 2️⃣ Abrir OTRA Terminal

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\Usuario\Desktop\web-earth\frontend
npm run dev
```

### 3️⃣ Abrir el navegador

Ir a: **http://localhost:5173**

---

## 🌐 URLs de la Aplicación

Una vez iniciado:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend** | http://localhost:5173 | Aplicación web principal |
| **Backend API** | http://localhost:8000 | API REST |
| **Documentación API** | http://localhost:8000/docs | Swagger UI (documentación interactiva) |

---

## 🛑 Cómo Detener la Aplicación

### Si usaste START.bat:
- Cierra las ventanas que se abrieron (Backend y Frontend)
- O presiona `Ctrl+C` en cada ventana

### Si iniciaste manualmente:
- Ve a cada terminal y presiona `Ctrl+C`

---

## 🐛 Solución de Problemas

### ❌ Error: "Puerto 8000 ya está en uso"

**Solución 1:** Cierra cualquier ventana que tenga el backend corriendo

**Solución 2:** Encuentra y mata el proceso:
```powershell
netstat -ano | findstr :8000
taskkill /PID [NUMERO_DE_PID] /F
```

### ❌ Error: "Puerto 5173 ya está en uso"

No te preocupes, Vite usará automáticamente el siguiente puerto disponible (5174, 5175, etc.)

### ❌ Error: "ModuleNotFoundError" en el backend

Instala las dependencias:
```powershell
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### ❌ Error: "node_modules not found" en el frontend

Instala las dependencias:
```powershell
cd frontend
npm install
```

---

## 📊 Estado Normal de la Aplicación

Cuando todo funciona correctamente, deberías ver:

### Backend Terminal:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:XXXXX - "GET /api/stations HTTP/1.1" 200 OK
```

### Frontend Terminal:
```
VITE v4.x.x  ready in XXX ms

➜  Local:   http://localhost:5173/
```

### Navegador:
- ✅ Mapa visible
- ✅ Estaciones de monitoreo
- ✅ Sin errores en la consola (F12)

---

## 📝 Resumen Ultra-Rápido

**Para iniciar todo:**
```
Doble clic en START.bat
```

**Para verificar:**
```
http://localhost:5173  ← Abre esto en tu navegador
```

**Para detener:**
```
Ctrl+C en las ventanas abiertas
```

---

## ✅ Estado Actual de tu Sistema

- ✅ Backend corriendo correctamente
- ✅ Frontend debería estar iniciando
- ✅ Navegador debería abrirse automáticamente
- ✅ Modelo ML entrenado y listo

---

## 💡 Consejos

1. **Mantén las ventanas abiertas** mientras uses la aplicación
2. Si modificas código del **backend**, reinicia el backend (`Ctrl+C` y volver a ejecutar)
3. Si modificas código del **frontend**, Vite recarga automáticamente (no necesitas hacer nada)
4. Usa **START.bat** para iniciar rápidamente en el futuro

---

¡Disfruta usando AirGuardian! 🌍💨

