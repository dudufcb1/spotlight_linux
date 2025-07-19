#!/bin/bash

# Script de instalación para Spotlight Linux

echo "🚀 Instalando Spotlight Linux..."

# Verificar que Python 3.8+ esté instalado
python3_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if [ -z "$python3_version" ]; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python detectado: $python3_version"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorio para assets si no existe
mkdir -p assets

echo "✅ Instalación completada!"
echo ""
echo "Para ejecutar Spotlight Linux:"
echo "  source venv/bin/activate"
echo "  python3 main.py"
echo ""
echo "Para crear un acceso directo, ejecuta:"
echo "  ./create_shortcut.sh"
