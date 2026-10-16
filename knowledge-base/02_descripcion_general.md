# 02 — Descripción General

## Stack Tecnológico
- **Frontend:** React (SPA) con Tailwind CSS para una interfaz moderna, limpia y responsive.
- **Backend:** Node.js / Express o Python / FastAPI (según definición de implementación).
- **Base de Datos:** PostgreSQL para datos relacionales estructurados (pacientes, turnos, profesionales, pagos).
- **Control de Versiones:** Git / GitHub sobre rama de trabajo y flujo OpenSpec.

## Arquitectura General
El sistema adopta una arquitectura de microservicios lógicos o monolito modular escalable (Clean Architecture / MVC modular), separando claramente:
1. **Capa de Presentación (Frontend):** Interfaz web orientada a usuario final, recepcionistas y odontólogos.
2. **Capa de Aplicación (Backend API REST):** Lógica de negocio, autenticación JWT, validación de reglas de negocio y transacciones de agenda.
3. **Capa de Datos:** PostgreSQL con ORM / Query builder para garantizar atomicidad en la reserva de turnos y evitar condiciones de carrera (race conditions) en la agenda.

## Integraciones Externas
- **WhatsApp Business API:** Envío automático de recordatorios de turnos (24hs y 2hs antes) y links de seña.
- **Mercado Pago API:** Procesamiento de pagos de señas para confirmación de turnos.
- **Google Calendar (Opcional):** Sincronización bidireccional de turnos para los profesionales.
