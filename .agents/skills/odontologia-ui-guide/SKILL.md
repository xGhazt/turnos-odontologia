---
name: odontologia-ui-guide
description: Guía de diseño UI/UX clínico y de arquitectura React para el frontend de turnos-odontologia (React + TypeScript + Vite + Tailwind). Usar SIEMPRE que se cree o modifique código en `frontend/`; layouts (PublicLayout, AuthLayout, DashboardLayout), login y registro, ProtectedRoute, AuthContext, menú lateral por rol (RBAC), cliente HTTP con cookies HttpOnly, formularios, estados de carga/error/sesión expirada, responsive, tests de UI y cualquier vista de los changes C-04, C-11, C-12 o C-13, aunque el pedido no mencione "diseño" ni "skill". Incluye el checklist de auditoría previo a cerrar una vista y la regla de datos 100% ficticios.
---

# odontologia-ui-guide

Guía para construir el frontend de **turnos-odontologia**: una interfaz clínica, calma y legible, con acceso por rol y sin datos reales. Resuelve tres problemas del proyecto: (1) que cada vista nueva se vea y se comporte igual que las anteriores, (2) que el menú y las rutas respeten la matriz RBAC en un único lugar, y (3) que ningún change de frontend se cierre sin auditoría.

## 1. Propósito y alcance

- **Aplica a**: todo lo que viva en `frontend/`. Hoy el foco es **C-04 `frontend-shell-auth`**; las reglas de diseño y arquitectura se reutilizan en C-11 (portal de reserva), C-12 (agenda) y C-13 (caja).
- **No reemplaza** a `CHANGES.md` ni a la knowledge-base: si algo de acá contradice el scope de un change, manda el scope del change. Registrar la desviación en `design.md` del change.
- **No decide negocio**: reglas de turnos, señas o historia clínica viven en el backend y en la knowledge-base.

## 2. Fuentes de verdad (leer antes de escribir código)

1. `CHANGES.md` → scope del change en curso (para C-04: sección `[C-04]`).
2. `knowledge-base/02_descripcion_general.md` §Stack Tecnológico (Frontend).
3. `knowledge-base/03_actores_y_roles.md` §Matriz RBAC y §Rutas y Accesibilidad.
4. `knowledge-base/08_arquitectura_propuesta.md` §Estructura de Directorios Propuesta (frontend). **Si define una estructura distinta a la de la sección 4.1, prevalece el documento 08**; anotar la diferencia en `design.md`.

Stack fijo: React (SPA) + TypeScript + Vite + Tailwind CSS + React Router v6 (fijar `react-router-dom@6`) + Vitest + React Testing Library. No agregar librerías fuera del stack (axios, React Hook Form, Zod, Redux, etc.) sin justificarlo por escrito en `design.md`; para este scope alcanzan `fetch`, estado controlado y validadores puros.

## 3. Estándares visuales y UX clínica

### 3.1 Principios

- **Calma y claridad antes que personalidad.** La persona puede estar nerviosa (paciente) o apurada (recepción). Pocas decisiones por pantalla, acciones obvias, errores que dicen qué hacer.
- **Una sola cosa memorable por pantalla** (el formulario, la acción principal); el resto queda silencioso.
- **Bordes antes que sombras.** Separar con borde de 1px y espacio; reservar la sombra para capas flotantes (drawer, modal, toast). No partir todo en tarjetas idénticas.
- **Sin movimiento decorativo.** Solo transiciones que responden a una acción (abrir el drawer, enviar un formulario). Respetar `prefers-reduced-motion`.

### 3.2 Paleta (tokens)

Definir como variables CSS en `src/styles/index.css` (`@theme` en Tailwind v4, o `theme.extend.colors` en v3) y consumir solo por nombre de token, nunca hex suelto en componentes.

