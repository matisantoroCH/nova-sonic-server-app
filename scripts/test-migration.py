#!/usr/bin/env python3
"""
Script de prueba para verificar que la migración funcione correctamente
"""

import os
import sys
import boto3
import asyncio

# Agregar el directorio padre al path para poder importar nova_sonic
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nova_sonic.tool_processor import NovaSonicToolProcessor

async def test_migration():
    """Prueba la funcionalidad después de la migración"""
    print("🧪 Probando funcionalidad después de la migración...")
    print("=" * 50)
    
    processor = NovaSonicToolProcessor()
    
    # Probar consulta de pedidos
    print("\n📦 Probando consulta de pedidos:")
    for i in range(1, 4):  # Probar pedidos 1, 2, 3
        try:
            result = await processor._consultar_pedido({"orderId": str(i)})
            if result.get("success"):
                order = result.get("order", {})
                print(f"  ✅ Pedido #{i}: {order.get('customerName', 'N/A')} - ${order.get('total', 0)}")
            else:
                print(f"  ❌ Pedido #{i}: {result.get('error', 'Error desconocido')}")
        except Exception as e:
            print(f"  ❌ Pedido #{i}: Error - {e}")
    
    # Probar consulta de citas
    print("\n📅 Probando consulta de citas:")
    for i in range(1, 4):  # Probar citas 1, 2, 3
        try:
            result = await processor._consultar_turno({"appointmentId": str(i)})
            if result.get("success"):
                appointment = result.get("appointment", {})
                print(f"  ✅ Cita #{i}: {appointment.get('patientName', 'N/A')} - {appointment.get('doctorName', 'N/A')}")
            else:
                print(f"  ❌ Cita #{i}: {result.get('error', 'Error desconocido')}")
        except Exception as e:
            print(f"  ❌ Cita #{i}: Error - {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas completadas!")

def main():
    """Función principal"""
    asyncio.run(test_migration())

if __name__ == "__main__":
    main() 