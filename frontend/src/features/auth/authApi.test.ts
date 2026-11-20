import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { login, logout, me, register } from './authApi';
import { PendingContractError } from './types';
import { tokenStore } from '../../lib/tokenStore';
import { setUnauthorizedHandler } from '../../lib/httpClient';

function jsonResponse(data: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
}

describe('authApi', () => {
  beforeEach(() => {
    tokenStore.clear();
    setUnauthorizedHandler(null);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('login guarda el token y normaliza role a roles', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        access_token: 'token-falso',
        token_type: 'bearer',
        user: { id: 1, email: 'demo@example.test', role: 'admin' },
      }),
    );
    vi.stubGlobal('fetch', fetchMock);

    const user = await login({ email: 'demo@example.test', password: 'not-a-real-password' });

    expect(tokenStore.get()).toBe('token-falso');
    expect(user).toEqual({
      id: 1,
      email: 'demo@example.test',
      role: 'admin',
      roles: ['admin'],
    });
    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/login$/);
  });

  it('login con rol desconocido cae en paciente', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse({
          access_token: 'token-falso',
          token_type: 'bearer',
          user: { id: 2, email: 'demo@example.test', role: 'rol-inexistente' },
        }),
      ),
    );

    const user = await login({ email: 'demo@example.test', password: 'not-a-real-password' });
    expect(user.role).toBe('paciente');
    expect(user.roles).toEqual(['paciente']);
  });

  it('me consulta /auth/me y normaliza el rol', async () => {
    tokenStore.set('token-falso');
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ id: 3, email: 'demo@example.test', role: 'odontologo' }));
    vi.stubGlobal('fetch', fetchMock);

    const user = await me();

    expect(user).toEqual({
      id: 3,
      email: 'demo@example.test',
      role: 'odontologo',
      roles: ['odontologo'],
    });
    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/auth\/me$/);
  });

  it('logout limpia el token aunque la API falle', async () => {
    tokenStore.set('token-falso');
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    await expect(logout()).resolves.toBeUndefined();
    expect(tokenStore.get()).toBeNull();
  });

  it('register no hace red y señala contrato pendiente', async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);

    await expect(
      register({
        email: 'demo@example.test',
        password: 'not-a-real-password',
        confirmPassword: 'not-a-real-password',
      }),
    ).rejects.toBeInstanceOf(PendingContractError);

    expect(fetchMock).not.toHaveBeenCalled();
  });
});
