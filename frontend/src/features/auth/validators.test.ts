import { describe, expect, it } from 'vitest';
import {
  MIN_PASSWORD_LENGTH,
  validateConfirmation,
  validateEmail,
  validateLogin,
  validatePassword,
  validateRegister,
} from './validators';

describe('validators', () => {
  it('valida el email obligatorio y con formato', () => {
    expect(validateEmail('')).toMatch(/obligatorio/i);
    expect(validateEmail('no-es-un-email')).toMatch(/válido/i);
    expect(validateEmail('demo@example.test')).toBeNull();
  });

  it('exige la longitud mínima de contraseña', () => {
    expect(validatePassword('')).toMatch(/obligatoria/i);
    expect(validatePassword('a'.repeat(MIN_PASSWORD_LENGTH - 1))).toMatch(/al menos/i);
    expect(validatePassword('a'.repeat(MIN_PASSWORD_LENGTH))).toBeNull();
  });

  it('valida la confirmación de contraseña', () => {
    expect(validateConfirmation('abcdefgh', '')).toMatch(/repetí/i);
    expect(validateConfirmation('abcdefgh', 'otra-cosa')).toMatch(/no coinciden/i);
    expect(validateConfirmation('abcdefgh', 'abcdefgh')).toBeNull();
  });

  it('validateLogin devuelve los errores de campos vacíos', () => {
    const errors = validateLogin({ email: '', password: '' });
    expect(errors.email).toBeDefined();
    expect(errors.password).toBeDefined();
  });

  it('validateLogin no devuelve errores con datos válidos', () => {
    expect(
      validateLogin({ email: 'demo@example.test', password: 'not-a-real-password' }),
    ).toEqual({});
  });

  it('validateRegister acumula los tres errores', () => {
    const errors = validateRegister({ email: 'mal', password: 'corta', confirmPassword: 'otra' });
    expect(errors.email).toBeDefined();
    expect(errors.password).toBeDefined();
    expect(errors.confirmPassword).toBeDefined();
  });

  it('validateRegister no devuelve errores con datos válidos', () => {
    expect(
      validateRegister({
        email: 'demo@example.test',
        password: 'not-a-real-password',
        confirmPassword: 'not-a-real-password',
      }),
    ).toEqual({});
  });
});
