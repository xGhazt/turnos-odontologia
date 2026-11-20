import { useRef, useState, type FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import {
  validateEmail,
  validateLogin,
  validatePassword,
  type LoginErrors,
} from '../validators';
import { ApiError, NetworkError } from '../../../lib/httpClient';
import { canAccess, homeFor } from '../../../lib/rbac';
import { Alert } from '../../../components/ui/Alert';
import { Button } from '../../../components/ui/Button';
import { TextField } from '../../../components/ui/TextField';

type AlertVariant = 'info' | 'error' | 'success' | 'warning';

interface FormAlert {
  variant: AlertVariant;
  message: string;
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<LoginErrors>({});
  const [touched, setTouched] = useState({ email: false, password: false });
  const [submitting, setSubmitting] = useState(false);
  const [formAlert, setFormAlert] = useState<FormAlert | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  const sessionExpired = new URLSearchParams(location.search).get('motivo') === 'sesion-expirada';

  function handleEmailChange(value: string) {
    setEmail(value);
    if (touched.email) setErrors((prev) => ({ ...prev, email: validateEmail(value) ?? undefined }));
  }

  function handlePasswordChange(value: string) {
    setPassword(value);
    if (touched.password) {
      setErrors((prev) => ({ ...prev, password: validatePassword(value) ?? undefined }));
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const nextErrors = validateLogin({ email, password });
    setErrors(nextErrors);
    setTouched({ email: true, password: true });

    if (Object.keys(nextErrors).length > 0) {
      (nextErrors.email ? emailRef : passwordRef).current?.focus();
      return;
    }

    setSubmitting(true);
    setFormAlert(null);

    try {
      const user = await login({ email: email.trim(), password });
      const from = (location.state as { from?: { pathname?: string } } | null)?.from;
      const target =
        from?.pathname && canAccess(user.roles, from.pathname)
          ? from.pathname
          : homeFor(user.roles);
      navigate(target, { replace: true });
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setFormAlert({ variant: 'error', message: 'El email o la contraseña no son correctos.' });
        setPassword('');
        passwordRef.current?.focus();
      } else if (error instanceof ApiError && error.status === 429) {
        const wait = error.retryAfter
          ? ` Probá de nuevo en ${error.retryAfter} segundos.`
          : ' Probá de nuevo en unos minutos.';
        setFormAlert({ variant: 'warning', message: `Hiciste demasiados intentos.${wait}` });
      } else if (error instanceof NetworkError || (error instanceof ApiError && error.status >= 500)) {
        setFormAlert({
          variant: 'error',
          message: 'No pudimos conectarnos con el servidor. Revisá tu conexión e intentá de nuevo.',
        });
      } else {
        setFormAlert({
          variant: 'error',
          message: 'No pudimos conectarnos con el servidor. Revisá tu conexión e intentá de nuevo.',
        });
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-ink">Ingresar</h1>
      <p className="mt-1 text-sm text-muted">Accedé con tu email y contraseña.</p>

      <div className="mt-4 space-y-3">
        {sessionExpired && (
          <Alert variant="info">Tu sesión expiró. Ingresá de nuevo para continuar.</Alert>
        )}
        {formAlert && <Alert variant={formAlert.variant}>{formAlert.message}</Alert>}
      </div>

      <form noValidate onSubmit={handleSubmit} aria-busy={submitting} className="mt-4 space-y-4">
        <TextField
          label="Email"
          id="login-email"
          type="email"
          autoComplete="username"
          value={email}
          inputRef={emailRef}
          error={touched.email ? errors.email : undefined}
          onChange={(event) => handleEmailChange(event.target.value)}
          onBlur={() => {
            setTouched((prev) => ({ ...prev, email: true }));
            setErrors((prev) => ({ ...prev, email: validateEmail(email) ?? undefined }));
          }}
          readOnly={submitting}
        />
        <TextField
          label="Contraseña"
          id="login-password"
          type={showPassword ? 'text' : 'password'}
          autoComplete="current-password"
          value={password}
          inputRef={passwordRef}
          error={touched.password ? errors.password : undefined}
          onChange={(event) => handlePasswordChange(event.target.value)}
          onBlur={() => {
            setTouched((prev) => ({ ...prev, password: true }));
            setErrors((prev) => ({ ...prev, password: validatePassword(password) ?? undefined }));
          }}
          readOnly={submitting}
          endAdornment={
            <button
              type="button"
              onClick={() => setShowPassword((value) => !value)}
              aria-pressed={showPassword}
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              className="px-2 text-sm font-semibold text-brand-700"
            >
              {showPassword ? 'Ocultar' : 'Mostrar'}
            </button>
          }
        />
        <Button type="submit" loading={submitting} className="w-full">
          {submitting ? 'Ingresando…' : 'Ingresar'}
        </Button>
      </form>

      <p className="mt-4 text-sm text-muted">
        ¿No tenés cuenta?{' '}
        <Link to="/registro" className="text-brand-700 underline">
          Crear cuenta
        </Link>
      </p>
    </div>
  );
}
