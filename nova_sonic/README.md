# Nova Sonic - Asistente Virtual

Integración de Nova Sonic con el backend para gestión de pedidos y citas médicas mediante comandos de voz.

## 🎯 Funcionalidades

### 📦 Gestión de Pedidos
- **Consultar pedido**: Obtener estado y detalles de un pedido por ID
- **Cancelar pedido**: Cancelar un pedido existente
- **Crear pedido**: Crear un nuevo pedido con items y datos del cliente

### 🏥 Gestión de Citas Médicas
- **Agendar cita**: Programar una nueva cita médica
- **Cancelar cita**: Cancelar una cita existente
- **Modificar cita**: Cambiar fecha u hora de una cita
- **Consultar cita**: Obtener detalles de una cita

## 🚀 Instalación

### 1. Instalar dependencias
```bash
cd nova_sonic
pip install -r requirements.txt
```

### 2. Configurar credenciales AWS (Opciones seguras)

#### Opción A: AWS CLI (Recomendado para desarrollo)
```bash
aws configure
# Ingresa tu Access Key ID, Secret Access Key, región (us-east-1)
```

#### Opción B: Variables de entorno (Solo para desarrollo)
```bash
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Opción C: AWS SSO
```bash
aws configure sso
```

#### Opción D: IAM Role (Para producción en ECS/EC2)
No requiere configuración - se usa automáticamente.

### 3. Configurar variables de entorno (opcional)
```bash
export ORDERS_TABLE="nova-sonic-server-app-demo-orders"
export APPOINTMENTS_TABLE="nova-sonic-server-app-demo-appointments"
```

## 🎤 Uso

### Ejecutar Nova Sonic
```bash
python main.py
```

### Opciones disponibles
```bash
python main.py --debug          # Modo debug
python main.py --voice carlos   # Usar voz específica
python main.py --region us-east-1  # Región AWS específica
```

## 💡 Ejemplos de Comandos de Voz

### Pedidos
- *"Consulta el pedido número 1"*
- *"Cancela el pedido número 2"*
- *"Crea un pedido para María González con un iPhone 15 Pro"*

### Citas Médicas
- *"Agenda una cita para mañana a las 10 con el Dr. Carlos Rodríguez"*
- *"Cancela la cita número 3"*
- *"Modifica la cita número 4 para el viernes a las 15:00"*
- *"Consulta la cita número 5"*

## 🏗️ Arquitectura

### Archivos principales
- **`nova_sonic_client.py`**: Cliente principal de Nova Sonic
- **`tool_processor.py`**: Procesador de herramientas (tools)
- **`main.py`**: Punto de entrada de la aplicación

### Flujo de trabajo
1. **Inicialización**: Conexión con AWS Bedrock y configuración de audio
2. **Reconocimiento**: Captura de audio del usuario
3. **Procesamiento**: Análisis del comando de voz
4. **Ejecución**: Llamada a la herramienta correspondiente
5. **Respuesta**: Respuesta de voz con el resultado

## 🔧 Herramientas (Tools) Implementadas

### consultarOrder
```json
{
  "orderId": "string"
}
```

### cancelarOrder
```json
{
  "orderId": "string"
}
```

### crearOrder
```json
{
  "customerName": "string",
  "customerEmail": "string",
  "items": [
    {
      "name": "string",
      "quantity": "integer",
      "price": "number",
      "description": "string"
    }
  ]
}
```

### agendarTurno
```json
{
  "patientName": "string",
  "patientEmail": "string",
  "doctorName": "string",
  "date": "string (ISO format)",
  "duration": "integer",
  "type": "string",
  "notes": "string"
}
```

### cancelarTurno
```json
{
  "appointmentId": "string"
}
```

### modificarTurno
```json
{
  "appointmentId": "string",
  "newDate": "string (optional)",
  "newTime": "string (optional)"
}
```

### consultarTurno
```json
{
  "appointmentId": "string"
}
```

## 🐛 Troubleshooting

### Error de credenciales AWS
```
❌ Error: No se encontraron credenciales AWS válidas
```
**Solución**: Configurar credenciales usando uno de estos métodos:
1. **AWS CLI**: `aws configure`
2. **Variables de entorno**: `export AWS_ACCESS_KEY_ID=...`
3. **AWS SSO**: `aws configure sso`
4. **IAM Role**: Para producción en ECS/EC2

### Error de audio
```
❌ Error: No se puede acceder al micrófono
```
**Solución**: Verificar permisos de micrófono y que no esté siendo usado por otra aplicación

### Error de conexión con DynamoDB
```
❌ Error: Error consultando la base de datos
```
**Solución**: Verificar que las tablas existen y las credenciales tienen permisos

## 🔄 Integración con el Backend

Nova Sonic se integra con:
- **DynamoDB**: Tablas de pedidos y citas
- **AWS Bedrock**: Modelo Nova Sonic para procesamiento de voz
- **API Gateway**: Para futura integración con WebSocket

## 📝 Notas de Desarrollo

- **Voz por defecto**: Carlos (español argentino)
- **Región por defecto**: us-east-1
- **Formato de audio**: LPCM, 16kHz entrada, 24kHz salida
- **Codificación**: Base64 para transmisión

## 🚧 Próximos Pasos

1. **WebSocket Integration**: Conectar con el frontend
2. **ECS Deployment**: Desplegar en contenedores
3. **Multi-idioma**: Soporte para otros idiomas
4. **Analytics**: Métricas de uso y performance 