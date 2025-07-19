#!/bin/bash

# 🚀 Spotlight Linux - Instalador Completo del Sistema
# TODO EN UNO: Verifica, compila, instala y configura automáticamente

set -e

echo "� Spotlight Linux - Instalador Completo"
echo "========================================"
echo ""

# Verificar permisos de administrador
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script requiere permisos de administrador"
    echo "💡 Ejecuta: sudo ./install_system.sh"
    exit 1
fi

# PASO 1: Verificar e instalar dependencias automáticamente
echo "� PASO 1: Verificando e instalando dependencias..."

# Detectar distribución
if command -v apt &> /dev/null; then
    PKG_MANAGER="apt"
    INSTALL_CMD="apt update && apt install -y"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
    INSTALL_CMD="yum install -y"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    INSTALL_CMD="dnf install -y"
else
    echo "❌ Gestor de paquetes no soportado"
    exit 1
fi

echo "� Detectado gestor de paquetes: $PKG_MANAGER"

# Instalar Python 3 si no existe
if ! command -v python3 &> /dev/null; then
    echo "📥 Instalando Python 3..."
    eval "$INSTALL_CMD python3 python3-pip python3-venv"
else
    echo "✅ Python 3 ya está instalado"
fi

# Instalar pip si no existe
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "📥 Instalando pip..."
    eval "$INSTALL_CMD python3-pip"
else
    echo "✅ pip ya está instalado"
fi

# Instalar dependencias básicas del sistema
echo "� Instalando dependencias del sistema para PyQt6..."
if [ "$PKG_MANAGER" = "apt" ]; then
    apt update
    apt install -y python3-dev build-essential
elif [ "$PKG_MANAGER" = "yum" ] || [ "$PKG_MANAGER" = "dnf" ]; then
    eval "$INSTALL_CMD python3-devel gcc gcc-c++ make"
fi

echo "✅ Dependencias básicas del sistema instaladas"

# PASO 2: Compilar aplicación automáticamente
echo ""
echo "� PASO 2: Compilando aplicación..."

# Verificar archivos necesarios
if [ ! -f "main.py" ]; then
    echo "❌ No se encontró main.py"
    echo "💡 Asegúrate de estar en el directorio correcto del proyecto"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ No se encontró requirements.txt"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias Python..."
pip install --upgrade pip

# Instalar PyQt6 primero (puede tomar tiempo)
echo "🎨 Instalando PyQt6 (esto puede tomar varios minutos)..."
if ! pip install PyQt6; then
    echo "⚠️ Error instalando PyQt6, intentando con --no-cache-dir..."
    pip install --no-cache-dir PyQt6
fi

# Instalar resto de dependencias
echo "📦 Instalando resto de dependencias..."
pip install -r requirements.txt

# Instalar PyInstaller
echo "🔨 Instalando PyInstaller..."
pip install pyinstaller

# Compilar con PyInstaller
echo "🔨 Compilando con PyInstaller..."
pyinstaller --onefile --windowed --name spotlight-linux main.py

# Verificar que la compilación fue exitosa
if [ ! -f "dist/spotlight-linux" ]; then
    echo "❌ Error en la compilación"
    exit 1
fi

echo "✅ Compilación exitosa"

# PASO 3: Instalar en el sistema
echo ""
echo "� PASO 3: Instalando en el sistema..."

# Crear directorios necesarios
echo "📁 Creando directorios del sistema..."
mkdir -p /usr/local/bin
mkdir -p /usr/share/applications
mkdir -p /usr/share/icons/hicolor/256x256/apps
mkdir -p /usr/share/pixmaps

echo "📦 Copiando ejecutable..."

