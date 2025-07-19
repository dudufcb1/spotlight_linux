#!/bin/bash

# Script de build automatizado para Spotlight Linux
# Genera ejecutable con PyInstaller y lo empaqueta en AppImage

set -e  # Salir si hay errores

PROJECT_DIR="/media/eduardo/56087475087455C9/Dev/Python/spotlight_linux"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"
APPDIR="$PROJECT_DIR/AppDir"

echo "🚀 Iniciando build de Spotlight Linux..."

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf "$BUILD_DIR" "$DIST_DIR" "$APPDIR" *.AppImage

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
cd "$PROJECT_DIR"
source venv/bin/activate

# Verificar que PyInstaller esté disponible
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller no encontrado. Instalando..."
    pip install pyinstaller
fi

# Crear ejecutable con PyInstaller
echo "📦 Creando ejecutable con PyInstaller..."
pyinstaller spotlight.spec --clean --noconfirm

# Verificar que el ejecutable se creó correctamente
if [ ! -f "$DIST_DIR/spotlight-linux" ]; then
    echo "❌ Error: No se pudo crear el ejecutable"
    exit 1
fi

echo "✅ Ejecutable creado en: $DIST_DIR/spotlight-linux"

# Crear estructura AppDir
echo "📁 Creando estructura AppDir..."
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"

# Copiar ejecutable
cp "$DIST_DIR/spotlight-linux" "$APPDIR/usr/bin/"

# Crear archivo .desktop
cat > "$APPDIR/spotlight-linux.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Spotlight Linux
Comment=Herramienta de búsqueda rápida para Linux
Exec=spotlight-linux
Icon=spotlight-linux
Categories=Utility;
StartupNotify=true
EOF

# Copiar .desktop a aplicaciones
cp "$APPDIR/spotlight-linux.desktop" "$APPDIR/usr/share/applications/"

# Crear icono simple si no existe
if [ ! -f "assets/icon.png" ]; then
    echo "🎨 Creando icono temporal..."
    mkdir -p assets
    # Crear un icono simple con ImageMagick si está disponible
    if command -v convert &> /dev/null; then
        convert -size 256x256 xc:transparent -fill '#0078d4' -draw 'circle 128,128 128,64' assets/icon.png
    fi
fi

# Copiar icono si existe
if [ -f "assets/icon.png" ]; then
    cp "assets/icon.png" "$APPDIR/spotlight-linux.png"
    cp "assets/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/spotlight-linux.png"
fi

# Hacer ejecutable el AppRun
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
exec "${HERE}/usr/bin/spotlight-linux" "$@"
EOF

chmod +x "$APPDIR/AppRun"

echo "✅ Estructura AppDir creada"

# Información sobre AppImage
echo ""
echo "📋 Para crear el AppImage final, necesitas:"
echo "1. Instalar appimagetool:"
echo "   wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
echo "   chmod +x appimagetool-x86_64.AppImage"
echo ""
echo "2. Generar el AppImage:"
echo "   ./appimagetool-x86_64.AppImage AppDir spotlight-linux.AppImage"
echo ""
echo "🎯 El ejecutable standalone está listo en: $DIST_DIR/spotlight-linux"
echo "📁 La estructura AppDir está preparada en: $APPDIR"
echo ""
echo "Para probar el ejecutable:"
echo "  $DIST_DIR/spotlight-linux"
