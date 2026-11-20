## Context

El sistema ya posee una configuración base (`C-01`) con Docker y FastAPI. Este diseño establece la arquitectura de persistencia asíncrona necesaria para el resto del desarrollo. Se requiere compatibilidad con PostgreSQL 16 y el uso de SQLAlchemy 2.0 con patrones modernos de Python.

## Goals / Non-Goals

**Goals:**
- Implementar un modelo de datos extensible mediante mixins.
- Proveer una capa de abstracción (Repositories) que facilite el testing.
- Garantizar que todas las entidades tengan trazabilidad de creación y modificación.

**Non-Goals:**
- Implementar lógica de autenticación (esto corresponde a `C-03`).
- Definir modelos relacionados con turnos o historias clínicas (correspondiente a fases posteriores).

## Decisions

### 1. Mixins de Auditoría y Borrado Lógico
Se utilizará un Mixin `AuditMixin` que incluirá `created_at`, `updated_at`, `deleted_at` e `is_active`.
- **Razón**: Evita la duplicación de código en cada modelo y estandariza el comportamiento de auditoría.
- **Alternativa**: Heredar de una clase `Base` única, pero los mixins ofrecen más flexibilidad si algunas tablas no requieren auditoría total.

### 2. Patrón Repository Genérico
Se implementará `BaseRepository[T]` con métodos asíncronos para operaciones CRUD básicas.
- **Razón**: Desacopla la lógica de negocio del ORM, facilitando el cambio de implementación o el uso de mocks en tests unitarios.
- **Alternativa**: Usar la sesión de SQLAlchemy directamente en las rutas de FastAPI. Se descarta para mantener la arquitectura limpia y facilitar el mantenimiento.

### 3. Migraciones con Alembic (Async)
Se configurará Alembic para usar el driver `postgresql+asyncpg`.
- **Razón**: Consistencia con el stack asíncrono definido en `C-01`.

## Risks / Trade-offs

- **[Riesgo] Complejidad del Patrón Repository** → El uso de genéricos en Python (`TypeVar`) puede ser complejo de tipar inicialmente. **Mitigación**: Usar una implementación simple y bien documentada siguiendo las convenciones de FastAPI.
- **[Riesgo] Drift entre modelos y base de datos** → Las migraciones manuales pueden fallar. **Mitigación**: Ejecutar tests que validen la creación del schema en una base de datos de prueba limpia.
