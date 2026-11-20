# Setup de MCP: Playwright para auditar el frontend (C-04)

Guía reproducible para conectar **Playwright MCP** al agente local y usarlo en el desarrollo y la auditoría de `frontend/`. Es gratuito, corre en tu máquina y no requiere cuentas, tokens ni claves.

## 1. Qué resuelve y por qué esta opción

Playwright MCP le da al agente un navegador real que puede abrir `http://localhost:5173`, leer el árbol de accesibilidad de la página, cambiar el tamaño de la ventana, completar formularios y leer la consola. Con eso el agente puede comprobar lo que el código no muestra: layout responsive, estados de formularios, foco, menú por rol y errores en runtime.

| Opción | Requiere cuenta/credenciales | Qué aporta a C-04 | Decisión |
|---|---|---|---|
| **Playwright MCP** | No | DOM real, accesibilidad, redimensionado, consola y red, en un navegador propio y aislado | **Elegida** |
| Browser MCP | No, pero usa tu navegador y sesiones existentes | Similar, menos reproducible y con riesgo de tocar sesiones personales | Alternativa |
| Figma MCP / Stitch MCP | Sí (cuenta y token) | Leen diseños; el proyecto todavía no tiene archivos de diseño y C-04 se define en código | Descartada para este change |

Motivos principales: el snapshot de accesibilidad es texto estructurado (barato en tokens frente a imágenes), es reproducible entre máquinas con un solo comando, permite fijar los orígenes permitidos a `localhost`, y sirve igual en la Fase 2 para inspeccionar cookies, CORS y llamadas de red contra el backend real.

## 2. Requisitos

- Node.js 18 o superior (`node -v`) y `npm`.
- Un cliente MCP local (OpenCode, Claude Code, u otro compatible).
- Navegador: Google Chrome instalado. Si no lo tenés, pedile al agente que ejecute `browser_install`, o instalalo con `npx playwright install chrome`.
- Para auditar la app: `npm run dev` corriendo en `http://localhost:5173`. Usá siempre `localhost` (no `127.0.0.1`), para que coincida con el origen permitido por el CORS del backend.

## 3. Configuración (sin secretos)

### Formato estándar (`mcpServers`)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--isolated",
        "--allowed-origins=http://localhost:5173;http://localhost:8000"
      ]
    }
  }
}
```

- `--isolated`: el perfil del navegador queda solo en memoria; no se guardan cookies ni datos en disco.
- `--allowed-origins`: limita los orígenes que el navegador puede pedir (frontend y backend locales; ajustá el puerto del backend al de tu `docker-compose`). Reduce la superficie, pero no es una barrera de seguridad.
- **Reproducibilidad**: después de verificar que todo funciona, reemplazá `@latest` por la versión exacta (`npm view @playwright/mcp version`) y commiteá ese valor.

### OpenCode (`opencode.json` en la raíz del repo)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "playwright": {
      "type": "local",
      "command": [
        "npx",
        "@playwright/mcp@latest",
        "--isolated",
        "--allowed-origins=http://localhost:5173;http://localhost:8000"
      ],
      "enabled": true
    }
  }
}
```

### Claude Code

```bash
claude mcp add playwright -- npx @playwright/mcp@latest --isolated "--allowed-origins=http://localhost:5173;http://localhost:8000"
```

### Notas por sistema operativo

- **Windows**: si el cliente no encuentra `npx`, usá `"command": "cmd"` con `"args": ["/c", "npx", "@playwright/mcp@latest", ...]`.
- Si el servidor deja una carpeta `.playwright-mcp/` en el repo, agregala a `.gitignore`.

## 4. Prueba rápida (verificar que responde)

**Paso 1. El paquete se ejecuta**

```bash
npx @playwright/mcp@latest --help
```

Debe imprimir la lista de opciones (`--isolated`, `--allowed-origins`, etc.).

**Paso 2. El cliente ve el servidor.** Reiniciá el cliente y pedile al agente:

