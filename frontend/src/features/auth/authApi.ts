import { AUTH_BASE } from '../../lib/config';
import { request } from '../../lib/httpClient';
import { tokenStore } from '../../lib/tokenStore';
import type { ApiUser, AuthUser, LoginCredentials, LoginResponse, RegisterData } from './types';
import { PendingContractError } from './types';
import { toRole } from './validators';

function normalizeUser(user: ApiUser): AuthUser {
  const role = toRole(user.role);
  return { id: user.id, email: user.email, role, roles: [role] };
}

/** Inicia sesión contra `POST /auth/login` y guarda el token en memoria. */
export async function login(credentials: LoginCredentials): Promise<AuthUser> {
  const data = await request<LoginResponse>(`${AUTH_BASE}/login`, {
    method: 'POST',
    body: credentials,
    auth: false,
    skipAuthRedirect: true,
  });
  tokenStore.set(data.access_token);
  return normalizeUser(data.user);
}

/** Obtiene el perfil del usuario autenticado desde `GET /auth/me`. */
export async function me(): Promise<AuthUser> {
  const data = await request<ApiUser>(`${AUTH_BASE}/me`);
  return normalizeUser(data);
}

/**
 * Cierra sesión contra `POST /auth/logout` y limpia el token local.
 * No propaga errores: el estado local se limpia igual.
 */
export async function logout(): Promise<void> {
  try {
    await request(`${AUTH_BASE}/logout`, { method: 'POST', skipAuthRedirect: true });
  } catch {
    // Se ignora el error de red/servidor: lo importante es limpiar el token local.
  } finally {
    tokenStore.clear();
  }
}

/**
 * El registro está aislado como contrato pendiente: C-03 no expone endpoint.
 * No realiza ninguna llamada de red ni inventa payload.
 */
export async function register(data: RegisterData): Promise<never> {
  void data;
  throw new PendingContractError();
}
