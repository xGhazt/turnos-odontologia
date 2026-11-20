import type { Role } from '../../lib/rbac';

export interface AuthUser {
  id: number;
  email: string;
  role: Role;
  /** Arreglo derivado de `role` para que el RBAC trabaje con roles. */
  roles: Role[];
}

/** Forma cruda del usuario tal como la devuelve la API de C-03 (`role` singular). */
export interface ApiUser {
  id: number;
  email: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: ApiUser;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  confirmPassword: string;
}

/** El registro todavía no tiene endpoint en la API (C-03 no lo expone). */
export class PendingContractError extends Error {
  constructor(message = 'El registro todavía no tiene un endpoint disponible en la API.') {
    super(message);
    this.name = 'PendingContractError';
  }
}
