# Spec Delta

## Purpose

Gestión integral del padrón de pacientes: modelo, validaciones de negocio (DNI único según RN-04), API REST CRUD con búsqueda y paginación, sirviendo como base para turnos, historia clínica y caja.

## ADDED Requirements

### Requirement: Alta de paciente con validación de DNI único
El sistema DEBE permitir crear un nuevo paciente validando que el DNI no exista en el padrón (RN-04). Si el DNI ya está registrado, DEBE rechazar la creación con error 409 Conflict y mensaje claro.

#### Scenario: Creación exitosa de paciente con DNI nuevo
- **WHEN** se envía POST /api/v1/patients con DNI no existente y datos válidos
- **THEN** el sistema crea el paciente, asigna ID, registra timestamps de auditoría y responde 201 con el paciente creado

#### Scenario: Rechazo por DNI duplicado
- **WHEN** se envía POST /api/v1/patients con un DNI que ya existe en la base de datos
- **THEN** el sistema responde 409 Conflict con detalle "DNI ya registrado"

#### Scenario: Rechazo por datos inválidos
- **WHEN** se envía POST /api/v1/patients con email inválido, DNI con formato incorrecto o campos obligatorios faltantes
- **THEN** el sistema responde 422 Unprocessable Entity con errores de validación específicos

### Requirement: Consulta de paciente por ID
El sistema DEBE permitir obtener la ficha completa de un paciente por su identificador interno.

#### Scenario: Consulta exitosa de paciente existente
- **WHEN** se envía GET /api/v1/patients/{id} con ID de paciente existente y activo
- **THEN** el sistema responde 200 con todos los campos del paciente (incluyendo obra social, afiliado, antecedentes)

#### Scenario: Paciente no encontrado
- **WHEN** se envía GET /api/v1/patients/{id} con ID que no existe o está marcado como inactivo (soft delete)
- **THEN** el sistema responde 404 Not Found

### Requirement: Listado paginado con búsqueda
El sistema DEBE exponer un listado de pacientes con paginación y búsqueda por DNI, apellido o nombre (coincidencia parcial, insensible a mayúsculas).

#### Scenario: Listado paginado sin filtros
- **WHEN** se envía GET /api/v1/patients con parámetros page=1 y size=20
- **THEN** el sistema responde 200 con lista de pacientes, metadatos de paginación (total, page, size, total_pages) y pacientes ordenados por apellido, nombre

#### Scenario: Búsqueda por DNI parcial
- **WHEN** se envía GET /api/v1/patients con query "12345"
- **THEN** el sistema responde 200 con pacientes cuyo DNI contiene "12345"

#### Scenario: Búsqueda por apellido parcial
- **WHEN** se envía GET /api/v1/patients con query "García"
- **THEN** el sistema responde 200 con pacientes cuyo apellido contiene "García" (insensible a mayúsculas)

#### Scenario: Búsqueda por nombre parcial
- **WHEN** se envía GET /api/v1/patients con query "Juan"
- **THEN** el sistema responde 200 con pacientes cuyo nombre contiene "Juan" (insensible a mayúsculas)

#### Scenario: Página vacía fuera de rango
- **WHEN** se envía GET /api/v1/patients con page mayor a total_pages
- **THEN** el sistema responde 200 con lista vacía y metadatos de paginación correctos

### Requirement: Modificación de datos de contacto y cobertura
El sistema DEBE permitir actualizar teléfono, email, obra social, número de afiliado y antecedentes médicos de un paciente existente. El DNI NO DEBE ser modificable.

#### Scenario: Actualización exitosa de datos de contacto
- **WHEN** se envía PUT /api/v1/patients/{id} con teléfono y email nuevos válidos
- **THEN** el sistema actualiza los campos, refresca updated_at y responde 200 con el paciente actualizado

#### Scenario: Actualización de obra social y afiliado
- **WHEN** se envía PUT /api/v1/patients/{id} con nueva obra social y número de afiliado
- **THEN** el sistema actualiza los campos de cobertura médica y responde 200

#### Scenario: Intento de modificación de DNI rechazado
- **WHEN** se envía PUT /api/v1/patients/{id} intentando cambiar el campo DNI
- **THEN** el sistema ignora el cambio de DNI (o responde 422) y mantiene el DNI original

#### Scenario: Actualización de paciente inexistente
- **WHEN** se envía PUT /api/v1/patients/{id} con ID que no existe
- **THEN** el sistema responde 404 Not Found

### Requirement: Auditoría automática en pacientes
El sistema DEBE registrar created_at y updated_at automáticamente en cada paciente, y soportar soft delete (is_active, deleted_at) para preservar integridad referencial.

#### Scenario: Timestamps en creación
- **WHEN** se crea un nuevo paciente
- **THEN** created_at y updated_at se establecen al momento de la creación

#### Scenario: updated_at en modificación
- **WHEN** se actualiza un paciente existente
- **THEN** updated_at se actualiza al momento de la modificación y created_at permanece inalterado

#### Scenario: Soft delete preserva datos
- **WHEN** se elimina lógicamente un paciente (is_active=false, deleted_at=now)
- **THEN** el paciente deja de aparecer en listados y búsquedas activas, pero sus datos persisten en BD para integridad referencial con turnos e historia clínica