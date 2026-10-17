# Informe de Discovery: Sistema de Gestión de Turnos Odontológicos (Argentina y LATAM)

**Proyecto:** `turnos-odontologia`  
**Asignatura:** Metodología I — Tecnicatura Universitaria en Programación (UTN)  
**Integrantes:** Gastón y Giovanna  
**Fecha:** Octubre 2026  

---

## 1. Portada y Resumen Ejecutivo

El presente documento constituye el **Informe de Discovery** para el desarrollo del software de gestión de turnos, agenda y operaciones clínicas orientado a consultorios y clínicas odontológicas en Argentina y la región de LATAM. El objetivo principal de esta investigación de mercado es analizar 15 soluciones existentes en la industria, evaluar sus capacidades técnicas, funcionales y comerciales mediante una matriz ponderada, identificar vacíos en el mercado actual (con especial foco en las fricciones operativas y fiscales de Argentina) y definir con precisión el alcance del Producto Mínimo Viable (MVP) y las etapas posteriores de nuestro sistema.

### Hallazgos Principales:
1. **Estandarización del mercado:** La mayoría de los softwares SaaS de LATAM (como Dentalink, Alegra Dental y AgendaPro) ofrecen una sólida gestión de agendas y recordatorios por WhatsApp, pero presentan costos elevados en moneda extranjera o limitaciones con las normativas fiscales locales de Argentina (AFIP / Facturación electrónica).
2. **Brecha en la experiencia del paciente y cobros:** Pocas plataformas integran de manera fluida pasarelas de pago locales (como MercadoPago) para el cobro de señas obligatorias en la reserva de turnos online, lo cual genera un alto índice de ausentismo (*no-show*).
3. **Complejidad regulatoria:** La gestión de obras sociales, prepagas y nomencladores odontológicos complejos en Argentina está pobremente soportada por herramientas genéricas de LATAM, siendo un punto crítico de dolor para los profesionales locales.

---

## 2. Sección A: Tabla Comparativa de Sistemas (15 Soluciones)

A continuación se detalla la comparativa técnica y funcional de 15 soluciones de software de gestión odontológica y médica operativas en Argentina y LATAM. Se utiliza la etiqueta *"No evidenciado"* cuando la funcionalidad no está documentada públicamente o requiere contacto comercial exclusivo.

