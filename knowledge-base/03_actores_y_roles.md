# 03 — Actores y Roles

## Actores del Sistema
1. **Administrador / Director de Clínica:** Control total del sistema, alta de profesionales, configuración de horarios y cajas.
2. **Odontólogo / Profesional:** Visualización de agenda propia, carga de evolución clínica y odontograma por paciente.
3. **Secretaria / Recepcionista:** Gestión diaria de turnos, alta de pacientes presenciales/telefónicos, control de pagos y asistencia.
4. **Paciente:** Usuario final que reserva turnos, abona señas y consulta su historial de citas.

## Matriz RBAC (Control de Acceso basado en Roles)

| Recurso / Acción | Administrador | Odontólogo | Secretaria | Paciente |
|------------------|---------------|------------|------------|----------|
| Gestionar Profesionales | SÍ | NO | NO | NO |
| Configurar Horarios/Box | SÍ | NO | SÍ | NO |
| Ver Agenda General | SÍ | SÍ (propia) | SÍ | NO (propia) |
| Crear / Modificar Turno | SÍ | SÍ | SÍ | SÍ (online) |
| Ver / Editar Historia Clínica | SÍ | SÍ | NO (solo lectura/básica) | NO |
| Registrar Pagos / Caja | SÍ | NO | SÍ | SÍ (seña online) |

## Rutas y Accesibilidad
- Rutas públicas: `/login`, `/registro`, `/reservar-turno`
- Rutas protegidas (Admin): `/admin/dashboard`, `/admin/profesionales`, `/admin/configuracion`
- Rutas protegidas (Profesional / Secretaria): `/agenda`, `/pacientes`, `/caja`
- Rutas protegidas (Paciente): `/mi-portal`, `/mis-turnos`
