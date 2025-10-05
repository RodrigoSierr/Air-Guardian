# 🔧 Solución al Error 404 - Notificaciones

## Problema Identificado

El error `404 (Not Found)` en `/api/send-notification` indica que:
- ✅ El frontend está funcionando
- ❌ El backend no está ejecutándose en el puerto 8000

## Solución Paso a Paso

### 1. **Iniciar el Backend**

**Opción A: Usar el script automático**
```bash
# Doble clic en:
START_BACKEND_NOTIFICATIONS.bat
```

**Opción B: Manualmente**
```bash
# Abre una terminal nueva
cd backend
python main.py
```

### 2. **Verificar que Funciona**

**Opción A: Usar el script de prueba**
```bash
# Doble clic en:
TEST_NOTIFICATIONS.bat
```

**Opción B: Verificar manualmente**
1. Abre http://localhost:8000 en tu navegador
2. Deberías ver: `{"message":"AirGuardian API","version":"1.0.0"}`

### 3. **Iniciar el Frontend**

En otra terminal:
```bash
cd frontend
npm run dev
```

### 4. **Probar las Notificaciones**

1. Abre http://localhost:5173
2. Haz clic en "Notificaciones" (botón azul en la parte superior)
3. Permite acceso a ubicación
4. Llena el formulario
5. Envía la notificación

## Estado Esperado

### ✅ Backend Funcionando
```
INFO:     Started server process [26588]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### ✅ Frontend Funcionando
- Modal se abre correctamente
- Formulario valida datos
- Envío muestra "Notificación enviada exitosamente"

### ✅ Logs del Backend
Cuando envíes una notificación, verás:
```
📧 Recibida solicitud de notificación:
   - Nombre: [Tu nombre]
   - Email: [Tu email]
   - Teléfono: [Tu teléfono]
   - Ciudad: [Tu ciudad]
   - Ubicación: [Tu ubicación]
✅ Notificación enviada exitosamente
```

## Archivos de Ayuda

- `START_BACKEND_NOTIFICATIONS.bat` - Inicia el backend automáticamente
- `TEST_NOTIFICATIONS.bat` - Prueba todo el sistema
- `GMAIL_SETUP.md` - Configuración de Gmail (opcional)

## Resumen

**El problema es que necesitas tener DOS terminales abiertas:**

1. **Terminal 1**: Backend (puerto 8000)
2. **Terminal 2**: Frontend (puerto 5173)

Una vez que ambos estén funcionando, las notificaciones funcionarán perfectamente.
