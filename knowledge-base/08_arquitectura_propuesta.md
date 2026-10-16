# 08 — Arquitectura Propuesta

## Patrones de Diseño
- **Arquitectura en Capas:** Separación entre presentación, servicios de negocio y acceso a datos (routers → services → repositories → models).
- **Inyección de Dependencias:** Uso de `Depends` de FastAPI para sesiones de base de datos y autenticación.
- **Transacciones Atómicas (ACID):** Uso de transacciones en PostgreSQL para evitar doble reserva de turnos (Race Conditions).
- **Tareas Asíncronas / Webhooks:** Recepción de notificaciones de pago desacopladas del flujo principal, apoyadas en Redis para colas y procesamiento en segundo plano.
- **Contenedores:** Servicios orquestados con Docker Compose (backend, frontend, PostgreSQL, Redis).

## Estructura de Directorios Propuesta
```text
turnos-odontologia/
├── backend/                # Backend API (Python / FastAPI)
│   ├── app/
│   │   ├── api/            # Routers (endpoints REST)
│   │   ├── core/           # Configuración, seguridad (JWT), dependencias
│   │   ├── models/         # Modelos SQLAlchemy (ORM)
│   │   ├── schemas/        # Esquemas Pydantic (validación I/O)
│   │   ├── services/       # Lógica de negocio
│   │   ├── repositories/   # Acceso a datos
│   │   └── main.py         # Punto de entrada FastAPI
│   ├── alembic/            # Migraciones de base de datos
│   └── tests/
├── frontend/               # Frontend React + TypeScript (Vite)
│   ├── src/components/
│   ├── src/views/
│   └── src/services/       # Cliente HTTP / consumo de API
├── docker-compose.yml      # Orquestación (backend, frontend, PostgreSQL, Redis)
├── knowledge-base/         # Base de conocimiento oficial
├── docs/                   # Documentación y Discovery
└── openspec/               # Especificaciones OpenSpec
```

## Seguridad y Variables de Entorno
- Autenticación basada en JSON Web Tokens (JWT) con expiración y roles.
- Variables sensibles configuradas mediante archivo `.env` (nunca hardcodeadas):
  - `DATABASE_URL`
  - `REDIS_URL`
  - `JWT_SECRET`
  - `MERCADOPAGO_ACCESS_TOKEN`
  - `WHATSAPP_API_TOKEN`
- Protección contra SQL Injection y XSS mediante validación de esquemas (Pydantic) y consultas parametrizadas (SQLAlchemy).
