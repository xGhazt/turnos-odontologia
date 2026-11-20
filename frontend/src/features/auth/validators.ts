import type { Role } from '../../lib/rbac';

const KNOWN_ROLES: readonly Role[] = ['admin', 'odontologo', 'secretaria', 'paciente'];

export const MIN_PASSWORD_LENGTH = 8;

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function toRole(value: string): Role {
  return (KNOWN_ROLES as readonly string[]).includes(value) ? (value as Role) : 'paciente';
}

export function validateEmail(value: string): string | null {
  const trimmed = value.trim();
  if (trimmed === '') return 'El email es obligatorio.';
  if (!EMAIL_PATTERN.test(trimmed)) return 'Ingresá un email válido.';
  return null;
}

export function validatePassword(value: string): string | null {
  if (value === '') return 'La contraseña es obligatoria.';
  if (value.length < MIN_PASSWORD_LENGTH) {
    return `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres.`;
  }
  return null;
}

export function validateConfirmation(password: string, confirmation: string): string | null {
  if (confirmation === '') return 'Repetí la contraseña.';
  if (password !== confirmation) return 'Las contraseñas no coinciden.';
  return null;
}

export interface LoginValues {
  email: string;
  password: string;
}

export interface LoginErrors {
  email?: string;
  password?: string;
}

export function validateLogin(values: LoginValues): LoginErrors {
  const errors: LoginErrors = {};
  const email = validateEmail(values.email);
  const password = validatePassword(values.password);
  if (email) errors.email = email;
  if (password) errors.password = password;
  return errors;
}

export interface RegisterValues {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface RegisterErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
}

export function validateRegister(values: RegisterValues): RegisterErrors {
  const errors: RegisterErrors = {};
  const email = validateEmail(values.email);
  const password = validatePassword(values.password);
  const confirmation = validateConfirmation(values.password, values.confirmPassword);
  if (email) errors.email = email;
  if (password) errors.password = password;
  if (confirmation) errors.confirmPassword = confirmation;
  return errors;
}
