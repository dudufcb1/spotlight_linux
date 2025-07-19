# 🔍 Spotlight Linux - MVP IA

Una herramienta de consulta IA inteligente para Linux inspirada en macOS Spotlight, construida con PyQt6 y Gemini AI.

## 🚀 Instalación Rápida

### Opción 1: Ejecutable Precompilado (Recomendado)
```bash
# Descargar el ejecutable autocontenido
# [Próximamente: enlace de descarga]

# Ejecutar directamente (sin instalación)
chmod +x spotlight-linux
./spotlight-linux
```

### Opción 2: Compilar desde Código Fuente
```bash
git clone <repository-url>
cd spotlight_linux
./install.sh      # Instalar dependencias
./build.sh        # Crear ejecutable empaquetado
./dist/spotlight-linux  # Ejecutar
```

## 📋 Requisitos del Sistema

- **Para ejecutable:** Linux x86_64 (cualquier distribución moderna)
- **Para compilar:** Python 3.8+, entorno de escritorio con X11/Wayland

## 🎯 Funcionalidades

### ✅ Fase 2 Completada - Búsqueda Real de Archivos + Fase 1
- Ventana flotante con diseño moderno y tema oscuro
- **Búsqueda real de archivos en el sistema**
- **Indexación de directorios comunes (Escritorio, Documentos, etc.)**
- **Categorización automática por tipo (documentos, imágenes, etc.)**
- **Ejecución de archivos y carpetas con aplicaciones por defecto**
- Lista de resultados con navegación por teclado
- Atajos de teclado (Escape para cerrar, Enter para ejecutar)
- **Ejecutable autocontenido sin dependencias externas**
- **Distribución AppImage lista para implementar**

### 🔄 Próximas Fases
- **Fase 3:** Ejecución avanzada (aplicaciones del sistema, comandos)
- **Fase 4:** Búsqueda fuzzy avanzada + ranking inteligente
- **Fase 5:** Hotkeys globales (Ctrl+Espacio) + optimización final

## 🖥️ Uso

### Ejecutable Empaquetado
```bash
./dist/spotlight-linux
```

### Desde Código Fuente
```bash
source venv/bin/activate
python3 main.py
```

### Controles
- `Escape`: Cerrar ventana
- `Enter`: Ejecutar elemento seleccionado
- `↑/↓`: Navegar por resultados

## 📦 Distribución y Empaquetado

### Ejecutable Autocontenido ✅
- **Archivo:** `dist/spotlight-linux` (~ 80MB)
- **Dependencias:** Cero - todo incluido con PyInstaller
- **Portabilidad:** Funciona en cualquier Linux x86_64

### AppImage (Preparado)
```bash
# Descargar herramienta AppImage
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Crear AppImage desde estructura preparada
./appimagetool-x86_64.AppImage AppDir spotlight-linux.AppImage

# Distribuir archivo único
./spotlight-linux.AppImage
```

## 🏗️ Arquitectura

```
spotlight_linux/
├── main.py              # Aplicación principal PyQt6
├── spotlight.spec       # Configuración PyInstaller  
├── build.sh            # Script de build automatizado
├── requirements.txt     # Dependencias desarrollo
├── install.sh          # Setup entorno desarrollo
├── dist/               # Ejecutable empaquetado
│   └── spotlight-linux # ← Ejecutable autocontenido
├── AppDir/             # Estructura AppImage preparada
└── README.md           # Esta documentación
```

## 🔧 Desarrollo

### Flujo de Trabajo
1. **Desarrollo** - Editar `main.py` y otros archivos
2. **Testing** - `python3 main.py` en entorno virtual
3. **Build** - `./build.sh` para crear ejecutable empaquetado
4. **Distribución** - Compartir `dist/spotlight-linux` o crear AppImage

### Build Automatizado
El script `build.sh` realiza:
- Limpieza de builds anteriores
- Empaquetado con PyInstaller
- Creación de estructura AppDir
- Verificación de integridad

## 🎨 Características de Diseño

- Tema oscuro profesional (#2b2b2b)
- Ventana frameless con bordes redondeados
- Tipografía Inter para mejor legibilidad  
- Efectos de hover y selección suaves
- Posicionamiento automático centrado

## 📈 Estado del Proyecto

**Versión actual:** 0.3.0 (Fases 1 + 2 completadas)

- [x] Interfaz gráfica funcional
- [x] **Búsqueda real de archivos del sistema**
- [x] **Indexación de directorios comunes** 
- [x] **Categorización automática por tipo**
- [x] **Ejecución de archivos y carpetas**
- [x] Navegación por teclado completa
- [x] Diseño responsivo y moderno
- [x] **Ejecutable autocontenido sin dependencias**
- [x] **Estructura AppImage preparada** 
- [ ] Búsqueda fuzzy avanzada (Fase 4)
- [ ] Hotkeys globales (Ctrl+Espacio)
- [ ] Integración completa con sistema

## 🚀 Ventajas del Empaquetado Actual

### ✅ Problema Resuelto: Dependencias
- **Antes:** Requería `sudo apt install libxcb-cursor0` 
- **Ahora:** Cero dependencias externas
- **Resultado:** Distribución universal de un solo archivo

### ✅ Portabilidad Total
- Funciona en Ubuntu, Debian, Fedora, Arch, etc.
- No requiere Python instalado en sistema destino
- No requiere PyQt6 instalado en sistema destino

### ✅ Experiencia Usuario
- **Descarga:** Un archivo (~80MB)
- **Instalación:** Ninguna (chmod +x)
- **Ejecución:** Inmediata
