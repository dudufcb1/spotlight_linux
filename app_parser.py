#!/usr/bin/env python3
"""
Parser avanzado de aplicaciones del sistema para Spotlight Linux
Mejora la detección y ejecución de aplicaciones y comandos
"""

import os
import re
import subprocess
from typing import List, Dict, Optional, Set
from pathlib import Path
from data_models import Application, SystemCommand
from integrated_commands import IntegratedCommands

class ApplicationParser:
    """Parser avanzado de aplicaciones y comandos del sistema"""
    
    def __init__(self):
        self.applications: Dict[str, Application] = {}
        self.system_commands: Dict[str, SystemCommand] = {}
        self.integrated_commands = IntegratedCommands()
        self.desktop_paths = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            "/var/lib/snapd/desktop/applications",
            "~/.local/share/applications"
        ]
        self.system_paths = [
            "/usr/bin",
            "/usr/local/bin",
            "/bin",
            "/usr/games",
            "/usr/local/games"
        ]
        
    def parse_desktop_file(self, file_path: str) -> Optional[Application]:
        """Parsea un archivo .desktop y extrae información de la aplicación"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer campos del archivo .desktop
            name = self._extract_field(content, 'Name')
            comment = self._extract_field(content, 'Comment')
            exec_cmd = self._extract_field(content, 'Exec')
            icon = self._extract_field(content, 'Icon')
            categories = self._extract_field(content, 'Categories')
            keywords = self._extract_field(content, 'Keywords')
            no_display = self._extract_field(content, 'NoDisplay')
            
            # Skip si NoDisplay=true
            if no_display and no_display.lower() == 'true':
                return None
            
            if not name or not exec_cmd:
                return None
            
            # Limpiar comando ejecutable
            exec_clean = self._clean_exec_command(exec_cmd)
            
            # Extraer categoría principal
            category = self._extract_main_category(categories) if categories else None
            
            # Procesar keywords
            keyword_list = []
            if keywords:
                keyword_list = [k.strip() for k in keywords.split(';') if k.strip()]
            
            # Agregar nombre y comentario a keywords para búsqueda
            keyword_list.extend([name.lower()])
            if comment:
                keyword_list.extend(comment.lower().split())
            
            return Application(
                name=name,
                description=comment or "",
                executable=exec_clean,
                icon=icon,
                category=category,
                desktop_file=file_path,
                keywords=keyword_list
            )
            
        except Exception as e:
            # Silencioso para archivos corruptos
            return None
    
    def _extract_field(self, content: str, field: str) -> Optional[str]:
        """Extrae un campo específico del archivo .desktop"""
        pattern = rf'^{field}=(.*)$'
        match = re.search(pattern, content, re.MULTILINE)
        return match.group(1).strip() if match else None
    
    def _clean_exec_command(self, exec_cmd: str) -> str:
        """Limpia el comando ejecutable removiendo argumentos de .desktop"""
        # Remover argumentos comunes de .desktop
        exec_cmd = re.sub(r'%[a-zA-Z]', '', exec_cmd)
        exec_cmd = exec_cmd.strip()
        
        # Obtener solo el ejecutable principal
        parts = exec_cmd.split()
        if parts:
            return parts[0]
        return exec_cmd
    
    def _extract_main_category(self, categories: str) -> Optional[str]:
        """Extrae la categoría principal de la lista de categorías"""
        category_map = {
            'AudioVideo': 'Multimedia',
            'Audio': 'Multimedia',
            'Video': 'Multimedia',
            'Development': 'Desarrollo',
            'Education': 'Educación',
            'Game': 'Juegos',
            'Graphics': 'Gráficos',
            'Network': 'Red',
            'Office': 'Oficina',
            'Science': 'Ciencia',
            'Settings': 'Configuración',
            'System': 'Sistema',
            'Utility': 'Utilidades'
        }
        
        for cat in categories.split(';'):
            cat = cat.strip()
            if cat in category_map:
                return category_map[cat]
        
        return 'Aplicaciones'
    
    def scan_applications(self) -> Dict[str, Application]:
        """Escanea todos los directorios de aplicaciones"""
        applications: Dict[str, Application] = {}
        
        for desktop_path in self.desktop_paths:
            expanded_path = os.path.expanduser(desktop_path)
            if os.path.exists(expanded_path):
                for filename in os.listdir(expanded_path):
                    if filename.endswith('.desktop'):
                        file_path = os.path.join(expanded_path, filename)
                        app = self.parse_desktop_file(file_path)
                        if app:
                            applications[app.name.lower()] = app
        
        self.applications = applications
        return applications
    
    def scan_system_commands(self) -> Dict[str, SystemCommand]:
        """Escanea comandos del sistema disponibles"""
        commands: Dict[str, SystemCommand] = {}
        
        # Obtener PATH del sistema
        path_env = os.environ.get('PATH', '')
        path_dirs = path_env.split(':') + self.system_paths
        
        # Comandos conocidos con descripciones
        known_commands = {
            'htop': 'Monitor de procesos interactivo',
            'code': 'Visual Studio Code',
            'gedit': 'Editor de texto GNOME',
            'nano': 'Editor de texto en terminal',
            'vim': 'Editor de texto Vi mejorado',
            'firefox': 'Navegador web Firefox',
            'chromium': 'Navegador web Chromium',
            'gimp': 'Editor de imágenes GIMP',
            'vlc': 'Reproductor multimedia VLC',
            'libreoffice': 'Suite ofimática LibreOffice',
            'terminal': 'Terminal del sistema',
            'gnome-terminal': 'Terminal GNOME',
            'konsole': 'Terminal KDE',
            'thunar': 'Gestor de archivos Thunar',
            'nautilus': 'Gestor de archivos GNOME',
            'dolphin': 'Gestor de archivos KDE',
            'calculator': 'Calculadora',
            'gnome-calculator': 'Calculadora GNOME',
            'kcalc': 'Calculadora KDE'
        }
        
        # Buscar ejecutables en PATH
        executables: Set[str] = set()
        for path_dir in path_dirs:
            if os.path.exists(path_dir) and os.path.isdir(path_dir):
                try:
                    for filename in os.listdir(path_dir):
                        file_path = os.path.join(path_dir, filename)
                        if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                            executables.add(filename)
                except PermissionError:
                    continue
        
        # Crear comandos del sistema
        for executable in executables:
            if executable in known_commands:
                description = known_commands[executable]
            else:
                description = f"Comando del sistema: {executable}"
            
            commands[executable] = SystemCommand(
                name=executable,
                description=description,
                command=executable,
                keywords=[executable, description.lower()]
            )
        
        # Agregar comandos internos útiles
        internal_commands = {
            'calc': SystemCommand(
                name='Calculadora',
                description='Abrir calculadora del sistema',
                command='gnome-calculator || kcalc || calculator',
                category='utility',
                keywords=['calc', 'calculadora', 'calculator', 'math', 'matemáticas']
            ),
            'terminal': SystemCommand(
                name='Terminal',
                description='Abrir terminal del sistema',
                command='gnome-terminal || konsole || xterm',
                category='utility',
                keywords=['terminal', 'consola', 'shell', 'bash']
            ),
            'files': SystemCommand(
                name='Gestor de archivos',
                description='Abrir gestor de archivos',
                command='nautilus || thunar || dolphin || pcmanfm',
                category='utility',
                keywords=['files', 'archivos', 'gestor', 'explorador', 'folders']
            ),
            'settings': SystemCommand(
                name='Configuración',
                description='Abrir configuración del sistema',
                command='gnome-control-center || systemsettings5 || xfce4-settings-manager',
                category='system',
                keywords=['settings', 'configuración', 'preferences', 'config']
            )
        }
        
        commands.update(internal_commands)
        
        # Agregar comandos integrados adicionales
        for integrated_cmd in self.integrated_commands.get_all_commands():
            commands[integrated_cmd.name] = integrated_cmd
        
        self.system_commands = commands
        return commands
    
    def get_all_items(self) -> List[Dict[str, str]]:
        """Obtiene todos los elementos (aplicaciones + comandos) para búsqueda"""
        items: List[Dict[str, str]] = []
        
        # Agregar aplicaciones
        for app in self.applications.values():
            items.append({
                'type': 'application',
                'name': app.name,
                'description': app.description,
                'path': app.executable,
                'category': app.category or 'Aplicaciones',
                'keywords': ' '.join(app.keywords or []),
                'icon': app.icon or '',
                'desktop_file': app.desktop_file or ''
            })
        
        # Agregar comandos del sistema
        for cmd in self.system_commands.values():
            items.append({
                'type': 'command',
                'name': cmd.name,
                'description': cmd.description,
                'path': cmd.command,
                'category': 'Comandos',
                'keywords': ' '.join(cmd.keywords or [])
            })
        
        return items
    
    def execute_item(self, item: Dict[str, str]) -> bool:
        """Ejecuta un elemento (aplicación o comando) con logging detallado"""
        import logging
        import os
        import shlex
        
        logger = logging.getLogger(__name__)
        logger.info(f"[EXECUTE] Iniciando ejecución: {item}")
        
        try:
            if item['type'] == 'application':
                path = item['path']
                logger.info(f"[APP] Ejecutando aplicación: {path}")
                
                # Verificar si existe
                if not os.path.exists(path):
                    logger.error(f"[APP] Archivo no existe: {path}")
                    return False
                
                # Verificar si es ejecutable
                if not os.access(path, os.X_OK):
                    logger.error(f"[APP] Archivo no ejecutable: {path}")
                    return False
                
                # Intentar diferentes formas de ejecución
                try:
                    # Método 1: Ejecución directa
                    logger.info(f"[APP] Método 1: Ejecución directa de {path}")
                    process = subprocess.Popen([path], 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE,
                                             start_new_session=True)
                    logger.info(f"[APP] Proceso iniciado PID: {process.pid}")
                    return True
                    
                except Exception as e1:
                    logger.warning(f"[APP] Método 1 falló: {e1}")
                    
                    try:
                        # Método 2: Con xdg-open
                        logger.info(f"[APP] Método 2: xdg-open {path}")
                        process = subprocess.Popen(['xdg-open', path],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 start_new_session=True)
                        logger.info(f"[APP] xdg-open proceso PID: {process.pid}")
                        return True
                        
                    except Exception as e2:
                        logger.error(f"[APP] Método 2 falló: {e2}")
                        return False
                        
            elif item['type'] == 'command':
                command = item['path']
                logger.info(f"[CMD] Ejecutando comando: {command}")
                
                if '||' in command:
                    # Probar comandos alternativos
                    alternatives = [cmd.strip() for cmd in command.split('||')]
                    logger.info(f"[CMD] Probando alternativas: {alternatives}")
                    
                    for alt in alternatives:
                        try:
                            logger.info(f"[CMD] Probando: {alt}")
                            cmd_parts = shlex.split(alt)
                            process = subprocess.Popen(cmd_parts,
                                                     stdout=subprocess.PIPE,
                                                     stderr=subprocess.PIPE,
                                                     start_new_session=True)
                            logger.info(f"[CMD] Éxito con {alt}, PID: {process.pid}")
                            return True
                        except FileNotFoundError as e:
                            logger.warning(f"[CMD] {alt} no encontrado: {e}")
                            continue
                        except Exception as e:
                            logger.warning(f"[CMD] {alt} falló: {e}")
                            continue
                    logger.error(f"[CMD] Todas las alternativas fallaron para: {command}")
                    return False
                else:
                    try:
                        cmd_parts = shlex.split(command)
                        logger.info(f"[CMD] Ejecutando comando simple: {cmd_parts}")
                        process = subprocess.Popen(cmd_parts,
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE,
                                                 start_new_session=True)
                        logger.info(f"[CMD] Comando ejecutado, PID: {process.pid}")
                        return True
                    except Exception as e:
                        logger.error(f"[CMD] Error ejecutando {command}: {e}")
                        return False
            else:
                logger.error(f"[EXECUTE] Tipo desconocido: {item['type']}")
                return False
                
        except Exception as e:
            logger.error(f"[EXECUTE] Error general ejecutando {item}: {e}", exc_info=True)
            return False
    
    def initialize(self):
        """Inicializa el parser escaneando aplicaciones y comandos"""
        self.scan_applications()
        self.scan_system_commands()
        return len(self.applications) + len(self.system_commands)

if __name__ == "__main__":
    # Test del parser
    parser = ApplicationParser()
    count = parser.initialize()
    print(f"Parser inicializado: {len(parser.applications)} aplicaciones, {len(parser.system_commands)} comandos")
    print(f"Total de elementos: {count}")
