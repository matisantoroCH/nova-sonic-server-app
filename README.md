# Nova Sonic Server App

Backend server for Nova Sonic with AWS Lambda functions and DynamoDB integration, deployed using Terraform.

## 🚀 Características

### Lambda Function
- **Unified API Handler**: Una sola Lambda con routing interno para todos los endpoints
- **Orders Management**: Consulta de pedidos desde DynamoDB
- **Appointments Management**: Consulta de citas desde DynamoDB
- **API Gateway Integration**: Endpoints REST para el frontend
- **CORS Support**: Configurado para comunicación con el frontend

### DynamoDB Tables
- **Orders Table**: Almacenamiento de pedidos con índices optimizados
- **Appointments Table**: Almacenamiento de citas con índices para consultas eficientes

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

## 📦 Instalación

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

## 🏗️ Estructura del Proyecto

```
nova-sonic-server-app/
├── src/
│   ├── handlers/
│   │   ├── api.ts             # Handler principal con routing
│   │   ├── orders.ts          # Funciones para pedidos
│   │   └── appointments.ts    # Funciones para citas
│   ├── utils/
│   │   └── dynamodb.ts        # Utilidades de DynamoDB
│   └── types/
│       └── index.ts           # Interfaces TypeScript
├── terraform/
│   ├── main.tf                # Recursos principales
│   ├── variables.tf           # Variables de configuración
│   ├── outputs.tf             # Outputs de Terraform
│   ├── versions.tf            # Versiones de providers
│   ├── providers.tf           # Configuración de providers
│   └── terraform.tfvars.example # Ejemplo de variables
├── scripts/
│   └── seed-data.js           # Script para poblar datos
└── dist/                      # Código compilado
```

## 📋 Endpoints API

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

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "customerName": "Juan Pérez",
    "customerEmail": "juan.perez@email.com",
    "items": [...],
    "total": 67.48,
    "status": "pending",
    "createdAt": "2024-01-15T00:00:00.000Z",
    "updatedAt": "2024-01-15T00:00:00.000Z"
  },
  "message": "Order retrieved successfully"
}
```

### Appointments Endpoints

#### GET /appointments
Obtiene todas las citas o filtra por fecha.

**Query Parameters:**
- `date` (opcional): Fecha en formato YYYY-MM-DD

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "1",
      "patientName": "Ana Martínez",
      "patientEmail": "ana.martinez@email.com",
      "doctorName": "Dr. Carlos Rodríguez",
      "date": "2024-01-20T10:00:00.000Z",
      "duration": 30,
      "type": "consultation",
      "notes": "Consulta de rutina",
      "status": "scheduled"
    }
  ],
  "message": "Retrieved 3 appointments successfully"
}
```

#### GET /appointments/{id}
Obtiene una cita específica por ID.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "patientName": "Ana Martínez",
    "patientEmail": "ana.martinez@email.com",
    "doctorName": "Dr. Carlos Rodríguez",
    "date": "2024-01-20T10:00:00.000Z",
    "duration": 30,
    "type": "consultation",
    "notes": "Consulta de rutina",
    "status": "scheduled"
  },
  "message": "Appointment retrieved successfully"
}
```

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

1. **WebSocket Integration**: Implementar WebSocket para chat en tiempo real
2. **Authentication**: Agregar autenticación con Cognito
3. **Caching**: Implementar caching con ElastiCache
4. **Monitoring**: Agregar CloudWatch dashboards
5. **Testing**: Implementar tests unitarios y de integración
6. **CI/CD**: Configurar pipeline de deployment automático 