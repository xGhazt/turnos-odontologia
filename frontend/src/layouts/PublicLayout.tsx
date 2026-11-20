import { Link, Outlet } from 'react-router-dom';
import { Brand } from '../components/ui/Brand';

export function PublicLayout() {
  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex max-w-[1120px] items-center justify-between px-4 py-3">
          <Brand to="/reservar-turno" />
          <Link to="/login" className="font-semibold text-brand-700 underline">
            Ingresar
          </Link>
        </div>
      </header>
      <main id="contenido" className="mx-auto max-w-[1120px] px-4 py-6">
        <Outlet />
      </main>
      <footer className="mx-auto max-w-[1120px] px-4 py-6 text-sm text-muted">
        Turnos Odontología
      </footer>
    </div>
  );
}
