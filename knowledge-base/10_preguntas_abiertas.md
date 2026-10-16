# 10 — Preguntas Abiertas

| ID | Pregunta / Incertidumbre | Estado | Acciones / Notas |
|----|--------------------------|--------|------------------|
| **PA-01** | ¿Cómo se manejarán las obras sociales y prepagas con validación online compleja en la primera versión? | Abierta | Se propone registrar la obra social como texto y número de afiliado básico en el MVP, dejando la integración con webs de validación de prepagas para versiones futuras. |
| **PA-02** | ¿Cuál será la pasarela de respaldo en caso de caída temporal de Mercado Pago? | Abierta | Evaluar transferencia bancaria manual con comprobante subido por el paciente para casos excepcionales. |
| **PA-03** | ¿Se requiere soporte multi-moneda (pesos / dólares) o exclusivamente pesos argentinos (ARS)? | Abierta | Se propone fijar exclusivamente ARS para el MVP dado el contexto local; pendiente de confirmación del equipo. |
| **PA-04** | **Stack Backend:** ¿Node.js/Express o Python/FastAPI? | **Resuelta** | Definido por el equipo: Python + FastAPI, autenticación JWT, ORM SQLAlchemy (migraciones Alembic), PostgreSQL, Redis para asincronía y Docker/Docker Compose. Frontend: React + TypeScript + Vite. Ver `09_decisiones_y_supuestos.md`. |
| **PA-05** | **Proveedor WhatsApp:** ¿API oficial de Meta o proveedor tercero (Twilio, Wati, etc.)? | Abierta | La verificación de fuentes reveló que competidores no aclaran su implementación. API oficial tiene costos por conversación; terceros añaden dependencia. Impacta en presupuesto y arquitectura de notificaciones. |
| **PA-06** | **Alegra Dental:** ¿Se descarta como competidor de nicho clínico (odontograma) para Argentina? | Abierta | Verificación confirmó que en Argentina Alegra es solo facturación/gestión general. El informe de discovery lo trata como competidor clínico. Requiere corrección en análisis competitivo o nota explicativa. |
| **PA-07** | **AFIP / Facturación electrónica:** ¿Alcance exacto del MVP respecto a facturación? | Abierta | Verificación confirma complejidad alta (Alegra la promociona como "superpoder"). MVP define "simulación/estructura modular" — se necesita definir qué significa exactamente (solo PDF, CAE mock, integración real sandbox). |
