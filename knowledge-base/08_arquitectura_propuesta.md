# 08 — Arquitectura Propuesta

## Patrones de Diseño
- **Arquitectura en Capas:** Separación entre presentación, servicios de negocio y acceso a datos.
- **Transacciones Atómicas (ACID):** Uso de transacciones en base de datos para evitar doble reserva de turnos (Race Conditions).
- **Webhooks Asíncronos:** Recepción de notificaciones de pago desacopladas del flujo principal de reserva.

## Estructura de Directorios Propuesta
```text
turnos-odontologia/
├── client/                 # Frontend React (SPA)
│   ├── src/components/
│   ├── src/views/
│   └── src/services/
├── server/                 # Backend API
│   ├── src/controllers/
│   ├── src/models/
│   ├── src/routes/
│   └── src/services/
├── knowledge-base/         # Base de conocimiento oficial
├── docs/                   # Documentación y Discovery
└── openspec/               # Especificaciones OpenSpec
```

## Seguridad y Variables de Entorno
- Autenticación basada en JSON Web Tokens (JWT) con expiración y roles.
- Variables sensibles configuradas mediante archivo `.env` (nunca hardcodeadas):
  - `DATABASE_URL`
  - `JWT_SECRET`
  - `MERCADOPAGO_ACCESS_TOKEN`
  - `WHATSAPP_API_TOKEN`
- Protección contra SQL Injection y XSS mediante validación de esquemas (Zod / Joi) y consultas parametrizadas.
