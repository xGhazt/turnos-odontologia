import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center p-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-ink">Página no encontrada</h1>
        <p className="mt-2 text-muted">La dirección que buscás no existe.</p>
        <Link
          to="/"
          className="mt-4 inline-block rounded-lg bg-brand-700 px-4 py-2 font-semibold text-surface"
        >
          Volver al inicio
        </Link>
      </div>
    </main>
  );
}
