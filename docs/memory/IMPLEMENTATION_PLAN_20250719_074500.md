# 🎯 Task: IMPLEMENTATION_PLAN_20250719_074500
**Status:** todo | **Created:** 2025-07-19T07:45:00Z | **Project:** spotlight_linux

---

## 📋 Resumen Ejecutivo
### Solicitud del Usuario
Documentar plan aprobado e implementar nuevas características en orden lógico

### Objetivo de Negocio
Implementar memoria conversacional y code snippets según especificaciones del líder

### Estado Actual
- [ ] Análisis completado
- [ ] Solución diseñada  
- [ ] Implementación en progreso
- [ ] Testing realizado
- [ ] Entregado al usuario

---

## 🔍 Análisis Técnico

### Causa Raíz Identificada
Plan de implementación necesita documentarse para guiar desarrollo ordenado

### Archivos Afectados
- config.py
- main.py
- ai_engine.py

### Componentes Involucrados
- Memoria Conversacional
- Code Snippets UI
- Config Manager
- AI Engine
- Main UI

### Restricciones y Limitaciones
- Solo 10 mensajes en memoria
- Snippets solo en modo no-grounding
- Botón escoba antes de configuración

---

## 🛠️ Plan de Implementación

### Pasos Detallados
1. **Modificar config.py para límite 10 mensajes** (5min) - todo
2. **Agregar botón escoba en main.py header** (20min) - todo
3. **Integrar guardado memoria en main.py** (15min) - todo
4. **Integrar historial en ai_engine.py** (10min) - todo
5. **Implementar UI code snippets en main.py** (25min) - todo
6. **Testing completo de memoria + snippets** (10min) - todo

### Tiempo Estimado Total
~6 pasos definidos

### Riesgos Identificados
- **Riesgo 1:** Descripción y mitigación
- **Riesgo 2:** Descripción y mitigación

---

## 🧪 Experimentos y Pruebas

### Casos de Prueba
Ninguno registrado

### Estrategias Intentadas
Ninguna registrada

---

## 🤔 Decisiones de Diseño

### Trade-offs Considerados
- Memoria primero vs snippets primero
- Límite 10 vs 50 mensajes
- Ubicación botón escoba vs otras ubicaciones

### Alternativas Evaluadas
1. **Opción A:** Pros/Contras
2. **Opción B:** Pros/Contras
3. **Opción Elegida:** Justificación

---

## ❓ Preguntas Pendientes


---

## 🚀 Próximos Pasos
- Modificar config.py para límite 10 mensajes
- Implementar botón escoba antes de configuración
- Integrar memoria conversacional en main.py
- Integrar historial en ai_engine.py
- Implementar UI code snippets

---

## 📚 Referencias y Enlaces
- **Documentación:** Ninguno
- **Tickets Relacionados:** Ninguno
- **Diseños:** Ninguno
- **Logs/Runs:** Ninguno

---

## 📝 Notas del Agente
# Plan de Implementación de Nuevas Características - APROBADO

## Estado Inicial Verificado
- ✅ **FASE 1 - Grounding Toggle**: COMPLETADA 100%
- ❌ **FASE 2 - Code Snippets**: PENDIENTE  
- 🔄 **FASE 3 - Memoria Conversacional**: PARCIAL (backend listo)

## Plan de Implementación Aprobado

### ORDEN LÓGICO DE IMPLEMENTACIÓN

#### 1. PRIMERO: Memoria Conversacional (Fundamental)
- **Config**: Cambiar `max_history_length` de 50 a 10 mensajes
- **Main.py**: 
  - Agregar botón escoba antes del botón configuración
  - Integrar guardado de mensajes usuario/IA en cada consulta
  - Cargar historial al iniciar
- **AI Engine**: 
  - Usar historial conversacional en prompts
  - Pasar historial en método `_build_conversation_prompt`

#### 2. SEGUNDO: Code Snippets UI (Visual)
- **Main.py**:
  - Detectar respuestas estructuradas (`AIResponse.is_structured`)
  - Crear sección debajo de respuesta principal
  - Mostrar comandos y código con botones copy individuales
  - Solo en modo NO-grounding (limitación JSON schema)

### ESPECIFICACIONES TÉCNICAS

#### Memoria Conversacional
- **Límite**: 10 mensajes máximo
- **Persistencia**: JSON en directorio de configuración
- **UI**: Botón escoba (🧹) antes de configuración (⚙️)
- **Integración**: Automática en cada consulta AI

#### Code Snippets
- **Ubicación**: Debajo del área de respuesta principal
- **Estructura**: Lista de items con texto + botón copy
- **Formato**: "Comando 1 [Copiar]", "Código 1 [Copiar]"
- **Condición**: Solo si `AIResponse.is_structured == True`

### ARCHIVOS A MODIFICAR
1. `config.py` - Ajustar límite memoria
2. `main.py` - UI memoria + snippets  
3. `ai_engine.py` - Integrar historial

## APROBACIÓN DEL LÍDER
✅ Plan aprobado para implementación inmediata
✅ Orden lógico confirmado: Memoria → Snippets
✅ Especificaciones técnicas validadas

---

## 🔄 Historial de Cambios
- **2025-07-19T07:45:00Z:** Creación inicial
<!-- El agente puede añadir entradas cuando actualice la memoria -->
