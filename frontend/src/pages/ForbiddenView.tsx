import { Link } from 'react-router-dom';

export function ForbiddenView() {
  return (
    <section role="alert" className="mx-auto max-w-lg p-6">
      <h1 className="text-2xl font-bold text-ink">Acceso denegado</h1>
      <p className="mt-2 text-muted">
        No tenés permiso para ver esta sección con tu rol actual.
      </p>
      <Link to="/" className="mt-4 inline-block text-brand-700 underline">
        Volver al inicio
      </Link>
    </section>
  );
}
