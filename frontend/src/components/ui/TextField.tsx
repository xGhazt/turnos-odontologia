import type { InputHTMLAttributes, ReactNode, Ref } from 'react';

export interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  hint?: string;
  endAdornment?: ReactNode;
  inputRef?: Ref<HTMLInputElement>;
}

export function TextField({
  label,
  error,
  hint,
  id,
  endAdornment,
  inputRef,
  className = '',
  ...rest
}: TextFieldProps) {
  const fieldId = id ?? `field-${label.replace(/\s+/g, '-').toLowerCase()}`;
  const errorId = `${fieldId}-error`;
  const hintId = `${fieldId}-hint`;
  const describedBy =
    [error ? errorId : null, hint ? hintId : null].filter(Boolean).join(' ') || undefined;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={fieldId} className="text-sm font-semibold text-ink">
        {label}
      </label>
      <div className="relative">
        <input
          id={fieldId}
          ref={inputRef}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          className={`min-h-11 w-full rounded-lg border bg-surface px-3 py-2 text-base text-ink ${
            error ? 'border-danger' : 'border-line'
          } ${endAdornment ? 'pr-12' : ''} ${className}`}
          {...rest}
        />
        {endAdornment && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-2">{endAdornment}</div>
        )}
      </div>
      {hint && !error && (
        <p id={hintId} className="text-sm text-muted">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="flex items-center gap-1 text-sm text-danger">
          <span aria-hidden="true">⚠</span>
          {error}
        </p>
      )}
    </div>
  );
}
