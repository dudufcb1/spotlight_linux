# 🔍 Spotlight Linux - AI Search Tool

Una herramienta de consulta IA inteligente para Linux inspirada en macOS Spotlight, construida con PyQt6 y Google Gemini AI.

## ✨ Características Principales

- 🤖 **IA Conversacional**: Integración completa con Google Gemini AI
- 🔍 **Búsqueda Inteligente**: Archivos, aplicaciones y comandos del sistema
- ⚡ **Hotkeys Globales**: Ctrl+Alt+Space para acceso instantáneo
- 🎨 **Interfaz Moderna**: Diseño dark theme estilo macOS Spotlight
- 🔒 **Instancia Única**: Sistema de candado para evitar duplicidad
- ⚙️ **Personalización**: Configuración de usuario, tono y preferencias
- 🐧 **Contexto del Sistema**: Detección automática de distribución Linux

## 🚀 Instalación Rápida

### Instalación Automática (Recomendado)
```bash
# Clonar repositorio
git clone <repository-url>
cd spotlight_linux

# Instalación automática con script
chmod +x install_system.sh
./install_system.sh

# Ejecutar
python main.py
```

### Instalación Manual
```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

## 📋 Requisitos del Sistema

### Mínimos
- **OS**: Linux (cualquier distribución moderna)
- **Python**: 3.8+ (para ejecución desde código fuente)
- **Desktop**: X11 o Wayland
- **RAM**: 512MB disponible
- **Espacio**: 100MB para instalación

### Dependencias
- PyQt6 >= 6.6.0
- google-genai >= 0.3.0
- pynput >= 1.7.6 (hotkeys globales)
- psutil >= 5.9.0

## 🎯 Funcionalidades Completas

### 🤖 Motor de IA
- **Integración Gemini AI**: Consultas inteligentes con contexto
- **Personalización**: Nombre de usuario y tono configurable
- **Contexto del Sistema**: Detección automática de distribución Linux
- **Modos de Respuesta**: Grounding (búsqueda web) y estructurado (comandos/código)
- **Snippets Dinámicos**: Comandos y código sugeridos integrados

### 🔍 Búsqueda Avanzada
- **Archivos del Sistema**: Indexación inteligente de directorios
- **Aplicaciones**: Búsqueda de aplicaciones instaladas
- **Comandos Integrados**: Accesos directos del sistema
- **Categorización**: Automática por tipo de archivo
- **Ejecución**: Apertura con aplicaciones por defecto

### ⚡ Interfaz y UX
- **Hotkeys Globales**: Ctrl+Alt+Space para acceso instantáneo
- **Ventana Flotante**: Diseño moderno estilo macOS Spotlight
- **Dark Theme**: Interfaz oscura optimizada
- **Instancia Única**: Sistema de candado anti-duplicidad
- **Configuración**: Panel de preferencias completo

### 🔧 Sistema
- **Auto-instalación**: Script automatizado de dependencias
- **Configuración Segura**: Encriptación de API keys
- **Logging**: Sistema de debug y monitoreo
- **Memoria Conversacional**: Historial de interacciones

## 🖥️ Uso

### Primera Ejecución
```bash
# Ejecutar aplicación
python main.py

# Configurar en primera ejecución:
# 1. Hacer clic en ⚙️ (esquina superior derecha)
# 2. Ingresar nombre y API key de Gemini
# 3. Seleccionar tono de respuesta
```

### Controles Principales
- **Ctrl+Alt+Space**: Mostrar ventana (global)
- **Escape**: Cerrar ventana
- **Enter**: Consultar IA / Ejecutar elemento
- **↑/↓**: Navegar por resultados
- **⚙️**: Abrir preferencias

### Modos de Uso
1. **Consulta IA**: Escribir pregunta y presionar Enter
2. **Búsqueda de Archivos**: Escribir nombre de archivo
3. **Comandos del Sistema**: Usar comandos integrados

## 🏗️ Arquitectura del Proyecto

```
spotlight_linux/
├── 📁 Core Application
│   ├── main.py                 # Aplicación principal PyQt6 + UI
│   ├── ai_engine.py           # Motor de IA con Gemini
│   ├── search_engine.py       # Búsqueda de archivos/apps
│   ├── config.py              # Gestión de configuración
│   └── preferences.py         # Panel de preferencias
├── 📁 Data & Models
│   ├── data_models.py         # Modelos de datos
│   ├── app_parser.py          # Parser de aplicaciones
│   └── integrated_commands.py # Comandos del sistema
├── 📁 Installation & Config
│   ├── install_system.sh      # Instalador automático
│   ├── uninstall_system.sh    # Desinstalador
│   ├── requirements.txt       # Dependencias Python
│   └── spotlight.spec         # Configuración PyInstaller
├── 📁 Distribution
│   ├── AppDir/                # Estructura AppImage
│   ├── dist/                  # Ejecutables compilados
│   └── spotlight-linux.desktop # Archivo desktop
└── 📁 Documentation
    ├── README.md              # Esta documentación
    ├── docs/memory/           # Memoria del proyecto
    └── tools/                 # Herramientas de desarrollo
```

## 🔧 Solución de Problemas

### Error de Clave GPG de Microsoft (VS Code)
Si encuentras este error durante la instalación:
```
W: Error de GPG: https://packages.microsoft.com/repos/code stable InRelease:
Las firmas siguientes no se pudieron verificar porque su clave pública no está disponible:
NO_PUBKEY EB3E94ADBE1229CF
```

**Solución:**
```bash
# Descargar e instalar la clave GPG de Microsoft
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'

