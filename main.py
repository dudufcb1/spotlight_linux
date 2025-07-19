#!/usr/bin/env python3
"""
Spotlight Linux - Interfaz PyQt6 estilo macOS Spotlight
"""

import sys
import os
import logging
import signal
import threading
import fcntl
import atexit
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QFrame, QTextEdit, QPushButton, QGroupBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QKeySequence, QShortcut, QClipboard

from ai_engine import ai_engine, AIResponse
from config import config_manager
from preferences import PreferencesDialog

try:
    from pynput import keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('spotlight_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Manejo de señales para Ctrl+C
def signal_handler(signum, frame):
    logger.info("Recibida señal de interrupción (Ctrl+C)")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class SingleInstanceLock:
    """Sistema de candado para evitar múltiples instancias"""

    def __init__(self, app_name="spotlight-linux"):
        self.app_name = app_name
        self.lock_file_path = Path.home() / ".config" / app_name / f"{app_name}.lock"
        self.lock_file = None
        self.is_locked = False

        # Asegurar que el directorio existe
        self.lock_file_path.parent.mkdir(parents=True, exist_ok=True)

    def acquire_lock(self) -> bool:
        """Intentar adquirir el lock. Retorna True si exitoso, False si ya hay otra instancia"""
        try:
            # Abrir archivo de lock
            self.lock_file = open(self.lock_file_path, 'w')

            # Intentar lock exclusivo no-bloqueante
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Escribir PID al archivo
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()

            self.is_locked = True

            # Registrar cleanup al salir
            atexit.register(self.release_lock)

            logger.info(f"Lock adquirido exitosamente: {self.lock_file_path}")
            return True

        except (IOError, OSError) as e:
            # Lock ya está en uso por otra instancia
            if self.lock_file:
                self.lock_file.close()
                self.lock_file = None

            logger.info(f"No se pudo adquirir lock - otra instancia ejecutándose: {e}")
            return False

    def release_lock(self):
        """Liberar el lock"""
        if self.is_locked and self.lock_file:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()

                # Eliminar archivo de lock
                if self.lock_file_path.exists():
                    self.lock_file_path.unlink()

                logger.info("Lock liberado exitosamente")
            except Exception as e:
                logger.warning(f"Error liberando lock: {e}")
            finally:
                self.is_locked = False
                self.lock_file = None

    def get_running_pid(self) -> int:
        """Obtener PID de la instancia que tiene el lock"""
        try:
            if self.lock_file_path.exists():
                with open(self.lock_file_path, 'r') as f:
                    return int(f.read().strip())
        except (ValueError, IOError):
            pass
        return 0

def show_already_running_alert():
    """Mostrar alert cuando ya hay una instancia ejecutándose"""
    app = QApplication(sys.argv)

    # Crear mensaje de alerta
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Spotlight Linux - Ya está ejecutándose")
    msg_box.setIcon(QMessageBox.Icon.Information)
    msg_box.setText("🔍 Spotlight Linux ya está ejecutándose")
    msg_box.setInformativeText(
        "Ya hay una instancia de Spotlight Linux activa en segundo plano.\n\n"
        "💡 Para mostrar la ventana, usa el atajo de teclado:\n"
        "   Ctrl+Alt+Space\n\n"
        "O presiona Ctrl+Alt+P desde cualquier lugar del sistema."
    )
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)

    # Configurar estilo del mensaje
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        }
        QMessageBox QLabel {
            color: #ffffff;
            font-size: 14px;
            padding: 10px;
        }
        QPushButton {
            background-color: #0078d4;
            border: 1px solid #106ebe;
            border-radius: 6px;
            color: white;
            font-weight: bold;
            padding: 8px 16px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #106ebe;
        }
        QPushButton:pressed {
            background-color: #005a9e;
        }
    """)

    # Mostrar el mensaje
    msg_box.exec()

    # Salir de la aplicación temporal
    app.quit()
    sys.exit(0)

class AIThread(QThread):
    """Thread para consultas IA sin bloquear la UI"""
    response_ready = pyqtSignal(object)  # Cambiar a object para pasar AIResponse completo
    error_occurred = pyqtSignal(str)

    def __init__(self, query, conversation_history=None):
        super().__init__()
        self.query = query
        self.conversation_history = conversation_history or []

    def run(self):
        """Ejecuta la consulta IA en background"""
        try:
            # Usar el ai_engine real con historial
            response = ai_engine.ask_sync(self.query, conversation_history=self.conversation_history)
            if response and response.success:
                self.response_ready.emit(response)  # Emitir objeto AIResponse completo
            else:
                error_msg = response.error_message if response else "No se recibió respuesta de la IA"
                self.error_occurred.emit(error_msg)
        except Exception as e:
            self.error_occurred.emit(f"Error al consultar IA: {str(e)}")

class SpotlightWindow(QMainWindow):
    """Ventana principal del Spotlight Linux con PyQt6"""
    
    def __init__(self):
        super().__init__()
        self.window_visible = False
        self.ai_thinking = False
        
        self.init_ui()
        self.setup_style()
        self.setup_global_hotkeys()

        # Verificar configuración inicial
        self.check_first_run()
        
        # Inicializar motor de IA con configuración actual
        self.initialize_ai_engine()
        
        # Cargar estado inicial del grounding
        self.load_grounding_state()

        # Ocultar ventana al inicio
        self.hide()
        
    def init_ui(self):
        """Inicializa la interfaz de usuario PyQt6"""
        # Configuración de la ventana
        self.setWindowTitle("Spotlight Linux")
        self.setFixedSize(700, 600)  # Incrementar altura para snippets
        
        # Configurar como ventana flotante sin decoraciones
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Centrar ventana
        self.center_window()
        
        # Crear widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header con icono de preferencias
        header_layout = QHBoxLayout()

        # Título
        title_label = QLabel("🔍 Spotlight Linux")
        title_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Botón escoba para limpiar contexto
        self.clear_context_button = QPushButton("🧹")
        self.clear_context_button.setFixedSize(32, 32)
        self.clear_context_button.setToolTip("Limpiar historial de conversación")
        self.clear_context_button.clicked.connect(self.clear_conversation_history)
        header_layout.addWidget(self.clear_context_button)

        # Icono de preferencias
        self.preferences_button = QPushButton("⚙️")
        self.preferences_button.setFixedSize(32, 32)
        self.preferences_button.setToolTip("Preferencias")
        self.preferences_button.clicked.connect(self.show_preferences)
        header_layout.addWidget(self.preferences_button)

        main_layout.addLayout(header_layout)
        
        # Campo de búsqueda/consulta IA con grounding toggle
        input_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.update_placeholder_text()
        self.search_input.setFont(QFont("Inter", 16))
        input_layout.addWidget(self.search_input)
        
        # Checkbox de grounding
        self.grounding_checkbox = QCheckBox("🌐")
        self.grounding_checkbox.setToolTip("Grounding: Habilitar búsqueda en línea\n\n✅ Activado: La IA puede buscar información en internet\n❌ Desactivado: La IA proporciona comandos y código estructurado")
        self.grounding_checkbox.setChecked(False)  # Unchecked por defecto
        self.grounding_checkbox.stateChanged.connect(self.on_grounding_changed)
        input_layout.addWidget(self.grounding_checkbox)
        
        main_layout.addLayout(input_layout)

        # Área de respuesta de IA con scroll y markdown
        self.response_area = QTextEdit()
        self.response_area.setFont(QFont("Inter", 12))
        self.response_area.setMinimumHeight(250)
        self.response_area.setReadOnly(True)
        self.response_area.setPlainText("Escribe tu consulta y presiona Enter...")
        main_layout.addWidget(self.response_area)

        # Los snippets ahora se generan dinámicamente dentro del response_area
        # No necesitamos un frame separado que siempre ocupe espacio

        # Label de estado con spinner
        self.status_label = QLabel("Listo para consultar IA")
        self.status_label.setFont(QFont("Inter", 10))
        main_layout.addWidget(self.status_label)

        # Timer para spinner
        self.spinner_timer = QTimer()
        self.spinner_timer.timeout.connect(self.update_spinner)
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0
        
        # Conectar eventos
        self.search_input.returnPressed.connect(self.on_enter_pressed)

        # Atajos de teclado
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.hide_window)

        # Shortcut Ctrl+Alt+Space para mostrar ventana
        show_shortcut = QShortcut(QKeySequence("Ctrl+Alt+Space"), self)
        show_shortcut.activated.connect(self.show_window)
        
    def setup_style(self):
        """Configura el estilo oscuro moderno"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1f2937;
                border-radius: 15px;
            }
            QLineEdit {
                padding: 15px;
                border: 2px solid #3b82f6;
                border-radius: 10px;
                background-color: #374151;
                color: white;
                font-size: 16px;
            }
            QLineEdit:focus {
                border-color: #60a5fa;
                background-color: #4b5563;
            }
            QTextEdit {
                color: #e5e7eb;
                padding: 10px;
                background-color: #374151;
                border-radius: 8px;
                border: 1px solid #4b5563;
                selection-background-color: #3b82f6;
            }
            QPushButton {
                background-color: #374151;
                border: 1px solid #4b5563;
                border-radius: 6px;
                color: #e5e7eb;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
                border-color: #6b7280;
            }
            QPushButton:pressed {
                background-color: #6b7280;
            }
            QLabel {
                color: #9ca3af;
                padding: 5px;
            }
        """)
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 700) // 2
        y = (screen.height() - 500) // 3
        self.move(x, y)
        
    def setup_global_hotkeys(self):
        """Configura atajos globales del sistema"""
        if HAS_PYNPUT:
            try:
                # Usar HotKey para Ctrl+Alt+Space (más específico, no interfiere)
                def show_spotlight():
                    self.show_window()

                # Configurar Ctrl+Alt+Space como hotkey global
                self.hotkey = keyboard.HotKey(
                    keyboard.HotKey.parse('<ctrl>+<alt>+<space>'),
                    show_spotlight
                )

                def for_canonical(f):
                    return lambda k: f(self.listener.canonical(k))

                # Listener para hotkeys globales
                self.listener = keyboard.Listener(
                    on_press=for_canonical(self.hotkey.press),
                    on_release=for_canonical(self.hotkey.release)
                )
                self.listener.start()
                logger.info("Hotkeys globales configurados: Ctrl+Alt+Space para mostrar")
            except Exception as e:
                logger.warning(f"No se pudieron configurar hotkeys globales: {e}")
        else:
            logger.warning("pynput no disponible - hotkeys globales deshabilitados")
            
    def toggle_window(self):
        """Alterna la visibilidad de la ventana"""
        if self.window_visible:
            self.hide_window()
        else:
            self.show_window()
            
    def show_window(self):
        """Muestra la ventana y enfoca el campo de búsqueda"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()
        self.search_input.selectAll()
        self.window_visible = True
        logger.info("Ventana mostrada")
        
    def hide_window(self):
        """Oculta la ventana"""
        self.hide()
        self.window_visible = False
        self.search_input.clear()
        self.response_area.setPlainText("Escribe tu consulta y presiona Enter...")
        self.status_label.setText("Listo para consultar IA")

        # Los snippets se limpian automáticamente al cambiar el HTML

        # Detener spinner si está activo
        if self.spinner_timer.isActive():
            self.spinner_timer.stop()
        logger.info("Ventana ocultada")
        
    def on_enter_pressed(self):
        """Maneja Enter para consultar IA directamente"""
        query = self.search_input.text().strip()
        if query:
            self.query_ai(query)
        else:
            self.status_label.setText("Escribe algo para consultar...")
        
    def query_ai(self, query):
        """Consulta a la IA con memoria conversacional"""
        # Agregar consulta del usuario al historial
        config_manager.add_conversation_message("Usuario", query)
        
        # Obtener historial para contexto
        conversation_history = config_manager.get_conversation_history()
        
        self.ai_thinking = True
        self.response_area.setPlainText("🤖 Consultando IA...")

        # Iniciar spinner
        self.spinner_index = 0
        self.spinner_timer.start(100)  # Actualizar cada 100ms

        # Crear thread para consulta IA real con historial
        self.ai_thread = AIThread(query, conversation_history)
        self.ai_thread.response_ready.connect(self.show_ai_response)
        self.ai_thread.error_occurred.connect(self.show_ai_error)
        self.ai_thread.start()

    def update_spinner(self):
        """Actualiza el spinner animado"""
        if self.ai_thinking:
            spinner_char = self.spinner_chars[self.spinner_index]
            self.status_label.setText(f"{spinner_char} Consultando IA...")
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)

    def _detect_markdown(self, text):
        """Detecta si el texto contiene markdown"""
        markdown_indicators = [
            '```', '**', '*', '##', '#', '- ', '1. ',
            '[', '](', '`', '>', '---', '***'
        ]
        return any(indicator in text for indicator in markdown_indicators)

    def show_ai_response(self, response):
        """Muestra respuesta de la IA y la guarda en memoria"""
        self.ai_thinking = False
        self.spinner_timer.stop()
        self.status_label.setText("✅ Respuesta recibida")

        # Guardar respuesta de IA en historial
        config_manager.add_conversation_message("IA", response.content)
        config_manager.save_config()

        # Construir respuesta completa con snippets integrados
        full_response = self.build_response_with_snippets(response)

        # Siempre usar HTML para tener control completo del formato
        self.response_area.setHtml(full_response)

        # Auto-ocultar después de un tiempo (opcional)
        # QTimer.singleShot(10000, self.hide_window)

    def build_response_with_snippets(self, response):
        """Construye la respuesta completa con snippets integrados dinámicamente"""
        # Comenzar con la respuesta base
        html_content = f"""
        <div style="font-family: 'Inter', sans-serif; color: #e5e7eb; line-height: 1.6;">
            <div style="margin-bottom: 20px;">
                <strong style="color: #60a5fa;">🤖 IA:</strong> {self.format_response_content(response.content)}
            </div>
        """

        # Agregar snippets si existen
        if response.is_structured and (response.suggested_commands or response.suggested_code_snippets):
            html_content += self.build_snippets_html(response.suggested_commands or [], response.suggested_code_snippets or [])

        html_content += "</div>"
        return html_content

    def format_response_content(self, content):
        """Formatea el contenido de la respuesta preservando markdown básico"""
        # Escapar HTML pero preservar algunos elementos markdown
        import html
        content = html.escape(content)

        # Convertir markdown básico a HTML
        content = content.replace('**', '<strong>').replace('**', '</strong>')
        content = content.replace('*', '<em>').replace('*', '</em>')
        content = content.replace('\n', '<br>')

        # Manejar bloques de código
        if '```' in content:
            parts = content.split('```')
            for i in range(1, len(parts), 2):  # Cada parte impar es código
                parts[i] = f'<pre style="background-color: #1f2937; padding: 10px; border-radius: 6px; margin: 10px 0; overflow-x: auto;"><code>{parts[i]}</code></pre>'
            content = ''.join(parts)

        return content

    def build_snippets_html(self, commands, code_snippets):
        """Construye el HTML para los snippets integrados"""
        snippets_html = """
        <div style="margin-top: 25px; padding-top: 20px; border-top: 2px solid #374151;">
            <h3 style="color: #fbbf24; margin-bottom: 15px; font-size: 16px;">
                📋 Comandos y Código Sugeridos
            </h3>
        """

        # Agregar comandos
        for i, command in enumerate(commands):
            if command.strip():
                snippets_html += self.build_snippet_item_html(f"💻 Comando {i+1}", command, "command", i)

        # Agregar código
        for i, code in enumerate(code_snippets):
            if code.strip():
                snippets_html += self.build_snippet_item_html(f"📝 Código {i+1}", code, "code", len(commands) + i)

        snippets_html += "</div>"
        return snippets_html

    def build_snippet_item_html(self, title, content, snippet_type, index):
        """Construye el HTML para un snippet individual"""
        # Escapar el contenido para HTML
        import html
        escaped_content = html.escape(content)

        return f"""
        <div style="margin-bottom: 15px; background-color: #1f2937; border: 1px solid #4b5563; border-radius: 8px; padding: 15px;" id="snippet-container-{index}">
            <div style="margin-bottom: 10px;">
                <strong style="color: #34d399; font-size: 14px;">{title}</strong>
            </div>
            <pre style="
                background-color: #111827;
                color: #e5e7eb;
                padding: 12px;
                border-radius: 6px;
                margin: 0;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                line-height: 1.4;
                overflow-x: auto;
                white-space: pre-wrap;
                word-wrap: break-word;
                cursor: text;
                user-select: all;
            " id="snippet-{index}">{escaped_content}</pre>
        </div>
        """

    # Métodos de botones de copiar eliminados - se usa click derecho para copiar

    # Métodos antiguos de snippets eliminados - ahora se generan dinámicamente
    
    def copy_to_clipboard(self, text):
        """Copiar texto al clipboard"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_label.setText(f"📋 Copiado: {text[:30]}...")
            # Restaurar estado después de 2 segundos
            QTimer.singleShot(2000, lambda: self.status_label.setText("✅ Respuesta recibida"))
        except Exception as e:
            logger.error(f"Error copiando al clipboard: {e}")
            self.status_label.setText("❌ Error copiando al clipboard")

    def show_ai_error(self, error_message):
        """Muestra error de la IA"""
        self.ai_thinking = False
        self.spinner_timer.stop()
        self.status_label.setText("❌ Error en consulta")

        # Mostrar error en el área de texto
        self.response_area.setPlainText(f"❌ Error: {error_message}")

    def update_placeholder_text(self):
        """Actualizar texto del placeholder con el nombre del usuario"""
        user_name = config_manager.get_user_name()
        self.search_input.setPlaceholderText(f"¡Hola {user_name}! ¿qué necesitas? (Presiona Enter para consultar)")
        
    def on_grounding_changed(self, state):
        """Manejar cambio en estado de grounding"""
        enabled = state == Qt.CheckState.Checked.value
        config_manager.set_grounding_enabled(enabled)
        config_manager.save_config()
        
        # Actualizar motor de IA
        if hasattr(ai_engine, 'grounding_enabled'):
            ai_engine.grounding_enabled = enabled
            
        # Actualizar tooltip
        if enabled:
            self.grounding_checkbox.setToolTip("🌐 Grounding activado: La IA puede buscar información en internet")
        else:
            self.grounding_checkbox.setToolTip("📋 Grounding desactivado: La IA proporcionará comandos y código estructurado")
            
        logger.info(f"Grounding {'habilitado' if enabled else 'deshabilitado'}")
        
    def load_grounding_state(self):
        """Cargar estado inicial del grounding desde configuración"""
        grounding_enabled = config_manager.get_grounding_enabled()
        self.grounding_checkbox.setChecked(grounding_enabled)

    def initialize_ai_engine(self):
        """Inicializar motor de IA con configuración actual"""
        try:
            api_key = config_manager.get_api_key()
            grounding_enabled = config_manager.get_grounding_enabled()
            
            if api_key:
                ai_engine.api_key = api_key
                ai_engine.grounding_enabled = grounding_enabled
                ai_engine._initialize_gemini()
                logger.info(f"Motor de IA inicializado - Grounding: {grounding_enabled}")
        except Exception as e:
            logger.error(f"Error inicializando motor de IA: {e}")

    def clear_conversation_history(self):
        """Limpiar historial de conversación"""
        try:
            config_manager.clear_conversation_history()
            config_manager.save_config()
            self.status_label.setText("🧹 Historial de conversación limpiado")
            logger.info("Historial de conversación limpiado")
        except Exception as e:
            logger.error(f"Error limpiando historial: {e}")
            self.status_label.setText("❌ Error limpiando historial")

    def show_preferences(self):
        """Mostrar ventana de preferencias"""
        try:
            dialog = PreferencesDialog(self)
            dialog.preferences_saved.connect(self.on_preferences_saved)
            dialog.exec()
        except Exception as e:
            logger.error(f"Error mostrando preferencias: {e}")

    def on_preferences_saved(self):
        """Manejar cuando se guardan las preferencias"""
        # Actualizar placeholder con nuevo nombre
        self.update_placeholder_text()

        # Reinicializar motor de IA con nueva configuración
        try:
            api_key = config_manager.get_api_key()
            grounding_enabled = config_manager.get_grounding_enabled()
            
            if api_key:
                # Actualizar API key y grounding en ai_engine
                ai_engine.api_key = api_key
                ai_engine.grounding_enabled = grounding_enabled
                ai_engine._initialize_gemini()
                logger.info(f"Motor de IA actualizado - Grounding: {grounding_enabled}")
            else:
                logger.warning("No hay API key configurada")
        except Exception as e:
            logger.error(f"Error actualizando motor de IA: {e}")

    def check_first_run(self):
        """Verificar si es la primera ejecución y mostrar configuración"""
        if not config_manager.is_configured():
            # Mostrar mensaje de bienvenida
            self.response_area.setPlainText(
                "👋 ¡Bienvenido a Spotlight Linux!\n\n"
                "Para comenzar, haz clic en el icono ⚙️ en la esquina superior derecha "
                "para configurar tu nombre y API key de Gemini.\n\n"
                "🔑 Necesitas una API key de Google Gemini para usar la IA.\n"
                "Puedes obtenerla gratis en: https://makersuite.google.com/app/apikey"
            )
            self.status_label.setText("⚙️ Configuración requerida - Haz clic en el icono de preferencias")

def main():
    """Función principal"""
    # Verificar si ya hay una instancia ejecutándose
    lock = SingleInstanceLock()

    if not lock.acquire_lock():
        # Ya hay una instancia ejecutándose
        logger.info("Otra instancia de Spotlight Linux ya está ejecutándose")
        show_already_running_alert()
        return

    logger.info("Lock adquirido - iniciando aplicación")

    app = QApplication(sys.argv)

    # Configurar aplicación
    app.setApplicationName("Spotlight Linux")
    app.setApplicationVersion("1.0")

    # Crear ventana principal
    window = SpotlightWindow()

    # Verificar argumentos de línea de comandos
    show_immediately = False
    if len(sys.argv) > 1:
        if "--show" in sys.argv:
            show_immediately = True
        elif "--help" in sys.argv or "-h" in sys.argv:
            print("🔍 Spotlight Linux - AI Search Tool")
            print("Uso: spotlight-linux [opciones]")
            print("")
            print("Opciones:")
            print("  --show    Mostrar ventana inmediatamente")
            print("  --help    Mostrar esta ayuda")
            print("")
            print("Atajos de teclado:")
            print("  Ctrl+Alt+Space    Mostrar ventana (global)")
            print("  Escape    Ocultar ventana")
            print("  Enter     Consultar IA")
            sys.exit(0)

    # Mostrar ventana si se solicita o en modo demo
    if show_immediately or len(sys.argv) == 1:
        window.show_window()

    logger.info("🚀 Spotlight Linux (PyQt6) iniciado")
    logger.info("💡 Presiona Escape para cerrar")
    logger.info("💡 Presiona Enter para consultar IA")
    logger.info("💡 Usa Ctrl+P para mostrar desde cualquier lugar")

    try:
        exit_code = app.exec()
        logger.info("Aplicación terminada normalmente")
        lock.release_lock()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Aplicación cerrada por Ctrl+C")
        lock.release_lock()
        sys.exit(0)

if __name__ == "__main__":
    main()
