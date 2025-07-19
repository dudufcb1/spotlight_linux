#!/bin/bash

echo "🔧 SOLUCIONANDO EL PROBLEMA DE DEPENDENCIAS PARA VER LA PANTALLA"
echo ""
echo "📝 El problema exacto:"
echo "   - PyQt6 necesita libxcb-cursor0 para mostrar interfaz gráfica"
echo "   - Esta librería NO se empaqueta automáticamente con PyInstaller"
echo "   - Es una dependencia del sistema gráfico X11"
echo ""
echo "💡 SOLUCIÓN RÁPIDA (para ver funcionando AHORA):"
echo "   sudo apt install -y libxcb-cursor0"
echo ""
echo "🎯 DESPUÉS de instalar, estos comandos mostrarán la pantalla:"
echo "   ./dist/spotlight-linux"
echo "   # O también:"
echo "   source venv/bin/activate && python3 main.py"
echo ""
echo "🚀 ¿Quieres instalar la dependencia ahora? (s/n)"
read -p "Respuesta: " respuesta

if [[ $respuesta == "s" || $respuesta == "S" ]]; then
    echo ""
    echo "📦 Instalando libxcb-cursor0..."
    sudo apt update && sudo apt install -y libxcb-cursor0
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ ¡Dependencia instalada exitosamente!"
        echo ""
        echo "🖥️ Ejecutando Spotlight Linux para mostrar pantalla..."
        ./dist/spotlight-linux &
        SPOTLIGHT_PID=$!
        
        echo ""
        echo "🎉 ¡La aplicación debería estar visible en pantalla!"
        echo "🎮 Puedes interactuar con ella:"
        echo "   - Escribir para buscar"
        echo "   - Presionar Escape para cerrar"
        echo "   - Usar flechas ↑↓ para navegar"
        echo ""
        echo "⏸️ Presiona ENTER para cerrar la aplicación..."
        read
        
        kill $SPOTLIGHT_PID 2>/dev/null
        echo "✅ Aplicación cerrada"
    else
        echo "❌ Error al instalar dependencia"
    fi
else
    echo ""
    echo "📋 Para ver la aplicación funcionando manualmente:"
    echo "   1. sudo apt install -y libxcb-cursor0"
    echo "   2. ./dist/spotlight-linux"
    echo ""
fi
