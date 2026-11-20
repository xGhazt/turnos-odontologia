import { describe, expect, it } from 'vitest';
import { APP_ROUTES, canAccess, homeFor, menuFor } from './rbac';

describe('rbac', () => {
  it('expone todas las rutas del shell sin duplicados', () => {
    const paths = APP_ROUTES.map((route) => route.path);
    expect(new Set(paths).size).toBe(paths.length);
  });

  it('el admin ve Panel, Profesionales, Configuración, Agenda, Pacientes y Caja', () => {
    expect(menuFor(['admin']).map((route) => route.path)).toEqual([
      '/admin/dashboard',
      '/admin/profesionales',
      '/admin/configuracion',
      '/agenda',
      '/pacientes',
      '/caja',
    ]);
  });

  it('el odontólogo ve Agenda y Pacientes', () => {
    expect(menuFor(['odontologo']).map((route) => route.path)).toEqual(['/agenda', '/pacientes']);
  });

  it('la secretaria ve Agenda, Pacientes y Caja', () => {
    expect(menuFor(['secretaria']).map((route) => route.path)).toEqual([
      '/agenda',
      '/pacientes',
      '/caja',
    ]);
  });

  it('el paciente ve Mi portal y Mis turnos', () => {
    expect(menuFor(['paciente']).map((route) => route.path)).toEqual(['/mi-portal', '/mis-turnos']);
  });

  it('canAccess respeta los roles de cada ruta', () => {
    expect(canAccess(['paciente'], '/agenda')).toBe(false);
    expect(canAccess(['secretaria'], '/agenda')).toBe(true);
    expect(canAccess(['odontologo'], '/caja')).toBe(false);
    expect(canAccess(['admin'], '/caja')).toBe(true);
  });

  it('canAccess devuelve false para rutas desconocidas', () => {
    expect(canAccess(['admin'], '/ruta-inexistente')).toBe(false);
  });

  it('homeFor aplica la prioridad admin > odontólogo > secretaria > paciente', () => {
    expect(homeFor(['paciente', 'secretaria'])).toBe('/agenda');
    expect(homeFor(['paciente', 'odontologo'])).toBe('/agenda');
    expect(homeFor(['paciente', 'admin'])).toBe('/admin/dashboard');
    expect(homeFor(['paciente'])).toBe('/mi-portal');
  });

  it('homeFor sin roles cae en /login', () => {
    expect(homeFor([])).toBe('/login');
  });
});