| Token | Hex | Uso |
|---|---|---|
| `brand-700` | `#0E6B73` | Acción primaria, links, foco, ítem activo |
| `brand-800` | `#0A545B` | Hover/pressed de acción primaria |
| `brand-100` | `#D6ECEE` | Bordes suaves sobre fondo brand |
| `brand-50` | `#EEF7F8` | Fondo de ítem activo en sidebar |
| `ink` | `#16232B` | Texto principal |
| `muted` | `#5B6B75` | Texto secundario, hints |
| `line` | `#D5DEE3` | Bordes y divisores |
| `canvas` | `#F5F8FA` | Fondo de la app |
| `surface` | `#FFFFFF` | Paneles, inputs, navbar |
| `success` / `success-50` | `#1F7A4D` / `#E7F4EC` | Confirmaciones |
| `warning` / `warning-50` | `#8A5A00` / `#FFF4DB` | Avisos |
| `danger` / `danger-50` | `#B3261E` / `#FDECEA` | Errores, acciones destructivas |
| `info` / `info-50` | `#1F5FA8` / `#E8F0FA` | Mensajes informativos (p. ej. sesión expirada) |

- Contraste mínimo **WCAG AA** (4.5:1 texto normal, 3:1 texto grande y bordes de controles). Verificar en la auditoría; si un par no pasa, oscurecer el token.
- El estado nunca se comunica solo con color: sumar icono y texto.
- Los colores por estado de turno (`pendiente_seña`, `confirmado`, etc.) **no** se definen en C-04; los define C-12.

### 3.3 Tipografía

- Una sola familia: **Atkinson Hyperlegible** (pensada para legibilidad; útil con pacientes mayores y números como horas y DNI). Instalar auto-hospedada (`@fontsource/atkinson-hyperlegible`), sin CDN. Fallback: `system-ui, -apple-system, "Segoe UI", sans-serif`. Si el paquete no está disponible, usar solo el fallback y anotarlo.
- Escala: `14` (apoyo) · `16` (base, y mínimo en inputs para evitar zoom en iOS) · `18` · `20` · `24` (título de vista) · `30` (título de auth/público). Pesos 400 y 600; 700 solo para títulos.
- Interlineado 1.5 en párrafos, 1.25 en títulos. Líneas de lectura < 75 caracteres.
- Sentence case en todo el texto. Sin MAYÚSCULAS sostenidas en etiquetas ni "eyebrows" decorativos.

### 3.4 Jerarquía y layout

- Un solo `h1` por vista; los `h2` agrupan secciones. Debajo del `h1`, una línea de contexto opcional (`muted`).
- Acción primaria: un solo botón relleno `brand-700` por vista/formulario. Secundaria: contorno. Destructiva: `danger`, siempre con confirmación (`ConfirmDialog`).
- Radios: controles `8px`, paneles `12px`, modal/drawer `16px`. Espaciado en múltiplos de 4px.
- Alineación a la izquierda; sin texto justificado ni centrado en párrafos (solo el título y el formulario de auth van centrados como bloque).
- Foco visible en todo elemento interactivo: anillo de 2px `brand-700` con offset de 2px.

### 3.5 Responsive

- Mobile-first. Breakpoints de Tailwind: base (360px), `md` 768px, `lg` 1024px, `xl` 1280px.
- `DashboardLayout`: bajo `lg` el sidebar es un **drawer** (abre desde la Navbar, overlay, cierra con Esc, al navegar y al tocar fuera, con foco atrapado y devuelto al botón); desde `lg` es fijo de 256px.
- Objetivos táctiles ≥ 44×44px. Sin scroll horizontal a 360px. Tablas anchas scrollean dentro de su propio contenedor.
- Viewports de verificación obligatorios: **360×740**, **768×1024**, **1280×800**.

### 3.6 Estados de formularios (explícitos, siempre)