| Sistema | Origen / Mercado | Gestión de Turnos & Agenda | Historia Clínica & Odontograma | Integraciones & API | Administración & Cobros | Experiencia del Paciente | Seguridad & Compliance | Modelo de Precios | Fuente & Fecha |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Dentalink** | Chile / LATAM | Agenda multi-sillón, recordatorios WhatsApp automáticos. | Odontograma gráfico avanzado, evoluciones y archivos adjuntos. | API REST parcial, WhatsApp Business, pasarelas de pago. | Caja, presupuestos, control de stock e insumos. | Portal del paciente y reserva online integrada. | Cifrado SSL, backups diarios en nube AWS. | SaaS mensual por profesional (Escalonado). | [Dentalink Web](https://www.getdentalink.com/), 2026-03 |
| **2. Alegra Dental** | Colombia / LATAM | Agenda por profesional/sillón, alertas por WhatsApp/Email. | Ficha clínica digital, odontograma básico y evoluciones. | Facturación electrónica nativa (AFIP / DIAN), pagos online. | Control de caja, facturación, reportes financieros avanzados. | Portal básico de gestión de citas. | Certificación de seguridad en servidores Cloud. | SaaS mensual con tiers según volumen. | [Alegra Dental](https://www.alegra.com/dental/), 2026-02 |
| **3. AgendaPro** | Chile / LATAM | Agenda general y por especialista, recordatorios SMS/WhatsApp. | Historia clínica personalizable, fichas y recetas digitales. | API propia, integraciones con pasarelas de pago y marketing. | Control de caja, comisiones de profesionales, ventas. | App de reservas, recordatorios y confirmación automática. | Protocolos de seguridad estándar SaaS. | SaaS mensual por sucursal/profesional. | [AgendaPro](https://www.agendapro.com/), 2026-01 |
| **4. Doctoralia** | España / Global (LATAM) | Agenda online pública con motor de búsqueda y reserva directa. | Historia clínica orientada a agenda (básica). | Integración con perfil médico público, telemedicina. | No evidenciado (enfocado en atracción de pacientes). | Perfil público verificado, app móvil para pacientes. | RGPD / Normativas de protección de datos locales. | Freemium + Comisión por paciente nuevo / SaaS premium. | [Doctoralia Argentina](https://www.doctoralia.com.ar/), 2026-03 |
| **5. Clinic Cloud** | España / LATAM | Gestión multi-agenda, citas recurrentes y avisos automáticos. | Odontograma completo, historia clínica especializada en odontología. | API de integración, firma digital, laboratorios. | Contabilidad, cobros, presupuestos y mutuas/seguros. | Portal de pacientes web y app. | Cumplimiento RGPD y LOPD, copias de seguridad cifradas. | SaaS mensual por clínica. | [Clinic Cloud](https://cliniccloud.es/), 2026-02 |
| **6. Trello / G Calendar (Custom)** | Global (No-code / DIY) | Visualización Kanban o calendario básico manual. | Fichas en documentos externos (Google Drive / Notion). | Zapier, Make (integraciones limitadas y frágiles). | Control manual en planillas de cálculo (Excel / Sheets). | Inexistente (requiere formularios manuales). | Dependiente de cuenta personal de Google/Atlassian. | Gratuito (costo operativo en tiempo y mantenimiento). | [Implementación comunitaria DIY](https://trello.com/), 2026-01 |
| **7. Dentaltix (Software)** | España / Europa | Agenda de citas y recordatorios básicos. | Historia clínica odontológica estandarizada. | No evidenciado. | Facturación y control de caja básico. | No evidenciado. | No evidenciado. | Modelo SaaS / Freemium ligado a e-commerce. | [Dentaltix](https://www.dentaltix.com/), 2025-11 |
| **8. Sismed Odonto** | Argentina | Agenda adaptada a consultorios y clínicas locales. | Ficha odontológica orientada al mercado argentino. | Facturación local (afip / impresoras fiscales). | Gestión de obras sociales, coseguros y caja. | Recordatorios por SMS/WhatsApp (parcial). | Almacenamiento local o nube con respaldo básico. | Licencia tradicional / Pago único + abono de soporte. | [Sismed Odonto](https://www.sismed.com.ar/), 2025-12 |
| **9. ProClinic** | España / LATAM | Agenda multi-agenda avanzada con control de tiempos. | Odontograma interactivo 2D/3D y periodontogramas. | Integración con equipos de radiología y DICOM. | Gestión financiera compleja, mutuas, laboratorios y caja. | Portal del paciente y firma biométrica. | Altas exigencias de seguridad médica europea. | Licencia perpetua con mantenimiento o SaaS. | [ProClinic](https://www.proclinic.es/), 2026-01 |
| **10. Denvi (Dental)** | México / LATAM | Agenda de turnos optimizada para consultorios independientes. | Historial clínico dental y notas de evolución. | WhatsApp Business y recordatorios automáticos. | Control de ingresos, gastos y presupuestos. | Enlace de reserva web personalizado. | Cifrado en tránsito (SSL/TLS). | SaaS mensual económico. | [Denvi Dental](https://denvi.com/), 2026-02 |
| **11. Odontogest** | Argentina / LATAM | Agenda de turnos por sillón y profesional. | Odontograma y fichas clínicas odontológicas. | No evidenciado. | Presupuestos por tratamientos y caja diaria. | No evidenciado. | Backup local o en servidor propio del cliente. | Licencia de pago único / Instalado. | [Odontogest Argentina](https://www.odontogest.com.ar/), 2025-10 |
| **12. DentalSoft** | Argentina / LATAM | Agenda con vista diaria, semanal y mensual. | Historia clínica y odontograma básico. | Facturación básica y control de caja. | Obras sociales y particulares. | No evidenciado. | Respaldo manual o automático local. | Licencia instalada / SaaS regional. | [DentalSoft](https://www.dentalsoft.com.ar/), 2025-09 |
| **13. DentalPad** | LATAM / Cloud | Agenda táctil optimizada para tablets y web. | Ficha clínica digital y notas rápidas. | Integración básica con WhatsApp. | Presupuestos y pagos parciales. | Portal móvil para pacientes. | Seguridad Cloud estándar. | SaaS mensual accesible. | [DentalPad](https://dentalpad.io/), 2026-01 |
| **14. Medics Dental** | Argentina / LATAM | Agenda médica y odontológica integrada. | Historia clínica electrónica (HCE) multipropósito. | Facturación de obras sociales y prepagas argentinas. | Vademécum, caja, liquidación de honorarios médicos. | Portal web de pacientes. | Cumplimiento Ley 25.326 de Protección de Datos Personales. | SaaS corporativo por módulos. | [Medics Argentina](https://www.medics.com.ar/), 2026-02 |
| **15. TurnosApp** | Argentina / LATAM | Motor de turnos online autogestionable por el paciente. | No disponible (foco exclusivo en agendamiento). | WhatsApp, Google Calendar, pasarelas de pago locales. | Cobro de seña online para evitar ausentismo. | Alta experiencia de usuario en reserva web móvil. | Servidores seguros con cifrado de datos. | SaaS mensual por volumen de turnos. | [TurnosApp](https://turnosapp.com.ar/), 2026-03 |

---

## 3. Sección B: Matriz de Puntuación y Nota Metodológica

### Nota Metodológica
Para evaluar objetivamente las soluciones analizadas, se establece una escala de puntuación de **0 a 5** enteros para cada criterio ponderado, donde:
- **0:** No disponible / Inexistente.
- **1:** Muy deficiente / Funcionalidad extremadamente básica o rudimentaria.
- **2:** Insuficiente / Presenta carencias operativas significativas.
- **3:** Aceptable / Cumple con los estándares mínimos del mercado.
- **4:** Bueno / Solución sólida con características avanzadas y buena usabilidad.
- **5:** Excelente / Lámpara de referencia en la industria, robusto, nativo y sin fricciones.

Los pesos oficiales asignados responden a la criticidad operativa de un sistema de gestión odontológica moderno en LATAM y Argentina:
1. **Gestión de turnos y agenda:** **25%**
2. **Clínica (Historia clínica y odontograma):** **20%**
3. **Integraciones y WhatsApp:** **15%**
4. **Administración, cobros y facturación:** **15%**
5. **Experiencia del paciente (Portal y autogestión):** **10%**
6. **Seguridad y Compliance (Ley 25.326 / Backups):** **10%**
7. **Precio y modelo comercial:** **5%**

### Matriz de Puntuación Ponderada (Top 5 Referencias del Mercado)

| Criterio (Peso) | Dentalink | Alegra Dental | AgendaPro | Doctoralia | Clinic Cloud |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **1. Gestión de turnos (25%)** | 5 (1.25) | 4 (1.00) | 5 (1.25) | 4 (1.00) | 4 (1.00) |
| **2. Clínica / Odontograma (20%)** | 5 (1.00) | 3 (0.60) | 4 (0.80) | 2 (0.40) | 5 (1.00) |
| **3. Integraciones / WhatsApp (15%)** | 4 (0.60) | 4 (0.60) | 4 (0.60) | 3 (0.45) | 3 (0.45) |
| **4. Administración / Cobros (15%)** | 4 (0.60) | 5 (0.75) | 4 (0.60) | 2 (0.30) | 4 (0.60) |
| **5. Experiencia paciente (10%)** | 4 (0.40) | 3 (0.30) | 5 (0.50) | 5 (0.50) | 3 (0.30) |
| **6. Seguridad & Compliance (10%)** | 4 (0.40) | 4 (0.40) | 4 (0.40) | 4 (0.40) | 4 (0.40) |
| **7. Precio / Modelo (5%)** | 3 (0.15) | 4 (0.20) | 3 (0.15) | 3 (0.15) | 3 (0.15) |
| **PUNTUACIÓN TOTAL (sobre 5.0)** | **4.40** | **3.85** | **4.30** | **3.20** | **3.90** |

---

## 4. Sección C: Análisis Competitivo

### 1. Estándar de Mercado
Hoy en día, cualquier software odontológico comercial competitivo en LATAM debe ofrecer como base indispensable:
- **Agenda multi-profesional y multi-sillón** con vista de día, semana y mes, codificada por colores según el estado de la cita (confirmada, en sala de espera, atendida, cancelada).
- **Recordatorios automáticos por WhatsApp y correo electrónico** para mitigar la tasa de ausentismo, configurable en intervalos de 24 y 2 horas previas.
- **Ficha clínica digital básica** con datos de contacto, antecedentes alérgicos, patológicos y notas de evolución por sesión.

### 2. Diferenciadores Reales
Las soluciones líderes se distancian del promedio incorporando:
- **Odontograma interactivo avanzado 2D/3D** con registro gráfico de tratamientos por pieza dental (permanente y temporal), superficies, caras y estados (caries, obturado, sellado, corona, ausencia).
- **Gestión financiera automatizada y multimoneda**, vinculando presupuestos aprobados directamente con planes de pago por cuotas y control de caja diaria por profesional.
- **Portal del paciente de marca blanca**, permitiendo que los pacientes consulten sus próximos turnos, accedan a presupuestos y descarguen recetas o constancias de atención sin intermediación telefónica.

### 3. Vacíos Frecuentes en Argentina
Al analizar el mercado desde la perspectiva de un consultorio o clínica en Argentina, se detectan carencias críticas:
- **Nomencladores de Obras Sociales y Prepagas locales:** Los softwares internacionales (Dentalink, Alegra) están optimizados para sistemas privados o seguros de salud estandarizados de México, Colombia o Chile, dificultando el manejo de coseguros, bonos de consulta y nomencladores complejos de OSDE, Swiss Medical, PAMI u otras prepagas argentinas.
- **Facturación electrónica AFIP nativa fluida:** Si bien algunos integran facturación general, la emisión de comprobantes fiscales electrónicos en Argentina (Factura C / B con validación en tiempo real de CUIT y régimen de IVA) suele requerir intermediarios o add-ons costosos.
- **Resiliencia ante conectividad inestable:** Muchos sistemas cloud puros carecen de modos offline parciales, generando cuellos de botella operativos ante cortes de internet locales.

### 4. Oportunidades de Innovación para Nuestro Producto
Nuestro desarrollo (`turnos-odontologia`) puede capitalizar estos vacíos posicionándose como la solución ideal para el mercado argentino y LATAM mediante:
- **Cobro de seña integrado con MercadoPago** directamente en el flujo de reserva online, reduciendo el ausentismo crónico a través de incentivos económicos automáticos.
- **Interfaz ultrarrápida Mobile-First** diseñada para odontólogos independientes y pequeñas clínicas que necesitan registrar una evolución o dar un turno en menos de 10 segundos desde su smartphone o tablet.
- **Estructura modular orientada a simplificar la burocracia local**, ofreciendo una gestión limpia de pacientes particulares, obras sociales y presupuestos sin la curva de aprendizaje agobiante de los grandes ERPs médicos.

---

## 5. Sección D: Recomendación Final

### 1. Competidores para Análisis Profundo (Demo)
Para auditar flujos de usuario y mejores prácticas de arquitectura de producto, se seleccionan los siguientes 5 competidores:
1. **Dentalink:** Referente indiscutido en gestión clínica y odontograma en LATAM.
2. **Alegra Dental:** Excelente modelo de integración contable y facturación.
3. **AgendaPro:** Benchmark en agendamiento ágil y recordatorios automatizados.
4. **Doctoralia:** Estándar en atracción y descubrimiento público de profesionales.
5. **TurnosApp:** Referente en autogestión de turnos y cobro de señas online.

### 2. Referencias de Experiencia de Usuario (UX)
1. **Dentalink:** Por la claridad en la distribución del consultorio, estado de sillones y la interacción táctil con el odontograma.
2. **Alegra Dental:** Por la limpieza visual de los módulos administrativos y reportes financieros sin sobrecarga cognitiva.
3. **AgendaPro:** Por la simpleza y velocidad del widget de reservas online integrado en redes sociales y sitio web.

### 3. Alcance del Producto Mínimo Viable (MVP)
Para la primera versión del sistema `turnos-odontologia`, se definen los siguientes componentes estrictos:

- **Imprescindibles (Core MVP):**
  - Gestión de agenda multi-profesional con estados de turnos.
  - Módulo de pacientes (alta, edición, historial básico de contactos y observaciones).
  - Historia clínica simplificada con odontograma funcional básico (registro de piezas y diagnósticos).
  - Panel de control de turnos y caja diaria básica (ingresos del día).
  - Simulación/Envío de recordatorios automáticos de turnos (vía webhook de WhatsApp o simulación controlada).

- **Diferenciador Clave del MVP:**
  - Flujo de reserva online para pacientes con validación de datos y opción de pago de seña simulada/integrada con pasarela local, reduciendo el ausentismo desde el día uno.

- **Etapas Posteriores (Roadmap Post-MVP):**
  - **Fase 2:** Integración nativa avanzada con API de WhatsApp Business para confirmación bidireccional automatizada de turnos.
  - **Fase 3:** Módulo de control de stock, insumos odontológicos y alertas de reposición crítica.
  - **Fase 4:** Facturación electrónica automatizada adaptada a normativas fiscales locales (AFIP).
  - **Fase 5:** Asistente conversacional por IA para triaje y asignación inteligente de turnos.

---
