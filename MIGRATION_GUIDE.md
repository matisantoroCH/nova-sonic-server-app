# 🚀 Migración a Arquitectura Workshop - Nova Sonic

## 📋 Resumen de Cambios

Se ha migrado completamente la implementación de Nova Sonic a la arquitectura más robusta del workshop `nova-s2s-workshop`. Los cambios principales incluyen:

### 🔧 Backend (Python)

#### Nuevos Archivos:
- `s2s_session_manager.py` - Gestor de sesiones bidireccionales con Bedrock
- `s2s_events.py` - Definición de eventos S2S estándar
- `websocket_server.py` - Servidor WebSocket mejorado
- `start_server.py` - Script de inicio simplificado

#### Cambios Principales:
1. **Arquitectura de Colas**: Sistema de colas asíncronas para audio input/output
2. **Eventos S2S**: Manejo estándar de eventos (sessionStart, promptStart, audioInput, etc.)
3. **Streaming Bidireccional**: Conexión directa con Bedrock usando `aws_sdk_bedrock_runtime`
4. **Manejo de Herramientas**: Integración mejorada con el procesador de herramientas existente

### 🎨 Frontend (React)

#### Nuevos Archivos:
- `helper/audioHelper.js` - Conversión base64 a Float32Array
- `helper/audioPlayer.js` - Reproductor de audio con AudioWorklets
- `helper/audioPlayerProcessor.worklet.js` - Procesador de audio de alta calidad
- `helper/s2sEvents.js` - Definición de eventos S2S en JavaScript

#### Cambios Principales:
1. **ScriptProcessor**: Reemplaza MediaRecorder para captura de audio más precisa
2. **Resampling**: Conversión automática a 16kHz requerido por Nova Sonic
3. **AudioWorklets**: Reproducción de audio de alta calidad con buffer inteligente
4. **Eventos S2S**: Manejo completo del protocolo de eventos del workshop

## 🎯 Diferencias Clave con Implementación Anterior

### Audio Input:
- **Antes**: MediaRecorder → WebM/Opus → base64
- **Ahora**: ScriptProcessor → Int16 PCM → resampling 16kHz → base64

### Audio Output:
- **Antes**: AudioContext básico
- **Ahora**: AudioWorklets con buffer expandible y manejo de underflow

### Comunicación:
- **Antes**: Protocolo personalizado
- **Ahora**: Protocolo S2S estándar con eventos tipados

### Herramientas:
- **Antes**: Integración básica
- **Ahora**: Manejo completo de toolUse con eventos start/result/end

## 🚀 Instrucciones de Uso

### 1. Instalar Dependencias Backend
```bash
cd nova-sonic-server-app
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

### 3. Iniciar Servidor
```bash
python start_server.py
```

### 4. Iniciar Frontend
```bash
cd nova-sonic-web-app
npm run dev
```

## 🔍 Características Mejoradas

### ✅ Audio de Alta Calidad
- Resampling automático a 16kHz
- Conversión precisa a Int16 PCM
- Buffer inteligente para reproducción

### ✅ Manejo Robusto de Eventos
- Protocolo S2S estándar
- Eventos tipados y validados
- Manejo de errores mejorado

### ✅ Herramientas Integradas
- Soporte completo para getOrders y getAppointments
- Manejo automático de toolUse
- Respuestas estructuradas

### ✅ Experiencia de Usuario
- Transcriptions en tiempo real
- Indicadores de estado visual
- Manejo de conexión robusto

## 🐛 Solución de Problemas

### Error de Credenciales AWS
```bash
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
```

### Error de Puerto WebSocket
```bash
export WS_PORT="8081"
```

### Error de Audio
- Verificar permisos de micrófono
- Asegurar que el navegador soporte AudioWorklets
- Verificar que el audio esté habilitado

## 📚 Referencias

- [Nova S2S Workshop](https://github.com/aws-samples/amazon-nova-samples)
- [AudioWorklets API](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API) 