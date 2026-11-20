import { render, screen } from '@testing-library/react';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { routes } from './router';
import { AuthContext, type AuthContextValue } from '../features/auth/AuthContext';
import { makeAuthContext, pacienteUser } from '../test/authContextValue';

function renderRouter(context: AuthContextValue, initialEntry: string) {
  const router = createMemoryRouter(routes, { initialEntries: [initialEntry] });
  return render(
    <AuthContext.Provider value={context}>
      <RouterProvider router={router} />
    </AuthContext.Provider>,
  );
}

describe('router', () => {
  it('la raíz sin sesión redirige al login', () => {
    renderRouter(makeAuthContext({ status: 'unauthenticated', user: null }), '/');
    expect(screen.getByRole('heading', { name: 'Ingresar' })).toBeInTheDocument();
  });

  it('una ruta inexistente muestra NotFoundPage', () => {
    renderRouter(makeAuthContext({ status: 'unauthenticated', user: null }), '/ruta-inexistente');
    expect(screen.getByRole('heading', { name: /página no encontrada/i })).toBeInTheDocument();
  });

  it('con sesión iniciada en /login redirige al inicio según el rol', () => {
    renderRouter(makeAuthContext(), '/login');
    expect(screen.getByRole('heading', { name: 'Panel' })).toBeInTheDocument();
  });

  it('la raíz con sesión iniciada muestra el inicio según el rol', () => {
    renderRouter(makeAuthContext(), '/');
    expect(screen.getByRole('heading', { name: 'Panel' })).toBeInTheDocument();
  });

  it('un rol no permitido renderiza ForbiddenView en el lugar', () => {
    renderRouter(
      makeAuthContext({ user: pacienteUser }),
      '/agenda',
    );
    expect(screen.getByRole('heading', { name: /acceso denegado/i })).toBeInTheDocument();
  });

  it('la ruta pública de reserva muestra su marcador de posición', () => {
    renderRouter(makeAuthContext({ status: 'unauthenticated', user: null }), '/reservar-turno');
    expect(screen.getByRole('heading', { name: 'Reservar turno' })).toBeInTheDocument();
  });
});
