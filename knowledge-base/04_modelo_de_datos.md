# 04 — Modelo de Datos

## Entidades Principales
1. **Usuario (`users`):** Credenciales de acceso, rol (admin, odontologo, secretaria, paciente), datos de contacto.
2. **Paciente (`patients`):** Datos personales, obra social/prepara, número de afiliado, historial médico general.
3. **Profesional (`professionals`):** Datos del odontólogo, matrícula, especialidad (ortodoncia, endodoncia, general, etc.).
4. **Consultorio / Sillón (`chairs` o `boxes`):** Unidades físicas de atención para evitar solapamientos concurrentes.
5. **Agenda / Horarios (`schedules`):** Días y franjas horarias disponibles por profesional y box.
6. **Turno (`appointments`):** Cita médica. Relaciona paciente, profesional, box, fecha/hora, estado (`pendiente_seña`, `confirmado`, `atendido`, `cancelado`, `ausente`).
7. **Tratamiento / Evolución (`clinical_records`):** Detalle de prácticas realizadas, odontograma, notas clínicas.
8. **Pago / Seña (`payments`):** Registro de transacciones asociadas a un turno (monto, estado, ID de pasarela de pago).

## Relaciones Clave (ERD Conceptual)
- 1 `Professional` ↔ N `Schedules`
- 1 `Patient` ↔ N `Appointments`
- 1 `Professional` ↔ N `Appointments`
- 1 `Chair` ↔ N `Appointments` (en una franja horaria no puede haber 2 turnos activos en el mismo `Chair`)
- 1 `Appointment` ↔ 1 `Payment` (seña)
- 1 `Patient` ↔ N `ClinicalRecords`

## Seed Data Requerido
- Usuarios iniciales de prueba para cada rol (Admin, Odontólogo Juan Pérez, Secretaria María, Paciente de prueba).
- Sillones / Box 1 y Box 2 configurados.
- Tipos de prácticas odontológicas frecuentes (Consulta, Limpieza, Extracción, Tratamiento de conducto).
