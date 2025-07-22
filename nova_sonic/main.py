#!/usr/bin/env python3
"""
Nova Sonic - Asistente Virtual para Gestión de Pedidos y Citas
"""

import asyncio
import argparse
import os
import sys
import boto3
from nova_sonic_client import NovaSonicClient

def check_aws_credentials():
    """Check if AWS credentials are available through any provider"""
    try:
        # Try to create a simple client to test credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ Conectado como: {identity['Arn']}")
        return True
    except Exception as e:
        return False

async def main():
    """Main function to run Nova Sonic"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Nova Sonic - Asistente Virtual')
    parser.add_argument('--debug', action='store_true', help='Habilitar modo debug')
    parser.add_argument('--voice', default='carlos', help='ID de voz a usar')
    parser.add_argument('--region', default='us-east-1', help='Región de AWS')
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        print("🐛 Modo debug habilitado")
    
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
    
    # Create Nova Sonic client
    client = NovaSonicClient(
        voice_id=args.voice,
        region=args.region
    )
    
    try:
        print("🚀 Iniciando Nova Sonic...")
        print("=" * 50)
        print("🎯 Funciones disponibles:")
        print("  📦 Pedidos:")
        print("    - Consultar pedido por ID")
        print("    - Cancelar pedido")
        print("    - Crear nuevo pedido")
        print("  🏥 Citas Médicas:")
        print("    - Agendar cita")
        print("    - Cancelar cita")
        print("    - Modificar fecha/hora")
        print("    - Consultar cita")
        print("=" * 50)
        
        # Initialize stream
        await client.initialize_stream()
        
        # Start audio tasks
        playback_task = asyncio.create_task(client.play_output_audio())
        capture_task = asyncio.create_task(client.capture_audio())
        
        print("\n🎤 ¡Nova Sonic está listo!")
        print("💡 Ejemplos de comandos de voz:")
        print("   - 'Consulta el pedido número 1'")
        print("   - 'Cancela el pedido número 2'")
        print("   - 'Agenda una cita para mañana a las 10'")
        print("   - 'Modifica la cita número 3 para el viernes'")
        print("\n⏹️  Presiona Ctrl+C para salir")
        
        # Keep the session alive
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo Nova Sonic...")
        
    except Exception as e:
        print(f"❌ Error en Nova Sonic: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Clean up
        try:
            client.is_active = False
            for task in [playback_task, capture_task]:
                if not task.done():
                    task.cancel()
            await asyncio.gather(playback_task, capture_task, return_exceptions=True)
            await client.stop_session()
        except Exception as e:
            print(f"Error durante la limpieza: {str(e)}")
        
        print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Sesión interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        sys.exit(1) 