| Estado | Comportamiento esperado |
|---|---|
| Reposo | Label visible encima del campo (nunca placeholder como label), hint opcional en `muted`. |
| Validación de campo | Validar al salir del campo (`onBlur`) la primera vez y luego en cada cambio. Mensaje bajo el campo con icono + texto; `aria-invalid="true"` y `aria-describedby` apuntando al mensaje. Formulario con `noValidate` para controlar los textos. |
| Envío con errores | No enviar; llevar el foco al primer campo inválido. |
| Enviando | Botón deshabilitado con spinner y texto de progreso ("Ingresando…"), campos `readOnly`, `aria-busy="true"`. Impedir envíos duplicados. |
| Credenciales inválidas (401) | `Alert` `role="alert"` sobre el formulario: "El email o la contraseña no son correctos." No revelar cuál falló. Conservar el email, vaciar la contraseña y enfocarla. |
| Demasiados intentos (429) | "Hiciste demasiados intentos. Probá de nuevo en unos minutos." Si llega `Retry-After`, mostrar el tiempo. |
| Error de red o 5xx | "No pudimos conectarnos con el servidor. Revisá tu conexión e intentá de nuevo." Conservar lo tipeado. |
| Sesión expirada | Redirigir a `/login?motivo=sesion-expirada` y mostrar `Alert` informativo (`role="status"`): "Tu sesión expiró. Ingresá de nuevo para continuar." Tras el login, volver a la ruta original si el rol la permite. |
| Verificando sesión (arranque) | Pantalla completa con spinner y "Verificando sesión…". Sin parpadeo de la pantalla de login. |
| Registro | Email con formato válido; contraseña con el mínimo que defina el backend (provisional: 8 caracteres); confirmación que coincida; mostrar/ocultar contraseña con `button type="button"` y `aria-pressed`. |

Atributos obligatorios: `autocomplete` (`username`, `current-password`, `new-password`), `type="email"`, `lang="es"` en `<html>`.

### 3.7 Voz y copy

- Español rioplatense con voseo ("Ingresá", "Volvé", "Probá"). Verbos claros en botones: "Ingresar", "Crear cuenta", "Cerrar sesión".
- Un mismo nombre para una misma acción en todo el flujo (botón, toast, título).
- Los errores explican qué pasó y cómo seguir; no piden disculpas ni son vagos.
- Identificadores de código en inglés, salvo términos de dominio y valores de rol/ruta (`odontologo`, `secretaria`, `/pacientes`).

## 4. Convenciones de arquitectura React

### 4.1 Estructura de carpetas (propuesta; ver sección 2 sobre el documento 08)

```
frontend/
├── index.html
├── package.json · vite.config.ts · tsconfig*.json · eslint config
├── .env.example                  # solo VITE_API_BASE_URL (sin secretos)
└── src/
    ├── main.tsx
    ├── app/                      # App.tsx, router.tsx, providers.tsx
    ├── layouts/                  # PublicLayout · AuthLayout · DashboardLayout
    ├── features/
    │   └── auth/                 # AuthContext, useAuth, ProtectedRoute, authApi,
    │                             # types.ts, validators.ts, pages/LoginPage · RegisterPage
    ├── pages/                    # NotFoundPage, ForbiddenView, ModulePlaceholder
    ├── components/ui/            # Button, TextField, Alert, Spinner, ConfirmDialog, Toast
    ├── lib/                      # httpClient.ts, tokenStore.ts, rbac.ts, config.ts
    ├── styles/index.css          # tokens
    └── test/                     # setup.ts, renderWithProviders.tsx
```

Regla de dependencias: `pages` y `features` usan `components/ui` y `lib`; `lib` no importa de `features`. Cada feature guarda sus tipos y su cliente de API (`authApi.ts`); los componentes no llaman a `fetch` directamente.

### 4.2 Fuente única de RBAC (`lib/rbac.ts`)

Un solo arreglo describe rutas, roles y menú. El router y el sidebar se derivan de él; no duplicar listas de roles en componentes.

