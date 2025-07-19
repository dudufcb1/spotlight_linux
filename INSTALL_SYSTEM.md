# 🚀 Instalación del Sistema - Spotlight Linux

Esta guía te ayudará a instalar Spotlight Linux como una aplicación nativa del sistema, permitiendo configurar atajos de teclado globales desde la configuración de Linux.

## 📋 Requisitos Previos

- Linux con entorno de escritorio (GNOME, KDE, XFCE, etc.)
- Permisos de administrador (sudo)
- Ejecutable compilado (`dist/spotlight-linux`)

## 🔧 Instalación Automática

### 1. Compilar la aplicación (si no está compilada)
```bash
./build.sh
```

### 2. Instalar en el sistema
```bash
sudo ./install_system.sh
```

Este script:
- ✅ Copia el ejecutable a `/usr/local/bin/`
- ✅ Instala el archivo `.desktop` en `/usr/share/applications/`
- ✅ Crea iconos del sistema
- ✅ Actualiza el cache de aplicaciones

## ⌨️ Configurar Atajos de Teclado

### GNOME (Ubuntu, Fedora, etc.)
1. Abre **Configuración** → **Teclado** → **Atajos de teclado**
2. Desplázate hasta **Atajos personalizados**
3. Haz clic en **+** para añadir un nuevo atajo
4. Configura:
   - **Nombre**: `Spotlight Linux`
   - **Comando**: `/usr/local/bin/spotlight-linux --show`
   - **Atajo**: `Ctrl+P` (o el que prefieras)

### KDE Plasma
1. Abre **Configuración del sistema** → **Atajos**
2. Ve a **Atajos personalizados**
3. Haz clic en **Editar** → **Nuevo** → **Comando/URL global**
4. Configura:
   - **Nombre**: `Spotlight Linux`
   - **Comando**: `/usr/local/bin/spotlight-linux --show`
   - **Atajo**: `Ctrl+P`

### XFCE
1. Abre **Configuración** → **Teclado** → **Atajos de aplicación**
2. Haz clic en **Añadir**
3. Configura:
   - **Comando**: `/usr/local/bin/spotlight-linux --show`
   - **Atajo**: `Ctrl+P`

## 🎯 Uso

### Métodos de ejecución:
1. **Atajo de teclado**: `Ctrl+P` (configurado)
2. **Menú de aplicaciones**: Busca "Spotlight Linux"
3. **Terminal**: `spotlight-linux`
4. **Mostrar directamente**: `spotlight-linux --show`

### Controles:
- **Enter**: Consultar IA
- **Escape**: Ocultar ventana
- **Ctrl+P**: Mostrar ventana (global)

## 🗑️ Desinstalación

```bash
sudo ./uninstall_system.sh
```

Recuerda eliminar manualmente los atajos de teclado configurados.

## 🔧 Solución de Problemas

### El atajo Ctrl+P no funciona
1. Verifica que el comando esté correcto: `/usr/local/bin/spotlight-linux --show`
2. Prueba el comando desde terminal
3. Asegúrate de que no haya conflictos con otros atajos
4. Reinicia la sesión de escritorio

### La aplicación no aparece en el menú
1. Ejecuta: `sudo update-desktop-database /usr/share/applications`
2. Cierra sesión y vuelve a entrar
3. Verifica que el archivo existe: `/usr/share/applications/spotlight-linux.desktop`

### Problemas de permisos
1. Verifica que el ejecutable tenga permisos: `ls -la /usr/local/bin/spotlight-linux`
2. Si es necesario: `sudo chmod +x /usr/local/bin/spotlight-linux`

## 📁 Archivos Instalados

- `/usr/local/bin/spotlight-linux` - Ejecutable principal
- `/usr/share/applications/spotlight-linux.desktop` - Archivo de aplicación
- `/usr/share/pixmaps/spotlight-linux.svg` - Icono SVG
- `/usr/share/pixmaps/spotlight-linux.png` - Icono PNG
- `/usr/share/icons/hicolor/256x256/apps/spotlight-linux.png` - Icono del tema
