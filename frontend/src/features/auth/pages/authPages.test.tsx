import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { LoginPage } from './LoginPage';
import { RegisterPage } from './RegisterPage';
import { AuthContext, type AuthContextValue } from '../AuthContext';
import { ApiError, NetworkError } from '../../../lib/httpClient';
import { PendingContractError } from '../types';
import { adminUser, makeAuthContext } from '../../../test/authContextValue';

vi.mock('../authApi', () => ({
  login: vi.fn(),
  me: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
}));

import * as authApi from '../authApi';

const mockedRegister = vi.mocked(authApi.register);

type LoginMock = AuthContextValue['login'];

function renderLogin(
  overrides: Partial<AuthContextValue> = {},
  initialEntry: string | { pathname: string; state?: unknown } = '/login',
) {
  const value = makeAuthContext(overrides);
  return render(
    <AuthContext.Provider value={value}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/registro" element={<div>Registro destino</div>} />
          <Route path="/agenda" element={<div>Agenda destino</div>} />
          <Route path="/admin/dashboard" element={<div>Panel destino</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

function renderRegister() {
  return render(
    <MemoryRouter initialEntries={['/registro']}>
      <Routes>
        <Route path="/registro" element={<RegisterPage />} />
        <Route path="/login" element={<div>Login destino</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('LoginPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renderiza el formulario de ingreso', () => {
    renderLogin();
    expect(screen.getByRole('heading', { name: 'Ingresar' })).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Ingresar' })).toBeInTheDocument();
  });

  it('no envía con campos vacíos y enfoca el email', async () => {
    const user = userEvent.setup();
    const loginSpy = vi.fn();
    renderLogin({ login: loginSpy as unknown as LoginMock });

    await user.click(screen.getByRole('button', { name: 'Ingresar' }));

    expect(loginSpy).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Email')).toHaveFocus();
    expect(screen.getAllByText(/obligatorio/i).length).toBeGreaterThan(0);
  });

  it('muestra el mensaje de credenciales inválidas y vacía la contraseña', async () => {
    const user = userEvent.setup();
    const loginSpy = vi.fn().mockRejectedValue(new ApiError(401, 'Credenciales inválidas'));
    renderLogin({ login: loginSpy as unknown as LoginMock });

    await user.type(screen.getByLabelText('Email'), 'demo@example.test');
    await user.type(screen.getByLabelText('Contraseña'), 'not-a-real-password');
    await user.click(screen.getByRole('button', { name: 'Ingresar' }));

    expect(await screen.findByText(/no son correctos/i)).toBeInTheDocument();
    expect((screen.getByLabelText('Contraseña') as HTMLInputElement).value).toBe('');
  });

  it('muestra el tiempo de espera ante un 429', async () => {
    const user = userEvent.setup();
    const loginSpy = vi.fn().mockRejectedValue(new ApiError(429, 'Demasiados intentos', 120));
    renderLogin({ login: loginSpy as unknown as LoginMock });

    await user.type(screen.getByLabelText('Email'), 'demo@example.test');
    await user.type(screen.getByLabelText('Contraseña'), 'not-a-real-password');
    await user.click(screen.getByRole('button', { name: 'Ingresar' }));

    expect(await screen.findByText(/demasiados intentos/i)).toBeInTheDocument();
    expect(screen.getByText(/120 segundos/i)).toBeInTheDocument();
  });

  it('muestra el mensaje de error de red', async () => {
    const user = userEvent.setup();
    const loginSpy = vi.fn().mockRejectedValue(new NetworkError());
    renderLogin({ login: loginSpy as unknown as LoginMock });

    await user.type(screen.getByLabelText('Email'), 'demo@example.test');
    await user.type(screen.getByLabelText('Contraseña'), 'not-a-real-password');
    await user.click(screen.getByRole('button', { name: 'Ingresar' }));

    expect(await screen.findByText(/no pudimos conectarnos/i)).toBeInTheDocument();
  });

  it('muestra el aviso de sesión expirada', () => {
    renderLogin({}, '/login?motivo=sesion-expirada');
    expect(screen.getByText(/tu sesión expiró/i)).toBeInTheDocument();
  });

  it('alterna la visibilidad de la contraseña', async () => {
    const user = userEvent.setup();
    renderLogin();

    const password = screen.getByLabelText('Contraseña');
    expect(password).toHaveAttribute('type', 'password');

    const toggle = screen.getByRole('button', { name: /mostrar contraseña/i });
    await user.click(toggle);

    expect(screen.getByLabelText('Contraseña')).toHaveAttribute('type', 'text');
    expect(screen.getByRole('button', { name: /ocultar contraseña/i })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
  });

  it('redirige a la ruta de origen permitida tras el login', async () => {
    const user = userEvent.setup();
    const loginSpy = vi.fn().mockResolvedValue(adminUser);
    renderLogin(
      { login: loginSpy as unknown as LoginMock },
      { pathname: '/login', state: { from: { pathname: '/agenda' } } },
    );

    await user.type(screen.getByLabelText('Email'), 'demo@example.test');
    await user.type(screen.getByLabelText('Contraseña'), 'not-a-real-password');
    await user.click(screen.getByRole('button', { name: 'Ingresar' }));

    expect(await screen.findByText('Agenda destino')).toBeInTheDocument();
  });
});

describe('RegisterPage', () => {
  beforeEach(() => vi.clearAllMocks());

  it('renderiza el formulario de registro', () => {
    renderRegister();
    expect(screen.getByRole('heading', { name: 'Crear cuenta' })).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Contraseña')).toBeInTheDocument();
    expect(screen.getByLabelText('Repetir contraseña')).toBeInTheDocument();
  });

  it('no envía cuando la confirmación no coincide', async () => {
    const user = userEvent.setup();
    renderRegister();

    await user.type(screen.getByLabelText('Email'), 'demo@example.test');
    await user.type(screen.getByLabelText('Contraseña'), 'not-a-real-password');
    await user.type(screen.getByLabelText('Repetir contraseña'), 'otra-password');
    await user.click(screen.getByRole('button', { name: 'Crear cuenta' }));

    expect(mockedRegister).not.toHaveBeenCalled();
    expect(screen.getByText(/no coinciden/i)).toBeInTheDocument();
  });

  it('informa que el registro es un contrato pendiente', async () => {
    const user = userEvent.setup();
    mockedRegister.mockRejectedValue(new PendingContractError());
    renderRegister();

    await user.type(screen.getByLabelText('Email'), 'demo@example.test');
    await user.type(screen.getByLabelText('Contraseña'), 'not-a-real-password');
    await user.type(screen.getByLabelText('Repetir contraseña'), 'not-a-real-password');
    await user.click(screen.getByRole('button', { name: 'Crear cuenta' }));

    expect(await screen.findByText(/todavía no está disponible/i)).toBeInTheDocument();
  });
});
