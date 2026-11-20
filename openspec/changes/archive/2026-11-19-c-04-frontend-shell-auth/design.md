# Design

## Context

Ver `proposal.md` §Why. Este change crea el frontend desde cero (`frontend/` no existe) y lo integra con el backend de autenticación **ya mergeado en C-03**.

El contrato real de C-03 (leído del código en `backend/app/auth/router.py` y `backend/app/main.py`) difiere del plan y de la guía de UI:

| Aspecto | Plan (`CHANGES.md`) / guía UI | Implementación real (C-03 mergeado) |
|---|---|---|
| Base de auth | `/api/v1/auth/*` | `/auth/*` (sin prefijo `/api/v1`) |
| Login | devuelve tokens + roles | `{ access_token, token_type, user: { id, email, role } }` |
| `/me` | `roles` (plural) | `{ id, email, role }` (`role` singular) |
| Refresh | `POST /auth/refresh` | **No existe** |
| Persistencia de sesión | cookie HttpOnly + refresh | token devuelto en el body (Bearer) |
| Registro | endpoint de registro | **No existe** |
| Health | — | `/api/health` |

C-04 es frontend-only: no modifica el backend. Por lo tanto el cliente se construye contra el contrato real y centraliza los supuestos en un único punto para absorber cambios futuros.

## Goals / Non-Goals

**Goals:**
- Scaffolding reproducible del SPA y estructura de carpetas de la guía de UI.
- Consumir la autenticación real de C-03 y derivar estado de sesión y RBAC.
- Base reutilizable por C-11, C-12 y C-13 (layouts, RBAC, componentes, cliente HTTP).

**Non-Goals:**
- Cambiar el backend (endpoints, prefijos, refresh, cookies, registro).
- Pantallas de módulos de negocio (turnos, pacientes, profesionales, caja, historia clínica).
- Persistencia de sesión entre recargas o "recordarme".

## Decisions

### 1. Scaffolding: Vite + React + TypeScript + Tailwind + Router v6 + Vitest/RTL
Se usa el stack fijo del proyecto. `react-router-dom` se fija en v6 (la guía lo exige explícitamente). Tests con Vitest + React Testing Library + `@testing-library/user-event` en jsdom. **Sin** axios, React Hook Form, Zod ni librerías de estado: para este alcance alcanzan `fetch`, estado controlado y validadores puros. Cualquier dependencia extra requiere justificación en este documento.

- **Alternativa descartada**: Next.js — el proyecto es una SPA servida aparte del backend; no aporta SSR y suma complejidad.
- **Tailwind**: se usa Tailwind v4 con el plugin `@tailwindcss/vite` y tokens vía `@theme` en `src/styles/index.css`. Nota: `AGENTS.md` menciona "Tailwind ^5.x", versión que no existe al momento; se registra como discrepancia documental (ver Open Questions).

### 2. Alineación al contrato real de C-03 (punto único de cambio)
`lib/config.ts` expone `API_BASE_URL` (`VITE_API_BASE_URL`, por defecto `http://localhost:8000`) y `AUTH_BASE = ${API_BASE_URL}/auth`. `features/auth/authApi.ts` implementa `login`, `me`, `logout` contra `/auth/*`. Si el backend adopta luego `/api/v1`, se cambia solo `config.ts`/`authApi.ts`. Los tipos (`AuthUser`, `LoginResponse`) viven en `features/auth/types.ts`.

- **Alternativa descartada**: usar `/api/v1/auth/*` según el plan → fallaría contra el backend actual (404).

### 3. Sesión en memoria, sin refresh (seguridad sobre comodidad)
El access token se guarda **solo en memoria** (`lib/tokenStore.ts`), nunca en `localStorage`/`sessionStorage`/IndexedDB. Como C-03 no expone `/auth/refresh` ni cookie HttpOnly:
- Al arrancar, si no hay token en memoria → `unauthenticated` inmediato (no hay "checking" prolongado ni restauración silenciosa).
- Al recargar la página la sesión se pierde y se exige login de nuevo. Es el costo aceptado por no persistir credenciales.
- Un `401` en una ruta protegida dispara el flujo de sesión expirada (limpiar estado + `/login?motivo=sesion-expirada`).

- **Alternativa descartada**: persistir el token en `localStorage` → viola la regla de seguridad de la guía y expone credenciales a XSS.
- **Alternativa descartada**: agregar refresh/cookies en el backend → fuera del alcance frontend de C-04.