```ts
export type Role = 'admin' | 'odontologo' | 'secretaria' | 'paciente';

export interface AppRoute {
  path: string;
  label: string;
  roles: readonly Role[];
  inMenu: boolean;
  /** Change que implementa la vista real (para el placeholder). */
  change?: string;
}

export const APP_ROUTES: readonly AppRoute[] = [
  { path: '/admin/dashboard',     label: 'Panel',         roles: ['admin'],                            inMenu: true },
  { path: '/admin/profesionales', label: 'Profesionales', roles: ['admin'],                            inMenu: true, change: 'C-06' },
  { path: '/admin/configuracion', label: 'Configuración', roles: ['admin'],                            inMenu: true },
  { path: '/agenda',              label: 'Agenda',        roles: ['admin', 'odontologo', 'secretaria'], inMenu: true, change: 'C-12' },
  { path: '/pacientes',           label: 'Pacientes',     roles: ['admin', 'odontologo', 'secretaria'], inMenu: true, change: 'C-05' },
  { path: '/caja',                label: 'Caja',          roles: ['admin', 'secretaria'],              inMenu: true, change: 'C-13' },
  { path: '/mi-portal',           label: 'Mi portal',     roles: ['paciente'],                         inMenu: true },
  { path: '/mis-turnos',          label: 'Mis turnos',    roles: ['paciente'],                         inMenu: true },
];
```

Decisiones derivadas de `03_actores_y_roles.md` (documentarlas en `design.md` y confirmarlas con el equipo):

- La matriz es más fina que la lista de rutas: `/caja` queda para `admin` y `secretaria` porque el odontólogo no registra pagos/caja.
- `admin` tiene "SÍ" en agenda, pacientes y caja, por eso accede a esas rutas además de `/admin/*`.
- La matriz da a Secretaria "Configurar Horarios/Box", pero no existe una ruta para eso. **No inventarla**; dejarla como pregunta abierta.
- `GET /api/v1/auth/me` devuelve **roles** (plural). Tratar `roles` como arreglo: se accede si **algún** rol coincide.

Menú resultante: **admin** → Panel, Profesionales, Configuración, Agenda, Pacientes, Caja · **odontologo** → Agenda, Pacientes · **secretaria** → Agenda, Pacientes, Caja · **paciente** → Mi portal, Mis turnos.

Helpers exportados: `canAccess(roles, path)`, `menuFor(roles)` y `homeFor(roles)` (admin → `/admin/dashboard`; odontologo y secretaria → `/agenda`; paciente → `/mi-portal`; con varios roles, prioridad admin > odontologo > secretaria > paciente).

El frontend solo **oculta y bloquea por UX**; la autoridad de acceso es siempre el backend (`require_role`).

### 4.3 Layouts y árbol de rutas (React Router v6, `createBrowserRouter`)

```
AuthLayout        /login · /registro             (con sesión activa → redirigir a homeFor)
PublicLayout      /reservar-turno                (placeholder → C-11)
ProtectedRoute                                   (exige sesión)
 └─ DashboardLayout                              (Navbar + Sidebar + <Outlet/>)
     └─ ProtectedRoute allowedRoles=[...]        (uno por grupo, generado desde APP_ROUTES)
/                 → con sesión: homeFor(roles); sin sesión: /login   (no hay landing)
*                 → NotFoundPage
```

- **PublicLayout**: header simple (marca + "Ingresar"), `main`, footer mínimo. Ancho máximo de contenido 1120px.
- **AuthLayout**: bloque centrado, `max-w-md`, marca arriba, formulario en un panel con borde. Sin navegación.
- **DashboardLayout**: Navbar fija arriba (botón de menú en móvil, nombre y rol del usuario, "Cerrar sesión"), Sidebar con `menuFor(user.roles)` y `aria-current="page"` en el ítem activo, `main` con `max-w-7xl`. Incluir "Saltar al contenido" como primer elemento enfocable.
- Las rutas de módulos que **todavía no tienen backend** renderizan `ModulePlaceholder`: título de la vista, una línea ("Este módulo se implementa en un change posterior.") y el change si `APP_ROUTES` lo indica. Sin tablas, tarjetas, filtros ni datos de ejemplo.

