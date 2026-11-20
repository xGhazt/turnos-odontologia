import { useCallback, useEffect, useRef, useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthContext';
import { menuFor } from '../lib/rbac';
import { Brand } from '../components/ui/Brand';
import { Button } from '../components/ui/Button';

export function DashboardLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const menuButtonRef = useRef<HTMLButtonElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  const items = menuFor(user?.roles ?? []);

  const closeDrawer = useCallback((restoreFocus = true) => {
    setDrawerOpen(false);
    if (restoreFocus) menuButtonRef.current?.focus();
  }, []);

  useEffect(() => {
    if (!drawerOpen) return undefined;

    closeButtonRef.current?.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeDrawer();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [drawerOpen, closeDrawer]);

  async function handleLogout() {
    await logout();
    navigate('/login', { replace: true });
  }

  return (
    <div className="min-h-screen bg-canvas">
      <a
        href="#contenido"
        className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-brand-700 focus:px-3 focus:py-2 focus:text-surface"
      >
        Saltar al contenido
      </a>

      <header className="border-b border-line bg-surface">
        <div className="flex items-center gap-3 px-4 py-3">
          <button
            ref={menuButtonRef}
            type="button"
            aria-expanded={drawerOpen}
            aria-controls="app-sidebar"
            aria-label="Abrir menú"
            onClick={() => setDrawerOpen((value) => !value)}
            className="grid h-11 w-11 place-items-center rounded-lg border border-line text-ink lg:hidden"
          >
            <span aria-hidden="true">☰</span>
          </button>
          <Brand to="/" />
          <div className="ml-auto flex items-center gap-3">
            <span className="hidden text-sm text-muted sm:inline">
              {user?.email} · {user?.role}
            </span>
            <Button variant="secondary" onClick={() => void handleLogout()}>
              Cerrar sesión
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {drawerOpen && (
          <div
            className="fixed inset-0 z-40 bg-ink/40 lg:hidden"
            onClick={() => closeDrawer()}
            aria-hidden="true"
            data-testid="drawer-overlay"
          />
        )}

        <aside
          id="app-sidebar"
          className={`fixed inset-y-0 left-0 z-50 w-64 border-r border-line bg-surface p-2 transition-transform lg:static lg:z-auto lg:w-64 lg:translate-x-0 ${
            drawerOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className="flex items-center justify-between p-2 lg:hidden">
            <span className="font-semibold text-ink">Menú</span>
            <button
              ref={closeButtonRef}
              type="button"
              aria-label="Cerrar menú"
              onClick={() => closeDrawer()}
              className="grid h-11 w-11 place-items-center rounded-lg text-xl text-ink"
            >
              ×
            </button>
          </div>
          <nav aria-label="Navegación principal">
            <ul className="space-y-1 p-2">
              {items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    onClick={() => closeDrawer(false)}
                    className={({ isActive }) =>
                      `block rounded-lg px-3 py-2 ${
                        isActive
                          ? 'bg-brand-50 font-semibold text-brand-700'
                          : 'text-ink hover:bg-brand-50'
                      }`
                    }
                  >
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </aside>

        <main id="contenido" className="min-w-0 flex-1 p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
