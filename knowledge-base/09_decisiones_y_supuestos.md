# 09 — Decisiones y Supuestos

## Decisiones de Arquitectura (Confirmadas)
1. **Separación de Frontend y Backend:** API REST desacoplada con React en el cliente para permitir futura escalabilidad hacia aplicación móvil.
2. **Stack Frontend:** React con TypeScript y Vite (bundler) + Tailwind CSS.
3. **Stack Backend:** Python con FastAPI (API REST sobre ASGI).
4. **Autenticación:** JWT (JSON Web Tokens) con expiración y roles.
5. **ORM / Migraciones:** SQLAlchemy para el mapeo objeto-relacional, con Alembic para migraciones.
6. **PostgreSQL como Base de Datos:** Elegida por su robustez en transacciones relacionales complejas y control de concurrencia en reservas de agenda (race conditions).
7. **Redis para Asincronía:** Cola de tareas / procesamiento en segundo plano para recordatorios y webhooks de pago.
8. **Infraestructura:** Docker y Docker Compose para orquestar backend, frontend, PostgreSQL y Redis.
9. **Uso de OpenSpec y Active Stack:** Metodología estricta de desarrollo guiado por especificaciones y control de etapas.

## Decisiones Técnicas Pendientes de Confirmación (No definidas en `openspec/config.yaml`)
- **Proveedor WhatsApp:** API oficial de Meta (costos por conversación) vs proveedores terceros (Twilio, Wati, etc.) — *impacta en costos operativos y estabilidad; ver PA-05*.

## Supuestos de Negocio
- **Suposición 1:** Los pacientes cuentan con acceso a WhatsApp y medios de pago digitales (Mercado Pago / Tarjeta) para abonar las señas.
- **Suposición 2:** La clínica cuenta con conectividad a Internet estable durante todo el horario de atención para procesar turnos online y webhooks de pago.
- **Suposición 3:** Los datos utilizados en pruebas y demostraciones académicas son 100% ficticios (**RN-06**).
- **Suposición 4:** El cobro de seña vía Mercado Pago es el diferencial validado por competidores locales (TurnoApp) para reducir ausentismo.

## Hallazgos de Verificación que Afectan Supuestos
- **Alegra Dental:** La verificación de fuentes confirmó que en Argentina **no existe un producto "Alegra Dental" con odontograma**; la oferta local es facturación/gestión general. Esto invalida la comparación directa en el criterio "Clínica/Odontograma" del discovery.
- **WhatsApp Business API:** Ningún competidor verificado aclara si usa API oficial o automatizaciones no oficiales. Esto introduce incertidumbre en costos y compliance para nuestra integración.
