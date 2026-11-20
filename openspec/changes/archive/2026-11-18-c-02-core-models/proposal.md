## Why

El sistema requiere una base sólida de persistencia y modelos de dominio para soportar las funcionalidades de autenticación y gestión que siguen en el roadmap. Sin estos modelos base, no existe una estructura para almacenar usuarios, profesionales o la infraestructura física (sillones) del consultorio.

## What Changes

- Implementación de la clase `Base` de SQLAlchemy y `AuditMixin` para auditoría automática (created_at, updated_at, deleted_at).
- Definición de entidades núcleo: `User`, `Role`, `Professional` y `Chair`.
- Implementación del patrón Repository genérico para desacoplar la lógica de acceso a datos.
- Configuración de la primera migración de base de datos con Alembic.
- Script de seed con datos 100% ficticios para roles y configuración inicial.

## Capabilities

### New Capabilities
- `core-domain`: Definición de las entidades base del sistema, su persistencia y comportamiento de auditoría.

### Modified Capabilities
- (ninguna)

## Impact

- **Base de Datos**: Creación de las tablas iniciales en PostgreSQL.
- **Backend**: Introducción de los modelos de SQLAlchemy y la infraestructura de repositorios asíncronos.
- **Alembic**: Inicialización del historial de migraciones.
