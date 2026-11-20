import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { API_BASE_URL, AUTH_BASE, deriveAuthBase, normalizeBaseUrl } from './config';

describe('config', () => {
  it('usa el default cuando no hay variable de entorno', () => {
    expect(normalizeBaseUrl(undefined)).toBe('http://localhost:8000');
    expect(normalizeBaseUrl('   ')).toBe('http://localhost:8000');
  });

  it('quita las barras finales de la URL base', () => {
    expect(normalizeBaseUrl('https://api.example.test/')).toBe('https://api.example.test');
    expect(normalizeBaseUrl('https://api.example.test///')).toBe('https://api.example.test');
  });

  it('deriva la base de auth agregando /auth', () => {
    expect(deriveAuthBase('https://api.example.test')).toBe('https://api.example.test/auth');
  });

  it('expone AUTH_BASE como API_BASE_URL + /auth', () => {
    expect(AUTH_BASE).toBe(`${API_BASE_URL}/auth`);
  });

  it('.env.example solo declara VITE_API_BASE_URL y no contiene secretos', () => {
    const here = dirname(fileURLToPath(import.meta.url));
    const envExample = readFileSync(resolve(here, '../../.env.example'), 'utf8');
    const keys = envExample
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line !== '' && !line.startsWith('#'))
      .map((line) => line.split('=')[0]);

    expect(keys).toEqual(['VITE_API_BASE_URL']);
  });
});
