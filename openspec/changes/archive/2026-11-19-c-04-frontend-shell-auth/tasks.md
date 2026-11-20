# Tasks

## 1. Scaffolding y tooling

- [x] 1.1 Crear el proyecto en `frontend/` con Vite + React + TypeScript (estructura de `design.md` §4.1 de la guía) y verificar que `npm run build` compila sin errores.
- [x] 1.2 Configurar Tailwind v4 (`@tailwindcss/vite`), tokens de color y tipografía Atkinson Hyperlegible con fallback en `src/styles/index.css`; verificar que `npm run build` pasa y que los tokens se aplican en una vista mínima.
- [x] 1.3 Instalar `react-router-dom@6`, Vitest, jsdom, React Testing Library y `@testing-library/user-event`; verificar que `npm test` corre un smoke test inicial en verde.
- [x] 1.4 Crear `src/lib/config.ts` y `frontend/.env.example` con solo `VITE_API_BASE_URL`; verificar con un test unitario que `AUTH_BASE` se deriva de la variable y no hay secretos en el repo.

## 2. Núcleo `lib/` (TDD)

- [x] 2.1 Implementar `lib/tokenStore.ts` (token solo en memoria) con tests RED→GREEN que verifiquen set/get/clear y que no usa `localStorage`/`sessionStorage`.
- [x] 2.2 Implementar `lib/rbac.ts` (`Role`, `APP_ROUTES`, `canAccess`, `menuFor`, `homeFor`) con tests que cubran los 4 roles, el acceso denegado y la prioridad admin > odontologo > secretaria > paciente.
- [x] 2.3 Implementar `lib/httpClient.ts` con `ApiError` tipado, `Authorization: Bearer` y manejo de `401`, error de red y `Retry-After`; verificar con tests que un `401` dispara sesión expirada y que no se registran tokens ni contraseñas.

## 3. Feature de autenticación (TDD)

- [x] 3.1 Implementar `features/auth/types.ts` y `authApi.ts` (`login`, `me`, `logout`) contra los endpoints reales `/auth/*`, normalizando `role` singular a `roles`; verificar con tests de `fetch` mockeado el parseo de login, `/me` y logout, y que `register()` no hace red (contrato pendiente).
- [x] 3.2 Implementar `features/auth/validators.ts` (email, contraseña mínima 8, confirmación) con tests RED→GREEN de casos válidos e inválidos.
- [x] 3.3 Implementar `AuthContext` (`checking`/`authenticated`/`unauthenticated`, `login`, `logout`) con tests: sin token en memoria → `unauthenticated`; login exitoso guarda usuario; logout limpia estado aunque la API falle; `401` en ruta protegida dispara sesión expirada.
- [x] 3.4 Implementar `ProtectedRoute` con tests: sin sesión redirige a `/login` recordando `from`; rol no permitido renderiza `ForbiddenView`; estado `checking` muestra spinner.

## 4. Componentes UI transversales (TDD)

- [x] 4.1 Implementar `Button`, `TextField`, `Alert` y `Spinner` con tests que verifiquen labels asociados, `aria-invalid`/`aria-describedby`, `aria-busy` y foco visible.
- [x] 4.2 Implementar `ConfirmDialog` y `Toast` con tests de foco atrapado, cierre con Escape y anuncio accesible (`role`/`aria-live`).
- [x] 4.3 Implementar `ModulePlaceholder`, `NotFoundPage` y `ForbiddenView` con tests de render y de la acción para volver al inicio.

## 5. Layouts, páginas y navegación (TDD)

- [x] 5.1 Implementar `AuthLayout`, `LoginPage` y `RegisterPage` con tests de render, campos obligatorios, estados enviando/401/429/red, banner de sesión expirada y mostrar/ocultar contraseña.
- [x] 5.2 Implementar `PublicLayout` y la ruta `/reservar-turno` con `ModulePlaceholder` (C-11); verificar con test de render que no hay datos ni tablas de ejemplo.
- [x] 5.3 Implementar `DashboardLayout` (Navbar + Sidebar responsive con drawer) con tests del menú por cada rol y del cierre por Esc, navegación y foco devuelto.
- [x] 5.4 Cablear el árbol de rutas con `createBrowserRouter` y verificar con tests: raíz sin sesión → `/login`, ruta inexistente → `NotFoundPage`, `/login` con sesión → `homeFor(roles)`.

## 6. Integración de entorno

- [x] 6.1 Agregar el servicio `frontend` a `docker-compose.yml` (puerto 5173, `VITE_API_BASE_URL=http://localhost:8000`) y verificar con `docker compose config` que el servicio resuelve sin errores.
- [x] 6.2 Verificar que el backend acepta el origen `http://localhost:5173` con credenciales (CORS ya configurado) usando un test de preflight existente o una comprobación manual documentada.

## 7. Integración y verificación

- [x] 7.1 Ejecutar `npm run lint`, `npm run build` y `npm test` en `frontend/` y verificar que los tres pasan sin errores ni `any`.
- [x] 7.2 Probar el flujo real contra el backend con C-03 mergeado: login válido, credenciales inválidas, `/me`, logout y sesión expirada; registrar evidencia en `docs/evidence/C-04/`.
- [x] 7.3 Verificar accesibilidad y responsive en 360×740, 768×1024 y 1280×800 con el MCP de navegador: snapshot de accesibilidad, capturas y consola sin errores.
- [x] 7.4 Documentar como pendientes de contrato el envío real de `/registro`, una eventual migración a `/api/v1/auth/*` y la ausencia de `refresh`/cookies, en `design.md` o notas del change.

## Workflow follow-up

- No archivar C-04 ni marcar `[x]` en `CHANGES.md` hasta completar la verificación contra el backend real con C-03 mergeado y la revisión.
- Ejecutar `/opsx-archive` solo tras la aprobación del usuario.
