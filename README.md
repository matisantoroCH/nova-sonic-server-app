# Nova Sonic Server App

Backend server for Nova Sonic with AWS Lambda functions, DynamoDB integration, and Nova Sonic S2S voice assistant, deployed using Terraform.

## 🚀 Características

### Backend (Lambda + DynamoDB)
- **Unified API Handler**: Una sola Lambda con routing interno para todos los endpoints
- **Orders Management**: CRUD completo de pedidos desde DynamoDB
- **Appointments Management**: CRUD completo de citas desde DynamoDB
- **API Gateway Integration**: Endpoints REST para el frontend
- **CORS Support**: Configurado para comunicación con el frontend

### Nova Sonic S2S Voice Assistant
- **Voice Interaction**: Asistente de voz para gestión de pedidos y citas
- **Tool Integration**: 7 herramientas para operaciones CRUD
- **Real-time Audio**: Streaming bidireccional con AWS Bedrock Nova Sonic
- **WebSocket Server**: Servidor WebSocket para comunicación con frontend
- **Local Development**: Ejecución local para desarrollo y testing

### Infrastructure as Code
- **Terraform**: Gestión completa de infraestructura
- **Modular Design**: Configuración organizada en archivos separados
- **Environment Variables**: Configuración flexible por stage

## 🛠️ Tecnologías Utilizadas

- **AWS Lambda** - Serverless functions
- **AWS DynamoDB** - Base de datos NoSQL
- **API Gateway** - REST API endpoints
- **S3** - Almacenamiento de Terraform state con locking
- **Terraform** - Infrastructure as Code
- **TypeScript** - Tipado estático
- **AWS SDK v3** - Cliente de DynamoDB
- **AWS Bedrock Nova Sonic** - Modelo para procesamiento de voz S2S
- **Python** - Nova Sonic S2S voice assistant
- **WebSockets** - Comunicación en tiempo real

## 📦 Instalación

### Prerequisites
- Node.js 14+ y npm
- Python 3.12+
- AWS CLI configurado
- Terraform instalado
- Acceso a AWS Bedrock Nova Sonic

### Setup Backend

1. **Instalar dependencias**
   ```bash
   npm install
   ```

2. **Compilar TypeScript**
   ```bash
   npm run build
   ```

3. **Configurar AWS credentials**
   ```bash
   aws configure
   ```

4. **Configurar Backend de Terraform (S3)**
   ```bash
   npm run setup-backend
   ```

5. **Deploy a AWS**
   ```bash
   npm run deploy:demo
   ```

### Setup Nova Sonic S2S

1. **Instalar dependencias Python**
   ```bash
   cd nova_sonic
   pip install -r requirements.txt
   ```

2. **Configurar credenciales AWS**
   ```bash
   export AWS_ACCESS_KEY_ID="tu_access_key"
   export AWS_SECRET_ACCESS_KEY="tu_secret_key"
   export AWS_DEFAULT_REGION="us-east-1"
   ```

3. **Ejecutar servidor S2S**
   ```bash
   python server.py --debug
   ```

## 🏗️ Estructura del Proyecto

```
nova-sonic-server-app/
├── src/                     # Lambda functions (TypeScript)
│   ├── handlers/
│   │   ├── api.ts           # Handler principal con routing
│   │   ├── orders.ts        # Funciones para pedidos
│   │   └── appointments.ts  # Funciones para citas
│   ├── utils/
│   │   └── dynamodb.ts      # Utilidades de DynamoDB
│   └── types/
│       └── index.ts         # Interfaces TypeScript
├── nova_sonic/              # Nova Sonic S2S Voice Assistant
│   ├── server.py            # Servidor WebSocket S2S
│   ├── s2s_events.py        # Eventos S2S con system prompt
│   ├── s2s_session_manager.py # Gestión de sesiones S2S
│   ├── tool_processor.py    # Procesador de herramientas
│   ├── requirements.txt     # Dependencias Python
│   └── __init__.py         # Inicialización del módulo
├── terraform/               # Infraestructura
├── scripts/                 # Scripts de utilidad
└── dist/                    # Código compilado
```

