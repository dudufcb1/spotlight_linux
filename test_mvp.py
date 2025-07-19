#!/usr/bin/env python3
"""
Test básico para el MVP de Spotlight Linux AI
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_engine import ai_engine

def test_ai_engine():
    """Probar el motor de IA"""
    print("🔍 Probando motor de IA...")
    
    # Verificar estado
    status = ai_engine.get_status()
    print(f"Estado del motor: {status}")
    
    if not status["initialized"]:
        print("❌ Motor de IA no inicializado")
        print("💡 Configure GEMINI_API_KEY en variables de entorno")
        return False
    
    # Prueba simple
    print("\n🧪 Enviando consulta de prueba...")
    response = ai_engine.ask_sync("Hola, ¿cómo estás?")
    
    print(f"\n📝 Respuesta:")
    print(f"  Éxito: {response.success}")
    print(f"  Contenido: {response.content[:100]}{'...' if len(response.content) > 100 else ''}")
    print(f"  Es Markdown: {response.is_markdown}")
    print(f"  Tiempo: {response.processing_time:.2f}s")
    
    return response.success

def test_dependencies():
    """Verificar dependencias"""
    print("📦 Verificando dependencias...")
    
    dependencies = {
        "tkinter": True,  # Siempre disponible en Python estándar
        "customtkinter": False,
        "pynput": False,
        "google.generativeai": False
    }
    
    try:
        import customtkinter
        dependencies["customtkinter"] = True
        print("✅ CustomTkinter disponible")
    except ImportError:
        print("⚠️  CustomTkinter no disponible (usar Tkinter básico)")
    
    try:
        import pynput
        dependencies["pynput"] = True
        print("✅ Pynput disponible (hotkeys globales)")
    except ImportError:
        print("⚠️  Pynput no disponible (sin hotkeys globales)")
    
    try:
        import google.generativeai
        dependencies["google.generativeai"] = True
        print("✅ Google GenerativeAI disponible")
    except ImportError:
        print("❌ Google GenerativeAI no disponible")
        print("💡 Instale con: pip install google-generativeai")
    
    return dependencies

def main():
    """Función principal de pruebas"""
    print("🚀 Test MVP Spotlight Linux AI\n")
    
    # Verificar dependencias
    deps = test_dependencies()
    print()
    
    # Probar motor de IA
    ai_works = test_ai_engine()
    print()
    
    # Resumen
    print("📊 Resumen:")
    print(f"  Tkinter: ✅ (siempre disponible)")
    print(f"  CustomTkinter: {'✅' if deps['customtkinter'] else '⚠️ '}")
    print(f"  Pynput: {'✅' if deps['pynput'] else '⚠️ '}")
    print(f"  Gemini AI: {'✅' if deps['google.generativeai'] else '❌'}")
    print(f"  Motor IA funcionando: {'✅' if ai_works else '❌'}")
    
    if ai_works:
        print("\n🎉 MVP listo para usar!")
        print("💡 Ejecute: python main.py")
    else:
        print("\n⚠️  Configure API key para usar IA")
        print("💡 export GEMINI_API_KEY='su_api_key'")

if __name__ == "__main__":
    main()
