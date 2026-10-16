# 09 — Decisiones y Supuestos

## Decisiones de Arquitectura (Confirmadas)
1. **Separación de Frontend y Backend:** API REST desacoplada con React en el cliente para permitir futura escalabilidad hacia aplicación móvil.
2. **PostgreSQL como Base de Datos:** Elegida por su robustez en transacciones relacionales complejas y control de concurrencia en reservas de agenda (race conditions).
3. **Uso de OpenSpec y Active Stack:** Metodología estricta de desarrollo guiado por especificaciones y control de etapas.

## Decisiones Técnicas Pendientes de Confirmación (No definidas en `openspec/config.yaml`)
- **Stack Backend:** Node.js/Express vs Python/FastAPI — *pendiente de definición por el equipo; no hay decisión vinculante en configuración*.
- **Proveedor WhatsApp:** API oficial de Meta (costos por conversación) vs proveedores terceros (Twilio, Wati, etc.) — *impacta en costos operativos y estabilidad; ver PA-04*.

## Supuestos de Negocio
- **Suposición 1:** Los pacientes cuentan con acceso a WhatsApp y medios de pago digitales (Mercado Pago / Tarjeta) para abonar las señas.
- **Suposición 2:** La clínica cuenta con conectividad a Internet estable durante todo el horario de atención para procesar turnos online y webhooks de pago.
- **Suposición 3:** Los datos utilizados en pruebas y demostraciones académicas son 100% ficticios (**RN-06**).
- **Suposición 4:** El cobro de seña vía Mercado Pago es el diferencial validado por competidores locales (TurnoApp) para reducir ausentismo.

## Hallazgos de Verificación que Afectan Supuestos
- **Alegra Dental:** La verificación de fuentes confirmó que en Argentina **no existe un producto "Alegra Dental" con odontograma**; la oferta local es facturación/gestión general. Esto invalida la comparación directa en el criterio "Clínica/Odontograma" del discovery.
- **WhatsApp Business API:** Ningún competidor verificado aclara si usa API oficial o automatizaciones no oficiales. Esto introduce incertidumbre en costos y compliance para nuestra integración.
