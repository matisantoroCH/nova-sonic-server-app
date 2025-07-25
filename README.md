# Nova Sonic Server App - Backend

Backend completo para Nova Sonic con AWS Lambda functions, DynamoDB, API Gateway, y servidor WebSocket para comunicación en tiempo real con Nova Sonic S2S voice assistant.

## 🚀 Características Principales

### Backend Serverless (Lambda + DynamoDB)
- **Unified API Handler**: Una sola Lambda con routing interno para todos los endpoints
- **Orders Management**: CRUD completo de pedidos desde DynamoDB
- **Appointments Management**: CRUD completo de citas desde DynamoDB
- **API Gateway Integration**: Endpoints REST para el frontend
- **CORS Support**: Configurado para comunicación con el frontend
- **Error Handling**: Manejo robusto de errores y logging

### Nova Sonic S2S Voice Assistant
- **Voice Interaction**: Asistente de voz para gestión de pedidos y citas
- **Tool Integration**: 7 herramientas para operaciones CRUD
- **Real-time Audio**: Streaming bidireccional con AWS Bedrock Nova Sonic
- **WebSocket Server**: Servidor WebSocket para comunicación con frontend
- **Local Development**: Ejecución local para desarrollo y testing
- **Session Management**: Gestión de sesiones de voz persistentes
- **Local Deployment**: Servidor ejecutándose localmente (no en ECS)

### Infrastructure as Code
- **Terraform**: Gestión de infraestructura (en revisión)
- **Modular Design**: Configuración organizada en archivos separados
- **Environment Variables**: Configuración flexible por stage
- **S3 Backend**: Almacenamiento seguro del estado de Terraform

## 🛠️ Tecnologías Utilizadas

### AWS Services
- **AWS Lambda** - Serverless functions
- **AWS DynamoDB** - Base de datos NoSQL
- **API Gateway** - REST API endpoints
- **S3** - Almacenamiento de Terraform state con locking
- **AWS Bedrock Nova Sonic** - Modelo para procesamiento de voz S2S
- **CloudWatch** - Logging y monitoreo

### Development Stack
- **TypeScript** - Tipado estático para Lambda functions
- **Python 3.12+** - Nova Sonic S2S voice assistant
- **Terraform** - Infrastructure as Code
- **AWS SDK v3** - Cliente de DynamoDB
- **WebSockets** - Comunicación en tiempo real
- **Boto3** - SDK de AWS para Python

## 📦 Instalación y Configuración

### Prerequisites
- Node.js 18+ y npm
- Python 3.12+
- AWS CLI configurado con permisos adecuados
- Terraform 5.0
- Acceso a AWS Bedrock Nova Sonic

### Setup Backend Serverless

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

5. **Deploy a AWS (Opcional - en revisión)**
   ```bash
   npm run deploy:demo
   ```

**Nota**: El Terraform está en revisión y el proyecto actualmente se ejecuta localmente.

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
   ```

3. **Configurar variables de entorno**
   ```bash
   export ORDERS_TABLE="nova-sonic-server-app-demo-orders"
   export APPOINTMENTS_TABLE="nova-sonic-server-app-demo-appointments"
   export HOST="localhost"
   export WS_PORT="8081"
   export HEALTH_PORT="80"
   ```

4. **Ejecutar servidor S2S**
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
│   ├── main.tf             # Recursos principales
│   ├── variables.tf        # Variables de Terraform
│   ├── outputs.tf          # Outputs de Terraform
│   ├── backend.tf          # Configuración de backend S3
│   ├── providers.tf        # Configuración de providers
│   └── versions.tf         # Versiones de providers
├── scripts/                 # Scripts de utilidad
│   ├── setup-backend.sh    # Setup de backend S3
│   ├── seed-data.js        # Poblar datos de prueba
│   ├── diagnose-tables.py  # Diagnóstico de tablas
│   └── test-migration.py   # Tests de migración
├── dist/                    # Código compilado
└── package.json            # Dependencias y scripts
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
      "items": [
        {
          "id": "1",
          "name": "Producto A",
          "quantity": 2,
          "price": 25.99,
          "description": "Descripción del producto A"
        }
      ],
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
- **Primary Key**: `PK` (String) - `ORDER#{id}`
- **Sort Key**: `SK` (String) - `ORDER#{id}`
- **GSI1**: CustomerEmailIndex - `customerEmail` (String)
- **GSI2**: StatusIndex - `status` (String) + `createdAt` (String)

