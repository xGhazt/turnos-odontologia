import { Link } from 'react-router-dom';

interface BrandProps {
  to?: string;
  className?: string;
}

/** Marca de la aplicación. Se usa en todos los layouts. */
export function Brand({ to = '/', className = '' }: BrandProps) {
  return (
    <Link
      to={to}
      className={`inline-flex items-center gap-2 font-bold text-brand-700 ${className}`}
    >
      <span
        aria-hidden="true"
        className="grid h-8 w-8 place-items-center rounded-lg bg-brand-700 text-surface"
      >
        T
      </span>
      <span>Turnos Odontología</span>
    </Link>
  );
}
