# 09 — Decisiones y Supuestos

## Decisiones de Arquitectura
1. **Separación de Frontend y Backend:** Se optó por una API REST desacoplada con React en el cliente para permitir futura escalabilidad hacia una aplicación móvil si fuera necesario.
2. **PostgreSQL como Base de Datos:** Elegida por su robustez en transacciones relacionales complejas y control de concurrencia en reservas de agenda.
3. **Uso de OpenSpec y Active Stack:** Metodología estricta de desarrollo guiado por especificaciones y control estricto de etapas.

## Supuestos de Negocio
- **Suposición 1:** Los pacientes cuentan con acceso a WhatsApp y medios de pago digitales (Mercado Pago / Tarjeta) para abonar las señas.
- **Suposición 2:** La clínica cuenta con conectividad a Internet estable durante todo el horario de atención para procesar turnos online y webhooks de pago.
- **Suposición 3:** Los datos utilizados en pruebas y demostraciones académicas son 100% ficticios (**RN-06**).
