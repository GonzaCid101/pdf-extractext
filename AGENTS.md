# Instrucciones para Agentes de IA

Este proyecto sigue lineamientos estrictos de Clean Architecture (3 capas) y principios SOLID, KISS y DRY.

## Convención TDD (Test-Driven Development)

Al implementar nuevas funcionalidades, debes evidenciar el ciclo TDD utilizando los siguientes pasos y comentarios explícitos en el código:

1. **RED:** Crea el test unitario primero y verifica que falla. Debe incluir el comentario: `# FASE RED: Este test fallará inicialmente`.
2. **GREEN:** Implementa la solución mínima necesaria para que el test pase. Debe incluir el comentario: `# FASE GREEN: Implementación mínima para pasar el test`.
3. **REFACTOR:** Mejora la implementación manteniendo los tests en verde (aplicando DRY y KISS), sin alterar el comportamiento.