import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from './AuthContext';
import * as authApi from './authApi';
import { tokenStore } from '../../lib/tokenStore';
import { request } from '../../lib/httpClient';
import type { AuthUser } from './types';

vi.mock('./authApi', () => ({
  login: vi.fn(),
  me: vi.fn(),
  logout: vi.fn(),
}));

const mockedApi = vi.mocked(authApi, true);

const adminUser: AuthUser = {
  id: 1,
  email: 'demo@example.test',
  role: 'admin',
  roles: ['admin'],
};

function Consumer() {
  const { status, user, expired, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="status">{status}</span>
      <span data-testid="email">{user?.email ?? ''}</span>
      <span data-testid="expired">{String(expired)}</span>
      <button onClick={() => void login({ email: 'demo@example.test', password: 'not-a-real-password' })}>
        login
      </button>
      <button onClick={() => void logout()}>logout</button>
    </div>
  );
}

function renderProvider() {
  return render(
    <AuthProvider>
      <Consumer />
    </AuthProvider>,
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    tokenStore.clear();
    vi.clearAllMocks();
  });

  it('sin token en memoria pasa a unauthenticated', async () => {
    renderProvider();
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));
  });

  it('login exitoso guarda el usuario y pasa a authenticated', async () => {
    const user = userEvent.setup();
    mockedApi.login.mockResolvedValue(adminUser);
    renderProvider();
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));

    await user.click(screen.getByRole('button', { name: 'login' }));

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('authenticated'));
    expect(screen.getByTestId('email')).toHaveTextContent('demo@example.test');
  });

  it('logout limpia el estado aunque la API falle', async () => {
    const user = userEvent.setup();
    mockedApi.login.mockResolvedValue(adminUser);
    mockedApi.logout.mockRejectedValue(new Error('network'));
    renderProvider();
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));

    await user.click(screen.getByRole('button', { name: 'login' }));
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('authenticated'));

    await user.click(screen.getByRole('button', { name: 'logout' }));

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));
    expect(screen.getByTestId('email')).toHaveTextContent('');
  });

  it('un 401 en una ruta protegida dispara la sesión expirada', async () => {
    const user = userEvent.setup();
    mockedApi.login.mockResolvedValue(adminUser);
    renderProvider();
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));

    await user.click(screen.getByRole('button', { name: 'login' }));
    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('authenticated'));

    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ detail: 'Token expirado' }), { status: 401 }));
    vi.stubGlobal('fetch', fetchMock);

    await act(async () => {
      await request('/auth/me').catch(() => undefined);
    });

    await waitFor(() => expect(screen.getByTestId('status')).toHaveTextContent('unauthenticated'));
    expect(screen.getByTestId('expired')).toHaveTextContent('true');

    vi.unstubAllGlobals();
  });
});
