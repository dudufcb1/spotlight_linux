#!/usr/bin/env python3
"""
Clases de datos comunes para Spotlight Linux
"""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Application:
    """Representa una aplicación del sistema"""
    name: str
    description: str
    executable: str
    icon: Optional[str] = None
    category: Optional[str] = None
    desktop_file: Optional[str] = None
    keywords: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

@dataclass
class SystemCommand:
    """Representa un comando del sistema"""
    name: str
    description: str
    command: str
    category: str = "system"
    keywords: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
