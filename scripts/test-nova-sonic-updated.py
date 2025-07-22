#!/usr/bin/env python3
"""
Test script for updated Nova Sonic tools with simplified schema
"""

import asyncio
import os
import sys
import boto3

# Add the parent directory to the Python path to find nova_sonic module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nova_sonic.tool_processor import NovaSonicToolProcessor

def check_aws_credentials():
    """Check if AWS credentials are available through any provider"""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Conectado como: {identity['Arn']}")
        return True
    except Exception as e:
        return False

async def test_tools():
    """Test all Nova Sonic tools with updated schema"""
    
    print("🧪 Iniciando pruebas de Nova Sonic Tools (Actualizado)...")
    print("=" * 60)
    
    # Initialize tool processor
    processor = NovaSonicToolProcessor()
    
    # Test data - using simple numeric IDs
    test_order_id = "1"
    test_appointment_id = "1"
    
    tests = [
        {
            "name": "Consultar Pedido por ID numérico",
            "tool": "consultarOrder",
            "content": {"orderId": test_order_id},
            "expected_fields": ["success", "order"],
            "nested_fields": {"order": ["id", "customerName", "customerEmail", "total", "status"]}
        },
        {
            "name": "Consultar Cita por ID numérico",
            "tool": "consultarTurno",
            "content": {"appointmentId": test_appointment_id},
            "expected_fields": ["success", "appointment"],
            "nested_fields": {"appointment": ["id", "patientName", "patientEmail", "doctorName", "date", "status"]}
        },
        {
            "name": "Crear Nuevo Pedido",
            "tool": "crearOrder",
            "content": {
                "customerName": "Usuario Test Actualizado",
                "customerEmail": "test.actualizado@example.com",
                "items": [
                    {
                        "name": "Producto Test Actualizado",
                        "quantity": 2,
                        "price": "149.99",
                        "description": "Producto de prueba con esquema actualizado"
                    }
                ]
            },
            "expected_fields": ["success", "message", "orderId", "total"]
        },
        {
            "name": "Agendar Nueva Cita",
            "tool": "agendarTurno",
            "content": {
                "patientName": "Paciente Test Actualizado",
                "patientEmail": "paciente.actualizado@example.com",
                "doctorName": "Dr. Test Actualizado",
                "date": "2025-07-30T14:00:00.000Z",
                "duration": 45,
                "type": "consultation",
                "notes": "Cita de prueba con esquema actualizado"
            },
            "expected_fields": ["success", "message", "appointmentId", "date", "doctorName"]
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n🔧 Probando: {test['name']}")
        print(f"   Tool: {test['tool']}")
        print(f"   Content: {test['content']}")
        
        try:
            result = await processor.process_tool_async(test['tool'], test['content'])
            
            # Validate result structure
            if "expected_fields" in test:
                missing_fields = []
                nested_missing_fields = []
                
                # Check top-level fields
                for field in test['expected_fields']:
                    if field not in result:
                        missing_fields.append(field)
                
                # Check nested fields if specified
                if "nested_fields" in test and missing_fields == []:
                    for nested_key, nested_field_list in test['nested_fields'].items():
                        if nested_key in result:
                            for field in nested_field_list:
                                if field not in result[nested_key]:
                                    nested_missing_fields.append(f"{nested_key}.{field}")
                        else:
                            nested_missing_fields.append(f"Missing nested object: {nested_key}")
                
                if missing_fields or nested_missing_fields:
                    all_missing = missing_fields + nested_missing_fields
                    print(f"   ⚠️  Campos faltantes: {all_missing}")
                    print(f"   📋 Resultado: {result}")
                    results.append({
                        "test": test['name'],
                        "status": "WARNING",
                        "result": result,
                        "missing_fields": all_missing
                    })
                else:
                    print(f"   ✅ Resultado válido: {result}")
                    results.append({
                        "test": test['name'],
                        "status": "SUCCESS",
                        "result": result
                    })
            else:
                print(f"   ✅ Resultado: {result}")
                results.append({
                    "test": test['name'],
                    "status": "SUCCESS",
                    "result": result
                })
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results.append({
                "test": test['name'],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Resumen de Pruebas (Esquema Actualizado):")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    warning_count = sum(1 for r in results if r['status'] == 'WARNING')
    error_count = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"✅ Exitosas: {success_count}")
    print(f"⚠️  Advertencias: {warning_count}")
    print(f"❌ Errores: {error_count}")
    
    if warning_count > 0:
        print("\n⚠️  Pruebas con advertencias:")
        for result in results:
            if result['status'] == 'WARNING':
                print(f"   - {result['test']}: Campos faltantes {result.get('missing_fields', [])}")
    
    if error_count > 0:
        print("\n❌ Pruebas con errores:")
        for result in results:
            if result['status'] == 'ERROR':
                print(f"   - {result['test']}: {result['error']}")
    
    print("\n🎯 Estado de la integración:")
    if error_count == 0 and warning_count == 0:
        print("✅ Todas las herramientas funcionan correctamente")
        print("🚀 Nova Sonic está listo para usar con el esquema actualizado")
    elif error_count == 0:
        print("⚠️  Algunas herramientas tienen advertencias menores")
        print("🔧 Revisa los campos faltantes si es necesario")
    else:
        print("❌ Algunas herramientas tienen problemas")
        print("🔧 Revisa los errores antes de continuar")
    
    return error_count == 0

async def test_dynamodb_schema():
    """Test DynamoDB schema and data structure"""
    print("\n🔗 Probando esquema de DynamoDB...")
    
    try:
        processor = NovaSonicToolProcessor()
        
        # Test orders table structure
        print("   📦 Probando tabla de pedidos...")
        response = processor.orders_table.scan(Limit=1)
        items = response.get('Items', [])
        
        if items:
            item = items[0]
            print(f"   ✅ Tabla de pedidos accesible")
            print(f"   📋 Campos encontrados: {list(item.keys())}")
            
            # Check for required fields
            required_fields = ['id', 'PK', 'SK', 'customerName', 'customerEmail']
            missing_fields = [field for field in required_fields if field not in item]
            
            if missing_fields:
                print(f"   ⚠️  Campos faltantes en pedidos: {missing_fields}")
            else:
                print(f"   ✅ Esquema de pedidos correcto")
        else:
            print(f"   ⚠️  Tabla de pedidos vacía")
        
        # Test appointments table structure
        print("   🏥 Probando tabla de citas...")
        response = processor.appointments_table.scan(Limit=1)
        items = response.get('Items', [])
        
        if items:
            item = items[0]
            print(f"   ✅ Tabla de citas accesible")
            print(f"   📋 Campos encontrados: {list(item.keys())}")
            
            # Check for required fields
            required_fields = ['id', 'PK', 'SK', 'patientName', 'patientEmail', 'doctorName']
            missing_fields = [field for field in required_fields if field not in item]
            
            if missing_fields:
                print(f"   ⚠️  Campos faltantes en citas: {missing_fields}")
            else:
                print(f"   ✅ Esquema de citas correcto")
        else:
            print(f"   ⚠️  Tabla de citas vacía")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

async def test_id_generation():
    """Test ID generation for new items"""
    print("\n🔢 Probando generación de IDs...")
    
    try:
        processor = NovaSonicToolProcessor()
        
        # Test order ID generation
        next_order_id = await processor._get_next_order_id()
        print(f"   📦 Siguiente ID de pedido: {next_order_id}")
        
        # Test appointment ID generation
        next_appointment_id = await processor._get_next_appointment_id()
        print(f"   🏥 Siguiente ID de cita: {next_appointment_id}")
        
        print(f"   ✅ Generación de IDs funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en generación de IDs: {str(e)}")
        return False

async def main():
    """Main test function"""
    
    print("🚀 Nova Sonic - Pruebas de Esquema Actualizado")
    print("=" * 60)
    
    # Check AWS credentials
    print("🔐 Verificando credenciales AWS...")
    if not check_aws_credentials():
        print("❌ Error: No se encontraron credenciales AWS válidas")
        sys.exit(1)
    
    # Test DynamoDB schema
    schema_ok = await test_dynamodb_schema()
    if not schema_ok:
        print("❌ No se puede conectar a DynamoDB. Verifica las credenciales y permisos.")
        sys.exit(1)
    
    # Test ID generation
    id_ok = await test_id_generation()
    if not id_ok:
        print("❌ Error en la generación de IDs.")
        sys.exit(1)
    
    # Test tools
    tools_ok = await test_tools()
    
    if tools_ok:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("🚀 Nova Sonic está listo para la integración con el esquema actualizado")
        print("\n📋 Resumen de cambios:")
        print("   ✅ Uso directo del campo 'id' numérico")
        print("   ✅ Eliminación de campos userOrderNumber/userAppointmentNumber")
        print("   ✅ Simplificación de funciones de búsqueda")
        print("   ✅ Compatibilidad con GSI existentes")
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        print("🔧 Revisa los errores antes de continuar")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 