### 4.4 `AuthContext`

```ts
type AuthStatus = 'checking' | 'authenticated' | 'unauthenticated';

interface AuthContextValue {
  status: AuthStatus;
  user: AuthUser | null;                 // tipo provisional en features/auth/types.ts
  login(c: { email: string; password: string }): Promise<void>;
  logout(): Promise<void>;
}
```

- **El access token vive solo en memoria** (`lib/tokenStore.ts`). Prohibido `localStorage`, `sessionStorage` e IndexedDB para tokens o datos de usuario.
- **Arranque**: `status='checking'` → `POST /api/v1/auth/refresh` (la cookie HttpOnly viaja sola) → `GET /api/v1/auth/me`. Si el refresh falla en el arranque, pasa a `unauthenticated` en silencio (no es "sesión expirada": nunca hubo sesión en esta carga).
- **Expiración**: si había sesión y un refresh falla, limpiar estado y redirigir a `/login?motivo=sesion-expirada`, recordando la ruta de origen.
- **Logout**: llamar a `POST /api/v1/auth/logout` y limpiar estado aunque la llamada falle.
- Contrato de C-03 **provisional**: concentrar los supuestos (forma de `/me`, nombre del campo del access token, formato de error de FastAPI `detail`) en `features/auth/types.ts` y `authApi.ts`, para ajustarlos en un solo lugar al mergear C-03.

### 4.5 `ProtectedRoute`

```tsx
export function ProtectedRoute({ allowedRoles }: { allowedRoles?: readonly Role[] }) {
  const { status, user } = useAuth();
  const location = useLocation();

  if (status === 'checking') return <FullPageSpinner label="Verificando sesión…" />;
  if (status === 'unauthenticated') {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  if (allowedRoles && !user?.roles.some((r) => allowedRoles.includes(r))) {
    return <ForbiddenView />; // se renderiza en el lugar, sin cambiar la URL
  }
  return <Outlet />;
}
```

Después del login: ir a `from` solo si `canAccess(roles, from.pathname)`; si no, a `homeFor(roles)`.

### 4.6 Cliente HTTP (`lib/httpClient.ts`)

- Envoltorio de `fetch` con base `${VITE_API_BASE_URL}/api/v1`, JSON por defecto y `credentials: 'include'` (necesario para la cookie HttpOnly). El origen del backend es el de `VITE_API_BASE_URL`; el CORS del backend debe permitir ese origen de Vite **con credenciales** (verificar en la Fase 2).
- Adjunta `Authorization: Bearer <accessToken>` desde `tokenStore`.
- Ante `401` en una ruta que no sea `/auth/login` ni `/auth/refresh`: un único refresh compartido (si hay varias llamadas fallando a la vez, todas esperan el mismo `refresh`), reintentar la llamada una vez; si el refresh falla, disparar el flujo de sesión expirada.
- Errores tipados (`ApiError` con `status`, `detail`, `retryAfter?`) y un caso aparte para fallas de red. Nunca loguear tokens, cuerpos de login ni contraseñas.
- Sin `any`; TypeScript en modo estricto.

### 4.8 Tests (Vitest + React Testing Library + `@testing-library/user-event`)

Mínimos de C-04: render del formulario de login, validación de campos obligatorios y redirección de usuarios no autenticados. Sumar:

- Menú del sidebar por cada rol (4 casos) y vista prohibida (`ForbiddenView`) para un rol no permitido.
- Estados del login: enviando, 401, 429, error de red, banner de sesión expirada.
- `httpClient`: 401 → refresh → reintento, y refresh compartido ante llamadas simultáneas.
- Sin red real: mockear `authApi`/`fetch`. Los tests no dependen del backend.

