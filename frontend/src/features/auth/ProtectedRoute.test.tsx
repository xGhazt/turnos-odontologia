import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { AuthContext, type AuthContextValue } from './AuthContext';
import { ProtectedRoute } from './ProtectedRoute';
import type { AuthUser } from './types';
import type { Role } from '../../lib/rbac';

const pacienteUser: AuthUser = {
  id: 2,
  email: 'demo@example.test',
  role: 'paciente',
  roles: ['paciente'],
};

const adminUser: AuthUser = {
  id: 1,
  email: 'admin@example.test',
  role: 'admin',
  roles: ['admin'],
};

function buildContext(overrides: Partial<AuthContextValue>): AuthContextValue {
  return {
    status: 'authenticated',
    user: null,
    expired: false,
    login: vi.fn(async () => adminUser),
    logout: vi.fn(async () => undefined),
    ...overrides,
  };
}

function LoginProbe() {
  const location = useLocation();
  const motivo = new URLSearchParams(location.search).get('motivo') ?? 'none';
  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? 'none';
  return (
    <div>
      <span>Login</span>
      <span data-testid="motivo">{motivo}</span>
      <span data-testid="from">{from}</span>
    </div>
  );
}

function renderRoute(
  context: AuthContextValue,
  allowedRoles?: readonly Role[],
  initialEntry = '/agenda',
) {
  return render(
    <AuthContext.Provider value={context}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/login" element={<LoginProbe />} />
          <Route element={<ProtectedRoute allowedRoles={allowedRoles} />}>
            <Route path="/agenda" element={<div>Contenido agenda</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('ProtectedRoute', () => {
  it('muestra un spinner mientras verifica la sesión', () => {
    renderRoute(buildContext({ status: 'checking' }));
    expect(screen.getByRole('status')).toHaveTextContent('Verificando sesión…');
  });

  it('redirige a /login recordando la ruta de origen', () => {
    renderRoute(buildContext({ status: 'unauthenticated' }));
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByTestId('from')).toHaveTextContent('/agenda');
    expect(screen.getByTestId('motivo')).toHaveTextContent('none');
  });

  it('redirige con motivo de sesión expirada cuando corresponde', () => {
    renderRoute(buildContext({ status: 'unauthenticated', expired: true }));
    expect(screen.getByTestId('motivo')).toHaveTextContent('sesion-expirada');
  });

  it('muestra ForbiddenView cuando el rol no está permitido', () => {
    renderRoute(buildContext({ user: pacienteUser }), ['admin']);
    expect(screen.getByRole('heading', { name: /acceso denegado/i })).toBeInTheDocument();
  });

  it('renderiza el contenido cuando el rol está permitido', () => {
    renderRoute(buildContext({ user: adminUser }), ['admin']);
    expect(screen.getByText('Contenido agenda')).toBeInTheDocument();
  });
});
