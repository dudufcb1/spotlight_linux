#!/usr/bin/env python3
"""
AI Engine para Spotlight Linux
Módulo para integración con Gemini AI
"""

import os
import asyncio
import logging
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

# Importar config_manager para acceder a configuración del usuario
from config import config_manager

@dataclass
class AIResponse:
    """Respuesta de la IA con metadatos"""
    content: str
    success: bool
    error_message: Optional[str] = None
    is_markdown: bool = False
    processing_time: float = 0.0
    # Nuevos campos para modo no-grounding
    suggested_commands: Optional[List[str]] = None
    suggested_code_snippets: Optional[List[str]] = None
    is_structured: bool = False  # True si es respuesta estructurada (JSON)

class AIEngine:
    def _get_gemini_client(self):
        from google import genai
        return genai.Client(api_key=self.api_key)

    def _ask_grounding_mode(self, prompt: str) -> str:
        from google import genai
        from google.genai import types
        import os
        client = genai.Client(api_key=self.api_key)
        model = "gemini-2.5-flash"
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        tools = [
            types.Tool(url_context=types.UrlContext()),
            types.Tool(googleSearch=types.GoogleSearch()),
        ]
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            tools=tools,
            response_mime_type="text/plain",
        )
        response_text = ""
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_content_config,
        ):
            if hasattr(chunk, 'text') and chunk.text:
                response_text += chunk.text
        return response_text
    """Motor de IA para procesamiento de consultas"""
    
    def __init__(self, api_key: Optional[str] = None, grounding_enabled: bool = False):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.grounding_enabled = grounding_enabled
        self.client = None
        self.model_name = None
        self.system_context = ""
        self.is_initialized = False
        self.logger = logging.getLogger(__name__)
        
        # Configurar logging para debugging
        if not self.logger.handlers:
            # Crear handler para archivo
            file_handler = logging.FileHandler('ai_engine_debug.log')
            file_handler.setLevel(logging.INFO)
            
            # Crear formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Añadir handler al logger
            self.logger.addHandler(file_handler)
            self.logger.setLevel(logging.INFO)
        
        if not HAS_GEMINI:
            self.logger.warning("Google GenAI no está disponible. Instale: pip install google-genai")
            return
            
        if not self.api_key:
            self.logger.warning("API key de Gemini no encontrada. Configure GEMINI_API_KEY en variables de entorno")
            return
            
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Inicializar conexión con Gemini"""
        try:
            from google import genai
            # Crear cliente con API key
            self.client = genai.Client(api_key=self.api_key)
            # Definir modelo a usar
            self.model_name = 'gemini-2.5-flash-lite-preview-06-17'

            # Obtener información del sistema operativo
            self.system_context = self._get_system_context()

            self.is_initialized = True
            self.logger.info("Motor AI inicializado correctamente con Gemini")
            self.logger.info(f"Contexto del sistema detectado: {self.system_context[:100]}...")
        except Exception as e:
            self.logger.error(f"Error inicializando Gemini: {e}")
            self.is_initialized = False
    
    def _detect_markdown(self, text: str) -> bool:
        """Detectar si el texto contiene markdown"""
        markdown_indicators = [
            '```', '**', '*', '##', '#', '- ', '1. ', 
            '[', '](', '`', '>', '---', '***'
        ]
        return any(indicator in text for indicator in markdown_indicators)
    
    async def ask(self, query: str, context: Optional[str] = None, conversation_history: Optional[List[Dict]] = None) -> AIResponse:
        """
        Enviar consulta a la IA y obtener respuesta
        
        Args:
            query: Pregunta o consulta del usuario
            context: Contexto adicional opcional
            
        Returns:
            AIResponse con la respuesta de la IA
        """
        if not self.is_initialized:
            return AIResponse(
                content="❌ Motor de IA no disponible. Verifique la configuración de Gemini API.",
                success=False,
                error_message="AI engine not initialized"
            )
        
        try:
            import time
            start_time = time.time()
            
            # Logging detallado para debugging
            self.logger.info(f"🔍 [DEBUG] Grounding enabled: {self.grounding_enabled}")
            
            # Construir prompt personalizado con configuración del usuario
            prompt = self._build_conversation_prompt(query, context, conversation_history, self.grounding_enabled)

            self.logger.info(f"📤 [DEBUG] Prompt enviado: {prompt[:200]}...")
            
            if self.grounding_enabled:
                # Modo GROUNDING: respuesta natural usando tools y config avanzada
                self.logger.info("🌐 [DEBUG] Usando modo GROUNDING (tools y config avanzada)")
                response_text = self._ask_grounding_mode(prompt)
                self.logger.info(f"📥 [DEBUG] Respuesta recibida (GROUNDING): {response_text}")
                processing_time = time.time() - start_time
                if response_text:
                    is_markdown = self._detect_markdown(response_text)
                    self.logger.info(f"✅ [DEBUG] Respuesta procesada - Markdown: {is_markdown}")
                    return AIResponse(
                        content=response_text,
                        success=True,
                        is_markdown=is_markdown,
                        processing_time=processing_time,
                        is_structured=False
                    )
            else:
                # Modo NO-GROUNDING: respuesta estructurada con schema JSON
                self.logger.info("📋 [DEBUG] Usando modo NO-GROUNDING (respuesta estructurada)")
                from google.genai import types

                generation_config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "required": ["general_answer", "suggested_commands", "suggested_code_snippets"],
                        "properties": {
                            "general_answer": {"type": "string"},
                            "suggested_commands": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "suggested_code_snippets": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                )

                self.logger.info(f"⚙️ [DEBUG] Generation config: {generation_config}")

                # Crear contenido usando el nuevo SDK
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    ),
                ]

                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=generation_config
                )
                
                self.logger.info(f"📥 [DEBUG] Respuesta recibida (NO-GROUNDING): {response.text}")
                
                processing_time = time.time() - start_time
                
                if response.text:
                    try:
                        # Parsear respuesta JSON estructurada
                        parsed_json = json.loads(response.text)
                        self.logger.info(f"✅ [DEBUG] JSON parseado correctamente: {parsed_json}")
                        return AIResponse(
                            content=parsed_json.get("general_answer", ""),
                            success=True,
                            is_markdown=False,
                            processing_time=processing_time,
                            suggested_commands=parsed_json.get("suggested_commands", []),
                            suggested_code_snippets=parsed_json.get("suggested_code_snippets", []),
                            is_structured=True
                        )
                    except json.JSONDecodeError as e:
                        # Fallback si falla el parsing
                        self.logger.error(f"❌ [DEBUG] Error parsing JSON: {str(e)}")
                        self.logger.info(f"📄 [DEBUG] Usando respuesta como texto plano fallback")
                        return AIResponse(
                            content=response.text,
                            success=True,
                            is_markdown=self._detect_markdown(response.text),
                            processing_time=processing_time,
                            error_message=f"JSON parse error: {str(e)}",
                            is_structured=False
                        )
            
            # Si llegamos aquí, no hay respuesta
            self.logger.warning("⚠️ [DEBUG] No se recibió respuesta de la IA")
            return AIResponse(
                content="❌ No se recibió respuesta de la IA",
                success=False,
                error_message="Empty response from AI"
            )
                
        except Exception as e:
            self.logger.error(f"Error en consulta AI: {e}")
            return AIResponse(
                content=f"❌ Error al consultar IA: {str(e)}",
                success=False,
                error_message=str(e)
            )
    
    def ask_sync(self, query: str, context: Optional[str] = None, conversation_history: Optional[List[Dict]] = None) -> AIResponse:
        """
        Versión síncrona de ask() para usar en interfaces que no soporten async
        """
        try:
            # Si ya hay un loop ejecutándose, usar run_until_complete puede fallar
            try:
                loop = asyncio.get_running_loop()
                # Si hay loop corriendo, crear tarea
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.ask(query, context, conversation_history))
                    return future.result()
            except RuntimeError:
                # No hay loop corriendo, usar asyncio.run
                return asyncio.run(self.ask(query, context, conversation_history))
        except Exception as e:
            return AIResponse(
                content=f"❌ Error en consulta síncrona: {str(e)}",
                success=False,
                error_message=str(e)
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del motor de IA"""
        return {
            "initialized": self.is_initialized,
            "has_gemini": HAS_GEMINI,
            "has_api_key": bool(self.api_key),
            "model_name": "gemini-2.5-flash-lite-preview-06-17" if self.is_initialized else None
        }

    def _build_conversation_prompt(self, query: str, context: Optional[str], conversation_history: Optional[List[Dict]], grounding_mode: bool) -> str:
        """Construir prompt personalizado con configuración del usuario"""
        prompt_parts = []

        # Obtener configuración del usuario
        user_name = config_manager.get_user_name()
        user_tone = config_manager.get_user_tone()

        # Agregar fecha y hora actual (especialmente importante para grounding)
        if grounding_mode:
            from datetime import datetime
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt_parts.append(f"Fecha y hora actual: {current_datetime}")
            prompt_parts.append("IMPORTANTE: Si la consulta requiere información actualizada, usa grounding para buscar datos recientes.")

        # Agregar contexto del sistema automáticamente
        if hasattr(self, 'system_context') and self.system_context:
            prompt_parts.append(self.system_context)

        # Agregar contexto adicional si existe
        if context:
            prompt_parts.append(f"Contexto adicional: {context}")

        # Agregar historial de conversación
        if conversation_history:
            prompt_parts.append("Historial de conversación:")
            for msg in conversation_history[-10:]:  # Solo últimos 10 mensajes
                role = msg.get("role", "")
                message = msg.get("message", "")
                if role and message:
                    prompt_parts.append(f"{role}: {message}")

        # Instrucciones personalizadas según configuración del usuario
        personality_instruction = self._build_personality_instruction(user_name, user_tone, grounding_mode)
        prompt_parts.append(personality_instruction)

        # Agregar consulta actual con nombre del usuario
        prompt_parts.append(f"{user_name}: {query}")

        return "\n\n".join(prompt_parts)

    def _build_personality_instruction(self, user_name: str, user_tone: str, grounding_mode: bool) -> str:
        """Construir instrucciones de personalidad basadas en configuración"""
        base_instruction = f"""
Instrucciones de personalidad:
- El usuario se llama {user_name}
- Usa un tono {user_tone} en tus respuestas
- Dirígete al usuario por su nombre cuando sea apropiado
"""

        if grounding_mode:
            mode_instruction = """
Modo de respuesta: Proporciona una respuesta natural, conversacional y completa.
Puedes buscar información actualizada si es necesario.
Usa markdown para formatear la respuesta si es apropiado.
"""
        else:
            mode_instruction = """
Modo de respuesta: Proporciona una respuesta estructurada en formato JSON con los siguientes campos:
- "general_answer": Respuesta general personalizada para el usuario (string)
- "suggested_commands": Array de comandos de terminal útiles para Linux (array de strings)
- "suggested_code_snippets": Array de snippets de código relevantes (array de strings)

Solo usa tus conocimientos internos, no busques información online.
Enfócate en comandos prácticos y código útil para Linux.
"""

        return base_instruction + mode_instruction

    def _get_system_context(self) -> str:
        """Obtener información del sistema operativo para contexto automático"""
        try:
            # Leer /etc/os-release
            with open('/etc/os-release', 'r') as f:
                os_release_content = f.read()

            # Parsear información relevante
            os_info = {}
            for line in os_release_content.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    # Remover comillas si existen
                    value = value.strip('"\'')
                    os_info[key] = value

            # Construir contexto del sistema
            system_context_parts = []
            system_context_parts.append("=== INFORMACIÓN DEL SISTEMA ===")

            # Información básica del OS
            if 'PRETTY_NAME' in os_info:
                system_context_parts.append(f"Sistema Operativo: {os_info['PRETTY_NAME']}")
            elif 'NAME' in os_info and 'VERSION' in os_info:
                system_context_parts.append(f"Sistema Operativo: {os_info['NAME']} {os_info['VERSION']}")

            if 'ID' in os_info:
                system_context_parts.append(f"Distribución: {os_info['ID']}")

            if 'VERSION_ID' in os_info:
                system_context_parts.append(f"Versión: {os_info['VERSION_ID']}")

            if 'ID_LIKE' in os_info:
                system_context_parts.append(f"Basado en: {os_info['ID_LIKE']}")

            # Información adicional del sistema
            try:
                import platform
                system_context_parts.append(f"Arquitectura: {platform.machine()}")
                system_context_parts.append(f"Kernel: {platform.release()}")
            except:
                pass

            system_context_parts.append("=== FIN INFORMACIÓN DEL SISTEMA ===")

            return "\n".join(system_context_parts)

        except Exception as e:
            self.logger.warning(f"No se pudo obtener información del sistema: {e}")
            return "Sistema: Linux (información no disponible)"

# Crear instancia global del motor de IA
# Se inicializa sin grounding por defecto, se actualiza dinámicamente desde main.py
ai_engine = AIEngine()
