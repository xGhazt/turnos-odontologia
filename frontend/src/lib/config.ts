const DEFAULT_API_BASE_URL = 'http://localhost:8000';

/**
 * Normaliza la URL base de la API: aplica el default si está vacía y quita
 * las barras finales para evitar `//` al concatenar rutas.
 */
export function normalizeBaseUrl(value: string | undefined): string {
  const raw = (value ?? '').trim();
  const base = raw === '' ? DEFAULT_API_BASE_URL : raw;
  return base.replace(/\/+$/, '');
}

/** Deriva la base de los endpoints de autenticación a partir de la URL base. */
export function deriveAuthBase(baseUrl: string): string {
  return `${normalizeBaseUrl(baseUrl)}/auth`;
}

export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);
export const AUTH_BASE = deriveAuthBase(API_BASE_URL);
