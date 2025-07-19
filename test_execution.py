#!/usr/bin/env python3
"""
Test directo de ejecución para diagnosticar el problema
"""
import subprocess
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_execution():
    """Test directo de diferentes métodos de ejecución"""
    
    print("=== TEST DE EJECUCIÓN SPOTLIGHT ===")
    logger.info("Iniciando tests de ejecución")
    
    # Test 1: nano directo
    print("\n1. Test nano directo")
    try:
        proc = subprocess.Popen(['nano', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print(f"   ✅ nano version: {stdout.decode().split()[2]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: xdg-open con archivo
    print("\n2. Test xdg-open")
    try:
        # Crear archivo test
        test_file = '/tmp/spotlight_test.txt'
        with open(test_file, 'w') as f:
            f.write("Test file for Spotlight Linux execution\n")
        
        print(f"   Archivo creado: {test_file}")
        print(f"   Archivo existe: {os.path.exists(test_file)}")
        
        # Intentar abrirlo
        proc = subprocess.Popen(['xdg-open', test_file],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               start_new_session=True)
        print(f"   ✅ xdg-open lanzado, PID: {proc.pid}")
        
        # Verificar si el proceso sigue vivo después de un momento
        import time
        time.sleep(1)
        poll = proc.poll()
        if poll is None:
            print(f"   ✅ Proceso activo")
        else:
            print(f"   ⚠️ Proceso terminó con código: {poll}")
            stdout, stderr = proc.communicate()
            if stderr:
                print(f"   Error: {stderr.decode()}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Simulación del app_parser actual
    print("\n3. Test método app_parser")
    try:
        item = {
            'type': 'command',
            'name': 'nano',
            'path': 'nano --version'
        }
        
        command = item['path']
        cmd_parts = command.split()
        print(f"   Comando: {cmd_parts}")
        
        proc = subprocess.Popen(cmd_parts,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               start_new_session=True)
        print(f"   ✅ Proceso lanzado, PID: {proc.pid}")
        
        # Obtener resultado
        stdout, stderr = proc.communicate()
        print(f"   Salida: {stdout.decode().strip()}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        logger.exception("Error en test app_parser")
    
    # Test 4: Verificar variables de entorno
    print("\n4. Test variables de entorno")
    important_vars = ['DISPLAY', 'XDG_CURRENT_DESKTOP', 'PATH']
    for var in important_vars:
        value = os.environ.get(var, 'NO DEFINIDA')
        print(f"   {var}: {value[:50]}{'...' if len(value) > 50 else ''}")

if __name__ == "__main__":
    test_execution()
