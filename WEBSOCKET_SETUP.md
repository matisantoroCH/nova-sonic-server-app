# WebSocket Server Setup para Nova Sonic

Este documento explica cómo configurar y ejecutar el WebSocket server que conecta el frontend con Nova Sonic.

## 🏗️ Arquitectura

```
Frontend (React) ←→ WebSocket Server ←→ Nova Sonic (Python)
```

- **Frontend**: Envía audio chunks en tiempo real
- **WebSocket Server**: Bridge entre frontend y Nova Sonic
- **Nova Sonic**: Procesa audio y devuelve transcripción + audio response

## 📋 Prerrequisitos

1. **Python 3.8+** instalado
2. **Dependencias de Nova Sonic** instaladas
3. **Credenciales AWS** configuradas

## 🚀 Instalación

### 1. Instalar dependencias del WebSocket

```bash
cd nova-sonic-server-app
python install-websocket-deps.py
```

O manualmente:

```bash
cd nova-sonic-server-app/nova_sonic
pip install websockets>=12.0
```

### 2. Verificar dependencias

```bash
pip list | grep websockets
```

## 🎯 Ejecución

### 1. Iniciar WebSocket Server

```bash
cd nova-sonic-server-app
python websocket_server.py
```

Deberías ver:
```
🚀 Iniciando WebSocket server en ws://localhost:8080
✅ WebSocket server iniciado en ws://localhost:8080
```

### 2. Iniciar Frontend

En otra terminal:

```bash
cd nova-sonic-web-app
npm run dev
```

## 🔧 Configuración

### WebSocket URL

El frontend está configurado para conectarse a `ws://localhost:8080`. Si necesitas cambiar esto:

1. **Frontend**: Editar `nova-sonic-web-app/src/lib/api-config.ts`
2. **Backend**: Editar `nova-sonic-server-app/websocket_server.py`

### Puerto

Por defecto usa el puerto 8080. Para cambiar:

```python
# En websocket_server.py
server = NovaSonicWebSocketServer(host='localhost', port=9000)
```

## 📡 Protocolo de Comunicación

### Mensajes del Frontend al Server

#### 1. Iniciar Sesión
```json
{
  "type": "chat",
  "payload": {
    "type": "start_session",
    "timestamp": "2024-01-01T00:00:00.000Z"
  }
}
```

#### 2. Audio Chunk
```json
{
  "type": "audio_chunk",
  "payload": {
    "audioData": "base64_encoded_audio_data",
    "timestamp": "2024-01-01T00:00:00.000Z"
  }
}
```

### Mensajes del Server al Frontend

#### 1. Sesión Iniciada
```json
{
  "type": "session_started",
  "payload": {
    "sessionId": "client_123",
    "message": "Sesión de Nova Sonic iniciada"
  }
}
```

#### 2. Transcripción
```json
{
  "type": "transcription",
  "payload": {
    "text": "Hola, ¿cómo estás?",
    "role": "user",
    "timestamp": 1704067200.0
  }
}
```

#### 3. Audio Response
```json
{
  "type": "audio_response",
  "payload": {
    "audioData": "base64_encoded_audio_data",
    "timestamp": 1704067200.0
  }
}
```

## 🐛 Troubleshooting

### Error: "WebSocket no está conectado"

1. Verificar que el server esté ejecutándose
2. Verificar la URL en `api-config.ts`
3. Verificar que no haya firewall bloqueando el puerto

### Error: "ModuleNotFoundError: No module named 'websockets'"

```bash
pip install websockets>=12.0
```

### Error: "AWS credentials not found"

1. Configurar credenciales AWS
2. Verificar variables de entorno
3. Verificar AWS CLI config

### Audio no se reproduce

1. Verificar permisos de micrófono en el navegador
2. Verificar que el AudioContext esté disponible
3. Verificar formato de audio (16-bit PCM, 16kHz, mono)

## 🔍 Debugging

### Logs del Server

El server muestra logs detallados:
- `🔗 Cliente conectado`
- `📨 Mensaje recibido`
- `✅ Sesión iniciada`
- `🔌 Cliente desconectado`

### Logs del Frontend

En la consola del navegador:
- `🟢 WebSocket conectado`
- `📨 Mensaje recibido de Nova Sonic`
- `🔊 Audio response played`

## 📝 Notas Técnicas

### Formato de Audio

- **Input**: 16-bit PCM, 16kHz, mono
- **Output**: 16-bit PCM, 24kHz, mono
- **Chunk Size**: 1024 bytes

### Estado de la Conversación

El server mantiene:
- Historial de mensajes
- Estado de la sesión
- Tareas de audio activas

### Limpieza de Recursos

El server limpia automáticamente:
- Conexiones WebSocket cerradas
- Sesiones de Nova Sonic
- Tareas de audio canceladas 