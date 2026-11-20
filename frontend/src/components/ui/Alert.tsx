import type { ReactNode } from 'react';

type AlertVariant = 'info' | 'error' | 'success' | 'warning';

const VARIANT_CLASSES: Record<AlertVariant, string> = {
  info: 'border-info bg-info-50 text-info',
  error: 'border-danger bg-danger-50 text-danger',
  success: 'border-success bg-success-50 text-success',
  warning: 'border-warning bg-warning-50 text-warning',
};

export interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  children: ReactNode;
}

export function Alert({ variant = 'info', title, children }: AlertProps) {
  const role = variant === 'error' ? 'alert' : 'status';
  return (
    <div role={role} className={`rounded-lg border px-3 py-2 text-sm ${VARIANT_CLASSES[variant]}`}>
      {title && <p className="font-semibold">{title}</p>}
      <div>{children}</div>
    </div>
  );
}
