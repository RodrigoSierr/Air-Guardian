# 🚀 Instrucciones Rápidas - AirGuardian

## ❌ Error: Backend no está corriendo

Si ves el error `ERR_CONNECTION_REFUSED` en la consola del navegador, significa que el backend no está corriendo.

## ✅ Solución en 3 pasos

### **Opción 1: Inicio Automático (Recomendado)**

Ejecuta el archivo principal:
```
START.bat
```

Este script iniciará automáticamente:
- ✅ Backend en http://localhost:8000
- ✅ Frontend en http://localhost:5173
- ✅ Abrirá el navegador automáticamente

---

### **Opción 2: Inicio Manual (Separado)**

Si prefieres controlar cada servidor por separado:

#### 1️⃣ Iniciar el Backend (PRIMERO)
```
START_BACKEND.bat
```
- Espera a ver el mensaje: `Uvicorn running on http://0.0.0.0:8000`
- **NO CIERRES ESTA VENTANA**

#### 2️⃣ Iniciar el Frontend (DESPUÉS)
```
START_FRONTEND.bat
```
- Espera a ver: `Local: http://localhost:5173/`
- **NO CIERRES ESTA VENTANA**

#### 3️⃣ Abrir en el navegador
```
http://localhost:5173
```

---

## 🔍 Verificar que todo funciona

### Backend (debe estar corriendo)
Abre en tu navegador: http://localhost:8000

Deberías ver:
```json
{
  "message": "AirGuardian API",
  "version": "1.0.0"
}
```

### Frontend (debe estar corriendo)
Abre en tu navegador: http://localhost:5173

Deberías ver la aplicación AirGuardian con el mapa.

---

## 🐛 Solución de problemas

### Error: "Python no está instalado"
Instala Python 3.9+ desde: https://www.python.org/downloads/

### Error: "Node.js no está instalado"
Instala Node.js 18+ desde: https://nodejs.org/

### Error: "El puerto 8000 está en uso"
Cierra cualquier otra aplicación que esté usando el puerto 8000, o cambia el puerto en `backend/main.py`.

### Error: "El puerto 5173 está en uso"
Vite automáticamente usará el siguiente puerto disponible (5174, 5175, etc.)

---

## 📝 Notas

- **Mantén ambas ventanas abiertas** mientras uses la aplicación
- Para detener los servidores: presiona `Ctrl+C` en cada ventana
- Si modificas el código del backend, necesitas reiniciar el servidor backend
- Vite (frontend) se recarga automáticamente cuando modificas el código

---

## ✨ Cambios recientes aplicados

✅ **Arreglado**: Error de Leaflet (`L is not defined`)
- Agregado script de Leaflet JS en `index.html`

✅ **Arreglado**: API de TEMPO usando URL incorrecta
- Actualizado `TempoHeatmap.jsx` para usar el cliente API correcto

⚠️ **Pendiente**: Iniciar el backend
- Ejecuta `START_BACKEND.bat` o `START.bat`