## 5. Guardarraíles de alcance (C-04)

- **Sí**: scaffolding, layouts, `/login`, `/registro`, `ProtectedRoute`, `AuthContext`, cliente HTTP, Navbar, Sidebar, `ConfirmDialog`, toasts, `ModulePlaceholder`, tests.
- **No**: pantallas, tablas, formularios ni datos de turnos, pacientes, profesionales, caja o historia clínica. Esos módulos pertenecen a C-05/C-06/C-10/C-11/C-12/C-13.
- **`/registro`**: C-03, tal como figura en `CHANGES.md`, no define un endpoint de registro. Construir el formulario y su validación, aislar la llamada en `authApi.register()` y dejar el envío real como **pendiente de contrato**. No inventar el endpoint ni su payload.
- **No archivar C-04** (`/opsx:archive`) ni marcar `[x]` en `CHANGES.md` hasta verificar contra el backend real con C-03 mergeado.

## 6. Datos ficticios y seguridad

- 100% ficticios (RN-06): nombres genéricos ("Persona Demo"), emails en dominios reservados (`@example.test`, `example.com`), teléfonos y DNI obviamente falsos (`00000000`). Nunca datos de personas reales ni copiados del seed del backend.
- Sin credenciales, tokens ni claves en el repo, los tests, los snapshots ni las capturas. En tests usar valores marcados como falsos (`not-a-real-password`). `.env.example` contiene solo `VITE_API_BASE_URL=http://localhost:8000` (ajustar al puerto del `docker-compose`).
- No renderizar HTML crudo desde datos del servidor (`dangerouslySetInnerHTML`).

## 7. Checklist de auditoría (antes de dar por cerrada cualquier vista)

**Alcance y datos**
- [ ] La vista está dentro del scope del change en `CHANGES.md`; no hay pantallas de módulos sin backend.
- [ ] Todos los datos de ejemplo son ficticios; no hay credenciales, tokens ni PII real en código, tests ni capturas.
- [ ] No se usó `localStorage`/`sessionStorage`/IndexedDB para tokens o datos de usuario.

**RBAC y navegación**
- [ ] El menú se genera desde `APP_ROUTES` y coincide con la matriz de `03_actores_y_roles.md` para los 4 roles.
- [ ] Sin sesión → `/login`; rol no permitido → `ForbiddenView`; con sesión en `/login` o `/registro` → redirección a `homeFor`.
- [ ] Ruta inexistente → `NotFoundPage`.

**Estados y copy**
- [ ] Formularios con los estados de 3.6: reposo, validación, enviando, 401, 429, red/5xx, sesión expirada.
- [ ] Textos en español rioplatense, sentence case, errores accionables.

**Responsive y accesibilidad**
- [ ] Verificada a 360×740, 768×1024 y 1280×800, sin scroll horizontal; el drawer del sidebar funciona (Esc, foco, cierre al navegar).
- [ ] Todo se opera con teclado; foco visible; un `h1` por vista; landmarks (`header`, `nav`, `main`); labels asociados; `aria-current`, `aria-invalid`, `aria-describedby`.
- [ ] Contraste AA en texto, bordes de controles y estados; `prefers-reduced-motion` respetado.

**Calidad técnica**
- [ ] `npm run lint`, `npm run build` y `npm test` pasan; sin `any`, sin `console.log` ni errores en la consola del navegador.
- [ ] Hay tests para el comportamiento nuevo (4.8) y no dependen de red.
- [ ] No se agregaron dependencias fuera del stack sin justificación.

**Evidencia**
- [ ] Auditoría con el MCP de navegador según `docs/MCP_SETUP.md`: snapshot de accesibilidad, capturas en los 3 viewports y consola sin errores, guardadas en `docs/evidence/C-04/`.
- [ ] Supuestos del contrato de C-03 listados como tareas pendientes de verificación contra el backend real.
