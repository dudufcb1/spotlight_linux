#!/usr/bin/env python3
"""
Sistema de Configuración para Spotlight Linux
Gestiona preferencias de usuario y configuración de la aplicación
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class ConfigManager:
    """Gestor de configuración de la aplicación"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "spotlight-linux"
        self.config_file = self.config_dir / "config.json"
        self.key_file = self.config_dir / ".key"
        
        # Configuración por defecto
        self.default_config = {
            "user": {
                "name": "Usuario",
                "tone": "amigable"
            },
            "ai": {
                "api_key_encrypted": "",
                "model": "gemini-2.5-flash-lite-preview-06-17"
            },
            "ui": {
                "theme": "dark",
                "language": "es"
            }
        }
        
        self._ensure_config_dir()
        self._config = self._load_config()
        
    def _ensure_config_dir(self):
        """Crear directorio de configuración si no existe"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Establecer permisos seguros
        os.chmod(self.config_dir, 0o700)
        
    def _get_encryption_key(self) -> bytes:
        """Obtener o crear clave de encriptación"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Generar nueva clave
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)
            return key
            
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encriptar API key"""
        if not api_key:
            return ""
            
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted = fernet.encrypt(api_key.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Error encriptando API key: {e}")
            return ""
            
    def _decrypt_api_key(self, encrypted_key: str) -> str:
        """Desencriptar API key"""
        if not encrypted_key:
            return ""
            
        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_key.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error desencriptando API key: {e}")
            return ""
            
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración desde archivo"""
        if not self.config_file.exists():
            return self.default_config.copy()
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Fusionar con configuración por defecto para nuevas claves
            merged_config = self.default_config.copy()
            self._deep_merge(merged_config, config)
            return merged_config
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self.default_config.copy()
            
    def _deep_merge(self, base: Dict, update: Dict):
        """Fusionar diccionarios recursivamente"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
                
    def save_config(self):
        """Guardar configuración a archivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            os.chmod(self.config_file, 0o600)
            logger.info("Configuración guardada exitosamente")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            
    # Getters
    def get_user_name(self) -> str:
        return self._config["user"]["name"]
        
    def get_user_tone(self) -> str:
        return self._config["user"]["tone"]
        
    def get_api_key(self) -> str:
        encrypted = self._config["ai"]["api_key_encrypted"]
        return self._decrypt_api_key(encrypted)
        
    def get_model(self) -> str:
        return self._config["ai"]["model"]
        
    def get_theme(self) -> str:
        return self._config["ui"]["theme"]
        
    # Setters
    def set_user_name(self, name: str):
        self._config["user"]["name"] = name
        
    def set_user_tone(self, tone: str):
        self._config["user"]["tone"] = tone
        
    def set_api_key(self, api_key: str):
        encrypted = self._encrypt_api_key(api_key)
        self._config["ai"]["api_key_encrypted"] = encrypted
        
    def set_model(self, model: str):
        self._config["ai"]["model"] = model
        
    def set_theme(self, theme: str):
        self._config["ui"]["theme"] = theme
        
    # Utilidades
    def is_configured(self) -> bool:
        """Verificar si la aplicación está configurada"""
        return bool(self.get_api_key() and self.get_user_name())
        
    def get_masked_api_key(self) -> str:
        """Obtener API key enmascarada para mostrar en UI"""
        api_key = self.get_api_key()
        if not api_key:
            return ""
        if len(api_key) <= 8:
            return "•" * len(api_key)
        return "•" * (len(api_key) - 4) + api_key[-4:]
        
    def get_tone_options(self) -> Dict[str, str]:
        """Obtener opciones de tono disponibles"""
        return {
            "amigable": "Amigable - Conversacional y cercano",
            "profesional": "Profesional - Formal y directo", 
            "tecnico": "Técnico - Preciso y detallado",
            "casual": "Casual - Relajado e informal",
            "entusiasta": "Entusiasta - Energético y motivador"
        }

# Instancia global del gestor de configuración
config_manager = ConfigManager()
