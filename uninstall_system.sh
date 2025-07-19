#!/bin/bash

# 🗑️ Spotlight Linux - Desinstalador del Sistema
# Elimina Spotlight Linux del sistema

set -e

echo "🗑️ Desinstalando Spotlight Linux del sistema..."

# Verificar permisos de administrador
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script requiere permisos de administrador"
    echo "💡 Ejecuta: sudo ./uninstall_system.sh"
    exit 1
fi

echo "📁 Eliminando archivos del sistema..."

# Eliminar ejecutable
if [ -f "/usr/local/bin/spotlight-linux" ]; then
    rm -f /usr/local/bin/spotlight-linux
    echo "✅ Ejecutable eliminado"
fi

# Eliminar archivo .desktop
if [ -f "/usr/share/applications/spotlight-linux.desktop" ]; then
    rm -f /usr/share/applications/spotlight-linux.desktop
    echo "✅ Archivo .desktop eliminado"
fi

# Eliminar iconos
if [ -f "/usr/share/pixmaps/spotlight-linux.png" ]; then
    rm -f /usr/share/pixmaps/spotlight-linux.png
    echo "✅ Icono PNG eliminado"
fi

if [ -f "/usr/share/pixmaps/spotlight-linux.svg" ]; then
    rm -f /usr/share/pixmaps/spotlight-linux.svg
    echo "✅ Icono SVG eliminado"
fi

if [ -f "/usr/share/icons/hicolor/256x256/apps/spotlight-linux.png" ]; then
    rm -f /usr/share/icons/hicolor/256x256/apps/spotlight-linux.png
    echo "✅ Icono del tema eliminado"
fi

echo "🔄 Actualizando cache de aplicaciones..."

# Actualizar cache de aplicaciones
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database /usr/share/applications
fi

if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

echo ""
echo "✅ Spotlight Linux desinstalado exitosamente!"
echo ""
echo "📋 Recuerda eliminar manualmente:"
echo "   - Atajos de teclado configurados en el sistema"
echo "   - Configuraciones personales en ~/.config/spotlight-linux (si existen)"
