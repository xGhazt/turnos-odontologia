# 07 — Flujos Principales

## Flujo 1: Reserva de Turno con Seña Online (Paciente)
1. El paciente ingresa al portal web y selecciona especialidad, profesional y fecha/hora disponible.
2. El sistema verifica que el box y el profesional estén libres (**RN-01**).
3. El paciente completa sus datos (validando DNI único, **RN-04**).
4. El sistema genera el turno en estado `pendiente_seña` y genera el link de pago en Mercado Pago (**RN-02**).
5. El paciente abona la seña dentro del plazo de 30 minutos.
6. La pasarela de pago notifica al backend vía webhook.
7. El turno pasa a estado `confirmado` y se envía confirmación por WhatsApp/Email.

## Flujo 2: Recordatorio y Confirmación Automática
1. Un servicio programado (cron job) verifica los turnos programados para las siguientes 24 y 2 horas.
2. Se envía un mensaje automático de WhatsApp con los botones "Confirmar" o "Cancelar".
3. Si el paciente hace clic en "Confirmar", el estado del turno se actualiza a `asistencia_confirmada`.
4. Si el paciente cancela con más de 24hs, se habilita la reprogramación y devolución de seña (**RN-03**).

## Flujo 3: Atención en Consultorio y Cierre de Cita
1. El paciente se presenta en recepción; la recepcionista marca el turno como `en_espera`.
2. El odontólogo llama al paciente, lo atiende y registra la evolución clínica y tratamientos realizados en el sistema.
3. Al finalizar, el odontólogo marca el turno como `atendido`.
4. La recepcionista registra el cobro del saldo restante en la caja de la clínica.