# Actualizar repositorios
sudo apt update

# Ahora instalar VS Code funcionará
sudo apt install code
```

### Problemas Comunes

#### 1. Error de Importación PyQt6
```bash
# Instalar PyQt6 manualmente
pip install PyQt6>=6.6.0
```

#### 2. Hotkeys Globales No Funcionan
```bash
# Instalar pynput
pip install pynput>=1.7.6

# Verificar permisos de accesibilidad en el sistema
```

#### 3. Error de API Key Gemini
1. Obtener API key en: https://makersuite.google.com/app/apikey
2. Configurar en Preferencias (⚙️)
3. Verificar que la key sea válida

#### 4. Múltiples Instancias
Si aparece el mensaje "Ya está ejecutándose":
- Usar **Ctrl+Alt+Space** para mostrar la ventana existente
- O terminar proceso: `pkill -f spotlight-linux`

## 🔧 Desarrollo

### Configuración del Entorno
```bash
# Clonar repositorio
git clone <repository-url>
cd spotlight_linux

# Configurar entorno automáticamente
./install_system.sh

# O manualmente:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Flujo de Desarrollo
1. **Desarrollo**: Editar archivos core (main.py, ai_engine.py, etc.)
2. **Testing**: `python main.py` para probar cambios
3. **Debugging**: Logs automáticos en archivos .log
4. **Distribución**: Usar `install_system.sh` para deployment

### Estructura de Archivos Core
```python
# Archivos principales - NO ELIMINAR
main.py              # Aplicación principal + UI + sistema de lock
ai_engine.py         # Motor de IA con Gemini + personalización
search_engine.py     # Búsqueda de archivos y aplicaciones
config.py            # Gestión de configuración + encriptación
preferences.py       # Panel de preferencias + validación
app_parser.py        # Parser de aplicaciones .desktop
data_models.py       # Modelos de datos y estructuras
integrated_commands.py # Comandos integrados del sistema
```

## 🎨 Características de Diseño

### Interfaz
- **Dark Theme**: Tema oscuro profesional (#2b2b2b)
- **Ventana Flotante**: Frameless con bordes redondeados
- **Tipografía**: Inter para mejor legibilidad
- **Efectos**: Hover y selección suaves
- **Responsive**: Adaptable a diferentes tamaños

### UX/UI
- **Snippets Dinámicos**: Comandos y código integrados en respuesta
- **Personalización**: Nombre de usuario y tono en prompts
- **Contexto Inteligente**: Detección automática del sistema operativo
- **Instancia Única**: Sistema de candado con alert informativo

## 📈 Estado del Proyecto

**Versión actual:** 1.0.0 - **COMPLETO**

### ✅ Funcionalidades Implementadas
- [x] **Motor de IA Completo**: Integración Gemini con personalización
- [x] **Búsqueda Avanzada**: Archivos, aplicaciones y comandos
- [x] **Hotkeys Globales**: Ctrl+Alt+Space funcionando
- [x] **Interfaz Moderna**: Dark theme estilo macOS Spotlight
- [x] **Sistema de Configuración**: Panel completo con encriptación
- [x] **Instancia Única**: Sistema de candado anti-duplicidad
- [x] **Contexto del Sistema**: Detección automática de distribución
- [x] **Snippets Dinámicos**: Comandos y código integrados
- [x] **Memoria Conversacional**: Historial de interacciones
- [x] **Instalación Automática**: Script completo de setup

### 🎯 Características Destacadas
- **Personalización Completa**: Nombre, tono y preferencias del usuario
- **IA Contextual**: Respuestas específicas para la distribución Linux detectada
- **UX Optimizada**: Snippets integrados sin botones innecesarios
- **Arquitectura Limpia**: Codebase optimizado y bien documentado

## 🚀 Distribución

### Instalación en Producción
```bash
# Instalación completa automática
./install_system.sh

# Desinstalación limpia
./uninstall_system.sh
```

### Características de Distribución
- **Instalación Automática**: Manejo completo de dependencias
- **Configuración Segura**: Encriptación de API keys
- **Sistema de Memoria**: Persistencia de configuración y conversaciones
- **Logs Estructurados**: Sistema de debugging y monitoreo
- **Limpieza Automática**: Desinstalación completa sin residuos

## 📚 Documentación

- **README.md**: Esta documentación completa
- **docs/memory/**: Memoria estructurada del desarrollo
- **tools/**: Herramientas de desarrollo y esquemas
- **Código**: Documentación inline en todos los módulos

## 🏆 Logros del Proyecto

### Técnicos
- ✅ Migración exitosa de SDK deprecado a nuevo Google GenAI
- ✅ Sistema de personalización completo con contexto del sistema
- ✅ UI optimizada con snippets dinámicos integrados
- ✅ Arquitectura de instancia única con UX excelente
- ✅ Codebase limpio y optimizado (50% de reducción)

### Funcionales
- ✅ Herramienta de IA completamente funcional para Linux
- ✅ Experiencia de usuario comparable a macOS Spotlight
- ✅ Sistema de configuración robusto y seguro
- ✅ Instalación y distribución automatizada
- ✅ Documentación completa y mantenible
