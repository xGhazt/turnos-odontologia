import { beforeEach, describe, expect, it } from 'vitest';
import { tokenStore } from './tokenStore';

describe('tokenStore', () => {
  beforeEach(() => {
    tokenStore.clear();
    localStorage.clear();
    sessionStorage.clear();
  });

  it('inicia vacío', () => {
    expect(tokenStore.get()).toBeNull();
  });

  it('guarda y lee un token en memoria', () => {
    tokenStore.set('token-falso');
    expect(tokenStore.get()).toBe('token-falso');
  });

  it('limpia el token', () => {
    tokenStore.set('token-falso');
    tokenStore.clear();
    expect(tokenStore.get()).toBeNull();
  });

  it('no escribe en localStorage ni sessionStorage', () => {
    tokenStore.set('token-falso');
    expect(localStorage.length).toBe(0);
    expect(sessionStorage.length).toBe(0);
  });
});
