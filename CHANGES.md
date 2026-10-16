# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **turnos-odontologia**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar (verificar que sus dependencias están en `openspec/changes/archive/`).
2. Leer los docs de la knowledge-base indicados en "Leer antes".
3. Ejecutar `/opsx:propose <nombre-del-change>`.
4. Al terminar el change, archivarlo con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` en este archivo.

---

## Árbol de dependencias

```
C-01 foundation-setup
  └── C-02 core-models
        └── C-03 auth-system                   ← desbloquea gestión base y frontend shell
              │
              ├── C-04 frontend-shell-auth     ← Agente C
              │
              ├── C-05 patients-management     ← Agente A (paralelo con C-06)
              │     └── C-07 appointments-engine (requiere C-05 + C-06)
              │
              └── C-06 professionals-schedules ← Agente B (paralelo con C-05)
                    └── C-07 appointments-engine
                          │
                          ├── C-08 payments-mercadopago     ← desbloquea portal de reserva y caja
                          │     ├── C-11 frontend-booking-portal (requiere C-04 + C-07 + C-08)
                          │     └── C-13 cash-register-dashboard (requiere C-08 + C-12)
                          │
                          ├── C-09 notifications-reminders   ← worker async Redis
                          │
                          ├── C-10 clinical-records-odontogram
                          │
                          └── C-12 frontend-agenda-calendar (requiere C-04 + C-07)
```

### Paralelismo por fase

> Cada "gate" es un punto de sincronización. Los changes dentro de un grupo pueden ejecutarse en paralelo.

```
GATE 0: ninguna
  → C-01 foundation-setup (solo)

GATE 1: C-01 ✓
  → C-02 core-models (solo)

GATE 2: C-02 ✓
  → C-03 auth-system (solo)

GATE 3: C-03 ✓                     ← PRIMER FORK (3 paralelos)
  → C-05 patients-management       [Agente A]
  → C-06 professionals-schedules   [Agente B]
  → C-04 frontend-shell-auth       [Agente C]

GATE 4: C-05 + C-06 ✓
  → C-07 appointments-engine       [Agente A]

GATE 5: C-07 ✓                     ← SEGUNDO FORK (3 paralelos)
  → C-10 clinical-records-odontogram [Agente A]
  → C-08 payments-mercadopago      [Agente B]
  → C-12 frontend-agenda-calendar  [Agente C — si C-04 ✓]

GATE 6: C-08 ✓
  → C-09 notifications-reminders   [Agente B]
  → C-11 frontend-booking-portal   [Agente C — si C-04 + C-07 + C-08 ✓]

GATE 7: C-08 + C-12 ✓
  → C-13 cash-register-dashboard   [Agente A]
```

### Camino crítico (7 changes — mínimo irreducible)

```
C-01 → C-02 → C-03 → C-05* → C-07 → C-08 → C-11
```
> Cadena indispensable para habilitar el flujo principal de valor: reserva online de turnos con cobro de seña verificado mediante pasarela de pagos. (*C-05 y C-06 tienen igual profundidad y ambos convergen en C-07).

### Plan óptimo con 3 agentes

```
Paso │ Agente A (Backend Core)          │ Agente B (Backend Aux)          │ Agente C (Frontend)
─────┼──────────────────────────────────┼─────────────────────────────────┼───────────────────────────────────
  1  │ C-01 foundation-setup            │                —                │                 —
  2  │ C-02 core-models                 │                —                │                 —
  3  │ C-03 auth-system                 │                —                │                 —
  4  │ C-05 patients-management         │ C-06 professionals-schedules    │ C-04 frontend-shell-auth
  5  │ C-07 appointments-engine         │                —                │                 —
  6  │ C-10 clinical-records-odontogram │ C-08 payments-mercadopago       │ C-12 frontend-agenda-calendar
  7  │                —                 │ C-09 notifications-reminders    │ C-11 frontend-booking-portal
  8  │ C-13 cash-register-dashboard     │                —                │                 —
