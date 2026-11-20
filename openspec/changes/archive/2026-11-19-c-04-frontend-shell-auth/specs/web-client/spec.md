# Spec Delta

## Purpose

Define el comportamiento observable del shell de la aplicación web: enrutamiento y layouts, inicio y cierre de sesión, control de acceso por rol, vistas públicas de acceso y componentes transversales accesibles, consumiendo la API de autenticación existente.

## ADDED Requirements

### Requirement: Inicio de sesión

El cliente web DEBE (MUST) permitir iniciar sesión con email y contraseña contra la API de autenticación, reflejando el resultado (éxito, credenciales inválidas, error de red) sin revelar cuál credencial falló.

#### Scenario: Login exitoso
- **WHEN** la persona ingresa credenciales válidas y envía el formulario
- **THEN** el cliente guarda el token de acceso en memoria, carga el perfil del usuario autenticado y la redirige a la ruta de origen o al inicio correspondiente a su rol.

#### Scenario: Credenciales inválidas
- **WHEN** la API responde `401` al intento de login
- **THEN** el formulario muestra un mensaje que indica que el email o la contraseña no son correctos, conserva el email, vacía la contraseña y devuelve el foco a ese campo.

#### Scenario: Campos obligatorios
- **WHEN** la persona envía el formulario con email o contraseña vacíos
- **THEN** el cliente no realiza la petición, marca los campos inválidos con su mensaje accesible y lleva el foco al primer campo inválido.

#### Scenario: Envío en curso
- **WHEN** el formulario se está enviando
- **THEN** el botón queda deshabilitado con indicación de progreso, los campos pasan a solo lectura y se impiden envíos duplicados.

#### Scenario: Error de red o del servidor
- **WHEN** la petición de login falla por red o por una respuesta `5xx`
- **THEN** el formulario muestra un mensaje de conexión y conserva los datos tipeados.

#### Scenario: Demasiados intentos
- **WHEN** la API responde `429` al login
- **THEN** el formulario informa que se hicieron demasiados intentos y, si la respuesta incluye un tiempo de espera, lo muestra.

### Requirement: Sesión y ciclo de vida

El cliente web DEBE (MUST) mantener el estado de sesión a partir del token en memoria y del perfil obtenido de la API, sin persistir el token ni los datos del usuario en almacenamiento del navegador.

#### Scenario: Verificación de sesión al arrancar
- **WHEN** la aplicación se carga y no hay token en memoria
- **THEN** el estado de sesión pasa a no autenticado sin mostrar la pantalla de login de forma intermitente.

#### Scenario: Sesión expirada
- **WHEN** una petición protegida recibe `401` por token expirado o invalidado y había una sesión activa
- **THEN** el cliente limpia el estado, recuerda la ruta de origen y redirige a `/login?motivo=sesion-expirada` mostrando un aviso informativo; tras el login vuelve a la ruta original si el rol la permite.

#### Scenario: Cierre de sesión
- **WHEN** la persona autenticada elige cerrar sesión
- **THEN** el cliente invoca el cierre de sesión de la API y limpia el estado local aunque la llamada falle, dejando a la persona en la vista de login.

#### Scenario: Sin persistencia de credenciales
- **WHEN** la persona recarga la página
- **THEN** el token en memoria se pierde y la aplicación exige un nuevo inicio de sesión, sin haber escrito tokens ni datos de usuario en almacenamiento del navegador.

### Requirement: Control de acceso por rol

El cliente web DEBE (MUST) restringir la navegación según el rol del usuario autenticado, derivando rutas y menú de una fuente única, sin sustituir la autoridad de acceso del backend.

#### Scenario: Ruta protegida sin sesión
- **WHEN** una persona no autenticada intenta acceder a una ruta protegida
- **THEN** el cliente la redirige a `/login` recordando la ruta solicitada.

#### Scenario: Rol no permitido
- **WHEN** una persona autenticada accede a una ruta cuyo rol no está entre sus roles permitidos
- **THEN** el cliente muestra una vista de acceso denegado en el lugar, sin cambiar la URL ni exponer contenido del módulo.

#### Scenario: Menú por rol
- **WHEN** una persona autenticada ve la navegación lateral
- **THEN** el menú muestra solo los módulos habilitados para su rol, coincidiendo con la matriz de roles del sistema.

#### Scenario: Inicio según rol
- **WHEN** una persona autenticada accede a la raíz o completa el login sin ruta de origen válida
- **THEN** el cliente la redirige al inicio correspondiente a su rol; con varios roles aplica la prioridad administrador, odontólogo, secretaria, paciente.

#### Scenario: Ruta con sesión en vista de acceso
- **WHEN** una persona autenticada intenta abrir `/login` o `/registro`
- **THEN** el cliente la redirige a su inicio según rol.

### Requirement: Registro público

El cliente web DEBE (MUST) ofrecer un formulario de registro público con validación de email, contraseña y confirmación, aislando el envío real como contrato pendiente hasta que la API exponga el endpoint.

#### Scenario: Validación del registro
- **WHEN** la persona envía el registro con email inválido, contraseña demasiado corta o confirmación que no coincide
- **THEN** el cliente no envía datos, muestra el mensaje de cada campo y enfoca el primero inválido.

#### Scenario: Contraseña visible
- **WHEN** la persona usa el control de mostrar u ocultar contraseña
- **THEN** el campo alterna su visibilidad y el control refleja su estado de forma accesible.

#### Scenario: Contrato de registro pendiente
- **WHEN** la API de autenticación no expone un endpoint de registro
- **THEN** el cliente conserva el formulario y su validación pero no inventa endpoint ni payload, registrando el envío real como pendiente de contrato.

### Requirement: Layouts y navegación

El cliente web DEBE (MUST) proveer layouts diferenciados para vistas públicas, de autenticación y de panel autenticado, además de respuestas para rutas inexistentes y módulos aún no implementados.

#### Scenario: Layout de panel en móvil
- **WHEN** una persona autenticada usa el panel en un ancho menor al de escritorio
- **THEN** la navegación lateral se presenta como un panel deslizante que abre desde la barra superior, cierra con Escape, al navegar y al tocar fuera, y devuelve el foco al control que lo abrió.

#### Scenario: Ruta inexistente
- **WHEN** una persona accede a una ruta no declarada
- **THEN** el cliente muestra una página de no encontrado con una acción para volver al inicio.

#### Scenario: Módulo sin implementar
- **WHEN** una persona accede a una ruta de un módulo que aún no tiene backend
- **THEN** el cliente muestra un marcador de posición con el nombre del módulo y una indicación de que se implementará en un change posterior, sin tablas ni datos de ejemplo.

### Requirement: Accesibilidad y datos ficticios

El cliente web DEBE (MUST) cumplir criterios de accesibilidad y usar exclusivamente datos ficticios, sin exponer credenciales ni datos de personas reales.

#### Scenario: Formularios accesibles
- **WHEN** una persona navega un formulario con teclado y lector de pantalla
- **THEN** cada campo tiene etiqueta asociada, los errores se anuncian y vinculan al campo, el foco es visible y hay un único título principal por vista.

#### Scenario: Navegación por landmarks
- **WHEN** una persona recorre la aplicación con tecnologías de asistencia
- **THEN** existen regiones de encabezado, navegación y contenido principal, y una acción para saltar directamente al contenido.

#### Scenario: Datos de ejemplo
- **WHEN** se usan datos en código, tests o capturas
- **THEN** son ficticios, con dominios de email reservados y valores obviamente falsos, sin credenciales ni tokens reales.
