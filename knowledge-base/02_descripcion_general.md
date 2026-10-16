# 02 — Descripción General

## Stack Tecnológico
- **Frontend:** React (SPA) con TypeScript y Vite como bundler, más Tailwind CSS para una interfaz moderna, limpia y responsive.
- **Backend:** Python con FastAPI (API REST) y autenticación basada en JWT.
- **ORM / Migraciones:** SQLAlchemy para el mapeo objeto-relacional (migraciones con Alembic).
- **Base de Datos:** PostgreSQL para datos relacionales estructurados (pacientes, turnos, profesionales, pagos).
- **Mensajería / Cola Asíncrona:** Redis para las funcionalidades asincrónicas (recordatorios, tareas en segundo plano).
- **Infraestructura / Contenedores:** Docker y Docker Compose para el entorno de desarrollo y despliegue.
- **Control de Versiones:** Git / GitHub sobre rama de trabajo y flujo OpenSpec.

## Arquitectura General
El sistema adopta un **monolito modular escalable con arquitectura en capas** (routers → services → repositories → models), separando claramente:
1. **Capa de Presentación (Frontend):** Interfaz web orientada a usuario final, recepcionistas y odontólogos.
2. **Capa de Aplicación (Backend API REST):** Lógica de negocio, autenticación JWT, validación de reglas de negocio y transacciones de agenda.
3. **Capa de Datos:** PostgreSQL con SQLAlchemy como ORM para garantizar atomicidad en la reserva de turnos y evitar condiciones de carrera (race conditions) en la agenda.

## Integraciones Externas
- **WhatsApp Business API:** Envío automático de recordatorios de turnos (24hs y 2hs antes) y links de seña.
- **Mercado Pago API:** Procesamiento de pagos de señas para confirmación de turnos.
- **Google Calendar (Opcional):** Sincronización bidireccional de turnos para los profesionales.
