#!/usr/bin/env python3
"""
Comandos integrados adicionales para Spotlight Linux
Funciones útiles y accesos directos del sistema
"""

import os
import subprocess
from typing import Dict, List
from data_models import SystemCommand

class IntegratedCommands:
    """Comandos integrados y funciones útiles del sistema"""
    
    def __init__(self):
        self.commands: Dict[str, SystemCommand] = {}
        self._initialize_commands()
    
    def _initialize_commands(self):
        """Inicializa los comandos integrados"""
        
        # Comandos de sistema útiles
        system_commands = [
            SystemCommand(
                name="Apagar sistema",
                description="Apagar el sistema inmediatamente",
                command="shutdown -h now",
                category="system",
                keywords=["apagar", "shutdown", "off", "poder"]
            ),
            SystemCommand(
                name="Reiniciar sistema",
                description="Reiniciar el sistema",
                command="reboot",
                category="system", 
                keywords=["reiniciar", "reboot", "restart", "reset"]
            ),
            SystemCommand(
                name="Monitor del sistema",
                description="Abrir monitor de procesos y recursos",
                command="gnome-system-monitor || ksysguard || htop",
                category="utility",
                keywords=["monitor", "procesos", "recursos", "cpu", "memoria", "system", "htop"]
            ),
            SystemCommand(
                name="Centro de control",
                description="Abrir centro de control del sistema",
                command="gnome-control-center || systemsettings5",
                category="system",
                keywords=["centro", "control", "configuración", "settings", "preferences"]
            ),
            SystemCommand(
                name="Editor de texto",
                description="Abrir editor de texto predeterminado",
                command="gedit || kate || mousepad || leafpad",
                category="utility",
                keywords=["editor", "texto", "edit", "text", "gedit", "kate"]
            ),
            SystemCommand(
                name="Captura de pantalla",
                description="Tomar captura de pantalla",
                command="gnome-screenshot || spectacle || scrot",
                category="utility",
                keywords=["captura", "pantalla", "screenshot", "imagen", "foto"]
            ),
            SystemCommand(
                name="Limpieza del sistema",
                description="Limpiar archivos temporales y cache",
                command="bleachbit || cleanmgr",
                category="utility", 
                keywords=["limpiar", "clean", "cache", "temporal", "bleachbit"]
            ),
            SystemCommand(
                name="Información del sistema",
                description="Ver información del hardware y sistema",
                command="hardinfo || inxi -Fxz || neofetch",
                category="utility",
                keywords=["info", "información", "hardware", "sistema", "specs", "neofetch"]
            )
        ]
        
        # Comandos de acceso rápido
        quick_access = [
            SystemCommand(
                name="Abrir terminal",
                description="Abrir terminal del sistema",
                command="gnome-terminal || konsole || xfce4-terminal || xterm",
                category="utility",
                keywords=["terminal", "consola", "bash", "shell", "cmd"]
            ),
            SystemCommand(
                name="Gestor de archivos",
                description="Abrir explorador de archivos",
                command="nautilus || thunar || dolphin || pcmanfm",
                category="utility",
                keywords=["archivos", "explorador", "files", "folders", "gestor"]
            ),
            SystemCommand(
                name="Navegador web",
                description="Abrir navegador web predeterminado",
                command="firefox || chromium || google-chrome",
                category="internet",
                keywords=["navegador", "web", "internet", "browser", "firefox", "chrome"]
            ),
            SystemCommand(
                name="Calculadora",
                description="Abrir calculadora",
                command="gnome-calculator || kcalc || galculator",
                category="utility",
                keywords=["calculadora", "calc", "math", "matemáticas", "números"]
            )
        ]
        
        # Comandos de desarrollo
        dev_commands = [
            SystemCommand(
                name="Visual Studio Code",
                description="Abrir editor de código VS Code",
                command="code",
                category="development",
                keywords=["vscode", "code", "editor", "desarrollo", "programming"]
            ),
            SystemCommand(
                name="Git Status",
                description="Ver estado del repositorio git",
                command="git status",
                category="development",
                keywords=["git", "status", "repository", "version", "control"]
            ),
            SystemCommand(
                name="Docker Desktop",
                description="Abrir Docker Desktop",
                command="docker",
                category="development",
                keywords=["docker", "container", "devops", "deployment"]
            )
        ]
        
        # Comandos de red
        network_commands = [
            SystemCommand(
                name="Test de conectividad",
                description="Probar conectividad a internet",
                command="ping -c 4 8.8.8.8",
                category="network",
                keywords=["ping", "internet", "conectividad", "network", "red"]
            ),
            SystemCommand(
                name="Configuración de red",
                description="Ver configuración de red",
                command="nm-connection-editor || network-admin",
                category="network", 
                keywords=["red", "network", "wifi", "ethernet", "ip", "configuración"]
            ),
            SystemCommand(
                name="Velocidad de internet",
                description="Probar velocidad de internet",
                command="speedtest-cli || fast",
                category="network",
                keywords=["velocidad", "speed", "internet", "test", "bandwidth"]
            )
        ]
        
        # Combinar todos los comandos
        all_commands = system_commands + quick_access + dev_commands + network_commands
        
        # Crear diccionario indexado por nombre
        for cmd in all_commands:
            self.commands[cmd.name.lower()] = cmd
    
    def get_all_commands(self) -> List[SystemCommand]:
        """Obtiene todos los comandos integrados"""
        return list(self.commands.values())
    
    def search_commands(self, query: str) -> List[SystemCommand]:
        """Busca comandos por nombre o keywords"""
        query_lower = query.lower()
        results = []
        
        for cmd in self.commands.values():
            # Buscar en nombre
            if query_lower in cmd.name.lower():
                results.append(cmd)
                continue
                
            # Buscar en keywords
            if cmd.keywords:
                for keyword in cmd.keywords:
                    if query_lower in keyword.lower():
                        results.append(cmd)
                        break
        
        return results
    
    def execute_command(self, command_name: str) -> bool:
        """Ejecuta un comando por nombre"""
        cmd = self.commands.get(command_name.lower())
        if not cmd:
            return False
        
        try:
            if '||' in cmd.command:
                # Probar comandos alternativos
                alternatives = [c.strip() for c in cmd.command.split('||')]
                for alt in alternatives:
                    try:
                        subprocess.Popen(alt.split(), 
                                       stdout=subprocess.DEVNULL, 
                                       stderr=subprocess.DEVNULL)
                        return True
                    except FileNotFoundError:
                        continue
                return False
            else:
                # Ejecutar comando único
                subprocess.Popen(cmd.command.split(), 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                return True
        except Exception:
            return False

if __name__ == "__main__":
    # Test de los comandos integrados
    integrated = IntegratedCommands()
    commands = integrated.get_all_commands()
    print(f"Comandos integrados inicializados: {len(commands)}")
    
    # Test de búsqueda
    results = integrated.search_commands("calculadora")
    print(f"Resultados para 'calculadora': {len(results)}")
    for result in results:
        print(f"  - {result.name}: {result.description}")
