# 01 — Visión y Objetivos

## Propósito del Sistema
El sistema **Turnos Odontología** es una plataforma web integral diseñada para optimizar la gestión de agendas, la atención de pacientes y la administración de consultorios y clínicas odontológicas en Argentina y LATAM. Su propósito principal es reducir drásticamente el ausentismo mediante recordatorios automatizados y asegurar la sostenibilidad financiera del consultorio a través del cobro anticipado de señas.

## Objetivos por Actor
- **Odontólogos / Directores de Clínica:** 
  - Centralizar la agenda multi-profesional y multi-sillón/box para evitar solapamientos.
  - Minimizar el ausentismo de pacientes con notificaciones multicanal (WhatsApp / Email).
  - Acceder a historiales clínicos y odontogramas digitales de forma rápida.
  - Llevar un control básico de caja y pagos (señas y saldos).
- **Secretarias / Recepcionistas:**
  - Agilizar la asignación, reasignación y cancelación de turnos.
  - Gestionar el alta rápida de nuevos pacientes y confirmación de asistencia.
- **Pacientes:**
  - Solicitar turnos online de manera intuitiva 24/7.
  - Recibir recordatorios automáticos de sus citas con opción de confirmar o cancelar.
  - Abonar señas online de forma segura (Mercado Pago).

## Alcance del MVP (Versión 1.0)
- Agenda multi-profesional y multi-sillón con validación de solapamientos.
- Módulo de pacientes (CRUD y datos de contacto).
- Gestión de turnos (crear, confirmar, cancelar, reagendar).
- Integración con pasarela de pagos (Mercado Pago) para cobro de señas obligatorias.
- Envío de recordatorios automatizados vía WhatsApp Business API / Simulación.
- Control de caja básico y estado de pagos por turno.

## Fuera de Alcance (MVP)
- Facturación electrónica avanzada conectada directamente con AFIP (se deja para versión futura).
- Odontograma 3D complejo con rasterización gráfica avanzada (se incluye odontograma básico por cuadrantes/dientes en v1).
- Múltiples sucursales complejas con inventario de insumos médicos avanzado.
