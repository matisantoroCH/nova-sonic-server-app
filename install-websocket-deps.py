#!/usr/bin/env python3
"""
Script para instalar dependencias del WebSocket server
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install WebSocket server dependencies"""
    print("🔧 Instalando dependencias del WebSocket server...")
    
    # Change to nova_sonic directory
    nova_sonic_dir = os.path.join(os.path.dirname(__file__), 'nova_sonic')
    os.chdir(nova_sonic_dir)
    
    # Install websockets
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'websockets>=12.0'])
        print("✅ websockets instalado correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando websockets: {e}")
        return False
    
    print("✅ Todas las dependencias instaladas correctamente")
    return True

if __name__ == "__main__":
    install_dependencies() 