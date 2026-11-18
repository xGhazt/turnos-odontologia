# core-domain Specification

## Purpose
Define la estructura de datos base y el comportamiento de persistencia esencial para todas las entidades del sistema, incluyendo auditoría y borrado lógico.

## Requirements

### Requirement: Auditoría Automática de Entidades
El sistema DEBE registrar automáticamente la fecha y hora de creación y la última actualización para todas las entidades que hereden del mixin de auditoría.

#### Scenario: Registro de creación
- **WHEN** se crea una nueva instancia de una entidad (ej. un Rol)
- **THEN** los campos `created_at` y `updated_at` deben persistirse con la fecha y hora actual del servidor.

#### Scenario: Registro de actualización
- **WHEN** se modifica un campo de una instancia existente
- **THEN** el campo `updated_at` debe actualizarse a la fecha y hora actual, mientras que `created_at` debe permanecer inalterado.

### Requirement: Borrado Lógico (Soft Delete)
El sistema DEBE soportar el borrado lógico de registros para preservar la integridad referencial histórica, marcando los registros como inactivos en lugar de eliminarlos físicamente.

#### Scenario: Ejecución de borrado lógico
- **WHEN** se solicita la eliminación de una entidad
- **THEN** el campo `is_active` debe cambiar a `false` y `deleted_at` debe registrar la fecha y hora de la operación.

### Requirement: Entidades de Dominio Base
El sistema DEBE permitir la persistencia de Usuarios, Roles, Profesionales (con su matrícula) y Sillones (boxes de atención) con sus atributos básicos obligatorios y restricciones de integridad.

#### Scenario: Restricciones de integridad en Usuario
- **WHEN** se intenta crear un Usuario con un email que ya existe en la base de datos
- **THEN** el sistema debe lanzar un error de unicidad (IntegrityError).

#### Scenario: Persistencia de un Profesional vinculado a Usuario
- **WHEN** se intenta guardar un Profesional vinculándolo a un Usuario existente y una matrícula única
- **THEN** el sistema debe persistir el registro, permitiendo acceder al email del usuario desde la entidad profesional.

#### Scenario: Integridad de Sillones (Chairs)
- **WHEN** se crea un Sillón con un nombre identificador (ej. "Box 1")
- **THEN** el sistema debe asegurar que no existan dos sillones activos con el mismo nombre.