### 4. RBAC en una sola fuente y normalización de `role`
`lib/rbac.ts` define `Role` (`admin | odontologo | secretaria | paciente`), `APP_ROUTES` (path, label, roles, inMenu, change) y helpers `canAccess`, `menuFor`, `homeFor`. El router y el sidebar se derivan de ahí; no se duplican listas de roles.

Como `/me` y el login devuelven `role` singular, `authApi` normaliza a `AuthUser { id, email, role }` y expone `roles = [role]` para que los helpers trabajen con arreglos (compatibles con un futuro `roles` plural). Prioridad de inicio con varios roles: admin > odontologo > secretaria > paciente.

Decisiones de rutas derivadas de `03_actores_y_roles.md`: `/caja` solo `admin` y `secretaria` (el odontólogo no registra pagos); `admin` accede además a `/agenda`, `/pacientes`, `/caja`. La capacidad "Configurar Horarios/Box" de secretaría no tiene ruta: se deja como pregunta abierta, no se inventa.

### 5. Árbol de rutas (`createBrowserRouter`)
```
AuthLayout      /login · /registro        (con sesión → homeFor)
PublicLayout    /reservar-turno           (placeholder → C-11)
ProtectedRoute  (exige sesión)
 └─ DashboardLayout (Navbar + Sidebar + <Outlet/>)
    └─ ProtectedRoute allowedRoles=[...]  (uno por grupo desde APP_ROUTES)
/               → sesión: homeFor; sin sesión: /login
*               → NotFoundPage
```
Las rutas de módulos sin backend (`/admin/profesionales`, `/agenda`, `/pacientes`, `/caja`) renderizan `ModulePlaceholder` con el change indicado en `APP_ROUTES`, sin tablas ni datos.

### 6. Cliente HTTP con errores tipados y sin fuga de datos
`lib/httpClient.ts` envuelve `fetch` con JSON por defecto, `Authorization: Bearer` desde `tokenStore` y `credentials: 'include'` (inocuo hoy, preparado por si el backend migra a cookies). Mapea errores a `ApiError { status, detail, retryAfter? }` y distingue fallo de red. Un `401` fuera de `/auth/login` y `/auth/logout` dispara sesión expirada. Nunca registra tokens, cuerpos de login ni contraseñas. TypeScript estricto, sin `any`.

- **Nota**: al no existir refresh, no hay reintento automático de la petición; el `401` lleva directo al flujo de expiración.

### 7. Layouts, responsive y accesibilidad
- `AuthLayout`: bloque centrado `max-w-md`, marca arriba, formulario en panel con borde.
- `PublicLayout`: header simple (marca + "Ingresar"), `main` (máx. 1120px), footer mínimo.
- `DashboardLayout`: Navbar fija (menú móvil, nombre y rol, "Cerrar sesión"), Sidebar desde `menuFor(roles)` con `aria-current="page"`; desde `lg` fijo 256px, bajo `lg` drawer con overlay, cierre por Esc/navegación/fuera y foco atrapado y devuelto. Primer elemento enfocable: "Saltar al contenido".
- Foco visible (anillo `brand-700`), un `h1` por vista, landmarks `header`/`nav`/`main`, labels asociados, `aria-invalid`/`aria-describedby`, `lang="es"`, `prefers-reduced-motion`.

### 8. Sistema visual
Tokens de color de la guía (`brand-700 #0E6B73`, etc.) como variables CSS consumidas por nombre. Tipografía Atkinson Hyperlegible auto-hospedada con `@fontsource/atkinson-hyperlegible`, fallback `system-ui`. Escala 14/16/18/20/24/30, pesos 400/600/700. Bordes antes que sombras; sombra solo en capas flotantes. Copy en español rioplatense con voseo, sentence case.

### 9. Formularios y estados
Validación al salir del campo y luego en cada cambio; `noValidate` para controlar mensajes; foco al primer inválido. Estados explícitos: reposo, validando, enviando (botón deshabilitado + spinner + `aria-busy`), `401` (mensaje genérico, conservar email, vaciar y enfocar contraseña), `429` (con `Retry-After` si viene), red/`5xx`, sesión expirada (`role="status"`). Registro: email válido, contraseña mínima 8 (provisional), confirmación coincidente, mostrar/ocultar con `aria-pressed`.

