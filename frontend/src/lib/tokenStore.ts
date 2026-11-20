let accessToken: string | null = null;

/**
 * Almacén del access token SOLO en memoria.
 * Prohibido persistirlo en localStorage, sessionStorage o IndexedDB.
 */
export const tokenStore = {
  get(): string | null {
    return accessToken;
  },
  set(token: string): void {
    accessToken = token;
  },
  clear(): void {
    accessToken = null;
  },
};
