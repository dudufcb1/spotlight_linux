#!/usr/bin/env python3
"""
Módulo de búsqueda de archivos para Spotlight Linux
Maneja indexación y búsqueda en el sistema de archivos + aplicaciones
"""

import os
import pathlib
import fnmatch
import threading
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from app_parser import ApplicationParser

@dataclass
class SearchResult:
    """Resultado de búsqueda con metadatos"""
    path: str
    name: str
    type: str  # 'file', 'directory', 'application', 'command'
    category: str  # 'document', 'image', 'video', 'audio', 'code', 'other', 'app', 'command'
    size: int
    modified: float
    icon: str
    relevance_score: float = 0.0
    description: str = ""
    executable: str = ""

class FileSearchEngine:
    """Motor de búsqueda de archivos y aplicaciones"""
    
    def __init__(self):
        self.indexed_files = {}  # path -> SearchResult
        self.app_parser = ApplicationParser()
        self.search_paths = [
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Pictures"),
            os.path.expanduser("~/Videos"),
            os.path.expanduser("~/Music"),
            "/usr/share/applications",
            "/usr/bin",
            "/opt"
        ]
        
        # Categorías por extensión
        self.file_categories = {
            'document': {'.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', '.md'},
            'image': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico'},
            'video': {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'},
            'audio': {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'},
            'code': {'.py', '.js', '.html', '.css', '.cpp', '.c', '.java', '.php'},
            'archive': {'.zip', '.rar', '.tar', '.gz', '.7z', '.deb', '.rpm'}
        }
        
        self.is_indexing = False
        self.last_index_time = 0
        self.index_cache_duration = 300  # 5 minutos
        
    def get_file_category(self, file_path: str) -> str:
        """Determina la categoría de un archivo por su extensión"""
        ext = pathlib.Path(file_path).suffix.lower()
        
        for category, extensions in self.file_categories.items():
            if ext in extensions:
                return category
        return 'other'
        
    def get_file_icon(self, result: SearchResult) -> str:
        """Obtiene el icono apropiado para un resultado"""
        if result.type == 'directory':
            return '📁'
        elif result.type == 'application':
            return '🖥️'
        elif result.category == 'document':
            return '📄'
        elif result.category == 'image':
            return '🖼️'
        elif result.category == 'video':
            return '🎬'
        elif result.category == 'audio':
            return '🎵'
        elif result.category == 'code':
            return '⚡'
        elif result.category == 'archive':
            return '📦'
        else:
            return '📄'
            
    def should_skip_directory(self, dir_path: str) -> bool:
        """Determina si debe saltar un directorio durante indexación"""
        skip_dirs = {
            '.git', '.svn', '__pycache__', 'node_modules', 
            '.cache', '.local/share/Trash', '.thumbnails',
            'venv', '.venv', 'env'
        }
        
        dir_name = os.path.basename(dir_path)
        return dir_name in skip_dirs or dir_name.startswith('.')
        
    def index_directory(self, path: str, max_files: int = 1000) -> List[SearchResult]:
        """Indexa un directorio específico"""
        results = []
        file_count = 0
        
        try:
            if not os.path.exists(path) or not os.access(path, os.R_OK):
                return results
                
            for root, dirs, files in os.walk(path):
                # Filtrar directorios a evitar
                dirs[:] = [d for d in dirs if not self.should_skip_directory(os.path.join(root, d))]
                
                # Añadir directorios
                for dir_name in dirs[:10]:  # Limitar directorios por carpeta
                    if file_count >= max_files:
                        break
                        
                    dir_path = os.path.join(root, dir_name)
                    try:
                        stat = os.stat(dir_path)
                        result = SearchResult(
                            path=dir_path,
                            name=dir_name,
                            type='directory',
                            category='folder',
                            size=0,
                            modified=stat.st_mtime,
                            icon='📁'
                        )
                        results.append(result)
                        file_count += 1
                    except (OSError, PermissionError):
                        continue
                
                # Añadir archivos
                for file_name in files:
                    if file_count >= max_files:
                        break
                        
                    file_path = os.path.join(root, file_name)
                    try:
                        stat = os.stat(file_path)
                        category = self.get_file_category(file_path)
                        
                        # Determinar tipo
                        file_type = 'application' if file_path.endswith('.desktop') else 'file'
                        
                        result = SearchResult(
                            path=file_path,
                            name=file_name,
                            type=file_type,
                            category=category,
                            size=stat.st_size,
                            modified=stat.st_mtime,
                            icon=''  # Se asignará después
                        )
                        result.icon = self.get_file_icon(result)
                        results.append(result)
                        file_count += 1
                        
                    except (OSError, PermissionError):
                        continue
                        
        except (OSError, PermissionError):
            pass
            
        return results
        
    def build_index(self, progress_callback=None):
        """Construye el índice de archivos y aplicaciones"""
        if self.is_indexing:
            return
            
        self.is_indexing = True
        self.indexed_files.clear()
        
        try:
            # Inicializar parser de aplicaciones
            if progress_callback:
                progress_callback("Inicializando parser de aplicaciones...", 0.0)
            
            app_count = self.app_parser.initialize()
            
            if progress_callback:
                progress_callback(f"Aplicaciones cargadas: {app_count}", 0.1)
            
            # Agregar aplicaciones al índice
            for app_item in self.app_parser.get_all_items():
                result = SearchResult(
                    path=app_item['path'],
                    name=app_item['name'],
                    type=app_item['type'],
                    category=app_item['category'],
                    size=0,
                    modified=0.0,
                    icon=self._get_app_icon(app_item),
                    description=app_item['description'],
                    executable=app_item['path']
                )
                self.indexed_files[f"app_{app_item['name']}"] = result
            
            # Indexar archivos
            total_paths = len(self.search_paths)
            
            for i, search_path in enumerate(self.search_paths):
                if progress_callback:
                    progress = 0.1 + (i / total_paths) * 0.9
                    progress_callback(f"Indexando {search_path}...", progress)
                
                # Determinar límite por directorio
                max_files = 500 if search_path.startswith('/usr') else 200
                
                results = self.index_directory(search_path, max_files)
                
                for result in results:
                    self.indexed_files[result.path] = result
                    
            self.last_index_time = time.time()
            
            if progress_callback:
                progress_callback(f"Índice completado: {len(self.indexed_files)} elementos", 1.0)
                
        finally:
            self.is_indexing = False
    
    def _get_app_icon(self, app_item: Dict[str, str]) -> str:
        """Obtiene el icono apropiado para un elemento de aplicación"""
        if app_item['type'] == 'application':
            category = app_item['category'].lower()
            if 'desarrollo' in category:
                return '⚡'
            elif 'multimedia' in category:
                return '🎬'
            elif 'gráficos' in category:
                return '🖼️'
            elif 'juegos' in category:
                return '🎮'
            elif 'oficina' in category:
                return '📄'
            elif 'red' in category:
                return '🌐'
            elif 'sistema' in category:
                return '⚙️'
            else:
                return '📱'
        elif app_item['type'] == 'command':
            return '⚡'
        else:
            return '📄'
            
    def needs_reindex(self) -> bool:
        """Determina si necesita reindexar"""
        return (time.time() - self.last_index_time) > self.index_cache_duration
        
    def calculate_relevance(self, result: SearchResult, query: str) -> float:
        """Calcula relevancia de un resultado para una consulta"""
        query_lower = query.lower()
        name_lower = result.name.lower()
        
        # Coincidencia exacta del nombre
        if name_lower == query_lower:
            return 1.0
            
        # Comienza con la consulta
        if name_lower.startswith(query_lower):
            return 0.9
            
        # Contiene la consulta
        if query_lower in name_lower:
            return 0.7
            
        # Coincidencia por palabras
        query_words = query_lower.split()
        name_words = name_lower.split()
        
        matches = sum(1 for qword in query_words 
                     for nword in name_words 
                     if qword in nword)
        
        if matches > 0:
            return 0.5 + (matches / len(query_words)) * 0.3
            
        return 0.0
        
    def search(self, query: str, max_results: int = 20) -> List[SearchResult]:
        """Busca archivos que coincidan con la consulta"""
        if not query.strip():
            return []
            
        # Reindexar si es necesario
        if not self.indexed_files or self.needs_reindex():
            self.build_index()
            
        results = []
        query_lower = query.lower()
        
        for file_path, result in self.indexed_files.items():
            # Buscar en nombre del archivo
            if query_lower in result.name.lower():
                relevance = self.calculate_relevance(result, query)
                if relevance > 0:
                    result.relevance_score = relevance
                    results.append(result)
                    
        # Ordenar por relevancia
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:max_results]
        
    def search_async(self, query: str, callback, max_results: int = 20):
        """Búsqueda asíncrona no bloqueante"""
        def search_thread():
            try:
                results = self.search(query, max_results)
                callback(results, None)
            except Exception as e:
                callback([], str(e))
                
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
        
    def get_quick_access_items(self) -> List[SearchResult]:
        """Obtiene elementos de acceso rápido"""
        quick_items = []
        
        # Directorios importantes
        important_dirs = [
            (os.path.expanduser("~/Desktop"), "Escritorio"),
            (os.path.expanduser("~/Documents"), "Documentos"),
            (os.path.expanduser("~/Downloads"), "Descargas"),
            (os.path.expanduser("~/Pictures"), "Imágenes"),
        ]
        
        for dir_path, display_name in important_dirs:
            if os.path.exists(dir_path):
                quick_items.append(SearchResult(
                    path=dir_path,
                    name=display_name,
                    type='directory',
                    category='folder',
                    size=0,
                    modified=0,
                    icon='📁',
                    relevance_score=1.0
                ))
                
        return quick_items
    
    def execute_result(self, result: SearchResult) -> bool:
        """Ejecuta un resultado de búsqueda con detección inteligente de tipos"""
        import logging
        import subprocess
        import os
        import stat
        import time
        
        logger = logging.getLogger(__name__)
        logger.info(f"[EXEC] Ejecutando: {result.name} (tipo: {result.type}, path: {result.path})")
        
        try:
            if result.type in ['application', 'command']:
                logger.info(f"[EXEC] Delegando a app_parser: {result.name}")
                
                # Usar el parser de aplicaciones para ejecutar
                item_dict = {
                    'type': result.type,
                    'name': result.name,
                    'path': result.executable or result.path,
                    'description': getattr(result, 'description', '')
                }
                
                success = self.app_parser.execute_item(item_dict)
                logger.info(f"[EXEC] app_parser resultado: {success}")
                return success
                
            else:
                # Para archivos y directorios - usar detección inteligente
                logger.info(f"[EXEC] Analizando archivo/directorio: {result.path}")
                
                if not os.path.exists(result.path):
                    logger.error(f"[EXEC] ❌ Archivo no existe: {result.path}")
                    return False
                
                # Obtener información del archivo
                file_stat = os.stat(result.path)
                is_executable = bool(file_stat.st_mode & stat.S_IEXEC)
                is_directory = os.path.isdir(result.path)
                
                logger.info(f"[EXEC] Análisis: ejecutable={is_executable}, directorio={is_directory}")
                
                # Estrategia de ejecución inteligente
                if is_directory:
                    # Directorios: siempre usar xdg-open
                    logger.info(f"[EXEC] 📁 Abriendo directorio: {result.path}")
                    cmd = ['xdg-open', result.path]
                    
                elif is_executable and (result.path.startswith('/usr/bin/') or 
                                      result.path.startswith('/bin/') or
                                      result.path.startswith('/usr/local/bin/')):
                    # Ejecutables del sistema: ejecutar directamente
                    logger.info(f"[EXEC] ⚡ Ejecutando binario directamente: {result.path}")
                    cmd = [result.path]
                    
                elif result.path.endswith('.desktop'):
                    # Archivos .desktop: usar gio launch
                    logger.info(f"[EXEC] 🚀 Lanzando aplicación .desktop: {result.path}")
                    cmd = ['gio', 'launch', result.path]
                    
                elif is_executable and not result.path.startswith('/'):
                    # Ejecutables relativos o en PATH
                    logger.info(f"[EXEC] ⚡ Ejecutando comando en PATH: {result.path}")
                    cmd = [result.path]
                    
                else:
                    # Archivos normales: usar xdg-open
                    logger.info(f"[EXEC] 📄 Abriendo archivo con aplicación predeterminada: {result.path}")
                    cmd = ['xdg-open', result.path]
                
                # Ejecutar comando
                logger.info(f"[EXEC] Comando final: {' '.join(cmd)}")
                
                process = subprocess.Popen(cmd, 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE,
                                         start_new_session=True)
                
                logger.info(f"[EXEC] Proceso lanzado, PID: {process.pid}")
                
                # Esperar brevemente para verificar el estado
                time.sleep(0.3)
                
                # Verificar resultado
                poll = process.poll()
                if poll is None:
                    logger.info(f"[EXEC] ✅ Proceso activo - aplicación ejecutándose")
                    return True
                elif poll == 0:
                    logger.info(f"[EXEC] ✅ Proceso terminó exitosamente")
                    return True
                else:
                    stdout, stderr = process.communicate()
                    logger.error(f"[EXEC] ❌ Comando falló con código {poll}")
                    if stderr:
                        logger.error(f"[EXEC] Error: {stderr.decode()}")
                    return False
                    
        except Exception as e:
            logger.error(f"[EXEC] ❌ Excepción ejecutando {result.name}: {str(e)}", exc_info=True)
            return False
