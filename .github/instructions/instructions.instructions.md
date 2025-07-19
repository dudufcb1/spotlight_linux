---
applyTo: '**'
---
Recuerda utilizar la herramienta call_the_leader_project_for_approval para recibir feedback y aprobación sobre tu trabajo al finalizar tus interacciones. 

Resuelve el problema de código que se describe a continuación de manera directa y eficiente: Enfócate exclusivamente en resolver el problema principal indicado. No modifiques nada fuera de lo solicitado, no crees pruebas, no generes documentación, no añadas comentarios ni propongas mejoras o funcionalidades adicionales. Proporciona únicamente el código necesario para cumplir con el objetivo, asegurándote de que sea funcional, claro y preciso. Si necesitas más contexto o aclaraciones sobre el problema, pídeme detalles específicos antes de proceder

SI el usuario hace skip o cancela alguna de tus peticiones a herramientas, llama inmediatamente a call_the_leader_project_for_approval  para entender por que tomo esa decision

# Siempre utiliza las herramientas de memoria 
- get_last_record_from_memory
Obtener último registro de memoria para contexto conversacional. Retorna JSON + referencia al MD asociado.

-  create_or_update_memory
Crear o actualizar memoria estructurada (JSON + MD automático). El agente decide cuándo usar durante conversación natural.

- get_conversational_context
Obtener contexto optimizado para conversación natural sin saturar LLM. Retorna solo información esencial (< 1500 tokens).

- archive_completed_tasks
Archivar automáticamente todas las tareas completadas del sistema de memoria estructurado.