> Listá las herramientas del MCP `playwright`.

Debe aparecer, entre otras, `browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_resize`, `browser_click`, `browser_fill_form`, `browser_console_messages` y `browser_network_requests`. Los nombres exactos pueden variar según la versión: usar los que liste el cliente.

**Paso 3. Navega y lee una página local**

Con el backend levantado (`docker compose up`), pedile al agente:

> Usá el MCP `playwright`: navegá a `http://localhost:8000/api/health` y devolveme el contenido de la página.

Resultado esperado: el cuerpo de la respuesta de liveness del backend (C-01). Si el puerto es otro, ajustalo (y el valor de `--allowed-origins`).

**Paso 4. (cuando exista `frontend/`)**

> Usá el MCP `playwright`: navegá a `http://localhost:5173/login` y devolveme el snapshot de accesibilidad.

Resultado esperado: un árbol con el `h1`, los campos con sus labels y el botón de envío.

### Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| "Browser not installed" o similar | Falta el navegador | `browser_install` o `npx playwright install chrome` |
| Navegación bloqueada | Origen fuera de `--allowed-origins` | Agregar el origen (puerto correcto) y reiniciar el cliente |
| El cliente no lista el servidor | Config sin recargar o JSON inválido | Validar el JSON y reiniciar el cliente |
| Errores de CORS en la Fase 2 | El backend no permite `http://localhost:5173` con credenciales | Revisar la configuración CORS del backend (`allow_credentials` y origen explícito) |

## 5. Uso durante C-04: qué herramienta ejecutamos y qué evidencia queda

La herramienta principal es **`browser_snapshot`** (árbol de accesibilidad de la página real), acompañada de **`browser_resize`** y **`browser_take_screenshot`** para el responsive y de **`browser_console_messages`** para detectar errores. Para cada vista de C-04 (`/login`, `/registro`, el shell autenticado por rol y los placeholders):

1. `browser_navigate` a la ruta.
2. `browser_snapshot` → comprobar `h1`, landmarks, labels asociados, `aria-invalid`/`aria-describedby` en errores y `aria-current` en el menú.
3. `browser_resize` a **360×740**, **768×1024** y **1280×800**, con `browser_take_screenshot` en cada tamaño (sin scroll horizontal; el drawer del sidebar funciona bajo 1024px).
4. Estados de formulario con `browser_fill_form` y `browser_click`: campos vacíos, formato inválido, enviando, credenciales inválidas, y `/login?motivo=sesion-expirada`.
5. Menú por rol: iniciar sesión contra el backend real usando los usuarios ficticios cargados por el seed de C-02 (admin, odontólogo, secretaria y paciente, tomando las credenciales desde el script de seed local sin dejarlas en el repo) y comparar el menú lateral contra la matriz RBAC.
6. `browser_console_messages` → sin errores ni advertencias inesperadas.
7. `browser_network_requests` → confirmar que las llamadas a `/api/v1/auth/*` viajan con credenciales (`credentials: 'include'`), que el CORS responde bien y que la cookie de refresh se establece.

### Evidencia mínima a dejar en el repo

Carpeta `docs/evidence/C-04/` con:

- `mcp-audit.md`: fecha, versión del MCP usada, lista de llamadas (herramienta + ruta + viewport) y resultado de cada una.
- Capturas de los 3 viewports para `/login`, `/registro` y el dashboard de al menos un rol.
- Extracto de `browser_console_messages` sin errores.

Todo lo que aparezca en capturas y snapshots debe ser ficticio (usuarios `@example.test`, sin datos reales ni credenciales).

## 6. Seguridad

- No iniciar sesión con cuentas reales en el navegador del MCP.
- No pegar contraseñas ni tokens en los prompts al agente; para el login usar el adaptador de desarrollo con usuarios ficticios o las credenciales del seed del backend guardadas **fuera** del repo.
- Mantener `--isolated` y `--allowed-origins` en la configuración versionada.
