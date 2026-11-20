import { useRef, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import {
  validateConfirmation,
  validateEmail,
  validatePassword,
  validateRegister,
  type RegisterErrors,
} from '../validators';
import { register } from '../authApi';
import { Alert } from '../../../components/ui/Alert';
import { Button } from '../../../components/ui/Button';
import { TextField } from '../../../components/ui/TextField';

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<RegisterErrors>({});
  const [touched, setTouched] = useState({ email: false, password: false, confirmPassword: false });
  const [submitting, setSubmitting] = useState(false);
  const [pendingNotice, setPendingNotice] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const emailRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);
  const confirmRef = useRef<HTMLInputElement>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const nextErrors = validateRegister({ email, password, confirmPassword });
    setErrors(nextErrors);
    setTouched({ email: true, password: true, confirmPassword: true });

    if (Object.keys(nextErrors).length > 0) {
      const firstInvalid = nextErrors.email
        ? emailRef
        : nextErrors.password
          ? passwordRef
          : confirmRef;
      firstInvalid.current?.focus();
      return;
    }

    setSubmitting(true);
    setPendingNotice(false);

    try {
      await register({ email: email.trim(), password, confirmPassword });
    } catch {
      setPendingNotice(true);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-ink">Crear cuenta</h1>
      <p className="mt-1 text-sm text-muted">Registrate para reservar y seguir tus turnos.</p>

      {pendingNotice && (
        <div className="mt-4">
          <Alert variant="info">
            El registro todavía no está disponible. El envío se habilitará cuando la API lo exponga.
          </Alert>
        </div>
      )}

      <form noValidate onSubmit={handleSubmit} aria-busy={submitting} className="mt-4 space-y-4">
        <TextField
          label="Email"
          id="register-email"
          type="email"
          autoComplete="username"
          value={email}
          inputRef={emailRef}
          error={touched.email ? errors.email : undefined}
          onChange={(event) => {
            setEmail(event.target.value);
            if (touched.email) {
              setErrors((prev) => ({ ...prev, email: validateEmail(event.target.value) ?? undefined }));
            }
          }}
          onBlur={() => {
            setTouched((prev) => ({ ...prev, email: true }));
            setErrors((prev) => ({ ...prev, email: validateEmail(email) ?? undefined }));
          }}
          readOnly={submitting}
        />
        <TextField
          label="Contraseña"
          id="register-password"
          type={showPassword ? 'text' : 'password'}
          autoComplete="new-password"
          value={password}
          inputRef={passwordRef}
          error={touched.password ? errors.password : undefined}
          onChange={(event) => {
            setPassword(event.target.value);
            if (touched.password) {
              setErrors((prev) => ({ ...prev, password: validatePassword(event.target.value) ?? undefined }));
            }
          }}
          onBlur={() => {
            setTouched((prev) => ({ ...prev, password: true }));
            setErrors((prev) => ({ ...prev, password: validatePassword(password) ?? undefined }));
          }}
          readOnly={submitting}
          hint="Al menos 8 caracteres."
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
        <TextField
          label="Repetir contraseña"
          id="register-confirm"
          type={showPassword ? 'text' : 'password'}
          autoComplete="new-password"
          value={confirmPassword}
          inputRef={confirmRef}
          error={touched.confirmPassword ? errors.confirmPassword : undefined}
          onChange={(event) => {
            setConfirmPassword(event.target.value);
            if (touched.confirmPassword) {
              setErrors((prev) => ({
                ...prev,
                confirmPassword: validateConfirmation(password, event.target.value) ?? undefined,
              }));
            }
          }}
          onBlur={() => {
            setTouched((prev) => ({ ...prev, confirmPassword: true }));
            setErrors((prev) => ({
              ...prev,
              confirmPassword: validateConfirmation(password, confirmPassword) ?? undefined,
            }));
          }}
          readOnly={submitting}
        />
        <Button type="submit" loading={submitting} className="w-full">
          {submitting ? 'Creando cuenta…' : 'Crear cuenta'}
        </Button>
      </form>

      <p className="mt-4 text-sm text-muted">
        ¿Ya tenés cuenta?{' '}
        <Link to="/login" className="text-brand-700 underline">
          Ingresar
        </Link>
      </p>
    </div>
  );
}
