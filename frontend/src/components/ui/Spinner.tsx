export interface SpinnerProps {
  label?: string;
  fullPage?: boolean;
}

/** Indicador de carga accesible. */
export function Spinner({ label = 'Cargando…', fullPage = false }: SpinnerProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={
        fullPage ? 'grid min-h-screen place-items-center' : 'inline-flex items-center gap-2'
      }
    >
      <span
        aria-hidden="true"
        className="h-5 w-5 animate-spin rounded-full border-2 border-brand-700 border-t-transparent"
      />
      <span className="text-sm text-muted">{label}</span>
    </div>
  );
}

export function FullPageSpinner({ label = 'Verificando sesión…' }: { label?: string }) {
  return <Spinner label={label} fullPage />;
}
