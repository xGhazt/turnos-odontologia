export type Role = 'admin' | 'odontologo' | 'secretaria' | 'paciente';

export interface AppRoute {
  path: string;
  label: string;
  roles: readonly Role[];
  inMenu: boolean;
  /** Change que implementa la vista real (para el marcador de posición). */
  change?: string;
}

/** Fuente única de rutas, roles y menú. El router y el sidebar se derivan de acá. */
export const APP_ROUTES: readonly AppRoute[] = [
  { path: '/admin/dashboard', label: 'Panel', roles: ['admin'], inMenu: true },
  {
    path: '/admin/profesionales',
    label: 'Profesionales',
    roles: ['admin'],
    inMenu: true,
    change: 'C-06',
  },
  { path: '/admin/configuracion', label: 'Configuración', roles: ['admin'], inMenu: true },
  {
    path: '/agenda',
    label: 'Agenda',
    roles: ['admin', 'odontologo', 'secretaria'],
    inMenu: true,
    change: 'C-12',
  },
  {
    path: '/pacientes',
    label: 'Pacientes',
    roles: ['admin', 'odontologo', 'secretaria'],
    inMenu: true,
    change: 'C-05',
  },
  { path: '/caja', label: 'Caja', roles: ['admin', 'secretaria'], inMenu: true, change: 'C-13' },
  { path: '/mi-portal', label: 'Mi portal', roles: ['paciente'], inMenu: true },
  { path: '/mis-turnos', label: 'Mis turnos', roles: ['paciente'], inMenu: true },
];

const HOME_PRIORITY: readonly { role: Role; path: string }[] = [
  { role: 'admin', path: '/admin/dashboard' },
  { role: 'odontologo', path: '/agenda' },
  { role: 'secretaria', path: '/agenda' },
  { role: 'paciente', path: '/mi-portal' },
];

export function hasAnyRole(userRoles: readonly Role[], allowed: readonly Role[]): boolean {
  return userRoles.some((role) => allowed.includes(role));
}

export function canAccess(userRoles: readonly Role[], path: string): boolean {
  const route = APP_ROUTES.find((candidate) => candidate.path === path);
  if (!route) return false;
  return hasAnyRole(userRoles, route.roles);
}

export function menuFor(userRoles: readonly Role[]): AppRoute[] {
  return APP_ROUTES.filter((route) => route.inMenu && hasAnyRole(userRoles, route.roles));
}

export function homeFor(userRoles: readonly Role[]): string {
  return HOME_PRIORITY.find((entry) => userRoles.includes(entry.role))?.path ?? '/login';
}