```

---

## FASE 0 — Cimientos e Infraestructura

### [C-01] `foundation-setup`
- **Estado**: `[ ]` pendiente
- **Scope**: Scaffolding completo del monorepo e infraestructura base con Docker Compose
  - Estructura de directorios: `backend/`, `frontend/`, `docs/`, `knowledge-base/`
  - `backend/`: aplicación base FastAPI con endpoint `/api/health`, Pydantic Settings para `.env`, logging estructurado, configuración CORS para Vite y setup inicial de Alembic
  - `frontend/`: aplicación React con TypeScript y Vite, Tailwind CSS configurado, React Router v6, cliente HTTP base (Axios/Fetch) con interceptor de errores
  - `docker-compose.yml`: servicios orquestados para `backend` (FastAPI), `frontend` (Vite dev), `db` (PostgreSQL 16) y `redis` (Redis 7) con healthchecks y volumen persistente
  - Archivos `.env.example` en raíz, `backend/` y `frontend/`
  - Tests: test unitario de healthcheck en FastAPI (`GET /api/health` → `{"status": "ok"}`), script de verificación de conexión a DB y Redis
- **Dependencias**: ninguna
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance del MVP
  - `knowledge-base/02_descripcion_general.md` §Stack Tecnológico
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de Directorios Propuesta
  - `knowledge-base/09_decisiones_y_supuestos.md` §Decisiones de Arquitectura

---

### [C-02] `core-models`
- **Estado**: `[ ]` pendiente
- **Scope**: Modelos base de SQLAlchemy, mixins transversales, repositorios genéricos y seed mínimo
  - Modelos SQLAlchemy: `Base`, `AuditMixin` (`created_at`, `updated_at`, `is_active`, `deleted_at`)
  - Entidades base: `User`, `Role`, `Professional` (matrícula, especialidad), `Chair` (box/sillón de atención)
  - Patrón Repository: `BaseRepository[T]` genérico con operaciones CRUD y sesión asíncrona inyectada vía `Depends(get_db)`
  - Migración Alembic 001: tablas `users`, `roles`, `professionals`, `chairs` con restricciones de unicidad e índices
  - Script de seed inicial: usuarios de prueba para roles Admin, Odontólogo, Secretaria y Paciente; configuración de Box 1 y Box 2; datos 100% ficticios (**RN-06**)
  - Tests: persistencia de entidades, funcionamiento de soft delete con `AuditMixin`, restricciones de unicidad en base de datos
- **Dependencias**: C-01
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Entidades Principales y §Seed Data Requerido
  - `knowledge-base/05_reglas_de_negocio.md` §RN-06 (Privacidad de Datos Sensibles)
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones de Diseño
  - `knowledge-base/09_decisiones_y_supuestos.md` §Decisiones de Arquitectura (PostgreSQL y SQLAlchemy)

---

## FASE 1 — Autenticación y Shell de Frontend

### [C-03] `auth-system`
- **Estado**: `[ ]` pendiente
- **Scope**: Sistema completo de autenticación JWT y control de acceso basado en roles (RBAC)
  - Endpoints REST en `app/api/v1/auth.py`:
    - `POST /api/v1/auth/login` (login con email y contraseña, hash bcrypt/passlib, rate limiting)
    - `POST /api/v1/auth/refresh` (rotación de refresh tokens con almacenamiento/blacklist en Redis)
    - `POST /api/v1/auth/logout` (invalidación del token activo)
    - `GET /api/v1/auth/me` (perfil del usuario autenticado con roles y permisos asociados)
  - Dependencias de seguridad FastAPI: `get_current_user`, `require_role(["admin", "odontologo", "secretaria", "paciente"])` conforme a la matriz RBAC
  - Refresh token gestionado en cookie HttpOnly (secure, samesite=lax)
  - Tests: login exitoso, rechazo por credenciales inválidas, bloqueo por token expirado, autorización por roles permitidos/denegados
- **Dependencias**: C-02
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Matriz RBAC y §Rutas y Accesibilidad
  - `knowledge-base/04_modelo_de_datos.md` §Usuario
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad y Variables de Entorno
  - `knowledge-base/09_decisiones_y_supuestos.md` §Decisiones de Arquitectura (JWT)

---

### [C-04] `frontend-shell-auth`
- **Estado**: `[ ]` pendiente
- **Scope**: Shell de la aplicación React con enrutador, layouts y autenticación integrada
  - Enrutamiento con React Router v6: `PublicLayout`, `AuthLayout` y `DashboardLayout` con barra lateral y menú adaptativo según rol del usuario
  - Estado global de autenticación (`AuthContext` o store liviano): manejo de login, logout, persistencia en sesión y redirección automática tras expiración
  - Vistas completas de inicio de sesión (`/login`) y registro público básico (`/registro`)
  - Rutas protegidas (`ProtectedRoute`) que validan autenticación y rol requerido
  - Componentes transversales de UI: Navbar, Sidebar, modal de confirmación, toasts de notificación
  - Tests: renderizado del formulario de login, validación de campos obligatorios, redirección de usuarios no autenticados
- **Dependencias**: C-03
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Stack Tecnológico (Frontend)
  - `knowledge-base/03_actores_y_roles.md` §Rutas y Accesibilidad
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de Directorios Propuesta (frontend)

---

## FASE 2 — Gestión Base (Pacientes, Profesionales y Horarios)

### [C-05] `patients-management`
- **Estado**: `[ ]` pendiente
- **Scope**: Modelo y API REST para gestión integral del padrón de pacientes
  - Modelo SQLAlchemy `Patient`: nombres, apellidos, DNI, teléfono, email, fecha de nacimiento, obra social/prepaga, número de afiliado, antecedentes médicos
  - Validación de negocio estricta: DNI único e irrepetible en el sistema (**RN-04**)
  - Endpoints REST en `app/api/v1/patients.py`:
    - `GET /api/v1/patients` (listado paginado con búsqueda por DNI, apellido o nombre)
    - `POST /api/v1/patients` (alta de nuevo paciente con validación de DNI duplicado)
    - `GET /api/v1/patients/{id}` (detalle completo de ficha del paciente)
    - `PUT /api/v1/patients/{id}` (modificación de datos de contacto y cobertura médica)
  - Migración Alembic 002: tabla `patients` con índice único sobre campo `dni`
  - Tests: creación exitosa de paciente, error 409 por DNI duplicado, paginación y búsqueda por término parcial
- **Dependencias**: C-03
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Paciente
  - `knowledge-base/05_reglas_de_negocio.md` §RN-04 (Identificación Única por DNI) y §RN-06 (PII Ficticia)
  - `knowledge-base/06_funcionalidades.md` §Épica 2 (F-04)
  - `knowledge-base/10_preguntas_abiertas.md` §PA-01 (Manejo de Obras Sociales en MVP)

---

### [C-06] `professionals-schedules`
- **Estado**: `[ ]` pendiente
- **Scope**: Gestión de odontólogos, configuración de consultorios/sillones y cálculo de franjas horarias
  - Modelo SQLAlchemy `Schedule`: vinculación entre `Professional` y `Chair`, día de la semana (0-6), hora de inicio, hora de fin y duración estándar del turno (ej. 30/60 min)
  - Endpoints REST en `app/api/v1/professionals.py` y `schedules.py`:
    - `GET /api/v1/professionals` (listado con especialidades)
    - `POST /api/v1/professionals` (alta de odontólogo con matrícula)
    - `GET /api/v1/chairs` y `POST /api/v1/chairs` (administración de boxes físicos)
    - `GET /api/v1/schedules` y `POST /api/v1/schedules` (definición de grilla horaria por box y profesional)
    - `GET /api/v1/professionals/{id}/availability?date=YYYY-MM-DD` (cálculo de slots libres considerando horarios laborales configurados)
  - Migración Alembic 003: tabla `schedules` con claves foráneas e índices compuestos
  - Tests: asignación de grilla horaria, prevención de configuración de franjas horarias invertidas o solapadas, cálculo de disponibilidad base
- **Dependencias**: C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Profesional, §Consultorio / Sillón y §Agenda / Horarios
  - `knowledge-base/05_reglas_de_negocio.md` §RN-01 (Exclusividad de Sillón y Profesional)
  - `knowledge-base/06_funcionalidades.md` §Épica 1 (F-01)
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (Paso 1 y 2)

---

## FASE 3 — Núcleo de Agenda y Turnos

### [C-07] `appointments-engine`
- **Estado**: `[ ]` pendiente
- **Scope**: Motor transaccional de turnos con validación ACID anti-solapamiento y máquina de estados
  - Modelo SQLAlchemy `Appointment`: paciente_id, profesional_id, chair_id, fecha_hora_inicio, fecha_hora_fin, motivo, costo_total, monto_seña, estado (`pendiente_seña`, `confirmado`, `en_espera`, `atendido`, `cancelado`, `ausente`), notas_cancelacion
  - Control de concurrencia y atomicidad ACID en PostgreSQL: validación estricta de exclusividad (**RN-01** — ni el mismo profesional ni el mismo sillón/box pueden tener dos citas en la misma franja)
  - Máquina de estados formal: transiciones permitidas, auditoría de cambios de estado y registro obligatorio del motivo en cancelaciones (**F-03**)
  - Endpoints REST en `app/api/v1/appointments.py`:
    - `POST /api/v1/appointments` (creación de turno con bloqueo de slot y cálculo de seña)
    - `GET /api/v1/appointments` (filtrado por rango de fechas, profesional, box y estado)
    - `GET /api/v1/appointments/{id}` (detalle del turno)
    - `PUT /api/v1/appointments/{id}/reschedule` (reprogramación con validación de disponibilidad en nueva fecha/hora)
    - `POST /api/v1/appointments/{id}/cancel` (cancelación registrando motivo)
    - `PATCH /api/v1/appointments/{id}/status` (cambio de estado operativo: `en_espera`, `atendido`, `ausente`)
  - Migración Alembic 004: tabla `appointments` con índices por profesional, box, fecha y restricciones
  - Tests: reserva exitosa, colisión concurrente por mismo box rechazada (409 Conflict), colisión por mismo profesional rechazada, reprogramación válida, cancelación con motivo
- **Dependencias**: C-05, C-06
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Turno
  - `knowledge-base/05_reglas_de_negocio.md` §RN-01 (Exclusividad de Sillón y Profesional)
  - `knowledge-base/06_funcionalidades.md` §Épica 1 (F-01, F-02, F-03)
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (Reserva de Turno)
  - `knowledge-base/08_arquitectura_propuesta.md` §Transacciones Atómicas (ACID)

---

## FASE 4 — Integraciones Asíncronas y Pagos

### [C-08] `payments-mercadopago`
- **Estado**: `[ ]` pendiente
- **Scope**: Integración con Mercado Pago para cobro de señas obligatorias, webhooks y timeout de liberación
  - Modelo SQLAlchemy `Payment`: appointment_id, preference_id, payment_id_mp, status (`pendiente`, `aprobado`, `rechazado`, `reembolsado`), payment_method, amount, currency (ARS), paid_at
  - Servicio de Checkout Pro de Mercado Pago: generación de preferencia de pago al reservar turno (seña configurada, ej. 30%, **RN-02**)
  - Endpoint de Webhook IPN: `POST /api/v1/payments/webhook` con validación de firma y procesamiento idempotente
  - Actualización transaccional: confirmación automática del turno (`pendiente_seña` → `confirmado`) al aprobarse el pago
  - Tarea periódica asíncrona con Redis (worker): liberación y cancelación automática de turnos en `pendiente_seña` tras 30 minutos sin pago confirmado (**RN-02**)
  - Lógica de política de cancelación: retención o devolución de seña según ventana límite de 24 horas (**RN-03**)
  - Migración Alembic 005: tabla `payments`
  - Tests: creación de preferencia (mock), webhook con pago aprobado, idempotencia ante webhooks duplicados, tarea de liberación tras 30 minutos, retención de seña según ventana horaria
- **Dependencias**: C-07
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Pago / Seña
  - `knowledge-base/05_reglas_de_negocio.md` §RN-02 (Política de Seña Obligatoria) y §RN-03 (Política de Cancelación y Retención)
  - `knowledge-base/06_funcionalidades.md` §Épica 3 (F-06)
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (Pasos 4 a 7)
  - `knowledge-base/08_arquitectura_propuesta.md` §Webhooks Asíncronos
  - `knowledge-base/10_preguntas_abiertas.md` §PA-02 y §PA-03 (Moneda ARS y Contingencia)

---

### [C-09] `notifications-reminders`
- **Estado**: `[ ]` pendiente
- **Scope**: Worker asíncrono en Redis para recordatorios automáticos y webhook de confirmación interactiva
  - Capa de abstracción `NotificationProvider` con interfaz común (preparada para API oficial Meta o proveedor alternativo, **PA-05**) y driver de simulación/desarrollo
  - Tarea programada (scheduler/cron): barrido periódico en Redis de turnos en estado `confirmado` para enviar recordatorios automáticos 24 horas y 2 horas antes de la cita (**F-08**)
  - Plantillas de mensaje con datos del turno (fecha, hora, odontólogo, dirección del consultorio) y botones de acción ("Confirmar Asistencia" / "Cancelar Turno") (**F-09**)
  - Endpoint de Webhook interactivo: `POST /api/v1/notifications/webhook/whatsapp` para capturar la respuesta del paciente
  - Lógica de actualización: si el paciente confirma, el turno pasa a `asistencia_confirmada`; si cancela, se evalúa política de 24 horas (**RN-03**)
  - Tests: encolado de recordatorios en Redis, generación de payloads de mensaje, procesamiento de confirmación por webhook, procesamiento de cancelación por webhook
- **Dependencias**: C-07
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Integraciones Externas (WhatsApp)
  - `knowledge-base/06_funcionalidades.md` §Épica 4 (F-08, F-09)
  - `knowledge-base/07_flujos_principales.md` §Flujo 2 (Recordatorio y Confirmación Automática)
  - `knowledge-base/08_arquitectura_propuesta.md` §Tareas Asíncronas / Webhooks
  - `knowledge-base/10_preguntas_abiertas.md` §PA-05 (Proveedor WhatsApp)

---

## FASE 5 — Módulos Clínicos y Experiencia de Usuario

### [C-10] `clinical-records-odontogram`
- **Estado**: `[ ]` pendiente
- **Scope**: Ficha clínica odontológica y odontograma digital básico por paciente y turno
  - Modelo SQLAlchemy `ClinicalRecord`: appointment_id, patient_id, professional_id, motivo_consulta, diagnostico, tratamientos_realizados, notas_privadas, odontograma_data (JSONB con estado de piezas dentales 11 a 48)
  - Componente de odontograma digital básico: visualización por cuadrantes (FDI) con asignación de estados visuales (sano, caries, obturado, ausente, tratamiento de conducto)
  - Endpoints REST en `app/api/v1/clinical-records.py`:
    - `GET /api/v1/patients/{id}/clinical-records` (historial cronológico completo del paciente)
    - `POST /api/v1/appointments/{id}/clinical-records` (registro de evolución clínica al atender la cita)
    - `GET /api/v1/patients/{id}/odontogram` (estado consolidado actual del odontograma)
  - Control de acceso: solo accesible por odontólogos y directores médicos (bloqueado para pacientes y secretarias)
  - Migración Alembic 006: tabla `clinical_records` con soporte JSONB para el estado del odontograma
  - Tests: guardado de evolución clínica, actualización de piezas en odontograma JSONB, validación de permisos RBAC
- **Dependencias**: C-07
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance del MVP (Odontograma básico)
  - `knowledge-base/03_actores_y_roles.md` §Odontólogo y §Matriz RBAC (Historia Clínica)
  - `knowledge-base/04_modelo_de_datos.md` §Tratamiento / Evolución
  - `knowledge-base/06_funcionalidades.md` §Épica 2 (F-05)
  - `knowledge-base/07_flujos_principales.md` §Flujo 3 (Atención en Consultorio)

---

### [C-11] `frontend-booking-portal`
- **Estado**: `[ ]` pendiente
- **Scope**: Portal web público y responsive para que los pacientes reserven turnos y abonen la seña online
  - Flujo guiado paso a paso (Wizard) en ruta pública `/reservar-turno`:
    - Paso 1: Selección de especialidad, profesional preferido y rango de fechas
    - Paso 2: Selección interactiva de franja horaria disponible (consumo de slots reactivos)
    - Paso 3: Identificación del paciente por DNI (**RN-04**) y datos de contacto (teléfono para WhatsApp)
    - Paso 4: Resumen de reserva con desglose de seña obligatoria (**RN-02**) y botón de checkout Mercado Pago
    - Paso 5: Pantalla de confirmación con código de reserva, instrucciones y advertencia sobre cancelación con 24 horas (**RN-03**)
  - Integración del botón de pago de Mercado Pago (redirección a Checkout Pro o modal)
  - Manejo de estados de carga, expiración de reserva temporal (contador regresivo de 30 minutos) y errores de concurrencia
  - Interfaz 100% responsive optimizada para dispositivos móviles
  - Tests: validación del wizard de reserva, verificación de DNI, redirección a pago, contador regresivo de 30 min
- **Dependencias**: C-04, C-07, C-08
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Paciente y §Rutas y Accesibilidad
  - `knowledge-base/05_reglas_de_negocio.md` §RN-02 (Seña Obligatoria), §RN-03 (Cancelación) y §RN-04 (DNI)
  - `knowledge-base/06_funcionalidades.md` §Épica 1 (F-01) y §Épica 3 (F-06)
  - `knowledge-base/07_flujos_principales.md` §Flujo 1 (Reserva de Turno con Seña Online)

---

### [C-12] `frontend-agenda-calendar`
- **Estado**: `[ ]` pendiente
- **Scope**: Vista de calendario interactivo multi-profesional y multi-sillón para secretarias y odontólogos
  - Vista principal en `/agenda`:
    - Grilla de calendario con vistas diaria, semanal y mensual
    - Selector/filtro por profesional y por sillón/box de atención
    - Código de colores visual por estado del turno (`pendiente_seña`, `confirmado`, `asistencia_confirmada`, `en_espera`, `atendido`, `cancelado`)
  - Modal de alta rápida de turno presencial o telefónico por parte de recepcionistas
  - Modal de reprogramación ágil (cambio de fecha/hora validando disponibilidad en tiempo real)
  - Acciones rápidas de recepción: marcar paciente `en_espera`, marcar `atendido` o registrar `ausente`
  - Modal de cancelación con campo obligatorio de motivo (**F-03**)
  - Tests: renderizado de slots en grilla horaria, cambio de vistas diaria/semanal, apertura de modal de nuevo turno, filtrado por profesional
- **Dependencias**: C-04, C-07
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Odontólogo, §Secretaria y §Rutas
  - `knowledge-base/05_reglas_de_negocio.md` §RN-01 (Exclusividad de Sillón y Profesional)
  - `knowledge-base/06_funcionalidades.md` §Épica 1 (F-02, F-03)
  - `knowledge-base/07_flujos_principales.md` §Flujo 3 (Atención en Consultorio y Cierre de Cita)

---

## FASE 6 — Cierre Operativo y Caja

### [C-13] `cash-register-dashboard`
- **Estado**: `[ ]` pendiente
- **Scope**: Control de caja diario, cobro de saldos restantes presenciales, métricas de recepción y bloqueo de pacientes
  - Modelo SQLAlchemy `CashMovement`: concepto, tipo (ingreso/egreso), monto, medio_pago (efectivo, tarjeta, transferencia), appointment_id, registrado_por
  - Endpoints REST en `app/api/v1/cash.py`:
    - `GET /api/v1/cash/daily-summary` (arqueo de caja: total señas online + total cobrado en consultorio)
    - `POST /api/v1/cash/transactions` (registro de cobro del saldo restante del turno al finalizar atención)
    - `GET /api/v1/cash/appointments-balance` (listado de citas del día con estado de cobro: seña abonada, saldo pendiente)
  - Lógica de bloqueo automático: paciente con 2 ausencias sin aviso previo (**RN-05**) queda marcado como `bloqueado_online: true`
  - Interfaz de usuario en `/caja`: tabla de movimientos del día, botón de cobro de saldo y resumen de ingresos
  - Migración Alembic 007: tabla `cash_movements` y columna `no_shows_count` en `patients`
  - Tests: cálculo de saldo deudor por turno, registro de cobro presencial, arqueo de caja diario, aplicación de bloqueo por 2 inasistencias (**RN-05**)
- **Dependencias**: C-08, C-12
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §Secretaria y §Administrador
  - `knowledge-base/05_reglas_de_negocio.md` §RN-03 (Retención de seña) y §RN-05 (Bloqueo por Ausencias Reiteradas)
  - `knowledge-base/06_funcionalidades.md` §Épica 3 (F-07)
  - `knowledge-base/07_flujos_principales.md` §Flujo 3 (Paso 4: Cobro del saldo restante)
  - `knowledge-base/10_preguntas_abiertas.md` §PA-07 (Facturación / Alcance MVP)