## 📋 Endpoints API (Backend)

### Orders Endpoints

#### GET /orders
Obtiene todos los pedidos.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "1",
      "customerName": "Juan Pérez",
      "customerEmail": "juan.perez@email.com",
      "items": [...],
      "total": 67.48,
      "status": "pending",
      "createdAt": "2024-01-15T00:00:00.000Z",
      "updatedAt": "2024-01-15T00:00:00.000Z",
      "estimatedDelivery": "2024-01-20T00:00:00.000Z",
      "trackingNumber": "TRK123456789"
    }
  ],
  "message": "Retrieved 5 orders successfully"
}
```

#### GET /orders/{id}
Obtiene un pedido específico por ID.

### Appointments Endpoints

#### GET /appointments
Obtiene todas las citas o filtra por fecha.

**Query Parameters:**
- `date` (opcional): Fecha en formato YYYY-MM-DD

#### GET /appointments/{id}
Obtiene una cita específica por ID.

## 🗄️ Estructura de DynamoDB

### Orders Table
- **Primary Key**: `id` (String)
- **GSI1**: CustomerEmailIndex - `customerEmail` (String)
- **GSI2**: StatusIndex - `status` (String) + `createdAt` (String)

**Atributos:**
- `id`: ID único del pedido
- `customerName`: Nombre del cliente
- `customerEmail`: Email del cliente
- `items`: Array de productos
- `total`: Total del pedido
- `status`: Estado (pending, processing, shipped, delivered, cancelled)
- `createdAt`: Fecha de creación (ISO string)
- `updatedAt`: Fecha de actualización (ISO string)
- `estimatedDelivery`: Fecha estimada de entrega (ISO string)
- `trackingNumber`: Número de seguimiento

### Appointments Table
- **Primary Key**: `id` (String)
- **GSI1**: PatientEmailIndex - `patientEmail` (String)
- **GSI2**: DoctorDateIndex - `doctorName` (String) + `appointmentDate` (String)
- **GSI3**: StatusIndex - `status` (String)

**Atributos:**
- `id`: ID único de la cita
- `patientName`: Nombre del paciente
- `patientEmail`: Email del paciente
- `doctorName`: Nombre del doctor
- `date`: Fecha y hora de la cita (ISO string)
- `duration`: Duración en minutos
- `type`: Tipo de cita (consultation, follow-up, emergency, routine)
- `notes`: Notas adicionales
- `status`: Estado (scheduled, confirmed, cancelled, completed)

## 🎤 Nova Sonic S2S Voice Assistant

### Configuración del Servidor

**Variables de Entorno:**
- `HOST`: Host del servidor (default: localhost)
- `WS_PORT`: Puerto WebSocket (default: 8081)
- `HEALTH_PORT`: Puerto health check (default: 80)
- `AWS_DEFAULT_REGION`: Región AWS (default: us-east-1)

**Ejecución:**
```bash
# Ejecución básica
python server.py

# Con debug habilitado
python server.py --debug

