import { vi } from 'vitest';
import type { AuthContextValue } from '../features/auth/AuthContext';
import type { AuthUser } from '../features/auth/types';

export const adminUser: AuthUser = {
  id: 1,
  email: 'admin@example.test',
  role: 'admin',
  roles: ['admin'],
};

export const pacienteUser: AuthUser = {
  id: 2,
  email: 'paciente@example.test',
  role: 'paciente',
  roles: ['paciente'],
};

export function makeAuthContext(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    status: 'authenticated',
    user: adminUser,
    expired: false,
    login: vi.fn(async () => adminUser),
    logout: vi.fn(async () => undefined),
    ...overrides,
  };
}
