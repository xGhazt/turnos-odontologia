import { API_BASE_URL } from './config';
import { tokenStore } from './tokenStore';

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;
  readonly retryAfter?: number;

  constructor(status: number, detail: string, retryAfter?: number) {
    super(detail);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
    this.retryAfter = retryAfter;
  }
}

export class NetworkError extends Error {
  constructor(message = 'No pudimos conectarnos con el servidor.') {
    super(message);
    this.name = 'NetworkError';
  }
}

export type UnauthorizedHandler = () => void;

let unauthorizedHandler: UnauthorizedHandler | null = null;

/** Registra el manejador que dispara el flujo de sesión expirada ante un 401. */
export function setUnauthorizedHandler(handler: UnauthorizedHandler | null): void {
  unauthorizedHandler = handler;
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  auth?: boolean;
  /** Evita disparar sesión expirada (login/logout). */
  skipAuthRedirect?: boolean;
  signal?: AbortSignal;
}

async function parseDetail(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: unknown };
    if (typeof data?.detail === 'string') return data.detail;
    if (Array.isArray(data?.detail)) return 'Los datos enviados no son válidos.';
  } catch {
    // respuesta sin cuerpo JSON: se usa el texto de estado
  }
  return response.statusText || `Error ${response.status}`;
}

function parseRetryAfter(response: Response): number | undefined {
  const raw = response.headers.get('Retry-After');
  if (!raw) return undefined;
  const seconds = Number(raw);
  return Number.isFinite(seconds) ? seconds : undefined;
}

/**
 * Cliente HTTP del SPA. Adjunta el Bearer desde memoria, mapea errores a tipos
 * y dispara sesión expirada en 401 (salvo `skipAuthRedirect`).
 * Nunca registra tokens ni cuerpos de credenciales.
 */
export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const {
    method = 'GET',
    body,
    headers = {},
    auth = true,
    skipAuthRedirect = false,
    signal,
  } = options;

  const url = path.startsWith('http') ? path : `${API_BASE_URL}${path}`;
  const finalHeaders: Record<string, string> = { ...headers };

  if (body !== undefined) {
    finalHeaders['Content-Type'] = 'application/json';
  }
  if (auth) {
    const token = tokenStore.get();
    if (token) finalHeaders.Authorization = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(url, {
      method,
      headers: finalHeaders,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: 'include',
      signal,
    });
  } catch {
    throw new NetworkError();
  }

  if (!response.ok) {
    const detail = await parseDetail(response);
    const retryAfter = parseRetryAfter(response);
    if (response.status === 401 && !skipAuthRedirect) {
      unauthorizedHandler?.();
    }
    throw new ApiError(response.status, detail, retryAfter);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