# Con puertos personalizados
HOST=0.0.0.0 WS_PORT=8080 HEALTH_PORT=8080 python server.py
```

### Herramientas Disponibles

#### 📦 Gestión de Pedidos
- **consultarOrder**: Consultar pedido por ID
- **cancelarOrder**: Cancelar pedido existente
- **crearOrder**: Crear nuevo pedido

#### 🏥 Gestión de Citas
- **agendarTurno**: Programar nueva cita
- **cancelarTurno**: Cancelar cita existente
- **modificarTurno**: Cambiar fecha/hora de cita
- **consultarTurno**: Obtener detalles de cita

### System Prompt

El asistente usa el siguiente system prompt:

```
"Eres Carlos, el asistente virtual de Nova Sonic. 
Eres amable, profesional y hablas en español argentino. 
Tu función es ayudar a los usuarios con: 
- Consultar, cancelar y crear pedidos 
- Agendar, cancelar, modificar y consultar citas médicas 
Siempre responde de forma clara y natural. 
Si necesitas más información, pídela amablemente. 
IMPORTANTE: Cuando uses herramientas (tools), SIEMPRE envía los números como dígitos, no como palabras. 
Por ejemplo: usa '6' en lugar de 'seis', '627' en lugar de 'seiscientos veintisiete', '10065' en lugar de 'diez mil sesenta y cinco'. 
Esto es crucial para que las herramientas funcionen correctamente."
```

### Ejemplos de Comandos de Voz
- *"Consulta el pedido número 1"*
- *"Cancela el pedido número 2"*
- *"Agenda una cita para mañana a las 10"*
- *"Modifica la cita número 3 para el viernes"*

### Flujo de Integración

1. **Usuario habla** → Frontend envía audio
2. **Bedrock procesa** → Detecta necesidad de tool
3. **S2sSessionManager** → Recibe evento `toolUse`
4. **Tool Processor** → Ejecuta función en DynamoDB
5. **Respuesta** → Vuelve a Bedrock → Frontend

### Protocolo WebSocket

El servidor S2S maneja eventos WebSocket para:

- **Inicialización de sesión**: Configuración inicial con Bedrock
- **Streaming de audio bidireccional**: Audio en tiempo real
- **Ejecución de herramientas**: Procesamiento de tools
- **Respuestas de texto y audio**: Respuestas del asistente

**Eventos Principales:**
- `sessionStart`: Inicio de sesión
- `promptStart`: Inicio de prompt
- `contentStart`: Inicio de contenido (texto/audio)
- `audioInput`: Entrada de audio
- `toolUse`: Uso de herramienta
- `textOutput`: Salida de texto
- `audioOutput`: Salida de audio
- `contentEnd`: Fin de contenido
- `promptEnd`: Fin de prompt
- `sessionEnd`: Fin de sesión

## 🔧 Configuración

### Variables de Terraform
Las variables se configuran en `terraform/terraform.tfvars`:

```hcl
# AWS Configuration
aws_region = "us-east-1"

# Deployment Configuration
stage = "demo"
project_name = "nova-sonic-server-app"

# Lambda Configuration
lambda_timeout = 30
lambda_memory_size = 128
```

### Deployment Commands
```bash
# Plan deployment
npm run plan:demo

# Deploy to demo environment
npm run deploy:demo

# Destroy infrastructure
npm run destroy

# Seed data after deployment
npm run seed
```

## 📊 Monitoreo

### CloudWatch Logs
Cada Lambda function genera logs en CloudWatch que incluyen:
- Eventos de entrada
- Errores y excepciones
- Métricas de rendimiento

### Métricas de DynamoDB
- Consumed Read/Write Capacity Units
- Throttled Requests
- User Errors

## 🔒 Seguridad

### IAM Roles
Las Lambda functions tienen permisos mínimos necesarios:
- `dynamodb:Query`
- `dynamodb:Scan`
- `dynamodb:GetItem`
- `dynamodb:PutItem`
- `dynamodb:UpdateItem`
- `dynamodb:DeleteItem`

### CORS
Configurado para permitir requests desde el frontend:
```json
{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
  "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}
```

## 🚀 Workflow de Deployment

1. **Desarrollo Local**
   ```bash
   npm install
   npm run build
   ```

2. **Plan de Infraestructura**
   ```bash
   npm run plan:demo
   ```

3. **Deploy**
   ```bash
   npm run deploy:demo
   ```

4. **Poblar Datos**
   ```bash
   npm run seed
   ```

5. **Obtener URLs**
   ```bash
   terraform -chdir=terraform output api_gateway_url
   ```

## 🚀 Próximos Pasos

1. **Frontend Integration**: Integrar con frontend WebSocket
2. **ECS Deployment**: Desplegar Nova Sonic S2S en contenedores
3. **Authentication**: Agregar autenticación con Cognito
4. **Caching**: Implementar caching con ElastiCache
5. **Monitoring**: Agregar CloudWatch dashboards
6. **Testing**: Implementar tests unitarios y de integración
7. **CI/CD**: Configurar pipeline de deployment automático
8. **Rate Limiting**: Implementar rate limiting en API Gateway
9. **Logging**: Mejorar logging estructurado 