# Verificar si el ejecutable está en uso y detenerlo si es necesario
if [ -f "/usr/local/bin/spotlight-linux" ]; then
    echo "🔄 Detectado ejecutable existente, verificando procesos..."

    # Buscar procesos que usen el ejecutable
    PIDS=$(pgrep -f "spotlight-linux" || true)

    if [ ! -z "$PIDS" ]; then
        echo "⚠️  Procesos de Spotlight Linux detectados, cerrándolos..."
        echo "PIDs encontrados: $PIDS"

        # Intentar cerrar gracefully primero
        pkill -TERM -f "spotlight-linux" || true
        sleep 2

        # Si aún hay procesos, forzar cierre
        REMAINING=$(pgrep -f "spotlight-linux" || true)
        if [ ! -z "$REMAINING" ]; then
            echo "🔨 Forzando cierre de procesos restantes..."
            pkill -KILL -f "spotlight-linux" || true
            sleep 1
        fi

        echo "✅ Procesos cerrados"
    fi

    # Hacer backup del ejecutable anterior
    echo "💾 Creando backup del ejecutable anterior..."
    cp /usr/local/bin/spotlight-linux /usr/local/bin/spotlight-linux.backup.$(date +%Y%m%d_%H%M%S) || true
fi

# Copiar nuevo ejecutable
echo "📁 Instalando nuevo ejecutable..."
cp dist/spotlight-linux /usr/local/bin/spotlight-linux
chmod +x /usr/local/bin/spotlight-linux

echo "✅ Ejecutable instalado correctamente"

echo "🎨 Instalando archivos de escritorio..."

# Copiar archivo .desktop
cp spotlight-linux.desktop /usr/share/applications/
chmod 644 /usr/share/applications/spotlight-linux.desktop

# Crear icono simple si no existe
if [ ! -f "/usr/share/pixmaps/spotlight-linux.png" ]; then
    echo "🎨 Creando icono temporal..."
    # Crear un icono SVG simple
    cat > /usr/share/pixmaps/spotlight-linux.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" rx="32" fill="#3b82f6"/>
  <circle cx="128" cy="128" r="80" fill="none" stroke="white" stroke-width="8"/>
  <circle cx="128" cy="128" r="16" fill="white"/>
  <text x="128" y="200" text-anchor="middle" fill="white" font-family="Arial" font-size="24" font-weight="bold">AI</text>
</svg>
EOF
    
    # Convertir a PNG si imagemagick está disponible
    if command -v convert &> /dev/null; then
        convert /usr/share/pixmaps/spotlight-linux.svg /usr/share/pixmaps/spotlight-linux.png
        cp /usr/share/pixmaps/spotlight-linux.png /usr/share/icons/hicolor/256x256/apps/
    fi
fi

echo "🔄 Actualizando cache de aplicaciones..."

# Actualizar cache de aplicaciones
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications
fi

if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

# Verificación final
echo "🔍 Verificando instalación..."

if [ -f "/usr/local/bin/spotlight-linux" ] && [ -x "/usr/local/bin/spotlight-linux" ]; then
    echo "✅ Ejecutable instalado correctamente"
else
    echo "❌ Error: Ejecutable no se instaló correctamente"
    exit 1
fi

if [ -f "/usr/share/applications/spotlight-linux.desktop" ]; then
    echo "✅ Archivo .desktop instalado correctamente"
else
    echo "❌ Error: Archivo .desktop no se instaló correctamente"
    exit 1
fi

# PASO 4: Configuración final
echo ""
echo "⚙️ PASO 4: Configuración final..."

# Limpiar archivos temporales de compilación
echo "🧹 Limpiando archivos temporales..."
rm -rf build/ *.spec

echo ""
echo "🎉 ¡Spotlight Linux instalado exitosamente!"
echo "=========================================="
echo ""
echo "📋 Configuración de atajos de teclado:"
echo "   1. Abre Configuración del Sistema"
echo "   2. Ve a 'Atajos de teclado' o 'Keyboard Shortcuts'"
echo "   3. Busca 'Atajos personalizados' o 'Custom Shortcuts'"
echo "   4. Añade un nuevo atajo:"
echo "      - Nombre: Spotlight Linux"
echo "      - Comando: /usr/local/bin/spotlight-linux"
echo "      - Atajo: Ctrl+P (o el que prefieras)"
echo ""
echo "🚀 Para ejecutar:"
echo "   - Desde terminal: spotlight-linux"
echo "   - Desde menú de aplicaciones: busca 'Spotlight Linux'"
echo "   - Con atajo configurado: Ctrl+P"
echo ""
echo "🗑️  Para desinstalar:"
echo "   sudo ./uninstall_system.sh"
