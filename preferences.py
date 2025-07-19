#!/usr/bin/env python3
"""
Ventana de Preferencias para Spotlight Linux
Interfaz para configurar preferencias de usuario
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QPushButton, QGroupBox, QMessageBox, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from config import config_manager

logger = logging.getLogger(__name__)

class PreferencesDialog(QDialog):
    """Diálogo de preferencias de la aplicación"""
    
    # Señal emitida cuando se guardan las preferencias
    preferences_saved = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Preferencias - Spotlight Linux")
        self.setFixedSize(500, 550)
        self.setModal(True)
        
        # Configurar ventana
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        self.init_ui()
        self.load_current_settings()
        self.setup_style()
        
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Título
        title_label = QLabel("⚙️ Configuración de Spotlight Linux")
        title_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Grupo: Información Personal
        personal_group = QGroupBox("👤 Información Personal")
        personal_layout = QVBoxLayout(personal_group)
        personal_layout.setSpacing(8)
        
        # Nombre de usuario
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nombre:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("¿Cómo quieres que te llame la IA?")
        name_layout.addWidget(self.name_input)
        personal_layout.addLayout(name_layout)
        
        layout.addWidget(personal_group)
        
        # Grupo: Configuración de IA
        ai_group = QGroupBox("🤖 Configuración de IA")
        ai_layout = QVBoxLayout(ai_group)
        ai_layout.setSpacing(8)
        
        # Tono de IA
        tone_layout = QHBoxLayout()
        tone_layout.addWidget(QLabel("Tono:"))
        self.tone_combo = QComboBox()
        self.populate_tone_options()
        self.tone_combo.currentTextChanged.connect(self.on_tone_changed)
        tone_layout.addWidget(self.tone_combo)
        ai_layout.addLayout(tone_layout)

        # Campo personalizado para tono (inicialmente oculto)
        self.custom_tone_input = QLineEdit()
        self.custom_tone_input.setPlaceholderText("Describe cómo quieres que actúe la IA...")
        self.custom_tone_input.setVisible(False)
        ai_layout.addWidget(self.custom_tone_input)
        
        layout.addWidget(ai_group)
        
        # Grupo: API Key
        api_group = QGroupBox("🔑 Credenciales")
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(8)
        
        # API Key
        api_layout.addWidget(QLabel("API Key de Gemini:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Ingresa tu API key de Google Gemini")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        # Conectar eventos para feedback visual
        self.api_key_input.textChanged.connect(self.on_api_key_changed)
        self.api_key_input.focusInEvent = self.api_key_focus_in
        self.api_key_input.focusOutEvent = self.api_key_focus_out
        api_layout.addWidget(self.api_key_input)
        
        # Botón para mostrar/ocultar API key
        self.toggle_api_button = QPushButton("👁️ Mostrar API Key")
        self.toggle_api_button.clicked.connect(self.toggle_api_visibility)
        self.toggle_api_button.setMaximumWidth(150)
        api_layout.addWidget(self.toggle_api_button)
        
        # Indicador de estado de API key
        self.api_status_label = QLabel("")
        self.api_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        api_layout.addWidget(self.api_status_label)

        # Link para obtener API key
        help_label = QLabel('<a href="https://makersuite.google.com/app/apikey">🔗 Obtener API Key de Gemini</a>')
        help_label.setOpenExternalLinks(True)
        help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        api_layout.addWidget(help_label)
        
        layout.addWidget(api_group)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Guardar")
        self.save_button.clicked.connect(self.save_preferences)
        self.save_button.setDefault(True)
        
        self.cancel_button = QPushButton("❌ Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def populate_tone_options(self):
        """Poblar opciones de tono"""
        tone_options = config_manager.get_tone_options()
        for key, description in tone_options.items():
            self.tone_combo.addItem(description, key)

        # Agregar opción personalizar
        self.tone_combo.addItem("🎨 Personalizar - Define tu propio estilo", "personalizar")

    def on_tone_changed(self, text):
        """Manejar cambio en selección de tono"""
        current_data = self.tone_combo.currentData()
        if current_data == "personalizar":
            self.custom_tone_input.setVisible(True)
            self.custom_tone_input.setFocus()
        else:
            self.custom_tone_input.setVisible(False)

    def on_api_key_changed(self, text):
        """Proporcionar feedback visual cuando se escribe en API key"""
        if text and self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            # Cambiar el estilo para mostrar que hay contenido (solo en modo password)
            self.api_key_input.setStyleSheet("""
                QLineEdit {
                    background-color: #0f172a;
                    border-color: #10b981;
                    color: #ffffff;
                }
                QLineEdit::placeholder {
                    color: #6b7280;
                }
            """)
        elif not text:
            # Volver al estilo normal si está vacío
            self.api_key_input.setStyleSheet("")

        # Actualizar indicador de estado
        self.update_api_status(text)

    def api_key_focus_in(self, event):
        """Feedback visual cuando se enfoca el campo API key"""
        # Llamar al evento original
        QLineEdit.focusInEvent(self.api_key_input, event)
        # Agregar indicador visual
        self.api_key_input.setStyleSheet("""
            QLineEdit {
                background-color: #0f172a;
                border-color: #60a5fa;
                border-width: 3px;
                color: #ffffff;
            }
            QLineEdit::placeholder {
                color: #94a3b8;
                font-style: italic;
            }
        """)

    def api_key_focus_out(self, event):
        """Feedback visual cuando se pierde el foco del campo API key"""
        # Llamar al evento original
        QLineEdit.focusOutEvent(self.api_key_input, event)
        # Restaurar estilo basado en contenido
        if self.api_key_input.text():
            self.api_key_input.setStyleSheet("""
                QLineEdit {
                    background-color: #0f172a;
                    border-color: #10b981;
                    color: #ffffff;
                }
            """)
        else:
            self.api_key_input.setStyleSheet("")

    def update_api_status(self, text):
        """Actualizar indicador de estado de la API key"""
        if not text:
            self.api_status_label.setText("⚠️ API Key requerida para usar la IA")
            self.api_status_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
        elif len(text) < 20:
            self.api_status_label.setText("⚠️ API Key parece muy corta")
            self.api_status_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
        else:
            self.api_status_label.setText("✅ API Key configurada")
            self.api_status_label.setStyleSheet("color: #10b981; font-weight: bold;")
            
    def load_current_settings(self):
        """Cargar configuración actual"""
        # Cargar nombre
        self.name_input.setText(config_manager.get_user_name())
        
        # Cargar tono
        current_tone = config_manager.get_user_tone()
        tone_found = False

        # Buscar en opciones predefinidas
        for i in range(self.tone_combo.count()):
            if self.tone_combo.itemData(i) == current_tone:
                self.tone_combo.setCurrentIndex(i)
                tone_found = True
                break

        # Si no se encontró, es un tono personalizado
        if not tone_found and current_tone not in ["amigable", "profesional", "tecnico", "casual", "entusiasta"]:
            # Seleccionar "Personalizar" y mostrar el campo
            for i in range(self.tone_combo.count()):
                if self.tone_combo.itemData(i) == "personalizar":
                    self.tone_combo.setCurrentIndex(i)
                    self.custom_tone_input.setVisible(True)
                    self.custom_tone_input.setText(current_tone)
                    break
                
        # Cargar API key (enmascarada)
        masked_key = config_manager.get_masked_api_key()
        if masked_key:
            self.api_key_input.setText(masked_key)
            self.api_key_input.setProperty("is_masked", True)
            self.update_api_status(masked_key)
        else:
            self.api_key_input.setProperty("is_masked", False)
            self.update_api_status("")
            
    def toggle_api_visibility(self):
        """Alternar visibilidad de API key"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            # Mostrar API key real
            real_key = config_manager.get_api_key()
            self.api_key_input.setText(real_key)
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_api_button.setText("🙈 Ocultar API Key")
            self.api_key_input.setProperty("is_masked", False)
            # Cambiar estilo para mostrar que está visible
            self.api_key_input.setStyleSheet("""
                QLineEdit {
                    background-color: #fef3c7;
                    border-color: #f59e0b;
                    color: #92400e;
                    font-family: monospace;
                }
            """)
        else:
            # Ocultar API key
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_api_button.setText("👁️ Mostrar API Key")
            # Restaurar estilo normal
            self.api_key_input.setStyleSheet("")
            
    def save_preferences(self):
        """Guardar preferencias"""
        try:
            # Validar campos
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Por favor ingresa tu nombre")
                return
                
            api_key = self.api_key_input.text().strip()
            
            # Si el campo está enmascarado y no se cambió, mantener el actual
            if self.api_key_input.property("is_masked") and api_key == config_manager.get_masked_api_key():
                api_key = config_manager.get_api_key()
            
            if not api_key:
                reply = QMessageBox.question(
                    self, 
                    "API Key Vacía", 
                    "No has ingresado una API key. La IA no funcionará sin ella.\n¿Continuar de todos modos?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Determinar tono a guardar
            selected_tone = self.tone_combo.currentData()
            if selected_tone == "personalizar":
                custom_tone = self.custom_tone_input.text().strip()
                if not custom_tone:
                    QMessageBox.warning(self, "Error", "Por favor describe cómo quieres que actúe la IA")
                    return
                tone_to_save = custom_tone
            else:
                tone_to_save = selected_tone

            # Guardar configuración
            config_manager.set_user_name(name)
            config_manager.set_user_tone(tone_to_save)
            config_manager.set_api_key(api_key)
            config_manager.save_config()
            
            # Emitir señal de guardado
            self.preferences_saved.emit()
            
            # Mostrar confirmación
            QMessageBox.information(self, "Éxito", "Preferencias guardadas correctamente")
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Error guardando preferencias: {e}")
            QMessageBox.critical(self, "Error", f"Error guardando preferencias:\n{str(e)}")
            
    def setup_style(self):
        """Configurar estilo de la ventana"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1f2937;
                color: #e5e7eb;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #374151;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: #f9fafb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #f9fafb;
                font-weight: bold;
                font-size: 14px;
            }
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #4b5563;
                border-radius: 8px;
                background-color: #1f2937;
                color: #f9fafb;
                font-size: 15px;
                font-weight: 500;
                min-height: 16px;
                max-height: 50px;
            }
            QLineEdit:focus {
                border-color: #60a5fa;
                border-width: 3px;
                background-color: #0f172a;
                color: #ffffff;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #d1d5db;
                font-style: italic;
                font-size: 15px;
            }
            QLineEdit[class="has-content"] {
                background-color: #0f172a;
                border-color: #10b981;
                color: #ffffff;
            }
            QComboBox {
                padding: 12px 16px;
                border: 2px solid #4b5563;
                border-radius: 8px;
                background-color: #1f2937;
                color: #f9fafb;
                font-size: 15px;
                font-weight: 500;
                min-height: 16px;
                max-height: 50px;
            }
            QComboBox:focus {
                border-color: #60a5fa;
                border-width: 3px;
                background-color: #0f172a;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #374151;
                width: 30px;
                border-radius: 6px;
                margin-right: 4px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #3b82f6;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #1f2937;
                border: 2px solid #4b5563;
                border-radius: 6px;
                color: #f9fafb;
                selection-background-color: #3b82f6;
                selection-color: #ffffff;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px;
                border-radius: 4px;
                margin: 1px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #17202b;
                color: #ffffff;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
            QPushButton {
                padding: 8px 16px;
                border: 2px solid #4b5563;
                border-radius: 6px;
                background-color: #3b82f6;
                color: #ffffff;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563eb;
                border-color: #3b82f6;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
                border-color: #2563eb;
            }
            QPushButton[class="secondary"] {
                background-color: #6b7280;
                border-color: #6b7280;
            }
            QPushButton[class="secondary"]:hover {
                background-color: #4b5563;
                border-color: #4b5563;
            }
            QLabel {
                color: #f3f4f6;
                font-weight: 500;
            }
            QLabel[class="title"] {
                color: #f9fafb;
                font-size: 16px;
                font-weight: bold;
            }
        """)
