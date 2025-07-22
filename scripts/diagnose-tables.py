#!/usr/bin/env python3
"""
Script de diagnóstico para revisar la estructura real de las tablas de DynamoDB
"""

import os
import boto3
import json

def diagnose_table(table_name, table_resource):
    """Diagnostica la estructura de una tabla"""
    print(f"\n🔍 Diagnóstico de tabla: {table_name}")
    print("=" * 50)
    
    try:
        # Obtener información de la tabla
        table_info = table_resource.meta.client.describe_table(TableName=table_name)
        
        # Mostrar esquema de clave primaria
        key_schema = table_info['Table']['KeySchema']
        print("📋 Esquema de Clave Primaria:")
        for key in key_schema:
            print(f"  - {key['AttributeName']} ({key['KeyType']})")
        
        # Mostrar atributos de clave
        attribute_definitions = table_info['Table']['AttributeDefinitions']
        print("\n📋 Definiciones de Atributos:")
        for attr in attribute_definitions:
            print(f"  - {attr['AttributeName']}: {attr['AttributeType']}")
        
        # Mostrar índices globales secundarios
        if 'GlobalSecondaryIndexes' in table_info['Table']:
            print("\n📋 Índices Globales Secundarios:")
            for gsi in table_info['Table']['GlobalSecondaryIndexes']:
                print(f"  - {gsi['IndexName']}:")
                for key in gsi['KeySchema']:
                    print(f"    * {key['AttributeName']} ({key['KeyType']})")
        
        # Escanear algunos items para ver la estructura real
        print("\n📋 Muestra de Items (primeros 3):")
        response = table_resource.scan(Limit=3)
        items = response.get('Items', [])
        
        if items:
            for i, item in enumerate(items, 1):
                print(f"\n  Item {i}:")
                for key, value in item.items():
                    print(f"    {key}: {value}")
        else:
            print("  No hay items en la tabla")
            
    except Exception as e:
        print(f"❌ Error diagnosticando tabla {table_name}: {e}")

def main():
    """Función principal"""
    print("🚀 Diagnóstico de tablas DynamoDB")
    print("=" * 50)
    
    # Configurar DynamoDB
    dynamodb = boto3.resource('dynamodb')
    orders_table_name = os.getenv('ORDERS_TABLE', 'nova-sonic-server-app-demo-orders')
    appointments_table_name = os.getenv('APPOINTMENTS_TABLE', 'nova-sonic-server-app-demo-appointments')
    
    try:
        # Diagnosticar tabla de pedidos
        orders_table = dynamodb.Table(orders_table_name)
        diagnose_table(orders_table_name, orders_table)
        
        # Diagnosticar tabla de citas
        appointments_table = dynamodb.Table(appointments_table_name)
        diagnose_table(appointments_table_name, appointments_table)
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    main() 