### 10. Registro aislado como contrato pendiente
`authApi.register()` existe pero **no** llama a la red (C-03 no expone endpoint): lanza un error tipado de "contrato pendiente". El formulario valida y muestra el estado correspondiente; no se inventa endpoint ni payload. Queda como tarea de verificación al aparecer el endpoint.

**Contratos pendientes registrados al cierre de C-04:**

- **Envío real de `/registro`**: no existe endpoint en C-03. `RegisterPage` valida y muestra "todavía no está disponible"; `authApi.register()` lanza `PendingContractError` sin red. Se habilitará cuando un change de backend defina método, ruta y payload.
- **Eventual migración a `/api/v1/auth/*`**: hoy el cliente consume `/auth/*` mediante `AUTH_BASE` en `lib/config.ts`; un cambio de prefijo se resuelve en un único punto.
- **Ausencia de `refresh`/cookies**: la sesión vive solo en memoria (`lib/tokenStore.ts`) y un `401` redirige a `/login?motivo=sesion-expirada`. No hay renovación silenciosa ni cookie HttpOnly; si se requiere, es un change de backend (refresh + cookie) seguido de un ajuste acotado en el cliente.

### 11. Tests sin red real
Vitest + RTL con `authApi`/`fetch` mockeados. Mínimos: render del login, campos obligatorios, redirección de no autenticado; más menú por rol (4 casos), `ForbiddenView`, estados del login (enviando/401/429/red/banner expirada) y `httpClient` (401 → sesión expirada). Datos 100% ficticios (`@example.test`, `not-a-real-password`).

### 12. Docker y entorno
Se agrega el servicio `frontend` a `docker-compose.yml` (puerto 5173, `VITE_API_BASE_URL=http://localhost:8000`) y `frontend/.env.example` con solo `VITE_API_BASE_URL`. El backend ya permite CORS desde `http://localhost:5173` con credenciales.

## Risks / Trade-offs

- **[Riesgo] Divergencia de contrato C-03 vs. plan** (`/auth` vs `/api/v1/auth`, sin refresh, `role` singular) → Mitigación: consumo del contrato real y centralización en `config.ts`/`authApi.ts`/`types.ts`; documentado para futuros changes.
- **[Riesgo] Pérdida de sesión al recargar** (token solo en memoria, sin refresh) → Mitigación: comportamiento explícito y aceptado; el flujo de sesión expirada cubre el `401`. Si se requiere persistencia, será un change de backend (refresh + cookie HttpOnly).
- **[Riesgo] Registro sin backend** → Mitigación: formulario + validación completos, envío aislado como pendiente; no se inventa contrato.
- **[Riesgo] Tailwind v4 vs. mención "5.x" en AGENTS.md** → Mitigación: se usa v4 estable y se registra la discrepancia; el sistema de tokens es portable.
- **[Riesgo] RBAC solo de UX** → Mitigación: el backend sigue siendo la autoridad (`get_current_user`); el frontend oculta y bloquea, no autoriza.
- **[Riesgo] Accesibilidad y responsive incompletos** → Mitigación: checklist de la guía + verificación en 360×740, 768×1024 y 1280×800 y evidencia con MCP de navegador.

## Migration Plan

1. Crear `frontend/` con el scaffolding y tokens; `npm run build` y `npm test` en verde.
2. Implementar `lib/` (config, tokenStore, httpClient, rbac) y `features/auth` (types, authApi, validators, AuthContext, ProtectedRoute).
3. Implementar layouts, páginas (`/login`, `/registro`, `NotFoundPage`, `ModulePlaceholder`, `ForbiddenView`) y componentes `components/ui`.
4. Agregar servicio `frontend` a `docker-compose.yml` y `.env.example`.
5. Verificar contra backend real (C-03) y registrar evidencia; **no archivar** hasta completar la verificación.

Rollback: al ser un directorio nuevo, se elimina `frontend/` y el servicio de `docker-compose.yml`; no afecta al backend.

## Open Questions

- ¿El backend migrará los endpoints de auth a `/api/v1/auth/*` y agregará `refresh` + cookie HttpOnly? (afecta persistencia de sesión; hoy no bloquea).
- ¿La secretaría necesita una ruta para "Configurar Horarios/Box"? (la matriz la habilita pero no hay ruta; no se inventa).
- ¿Se adopta Atkinson Hyperlegible vía `@fontsource` o se usa solo el fallback? (si el paquete no está disponible al implementar).
- ¿El contrato de `/registro` (endpoint y payload) lo define un change futuro?
