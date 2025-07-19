<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# Herramienta AI Spotlight para Linux: Guía Completa de Implementación

Crear una herramienta tipo Spotlight que consulte IA en lugar de buscar archivos es un proyecto fascinante que combina múltiples tecnologías modernas. Te explico cómo implementarlo paso a paso usando Python, PyQt6, y la API de Gemini.

## Arquitectura del Sistema

La aplicación se estructura en cuatro módulos principales que trabajan de forma coordinada para proporcionar una experiencia fluida similar a Spotlight de macOS.

![Arquitectura de la aplicación AI Spotlight - Componentes principales y flujo de datos](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/61d0ec8e048c7b18e05f7c7bc77dbd17/9f644709-4af4-4166-aae9-5308b6b93255/225738a0.png)

Arquitectura de la aplicación AI Spotlight - Componentes principales y flujo de datos

## Componentes Técnicos Principales

### 1. Framework GUI: PyQt6 vs Alternativas

Para evitar el aspecto anticuado de tkinter, **PyQt6** es la mejor opción disponible. Ofrece componentes modernos, soporte nativo para markdown, y capacidades de estilizado avanzadas.

![Comparación de librerías GUI de Python - Facilidad de uso, apariencia moderna y funcionalidades avanzadas](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/61d0ec8e048c7b18e05f7c7bc77dbd17/232b518a-0239-4520-ac09-4977587fcaab/bcd3edb9.png)

Comparación de librerías GUI de Python - Facilidad de uso, apariencia moderna y funcionalidades avanzadas

PyQt6 destaca por:

- **Funcionalidades avanzadas** (10/10): Soporte completo para markdown, efectos visuales, animaciones
- **Apariencia moderna** (9/10): Widgets con aspecto nativo y capacidades de personalización
- **Facilidad de uso** (7/10): Curva de aprendizaje moderada pero bien documentada


### 2. Atajos Globales con pynput

Para detectar Ctrl+Espacio globalmente, usamos **pynput**, que funciona excelentemente en Linux:

```python
from pynput import keyboard

class HotKeyManager:
    def __init__(self, window):
        self.window = window
        self.current_keys = set()
        
    def on_press(self, key):
        self.current_keys.add(key)
        
        # Detectar Ctrl+Espacio
        if (keyboard.Key.ctrl_l in self.current_keys or 
            keyboard.Key.ctrl_r in self.current_keys) and \
           keyboard.Key.space in self.current_keys:
            self.toggle_window()
```


### 3. Renderizado de Markdown

PyQt6 incluye soporte nativo para markdown através de `QTextDocument`:

```python
from PyQt6.QtGui import QTextDocument

# Configurar documento markdown
self.markdown_doc = QTextDocument()
self.result_area.setDocument(self.markdown_doc)

# Renderizar respuesta de Gemini
self.markdown_doc.setMarkdown(gemini_response)
```


### 4. Integración con Gemini API

Adaptando tu boilerplate para funcionar de forma asíncrona:

```python
from PyQt6.QtCore import QThread, pyqtSignal
from google import genai
from google.genai import types

class AIQueryThread(QThread):
    response_ready = pyqtSignal(str)
    
    def __init__(self, query_text):
        super().__init__()
        self.query_text = query_text
        
    def run(self):
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        
        model = "gemini-2.5-flash"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=self.query_text)],
            ),
        ]
        
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            response_mime_type="text/plain",
        )
        
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
            response_text += chunk.text
            
        self.response_ready.emit(response_text)
```


## Flujo de Trabajo de la Aplicación

El proceso completo sigue estos pasos secuenciales:

![Flujo de trabajo de la aplicación AI Spotlight desde la activación hasta la respuesta](https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/61d0ec8e048c7b18e05f7c7bc77dbd17/03361662-49c1-4e5e-889e-09c63dbfbab1/f5f79c5f.png)

Flujo de trabajo de la aplicación AI Spotlight desde la activación hasta la respuesta

## Implementación de la Ventana Principal

### Configuración de Ventana Tipo Spotlight

```python
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGraphicsDropShadowEffect, QColor

class SpotlightWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_window_properties()
        
    def setup_window_properties(self):
        # Ventana sin marco y siempre encima
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint
        )
        
        # Tamaño fijo tipo Spotlight
        self.setFixedSize(800, 600)
        
        # Efecto de sombra para aspecto moderno
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Centrar en pantalla
        self.center_window()
```


