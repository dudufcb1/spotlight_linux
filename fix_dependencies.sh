#!/bin/bash

# Script para instalar dependencias de PyQt6 en Linux Mint/Ubuntu

echo "🔧 Instalando dependencias de PyQt6 para Linux Mint..."

echo "Por favor ejecuta estos comandos con privilegios de administrador:"
echo ""
echo "sudo apt update"
echo "sudo apt install -y libxcb-cursor0 libxcb-cursor-dev"
echo ""
echo "Dependencias adicionales recomendadas:"
echo "sudo apt install -y python3-pyqt6 python3-pyqt6.qtwidgets"
echo ""
echo "Si continúan los problemas, también instala:"
echo "sudo apt install -y qt6-base-dev libqt6gui6 libqt6widgets6"
echo ""
echo "Después de instalar las dependencias, ejecuta nuevamente:"
echo "source venv/bin/activate && python3 main.py"
