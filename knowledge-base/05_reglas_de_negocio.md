# 05 — Reglas de Negocio

| Código | Regla de Negocio | Descripción |
|--------|------------------|-------------|
| **RN-01** | **Exclusividad de Sillón y Profesional** | Dos turnos no pueden solaparse en el mismo box/sillón físico ni ser asignados al mismo odontólogo en la misma franja horaria exacta. |
| **RN-02** | **Política de Seña Obligatoria** | Todo turno solicitado online requiere el pago de una seña (ej. 30% del valor de la consulta) en un plazo máximo de 30 minutos, caso contrario el turno se libera automáticamente. |
| **RN-03** | **Política de Cancelación y Retención** | Las cancelaciones realizadas por el paciente con más de 24 horas de anticipación permiten la devolución o reprogramación de la seña. Cancelaciones con menos de 24 horas o ausencias (no-show) implican la retención de la seña. |
| **RN-04** | **Identificación Única por DNI** | Los pacientes se registran de forma unívoca por su DNI (o documento de identidad equivalente). No se permiten duplicados en el padrón. |
| **RN-05** | **Bloqueo por Ausencias Reiteradas** | Un paciente que acumule 2 ausencias sin aviso previo (no-show) quedará bloqueado temporalmente para solicitar turnos online, requiriendo contacto telefónico con la clínica. |
| **RN-06** | **Privacidad de Datos Sensibles (PII)** | Está terminantemente prohibido almacenar datos reales de pacientes de personas físicas en repositorios públicos o entornos de prueba (datos 100% ficticios o anonimizados). |
