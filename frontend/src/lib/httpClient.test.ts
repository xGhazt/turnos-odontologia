import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { ApiError, NetworkError, request, setUnauthorizedHandler } from './httpClient';
import { tokenStore } from './tokenStore';

function jsonResponse(data: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(data), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
}

describe('httpClient', () => {
  beforeEach(() => {
    tokenStore.clear();
    setUnauthorizedHandler(null);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('adjunta el Bearer desde tokenStore', async () => {
    tokenStore.set('token-falso');
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));
    vi.stubGlobal('fetch', fetchMock);

    await request('/auth/me');

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer token-falso');
  });

  it('lanza ApiError con status y detail', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Credenciales inválidas' }), { status: 401 }),
      ),
    );

    await expect(request('/auth/me')).rejects.toMatchObject({
      status: 401,
      detail: 'Credenciales inválidas',
    });
  });

  it('dispara el handler de sesión expirada en 401, salvo con skipAuthRedirect', async () => {
    const handler = vi.fn();
    setUnauthorizedHandler(handler);
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Token expirado' }), { status: 401 }),
      ),
    );

    await expect(request('/auth/me')).rejects.toBeInstanceOf(ApiError);
    expect(handler).toHaveBeenCalledTimes(1);

    await expect(
      request('/auth/login', { method: 'POST', auth: false, skipAuthRedirect: true }),
    ).rejects.toBeInstanceOf(ApiError);
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('parsea Retry-After en una respuesta 429', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: 'Demasiados intentos' }), {
          status: 429,
          headers: { 'Retry-After': '120' },
        }),
      ),
    );

    await expect(
      request('/auth/login', { method: 'POST', auth: false, skipAuthRedirect: true }),
    ).rejects.toMatchObject({ status: 429, retryAfter: 120 });
  });

  it('lanza NetworkError cuando fetch falla por red', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));

    await expect(request('/auth/me')).rejects.toBeInstanceOf(NetworkError);
  });

  it('no registra tokens ni credenciales en consola', async () => {
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    const error = vi.spyOn(console, 'error').mockImplementation(() => {});
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {});

    tokenStore.set('token-super-secreto');
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ ok: true })));

    await request('/auth/me', { method: 'POST', body: { password: 'no-real-password' } });

    for (const spy of [log, error, warn]) {
      for (const call of spy.mock.calls) {
        expect(JSON.stringify(call)).not.toContain('token-super-secreto');
        expect(JSON.stringify(call)).not.toContain('no-real-password');
      }
    }
  });
});
