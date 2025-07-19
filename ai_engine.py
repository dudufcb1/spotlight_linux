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
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

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
    """Motor de IA para procesamiento de consultas"""
    
    def __init__(self, api_key: Optional[str] = None, grounding_enabled: bool = False):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.grounding_enabled = grounding_enabled
        self.model = None
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
            self.logger.warning("Google GenerativeAI no está disponible. Instale: pip install google-generativeai")
            return
            
        if not self.api_key:
            self.logger.warning("API key de Gemini no encontrada. Configure GEMINI_API_KEY en variables de entorno")
            return
            
        self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Inicializar conexión con Gemini"""
        try:
            genai.configure(api_key=self.api_key)
            # Usar modelo gemini-2.5-flash-lite-preview-06-17
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
            self.is_initialized = True
            self.logger.info("Motor AI inicializado correctamente con Gemini")
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
            
            # Preparar prompt base
            prompt = f"Usuario: {query}"
            if context:
                prompt = f"Contexto: {context}\n\n{prompt}"
            
            self.logger.info(f"📤 [DEBUG] Prompt enviado: {prompt}")
            
            if self.grounding_enabled:
                # Modo GROUNDING: respuesta natural sin restricciones
                self.logger.info("🌐 [DEBUG] Usando modo GROUNDING (respuesta natural)")
                response = self.model.generate_content(prompt)

                # Logging de la respuesta RAW completa para diagnóstico
                try:
                    self.logger.info(f"� [DEBUG] Respuesta RAW (GROUNDING): {response}")
                    # Si el objeto tiene __dict__ o atributos útiles, loguear también
                    if hasattr(response, '__dict__'):
                        self.logger.info(f"🟣 [DEBUG] Respuesta __dict__ (GROUNDING): {vars(response)}")
                except Exception as e:
                    self.logger.error(f"[DEBUG] Error al loguear respuesta RAW: {e}")

                self.logger.info(f"📥 [DEBUG] Respuesta recibida (GROUNDING): {response.text}")

                processing_time = time.time() - start_time

                if response.text:
                    is_markdown = self._detect_markdown(response.text)
                    self.logger.info(f"✅ [DEBUG] Respuesta procesada - Markdown: {is_markdown}")
                    return AIResponse(
                        content=response.text,
                        success=True,
                        is_markdown=is_markdown,
                        processing_time=processing_time,
                        is_structured=False
                    )
            else:
                # Modo NO-GROUNDING: respuesta estructurada con schema JSON
                self.logger.info("📋 [DEBUG] Usando modo NO-GROUNDING (respuesta estructurada)")
                generation_config = genai.GenerationConfig(
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
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=generation_config
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

# Crear instancia global del motor de IA
# Se inicializa sin grounding por defecto, se actualiza dinámicamente desde main.py
ai_engine = AIEngine()
