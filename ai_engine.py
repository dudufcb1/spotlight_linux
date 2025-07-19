#!/usr/bin/env python3
"""
AI Engine para Spotlight Linux
Módulo para integración con Gemini AI
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
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

class AIEngine:
    """Motor de IA para procesamiento de consultas"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_initialized = False
        self.logger = logging.getLogger(__name__)
        
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
    
    async def ask(self, query: str, context: Optional[str] = None) -> AIResponse:
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
            
            # Preparar prompt con contexto si está disponible
            prompt = f"Usuario: {query}"
            if context:
                prompt = f"Contexto: {context}\n\n{prompt}"
            
            # Llamada a Gemini
            response = self.model.generate_content(prompt)
            
            processing_time = time.time() - start_time
            
            if response.text:
                is_markdown = self._detect_markdown(response.text)
                
                return AIResponse(
                    content=response.text,
                    success=True,
                    is_markdown=is_markdown,
                    processing_time=processing_time
                )
            else:
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
    
    def ask_sync(self, query: str, context: Optional[str] = None) -> AIResponse:
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
                    future = executor.submit(asyncio.run, self.ask(query, context))
                    return future.result()
            except RuntimeError:
                # No hay loop corriendo, usar asyncio.run
                return asyncio.run(self.ask(query, context))
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

# Instancia global del motor de IA
ai_engine = AIEngine()