### Estilos Modernos Tipo iOS

Para conseguir un aspecto similar a iOS, aplicamos CSS personalizado:

```python
def apply_ios_style(self):
    self.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
            border-radius: 15px;
        }
        
        QLineEdit {
            padding: 15px;
            border: 2px solid #3498db;
            border-radius: 10px;
            background-color: #ffffff;
            font-family: 'Inter', 'SF Pro Display', sans-serif;
            font-size: 16px;
            font-weight: 500;
        }
        
        QLineEdit:focus {
            border: 2px solid #2980b9;
            background-color: #f8f9fa;
        }
        
        QPushButton {
            padding: 12px 24px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QTextEdit {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            background-color: #ffffff;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            line-height: 1.6;
        }
    """)
```


## Interfaz de Usuario Moderna

El diseño final combina elementos visuales limpios con funcionalidad intuitiva:

![Mockup de interfaz de la aplicación AI Spotlight con diseño moderno](https://user-gen-media-assets.s3.amazonaws.com/gpt4o_images/329cee3e-5714-407c-a454-af20cc573d0f.png)

Mockup de interfaz de la aplicación AI Spotlight con diseño moderno

## Instalación y Configuración

### Dependencias del Sistema

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y python3-pyqt6 python3-dev

# Permisos para atajos globales
sudo usermod -a -G input $USER
```


### Dependencias de Python

```bash
# Crear entorno virtual
python3 -m venv spotlight_env
source spotlight_env/bin/activate

# Instalar librerías
pip install PyQt6 pynput google-genai
pip install qdarkstyle pyqtdarktheme  # Para temas modernos opcionales
```


### Configuración de API

```bash
# Configurar API key de Gemini
export GEMINI_API_KEY="tu-api-key-aquí"
echo 'export GEMINI_API_KEY="tu-api-key"' >> ~/.bashrc
```


## Ejemplo de Código Completo

He creado un ejemplo funcional que integra todos estos componentes. El código incluye:

- **Gestión de atajos globales** con pynput
- **Interfaz moderna** con PyQt6 y estilos CSS
- **Procesamiento asíncrono** de consultas IA
- **Renderizado de markdown** nativo
- **Animaciones suaves** de entrada/salida


### Características Implementadas

- ✅ Activación con **Ctrl+Espacio**
- ✅ Ventana **siempre encima** sin marco
- ✅ **Cierre con Escape** o X
- ✅ **Renderizado de markdown** completo
- ✅ **Estilos modernos** tipo iOS
- ✅ **Procesamiento asíncrono** sin bloqueos
- ✅ **Efectos visuales** (sombras, animaciones)


## Consejos de Optimización

### Performance

- Usa `QThread` para consultas IA para evitar bloqueos
- Implementa caché de respuestas para consultas frecuentes
- Limita el historial de conversaciones


### Experiencia de Usuario

- Agrega indicadores de carga durante procesamiento
- Implementa autocompletado en el campo de búsqueda
- Permite copiar resultados con Ctrl+C


### Personalización

- Crea temas claros/oscuros intercambiables
- Permite ajustar tamaños de fuente
- Configura atajos personalizables


## Extensiones Futuras

### Funcionalidades Avanzadas

- **Historial de consultas** navegable
- **Comandos especiales** (ej: `/weather`, `/translate`)
- **Plugins personalizables** para diferentes IAs
- **Modo conversacional** con contexto


### Integración del Sistema

- **Notificaciones nativas** de Linux
- **Integración con clipboard** automática
- **Búsqueda en archivos locales** combinada con IA

Esta implementación te proporciona una base sólida para crear tu herramienta AI Spotlight personalizada. El código es modular y extensible, permitiendo agregar nuevas funcionalidades según tus necesidades específicas.

<div style="text-align: center">⁂</div>

[^1_1]: https://www.pythonguis.com/faq/which-python-gui-library/

[^1_2]: https://dev.to/codeitbro/10-best-python-gui-libraries-elevate-your-user-interfaces-2hdm

[^1_3]: https://blog.csdn.net/CaptainTakuya/article/details/113631112

[^1_4]: https://dev.to/codesharedot/best-python-framework-for-building-a-desktop-application-and-gui-58n5

[^1_5]: https://python.libhunt.com/tkinter-alternatives

[^1_6]: https://www.geeksforgeeks.org/python/python3-gui-application-overview/

[^1_7]: https://dev.to/amigosmaker/python-gui-pyqt-vs-tkinter-5hdd

[^1_8]: https://blog.udemy.com/python-gui/

[^1_9]: https://www.reddit.com/r/learnpython/comments/1h2w2zz/are_there_any_alternatives_to_tkinter_where_im/

[^1_10]: https://www.netguru.com/blog/python-gui-libraries

[^1_11]: https://dev.to/abpanic/tkinter-vs-pyqt-choosing-the-right-gui-library-for-your-python-projects-1oj0

[^1_12]: https://www.reddit.com/r/Python/comments/oauw9w/which_python_framework_is_used_by_professional_to/

[^1_13]: https://fullscale.io/blog/python-gui-frameworks/

[^1_14]: https://www.reddit.com/r/Python/comments/wedvzi/what_is_the_best_gui_library_for_python/

[^1_15]: https://blog.51cto.com/u_16123336/11673464

[^1_16]: https://discuss.python.org/t/gui-toolkits-for-desktop-development/58342

[^1_17]: https://python.plainenglish.io/exploring-python-gui-frameworks-in-2025-alternatives-to-pyqt-2a2d130260c7

[^1_18]: https://www.bairesdev.com/blog/best-python-gui-libraries/

[^1_19]: https://www.pythonguis.com/faq/pyqt-vs-tkinter/

[^1_20]: https://kivy.org

[^1_21]: https://stackoverflow.com/questions/1925015/pyqt-always-on-top

[^1_22]: https://askubuntu.com/questions/229129/python-global-hotkey

[^1_23]: https://github.com/btsdev/global_hotkeys

[^1_24]: https://github.com/mchobby/pynput-sample

[^1_25]: https://stackoverflow.com/questions/32801671/splash-window-and-always-on-top-at-the-same-time-in-pyqt4/32802518

[^1_26]: https://stackoverflow.com/questions/17937815/python-global-hotkey-hook-module-for-linux

[^1_27]: https://www.geeksforgeeks.org/how-to-create-a-hotkey-in-python/

[^1_28]: https://pypi.org/project/pynput/

[^1_29]: https://forum.qt.io/topic/127517/how-to-make-qpainter-elements-clickable-through-using-pyqt

[^1_30]: https://www.youtube.com/watch?v=m92CnVlFp3Y

[^1_31]: https://pypi.org/project/global-hotkeys/

[^1_32]: https://stackoverflow.com/questions/71828671/how-do-i-use-pynput-in-linux-or-is-pynput-not-working-on-linux

[^1_33]: https://riverbankcomputing.com/pipermail/pyqt/2010-January/025523.html

[^1_34]: https://pypi.org/project/keyboard/

[^1_35]: https://stackoverflow.com/questions/3337973/set-global-hotkey-with-python-2-6/3345475

[^1_36]: https://pynput.readthedocs.io/en/latest/keyboard.html

[^1_37]: https://www.riverbankcomputing.com/pipermail/pyqt/2020-July/043058.html

[^1_38]: https://libraries.io/pypi/python-hotkeys

[^1_39]: https://help.autodesk.com/view/MOBPRO/2025/ENU/?guid=GUID-2040874E-3526-4FCD-9012-8F4C29CB8E37

[^1_40]: https://nitratine.net/blog/post/how-to-make-hotkeys-in-python/

[^1_41]: https://stackoverflow.com/questions/66066115/render-markdown-with-pyqt5

[^1_42]: https://thepythoncode.com/article/markdown-editor-with-tkinter-in-python

[^1_43]: https://github.com/Qt-Widgets/qt-markdown-textedit

[^1_44]: https://qt.developpez.com/doc/6.4/qtquickcontrols2-ios/

[^1_45]: https://www.youtube.com/watch?v=DwmNANM7FAs

[^1_46]: https://shiny.posit.co/py/api/core/ui.markdown.html

[^1_47]: https://blog.csdn.net/gitblog_01236/article/details/143045772

[^1_48]: https://forum.qt.io/topic/76620/can-we-use-ios-native-style-for-qt-applications

[^1_49]: https://python-forum.io/thread-43468.html

[^1_50]: https://dev.to/taipy/enhancing-python-guis-with-augmented-markdown-477g

[^1_51]: https://www.youtube.com/watch?v=zVqDebsIBUM

[^1_52]: https://pythonbasics.org/pyqt-style/

[^1_53]: https://github.com/tanthehack/noted

[^1_54]: https://panel.holoviz.org/reference/panes/Markdown.html

[^1_55]: https://github.com/pbek/qmarkdowntextedit/blob/develop/README.md

[^1_56]: https://pypi.org/project/qtstylish/

[^1_57]: https://raymii.org/s/snippets/QML_Render_Markdown_in_Text.html

[^1_58]: https://stackoverflow.com/questions/77413562/how-to-display-markdown-content-in-a-popup-dialog-in-a-python-script-using-ipywi

[^1_59]: https://www.youtube.com/watch?v=zDfxM6vcuEo

[^1_60]: https://doc.qt.io/qtforpython-6/overviews/qtquickcontrols-ios.html

[^1_61]: https://github.com/gmarull/qtmodern

[^1_62]: https://blog.csdn.net/seniorwizard/article/details/111199155

[^1_63]: https://learn.microsoft.com/zh-tw/dotnet/api/system.windows.media.media3d.spotlight.clone?view=windowsdesktop-8.0

[^1_64]: https://developers.google.com/youtube/cobalt/docs/gen/starboard/tools/doc/abstract_launcher

[^1_65]: https://www.youtube.com/watch?v=fTWM_5H2Beo

[^1_66]: https://blog.csdn.net/weixin_39831567/article/details/110980375

[^1_67]: https://hub.jmonkeyengine.org/t/what-is-the-expected-meaning-of-light-clone/35100

[^1_68]: https://github.com/Nstamour-art/Python_Script_Launcher

[^1_69]: https://pypi.org/project/pyqtdarktheme/

[^1_70]: https://github.com/ColinDuquesnoy/QDarkStyleSheet

[^1_71]: https://wiki.reallusion.com/IC_Python_API:RLPy_RISpotLight

[^1_72]: https://github.com/vbokser/Python_App_Launcher

[^1_73]: https://www.reddit.com/r/learnpython/comments/rbn83y/modern_looking_gui/

[^1_74]: https://qdarkstylesheet.readthedocs.io/en/latest/reference/qdarkstyle.html

[^1_75]: https://learn.microsoft.com/nl-nl/dotnet/api/system.windows.media.media3d.spotlight.clonecurrentvalue?view=netframework-4.8.1

[^1_76]: https://pypi.org/project/python-embedded-launcher/0.10/

[^1_77]: https://github.com/5yutan5/PyQtDarkTheme

[^1_78]: https://pypi.org/project/QDarkStyle/

[^1_79]: https://github.com/maciejkula/spotlight

[^1_80]: https://github.com/travyyx/pylauncher

[^1_81]: https://doc.qt.io/qt-6/qtextdocument.html

[^1_82]: https://github.com/yhfyhf/Markdown-Parser-Python

[^1_83]: https://doc.qt.io/qtforpython-6/examples/example_widgets_effects_lighting.html

[^1_84]: https://phaedrusdeinus.org/2024/05/30/click-to-edit-in-pyqt6.html

[^1_85]: https://github.com/mib112/executablebooks-markdown-it-py

[^1_86]: https://stuff.mit.edu/afs/athena.mit.edu/software/texmaker_v5.0.2/qt57/doc/qtwebengine/qtwebengine-webenginewidgets-markdowneditor-example.html

[^1_87]: https://www.w3resource.com/python-exercises/pyqt/python-pyqt-basic-exercise-2.php

[^1_88]: https://doc.qt.io/qtforpython-6/PySide6/QtGui/QTextDocument.html

[^1_89]: https://pypi.org/project/marko/

[^1_90]: https://doc.qt.io/qt-5/qtwebengine-webenginewidgets-markdowneditor-example.html

[^1_91]: https://www.youtube.com/watch?v=V482dnqiNqc

[^1_92]: https://stackoverflow.com/questions/78389884/how-can-i-make-a-feature-using-python-pyqt6-that-is-able-to-both-take-markdown-i

[^1_93]: https://marko-py.readthedocs.io

[^1_94]: https://cloud.tencent.com/developer/article/1530190

[^1_95]: https://www.pythonguis.com/tutorials/creating-your-first-pyqt-window/

[^1_96]: https://doc-snapshots.qt.io/qtforpython-6.5/PySide6/QtGui/QTextDocumentFragment.html

[^1_97]: https://libraries.io/pypi/mrkdwn-analysis

[^1_98]: https://github.com/hellojudger/QMarkdownView

[^1_99]: https://www.pythonguis.com/tutorials/pyqt6-creating-your-first-window/

