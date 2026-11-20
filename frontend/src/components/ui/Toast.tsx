import type { ReactNode } from 'react';

type ToastVariant = 'info' | 'error' | 'success';

const VARIANT_CLASSES: Record<ToastVariant, string> = {
  info: 'border-info bg-info-50 text-info',
  error: 'border-danger bg-danger-50 text-danger',
  success: 'border-success bg-success-50 text-success',
};

export interface ToastProps {
  message: ReactNode;
  variant?: ToastVariant;
  onClose?: () => void;
}

export function Toast({ message, variant = 'info', onClose }: ToastProps) {
  const role = variant === 'error' ? 'alert' : 'status';
  return (
    <div
      role={role}
      aria-live={variant === 'error' ? 'assertive' : 'polite'}
      className={`flex items-start gap-2 rounded-lg border px-3 py-2 text-sm shadow-md ${VARIANT_CLASSES[variant]}`}
    >
      <div className="flex-1">{message}</div>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          aria-label="Cerrar notificación"
          className="rounded px-1 text-base leading-none"
        >
          ×
        </button>
      )}
    </div>
  );
}
