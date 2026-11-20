import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthContext, type AuthContextValue } from '../features/auth/AuthContext';
import { makeAuthContext } from '../test/authContextValue';
import type { Role } from '../lib/rbac';
import { DashboardLayout } from './DashboardLayout';
import { PublicLayout } from './PublicLayout';
import { ModulePlaceholder } from '../pages/ModulePlaceholder';

function renderPublic() {
  return render(
    <MemoryRouter initialEntries={['/reservar-turno']}>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route
            path="/reservar-turno"
            element={<ModulePlaceholder title="Reservar turno" change="C-11" />}
          />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

function renderDashboard(roles: Role[], overrides: Partial<AuthContextValue> = {}) {
  const user = {
    id: 9,
    email: 'demo@example.test',
    role: roles[0] ?? 'paciente',
    roles,
  };
  const value = makeAuthContext({ user, ...overrides });
  return render(
    <AuthContext.Provider value={value}>
      <MemoryRouter initialEntries={['/agenda']}>
        <Routes>
          <Route element={<DashboardLayout />}>
            <Route path="/agenda" element={<div>Contenido de agenda</div>} />
            <Route path="/pacientes" element={<div>Contenido de pacientes</div>} />
          </Route>
          <Route path="/login" element={<div>Login destino</div>} />
        </Routes>
      </MemoryRouter>
    </AuthContext.Provider>,
  );
}

describe('PublicLayout', () => {
  it('muestra la marca, el acceso y el contenido público', () => {
    renderPublic();
    expect(screen.getByRole('link', { name: /turnos odontología/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Ingresar' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Reservar turno' })).toBeInTheDocument();
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});

describe('DashboardLayout', () => {
  beforeEach(() => vi.clearAllMocks());

  const expected: Record<Role, string[]> = {
    admin: ['Panel', 'Profesionales', 'Configuración', 'Agenda', 'Pacientes', 'Caja'],
    odontologo: ['Agenda', 'Pacientes'],
    secretaria: ['Agenda', 'Pacientes', 'Caja'],
    paciente: ['Mi portal', 'Mis turnos'],
  };

  (Object.keys(expected) as Role[]).forEach((role) => {
    it(`muestra el menú correspondiente al rol ${role}`, () => {
      renderDashboard([role]);
      const nav = screen.getByRole('navigation', { name: /navegación principal/i });
      const labels = within(nav)
        .getAllByRole('link')
        .map((link) => link.textContent);
      expect(labels).toEqual(expected[role]);
    });
  });

  it('abre el drawer, enfoca el cierre y lo cierra con Escape devolviendo el foco', async () => {
    const user = userEvent.setup();
    renderDashboard(['admin']);

    const menuButton = screen.getByRole('button', { name: /abrir menú/i });
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');

    await user.click(menuButton);
    expect(menuButton).toHaveAttribute('aria-expanded', 'true');
    expect(screen.getByRole('button', { name: /cerrar menú/i })).toHaveFocus();

    await user.keyboard('{Escape}');
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    expect(menuButton).toHaveFocus();
  });

  it('cierra sesión, invoca logout y navega al login', async () => {
    const user = userEvent.setup();
    const logout = vi.fn(async () => undefined);
    renderDashboard(['admin'], { logout });

    await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }));

    expect(await screen.findByText('Login destino')).toBeInTheDocument();
    expect(logout).toHaveBeenCalledTimes(1);
  });
});