**Atributos:**
- `PK`: Partition key (ORDER#{id})
- `SK`: Sort key (ORDER#{id})
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
- **Primary Key**: `PK` (String) - `APPOINTMENT#{id}`
- **Sort Key**: `SK` (String) - `APPOINTMENT#{id}`
- **GSI1**: PatientEmailIndex - `patientEmail` (String)
- **GSI2**: DoctorDateIndex - `doctorName` (String) + `appointmentDate` (String)
- **GSI3**: StatusIndex - `status` (String)

**Atributos:**
- `PK`: Partition key (APPOINTMENT#{id})
- `SK`: Sort key (APPOINTMENT#{id})
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

### ¿Qué es Nova Sonic?

Nova Sonic es el modelo de AWS Bedrock para procesamiento de voz Speech-to-Speech (S2S). Permite conversaciones de voz naturales en tiempo real con capacidades de:

- **Transcripción automática**: Convierte audio a texto
- **Procesamiento de lenguaje natural**: Entiende el contexto y la intención
- **Generación de respuestas**: Crea respuestas contextuales
- **Síntesis de voz**: Convierte texto a audio natural
- **Tool Calling**: Ejecuta funciones específicas basadas en la conversación

### Configuración del Servidor

**Variables de Entorno:**
```bash
HOST=localhost                    # Host del servidor
WS_PORT=8081                      # Puerto WebSocket
HEALTH_PORT=80                    # Puerto health check
AWS_DEFAULT_REGION=us-east-1      # Región AWS
ORDERS_TABLE=nova-sonic-orders    # Tabla de pedidos
APPOINTMENTS_TABLE=nova-sonic-appointments # Tabla de citas
LOGLEVEL=INFO                     # Nivel de logging
```

**Ejecución:**
```bash
# Ejecución básica
python server.py

# Con debug habilitado
python server.py --debug

# Con puertos personalizados
HOST=0.0.0.0 WS_PORT=8080 HEALTH_PORT=8080 python server.py
```

### Tipos de Eventos S2S

#### 1. Eventos de Sesión
- **sessionStart**: Inicio de sesión con Nova Sonic
- **sessionEnd**: Fin de sesión

#### 2. Eventos de Prompt
- **promptStart**: Inicio de un prompt (conversación)
- **promptEnd**: Fin de un prompt

#### 3. Eventos de Contenido
- **contentStart**: Inicio de contenido (texto/audio)
- **contentEnd**: Fin de contenido

#### 4. Eventos de Audio
- **audioInput**: Entrada de audio del usuario
- **audioOutput**: Salida de audio de Nova Sonic

#### 5. Eventos de Texto
- **textInput**: Entrada de texto del usuario
- **textOutput**: Salida de texto de Nova Sonic

#### 6. Eventos de Tools
- **toolUse**: Uso de una herramienta
- **toolResult**: Resultado de la herramienta

### Herramientas Disponibles

#### 📦 Gestión de Pedidos

**consultarOrder**
- **Descripción**: Consultar pedido por ID con verificación de identidad
- **Parámetros**: `orderId`, `dni` o `customerName`
- **Ejemplo**: "Consulta el pedido número 1 con DNI 12345678"

**cancelarOrder**
- **Descripción**: Cancelar pedido existente con verificación de identidad
- **Parámetros**: `orderId`, `dni` o `customerName`
- **Ejemplo**: "Cancela el pedido número 2 para Juan Pérez"

**crearOrder**
- **Descripción**: Crear nuevo pedido con items y datos del cliente
- **Parámetros**: `customerName`, `customerEmail`, `items`, `total`
- **Ejemplo**: "Crea un pedido para María García con 2 productos"

#### 🏥 Gestión de Citas

**agendarTurno**
- **Descripción**: Programar nueva cita médica
- **Parámetros**: `patientName`, `patientEmail`, `doctorName`, `date`, `duration`, `type`
- **Ejemplo**: "Agenda una cita para mañana a las 10 con el Dr. Rodríguez"

**cancelarTurno**
- **Descripción**: Cancelar cita existente
- **Parámetros**: `appointmentId`, `patientName`
- **Ejemplo**: "Cancela la cita número 3 para Ana Martínez"

**modificarTurno**
- **Descripción**: Cambiar fecha/hora de cita
- **Parámetros**: `appointmentId`, `patientName`, `newDate`
- **Ejemplo**: "Modifica la cita número 1 para el viernes a las 15:00"

**consultarTurno**
- **Descripción**: Obtener detalles de cita
- **Parámetros**: `appointmentId`, `patientName`
- **Ejemplo**: "Consulta la cita número 2 para Luis Fernández"

### System Prompt

El asistente usa el siguiente system prompt optimizado:

```
"Eres Carlos, el asistente virtual de Nova Sonic. 
Eres amable, profesional y hablas en español argentino de forma natural y conversacional. 
Tu función es ayudar a los usuarios con pedidos y citas médicas. 

REGLAS CRÍTICAS PARA TUS RESPUESTAS: 
- Responde de forma NATURAL y CONVERSACIONAL, como si estuvieras hablando con un amigo. 
- NO hagas listas ni bullet points. Habla de forma fluida y natural. 
- Responde SOLO a lo que te preguntan, no des información extra que no pidieron. 
- Si preguntan por el ESTADO de un pedido, solo di el estado y fecha estimada de entrega. 
- Si preguntan por DETALLES de un pedido, entonces sí menciona los productos. 
- Si preguntan por el ESTADO de una cita, solo di la fecha, hora y estado. 
- Si preguntan por DETALLES de una cita, entonces sí menciona el doctor y tipo. 
- Sé CONCISO: máximo 2-3 frases naturales. 
- NO uses frases especulativas como 'podría', 'tal vez', 'quizás'. 
- Si necesitas más información, pídela de forma breve y natural. 
- Cuando uses herramientas, SIEMPRE envía los números como dígitos (ej: '6' no 'seis'). 
- Para pedidos, pide DNI o nombre completo para verificar identidad. 
- Para citas, pide nombre del paciente para verificar identidad. 
- Al final de cada respuesta, incluye [FINAL]."
```

### Ejemplos de Comandos de Voz
- *"Consulta el pedido número 1 con DNI 12345678"*
- *"Cancela el pedido número 2 para Juan Pérez"*
- *"Agenda una cita para mañana a las 10 con el Dr. Rodríguez"*
- *"Modifica la cita número 3 para el viernes a las 15:00"*

### Flujo de Integración

1. **Usuario habla** → Frontend envía audio chunks
2. **WebSocket Server** → Recibe audio y lo reenvía a Nova Sonic
3. **Bedrock procesa** → Detecta necesidad de tool
4. **S2sSessionManager** → Recibe evento `toolUse`
5. **Tool Processor** → Ejecuta función en DynamoDB
6. **Respuesta** → Vuelve a Bedrock → Frontend

## 🔌 WebSocket Server

### Arquitectura WebSocket

```
Frontend (React) ←→ WebSocket Server ←→ Nova Sonic (Python)
```

- **Frontend**: Envía audio chunks en tiempo real
- **WebSocket Server**: Bridge entre frontend y Nova Sonic
- **Nova Sonic**: Procesa audio y devuelve transcripción + audio response

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

### Configuración WebSocket

**Variables de Entorno:**
```bash
HOST=localhost          # Host del servidor WebSocket
WS_PORT=8081           # Puerto WebSocket
HEALTH_PORT=80         # Puerto health check
```

## 🔧 Scripts de Python y Bash

### Scripts de Python

**diagnose-tables.py**
```bash
python scripts/diagnose-tables.py
```
- Diagnostica el estado de las tablas DynamoDB
- Verifica conectividad y permisos
- Muestra estadísticas de datos

**test-migration.py**
```bash
python scripts/test-migration.py
```
- Prueba migraciones de datos
- Verifica integridad de datos
- Genera reportes de migración

### Scripts de Bash

**setup-backend.sh**
```bash
./scripts/setup-backend.sh
```
- Configura backend S3 para Terraform
- Crea bucket y configuración de locking
- Inicializa Terraform backend

**run-migration.sh**
```bash
./scripts/run-migration.sh
```
- Ejecuta migraciones de datos
- Backup automático antes de migrar
- Rollback en caso de error

**seed-data.js**
```bash
node scripts/seed-data.js
```
- Pobla tablas con datos de prueba
- Crea pedidos y citas de ejemplo
- Configura índices y datos iniciales

## 🔧 Configuración de Terraform

**⚠️ IMPORTANTE**: El Terraform está en revisión y necesita ser actualizado antes del despliegue en producción.

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

# DynamoDB Configuration
dynamodb_billing_mode = "PAY_PER_REQUEST"

# API Gateway Configuration
api_gateway_stage_name = "demo"
```

### Recursos Creados

**Lambda Functions:**
- `nova-sonic-server-app-demo-api`: Handler principal para API Gateway

**DynamoDB Tables:**
- `nova-sonic-server-app-demo-orders`: Tabla de pedidos
- `nova-sonic-server-app-demo-appointments`: Tabla de citas

**API Gateway:**
- REST API con endpoints para orders y appointments
- CORS configurado para frontend
- Métodos GET para consultas

**IAM Roles:**
- Lambda execution role con permisos mínimos
- DynamoDB access policies
- CloudWatch logging permissions

### Estado Actual del Terraform

- **Estado**: En revisión y desarrollo
- **Despliegue**: No desplegado en producción
- **Ejecución**: Proyecto ejecutándose localmente
- **Próximos pasos**: Revisar y actualizar configuración antes del despliegue

### Deployment Commands

```bash
# Plan deployment (en revisión)
npm run plan:demo

# Deploy to demo environment (en revisión)
npm run deploy:demo

# Destroy infrastructure
npm run destroy

# Seed data after deployment
npm run seed
```

**Nota**: Los comandos de deployment están en revisión. El proyecto actualmente se ejecuta localmente.

## 📊 Monitoreo y Logging

### CloudWatch Logs

Cada Lambda function genera logs en CloudWatch que incluyen:
- Eventos de entrada
- Errores y excepciones
- Métricas de rendimiento
- Tiempo de ejecución

**Log Groups:**
- `/aws/lambda/nova-sonic-server-app-demo-api`

### Métricas de DynamoDB

- Consumed Read/Write Capacity Units
- Throttled Requests
- User Errors
- System Errors

### Health Checks

El servidor WebSocket expone un endpoint de health check en el puerto configurado (por defecto 80).

## 🔒 Seguridad

### IAM Roles

Las Lambda functions tienen permisos mínimos necesarios:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/nova-sonic-*",
        "arn:aws:dynamodb:*:*:table/nova-sonic-*/index/*"
      ]
    }
  ]
}
```

### CORS

Configurado para permitir requests desde el frontend:
```json
{
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
  "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}
```

### Variables de Entorno

**Requeridas:**
```bash
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
ORDERS_TABLE=nova-sonic-server-app-demo-orders
APPOINTMENTS_TABLE=nova-sonic-server-app-demo-appointments
```

## 🚀 Workflow de Desarrollo Local

### 1. Desarrollo Local
```bash
npm install
npm run build
```

### 2. Configurar Variables de Entorno
```bash
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"
export ORDERS_TABLE="nova-sonic-server-app-demo-orders"
export APPOINTMENTS_TABLE="nova-sonic-server-app-demo-appointments"
```

### 3. Iniciar Nova Sonic Localmente
```bash
cd nova_sonic
python server.py --debug
```

### 4. Verificar Conexión
```bash
curl http://localhost:80/health
```

## 🚀 Workflow de Deployment (En Revisión)

### 1. Plan de Infraestructura
```bash
npm run plan:demo
```

### 2. Deploy
```bash
npm run deploy:demo
```

### 3. Poblar Datos
```bash
npm run seed
```

### 4. Obtener URLs
```bash
terraform -chdir=terraform output api_gateway_url
```

**Nota**: El deployment está en revisión. Actualmente el proyecto se ejecuta localmente.

## 🚧 Estado Actual del Proyecto

### ✅ Completado

1. **Infraestructura AWS (En Revisión)**
   - Lambda functions con TypeScript
   - DynamoDB tables con índices
   - API Gateway con CORS
   - Terraform IaC (necesita revisión)

2. **Nova Sonic S2S (Local)**
   - Servidor WebSocket funcional ejecutándose localmente
   - Integración con AWS Bedrock
   - 7 herramientas implementadas
   - System prompt optimizado

3. **Backend API (Local)**
   - Endpoints REST para orders y appointments
   - Manejo de errores robusto
   - Logging en CloudWatch
   - CORS configurado

4. **Scripts de Utilidad**
   - Setup de backend S3
   - Seed data para pruebas
   - Diagnóstico de tablas
   - Tests de migración

### 🚧 En Desarrollo

1. **Integración Frontend-Backend**
   - WebSocket connection estable
   - Audio streaming funcional
   - Tool execution working

2. **Infraestructura AWS**
   - Revisión y actualización de Terraform
   - Preparación para deployment en ECS
   - Optimización de configuración

### 🚨 Último Obstáculo

**Problema**: Integración completa entre frontend y backend Nova Sonic

**Detalles**:
- El WebSocket server está funcionando correctamente
- Nova Sonic S2S está procesando audio y ejecutando tools
- El frontend puede conectarse al WebSocket
- **Obstáculo**: La comunicación bidireccional de audio entre frontend y Nova Sonic no está completamente sincronizada

**Síntomas**:
- Audio chunks se envían correctamente desde frontend
- Nova Sonic procesa y responde
- La reproducción de audio de respuesta en frontend tiene latencia
- Ocasionalmente se pierden chunks de audio

**Causa Raíz**:
- Timing entre envío de audio chunks y procesamiento
- Buffer de audio no optimizado para streaming en tiempo real
- Latencia en la red entre frontend y servidor WebSocket

**Solución en Progreso**:
- Optimización del buffer de audio en frontend
- Implementación de acknowledgment system
- Mejora en el manejo de chunks de audio
- Reducción de latencia en WebSocket server

### 📋 Próximos Pasos

1. **Revisar y Actualizar Terraform**
   - Revisar configuración actual
   - Actualizar para deployment en ECS
   - Optimizar configuración de recursos
   - Preparar para producción

2. **Optimizar Audio Streaming**
   - Implementar buffer circular optimizado
   - Reducir latencia de audio chunks
   - Mejorar sincronización audio/texto

3. **Testing Completo**
   - Tests unitarios para Lambda functions
   - Tests de integración WebSocket
   - Tests de carga para audio streaming

4. **Monitoreo Avanzado**
   - CloudWatch dashboards
   - Métricas de latencia de audio
   - Alertas automáticas

5. **Documentación**
   - API documentation completa
   - Troubleshooting guide
   - Performance optimization guide



**Nova Sonic Server App** - Backend completo para aplicaciones de voz 🚀 