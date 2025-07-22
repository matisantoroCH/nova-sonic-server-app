#!/usr/bin/env python3
"""
Test script for Nova Sonic tools
"""

import asyncio
import os
import sys
import boto3
from tool_processor import NovaSonicToolProcessor

def check_aws_credentials():
    """Check if AWS credentials are available through any provider"""
    try:
        # Try to create a simple client to test credentials
        sts = boto3.client('sts')
        sts.get_caller_identity()
        return True
    except Exception as e:
        return False

async def test_tools():
    """Test all Nova Sonic tools"""
    
    print("🧪 Iniciando pruebas de Nova Sonic Tools...")
    print("=" * 50)
    
    # Initialize tool processor
    processor = NovaSonicToolProcessor()
    
    # Test data
    test_order_id = "1"
    test_appointment_id = "1"
    
    tests = [
        {
            "name": "Consultar Pedido",
            "tool": "consultarOrder",
            "content": {"orderId": test_order_id}
        },
        {
            "name": "Consultar Cita",
            "tool": "consultarTurno",
            "content": {"appointmentId": test_appointment_id}
        },
        {
            "name": "Crear Pedido",
            "tool": "crearOrder",
            "content": {
                "customerName": "Test User",
                "customerEmail": "test@example.com",
                "items": [
                    {
                        "name": "Producto Test",
                        "quantity": 1,
                        "price": 99.99,
                        "description": "Producto de prueba"
                    }
                ]
            }
        },
        {
            "name": "Agendar Cita",
            "tool": "agendarTurno",
            "content": {
                "patientName": "Paciente Test",
                "patientEmail": "paciente@example.com",
                "doctorName": "Dr. Test",
                "date": "2025-07-30T10:00:00.000Z",
                "duration": 30,
                "type": "consultation",
                "notes": "Cita de prueba"
            }
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n🔧 Probando: {test['name']}")
        print(f"   Tool: {test['tool']}")
        print(f"   Content: {test['content']}")
        
        try:
            result = await processor.process_tool_async(test['tool'], test['content'])
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
    print("\n" + "=" * 50)
    print("📊 Resumen de Pruebas:")
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    error_count = len(results) - success_count
    
    print(f"✅ Exitosas: {success_count}")
    print(f"❌ Errores: {error_count}")
    
    if error_count > 0:
        print("\n❌ Pruebas con errores:")
        for result in results:
            if result['status'] == 'ERROR':
                print(f"   - {result['test']}: {result['error']}")
    
    print("\n🎯 Estado de la integración:")
    if error_count == 0:
        print("✅ Todas las herramientas funcionan correctamente")
        print("🚀 Nova Sonic está listo para usar")
    else:
        print("⚠️  Algunas herramientas tienen problemas")
        print("🔧 Revisa los errores antes de continuar")
    
    return error_count == 0

async def test_dynamodb_connection():
    """Test DynamoDB connection"""
    print("\n🔗 Probando conexión con DynamoDB...")
    
    try:
        processor = NovaSonicToolProcessor()
        
        # Test orders table
        print("   📦 Probando tabla de pedidos...")
        response = processor.orders_table.scan(Limit=1)
        print(f"   ✅ Tabla de pedidos accesible ({len(response.get('Items', []))} items)")
        
        # Test appointments table
        print("   🏥 Probando tabla de citas...")
        response = processor.appointments_table.scan(Limit=1)
        print(f"   ✅ Tabla de citas accesible ({len(response.get('Items', []))} items)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

async def main():
    """Main test function"""
    
    # Check AWS credentials using the default provider chain
    print("🔐 Verificando credenciales AWS...")
    if not check_aws_credentials():
        print("❌ Error: No se encontraron credenciales AWS válidas")
        print("\n💡 Opciones para configurar credenciales:")
        print("   1. AWS CLI: aws configure")
        print("   2. Variables de entorno: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("   3. IAM Role (para ECS/EC2)")
        print("   4. AWS SSO: aws configure sso")
        print("\n🔗 Más información: https://docs.aws.amazon.com/sdk-for-python/v1/developer-guide/credentials.html")
        sys.exit(1)
    
    print("✅ Credenciales AWS encontradas")
    
    # Test DynamoDB connection first
    db_ok = await test_dynamodb_connection()
    if not db_ok:
        print("❌ No se puede conectar a DynamoDB. Verifica las credenciales y permisos.")
        sys.exit(1)
    
    # Test tools
    tools_ok = await test_tools()
    
    if tools_ok:
        print("\n🎉 ¡Todas las pruebas pasaron!")
        print("🚀 Nova Sonic está listo para la integración")
    else:
        print("\n⚠️  Algunas pruebas fallaron")
        print("🔧 Revisa los errores antes de continuar")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 