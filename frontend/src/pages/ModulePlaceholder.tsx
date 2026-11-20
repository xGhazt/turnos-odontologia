import { Link } from 'react-router-dom';

export interface ModulePlaceholderProps {
  title: string;
  change?: string;
}

/**
 * Marcador de posición para módulos cuyo backend todavía no existe.
 * No incluye tablas, tarjetas ni datos de ejemplo.
 */
export function ModulePlaceholder({ title, change }: ModulePlaceholderProps) {
  return (
    <section className="mx-auto max-w-2xl p-6">
      <h1 className="text-2xl font-bold text-ink">{title}</h1>
      <p className="mt-2 text-muted">
        Este módulo se implementará en un change posterior
        {change ? ` (${change})` : ''}.
      </p>
      <Link to="/" className="mt-4 inline-block text-brand-700 underline">
        Volver al inicio
      </Link>
    </section>
  );
}
