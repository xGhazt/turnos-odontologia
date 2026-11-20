import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { login as apiLogin, logout as apiLogout, me as apiMe } from './authApi';
import { setUnauthorizedHandler } from '../../lib/httpClient';
import { tokenStore } from '../../lib/tokenStore';
import type { AuthUser, LoginCredentials } from './types';

export type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated';

export interface AuthContextValue {
  status: AuthStatus;
  user: AuthUser | null;
  /** true cuando la sesión se perdió por un 401 (para el aviso de sesión expirada). */
  expired: boolean;
  login(credentials: LoginCredentials): Promise<AuthUser>;
  logout(): Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>('checking');
  const [user, setUser] = useState<AuthUser | null>(null);
  const [expired, setExpired] = useState(false);

  // Arranque: sin token en memoria no hay sesión que restaurar (C-03 no tiene refresh).
  useEffect(() => {
    let active = true;

    if (!tokenStore.get()) {
      setStatus('unauthenticated');
      return () => {
        active = false;
      };
    }

    apiMe()
      .then((profile) => {
        if (!active) return;
        setUser(profile);
        setStatus('authenticated');
      })
      .catch(() => {
        if (!active) return;
        tokenStore.clear();
        setUser(null);
        setStatus('unauthenticated');
      });

    return () => {
      active = false;
    };
  }, []);

  // Un 401 en una ruta protegida limpia la sesión y marca la expiración.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      tokenStore.clear();
      setUser(null);
      setStatus('unauthenticated');
      setExpired(true);
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  const login = useCallback(async (credentials: LoginCredentials) => {
    const profile = await apiLogin(credentials);
    setUser(profile);
    setStatus('authenticated');
    setExpired(false);
    return profile;
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiLogout();
    } catch {
      // El cierre local no depende del backend: se limpia el estado igual.
    } finally {
      setUser(null);
      setStatus('unauthenticated');
      setExpired(false);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ status, user, expired, login, logout }),
    [status, user, expired, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
}
