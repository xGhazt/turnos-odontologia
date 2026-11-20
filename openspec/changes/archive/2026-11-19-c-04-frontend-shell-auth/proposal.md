# Proposal

## Why

El change C-03 entregó la API de autenticación (JWT) pero el proyecto todavía no tiene frontend: no existe el directorio `frontend/`. Sin un shell web no hay forma de iniciar sesión, distinguir vistas por rol ni consumir los endpoints protegidos, y los changes de interfaz posteriores (C-11, C-12, C-13) no tendrían dónde montarse. C-04 crea ese cimiento y lo conecta con la autenticación ya existente.

## What Changes

- **Scaffolding del frontend**: proyecto React + TypeScript + Vite + Tailwind CSS + React Router v6 + Vitest + React Testing Library, con estructura de carpetas, tokens de diseño y `VITE_API_BASE_URL` en `.env.example`.
- **Layouts y enrutamiento**: `PublicLayout`, `AuthLayout` y `DashboardLayout` (Navbar + Sidebar responsive) más `NotFoundPage` y `ModulePlaceholder` para módulos aún no implementados.
- **Estado de autenticación**: `AuthContext` que consume el contrato real de C-03 (`POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout`), token en memoria, login, logout y redirección por expiración.
- **Vistas de acceso**: `/login` y `/registro` completas con validación, estados de carga/error y accesibilidad; el envío real de registro queda aislado como contrato pendiente (C-03 no expone endpoint de registro).
- **Protección por rol**: `ProtectedRoute` y una fuente única de RBAC (`lib/rbac.ts`) de la que se derivan rutas y menú según los 4 roles.
- **Componentes transversales**: `Button`, `TextField`, `Alert`, `Spinner`, `ConfirmDialog`, `Toast` y cliente HTTP con manejo de `401`, errores tipados y sin fuga de tokens.
- **Tests de UI**: render del login, validación de campos obligatorios, redirección de no autenticados, menú por rol, `ForbiddenView` y estados del login/cliente HTTP sin red real.

## Capabilities

### New Capabilities
- `web-client`: shell de la aplicación web (scaffolding, layouts, enrutamiento, RBAC, estado de sesión, vistas de autenticación y componentes transversales) que consumen los endpoints de C-03 y sirven de base a los módulos de interfaz posteriores.

### Modified Capabilities
- (ninguna — C-04 no cambia requisitos del backend ni de `core-domain`; solo agrega comportamiento del cliente web)

## Impact

- **Código nuevo**: directorio `frontend/` completo (aplicación SPA, estilos, tests). No se modifica el backend.
- **API consumida**: `POST /api/v1/auth/login`, `GET /api/v1/auth/me`, `POST /api/v1/auth/logout` (C-03 ya implementados). El CORS del backend ya permite `http://localhost:5173`.
- **Dependencias**: React, React DOM, React Router v6, Tailwind CSS, Vite, TypeScript, Vitest, React Testing Library, `@testing-library/user-event` y `@fontsource/atkinson-hyperlegible`. Sin librerías de estado, formularios ni HTTP adicionales.
- **Infraestructura**: se agrega el servicio `frontend` a `docker-compose.yml` (puerto 5173) y `.env.example` del frontend.
- **Supuestos documentados**: el contrato real de C-03 usa `Authorization: Bearer <token>`, devuelve `role` (singular) y no expone `/auth/refresh` ni endpoint de registro. Las diferencias con la guía `odontologia-ui-guide` (que asumía cookie HttpOnly y `roles` plural) se registran en `design.md`.
- **Fuera de alcance**: pantallas de turnos, pacientes, profesionales, caja o historia clínica (C-05/C-06/C-10/C-11/C-12/C-13); refresh tokens/cookies HttpOnly (requeriría cambios de backend); recuperación de contraseña, MFA y login social.
