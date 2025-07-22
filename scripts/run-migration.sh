#!/bin/bash

# Script para ejecutar la migración de números de usuario
# Este script debe ejecutarse una sola vez

set -e

echo "🚀 Iniciando migración de números de usuario para Nova Sonic"
echo "=========================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "nova_sonic/tool_processor.py" ]; then
    echo "❌ Error: Debes ejecutar este script desde el directorio nova-sonic-server-app"
    exit 1
fi

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

# Verificar que boto3 está instalado
if ! python3 -c "import boto3" &> /dev/null; then
    echo "❌ Error: boto3 no está instalado. Instalando..."
    pip3 install boto3
fi

# Verificar variables de entorno
if [ -z "$AWS_REGION" ]; then
    echo "⚠️  AWS_REGION no está configurado. Usando us-east-1 por defecto."
    export AWS_REGION=us-east-1
fi

if [ -z "$ORDERS_TABLE" ]; then
    echo "⚠️  ORDERS_TABLE no está configurado. Usando nova-sonic-server-app-demo-orders por defecto."
    export ORDERS_TABLE=nova-sonic-server-app-demo-orders
fi

if [ -z "$APPOINTMENTS_TABLE" ]; then
    echo "⚠️  APPOINTMENTS_TABLE no está configurado. Usando nova-sonic-server-app-demo-appointments por defecto."
    export APPOINTMENTS_TABLE=nova-sonic-server-app-demo-appointments
fi

echo ""
echo "📋 Configuración:"
echo "  - AWS Region: $AWS_REGION"
echo "  - Orders Table: $ORDERS_TABLE"
echo "  - Appointments Table: $APPOINTMENTS_TABLE"
echo ""

# Preguntar confirmación
read -p "¿Estás seguro de que quieres ejecutar la migración? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migración cancelada"
    exit 1
fi

echo ""
echo "🔄 Ejecutando migración..."
echo ""

# Ejecutar script de migración
python3 scripts/migrate-user-numbers.py

echo ""
echo "✅ Migración completada!"
echo ""
echo "📝 Próximos pasos:"
echo "  1. Reinicia tu aplicación Nova Sonic"
echo "  2. Prueba consultar un pedido con 'pedido 1' o 'pedido 2'"
echo "  3. Prueba consultar una cita con 'cita 1' o 'cita 2'"
echo ""
echo "🎉 ¡El sistema ahora soporta IDs amigables para el usuario!" 