#!/usr/bin/env python3
"""
Script de migración para agregar números de usuario amigables a pedidos y citas existentes.
Este script debe ejecutarse una sola vez para migrar datos existentes.
"""

import os
import boto3
from datetime import datetime
import json

def migrate_orders():
    """Migra pedidos existentes agregando userOrderNumber"""
    dynamodb = boto3.resource('dynamodb')
    orders_table = dynamodb.Table(os.getenv('ORDERS_TABLE', 'nova-sonic-server-app-demo-orders'))
    
    print("🔄 Migrando pedidos...")
    
    # Escanear todos los pedidos
    response = orders_table.scan()
    orders = response.get('Items', [])
    
    # Ordenar por fecha de creación para asignar números secuenciales
    orders.sort(key=lambda x: x.get('createdAt', ''))
    
    for i, order in enumerate(orders, 1):
        order_id = order.get('id')
        user_order_number = i
        
        print(f"  📦 Asignando pedido #{user_order_number} a {order_id}")
        
        try:
            # Actualizar el item con userOrderNumber y GSI1PK
            # Usar PK y SK como claves primarias
            orders_table.update_item(
                Key={'PK': f'ORDER#{order_id}', 'SK': f'ORDER#{order_id}'},
                UpdateExpression='SET userOrderNumber = :user_num, GSI1PK = :gsi_pk',
                ExpressionAttributeValues={
                    ':user_num': user_order_number,
                    ':gsi_pk': f'USER_ORDER_{user_order_number}'
                }
            )
        except Exception as e:
            print(f"    ❌ Error actualizando pedido {order_id}: {e}")
    
    print(f"✅ Migración de pedidos completada. {len(orders)} pedidos procesados.")

def migrate_appointments():
    """Migra citas existentes agregando userAppointmentNumber"""
    dynamodb = boto3.resource('dynamodb')
    appointments_table = dynamodb.Table(os.getenv('APPOINTMENTS_TABLE', 'nova-sonic-server-app-demo-appointments'))
    
    print("🔄 Migrando citas...")
    
    # Escanear todas las citas
    response = appointments_table.scan()
    appointments = response.get('Items', [])
    
    # Ordenar por fecha de creación para asignar números secuenciales
    appointments.sort(key=lambda x: x.get('date', ''))
    
    for i, appointment in enumerate(appointments, 1):
        appointment_id = appointment.get('id')
        user_appointment_number = i
        
        print(f"  📅 Asignando cita #{user_appointment_number} a {appointment_id}")
        
        try:
            # Actualizar el item con userAppointmentNumber y GSI1PK
            # Usar PK y SK como claves primarias
            appointments_table.update_item(
                Key={'PK': f'APPOINTMENT#{appointment_id}', 'SK': f'APPOINTMENT#{appointment_id}'},
                UpdateExpression='SET userAppointmentNumber = :user_num, GSI1PK = :gsi_pk',
                ExpressionAttributeValues={
                    ':user_num': user_appointment_number,
                    ':gsi_pk': f'USER_APPOINTMENT_{user_appointment_number}'
                }
            )
        except Exception as e:
            print(f"    ❌ Error actualizando cita {appointment_id}: {e}")
    
    print(f"✅ Migración de citas completada. {len(appointments)} citas procesadas.")

def verify_migration():
    """Verifica que la migración se completó correctamente"""
    dynamodb = boto3.resource('dynamodb')
    orders_table = dynamodb.Table(os.getenv('ORDERS_TABLE', 'nova-sonic-server-app-demo-orders'))
    appointments_table = dynamodb.Table(os.getenv('APPOINTMENTS_TABLE', 'nova-sonic-server-app-demo-appointments'))
    
    print("🔍 Verificando migración...")
    
    # Verificar pedidos
    orders_response = orders_table.scan()
    orders = orders_response.get('Items', [])
    orders_with_numbers = [o for o in orders if 'userOrderNumber' in o]
    
    print(f"  📦 Pedidos con userOrderNumber: {len(orders_with_numbers)}/{len(orders)}")
    
    # Verificar citas
    appointments_response = appointments_table.scan()
    appointments = appointments_response.get('Items', [])
    appointments_with_numbers = [a for a in appointments if 'userAppointmentNumber' in a]
    
    print(f"  📅 Citas con userAppointmentNumber: {len(appointments_with_numbers)}/{len(appointments)}")
    
    if len(orders_with_numbers) == len(orders) and len(appointments_with_numbers) == len(appointments):
        print("✅ Migración verificada exitosamente!")
    else:
        print("⚠️  Algunos items no fueron migrados correctamente.")

def main():
    """Función principal del script de migración"""
    print("🚀 Iniciando migración de números de usuario...")
    print("=" * 50)
    
    # Verificar variables de entorno
    if not os.getenv('AWS_REGION'):
        print("⚠️  AWS_REGION no está configurado. Usando región por defecto.")
    
    try:
        # Ejecutar migración
        migrate_orders()
        print()
        migrate_appointments()
        print()
        
        # Verificar migración
        verify_migration()
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return 1
    
    print("=" * 50)
    print("🎉 Migración completada exitosamente!")
    print("\n📝 Notas importantes:")
    print("  - Los números de usuario se asignaron secuencialmente por fecha de creación")
    print("  - Los nuevos pedidos/citas usarán números continuos desde el último existente")
    print("  - El sistema ahora puede manejar IDs amigables como 'pedido 3' o 'cita 15'")
    
    return 0

if __name__ == "__main__":
    exit(main()) 