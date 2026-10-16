# Verificación de Fuentes - Discovery Research
**Fecha de consulta:** 15 de octubre de 2026
**Proyecto:** `turnos-odontologia`

## 1. Resumen de Acceso y Verificación

| Fuente (Informe) | URL Original | URL Alternativa Consultada | Estado |
| :--- | :--- | :--- | :--- |
| **Dentalink** | getdentalink.com | softwaredentalink.com/ar/ | **Verificado (AR)** |
| **Alegra Dental** | alegra.com/dental/ | alegra.com/argentina/ | **Discrepancia detectada** |
| **AgendaPro** | agendapro.com | agendapro.com/es/dental/... | **Verificado (Sectorial)** |
| **Doctoralia** | doctoralia.com.ar | pro.doctoralia.com/ar/... | **Verificado (PRO)** |
| **TurnosApp** | turnosapp.com.ar | turnoapp.com.ar | **Verificado (Local)** |

---

## 2. Resultados Detallados por Fuente

### A. Dentalink Argentina
- **URL Consultada:** [softwaredentalink.com/ar/](https://www.softwaredentalink.com/ar/)
- **Funcionalidades Respaldadas:**
    - Registro clínico digital con odontograma y periodontograma.
    - Agendamiento online y confirmaciones automáticas de citas.
    - Gestión de cobranza, presupuestos y control de stock (insumos).
    - Módulo específico para **Obras Sociales** (crítico para el mercado argentino).
- **Afirmaciones del Informe:** Se confirma su liderazgo regional y su robustez en el apartado clínico/odontograma.
- **Pendiente:** Verificar el flujo exacto de la "firma electrónica" mencionada para consentimientos.

### B. Alegra Argentina
- **URL Consultada:** [alegra.com/argentina/](https://www.alegra.com/argentina/)
- **Hallazgos:** La página oficial para Argentina se enfoca en **Facturación Electrónica AFIP** y **Gestión Administrativa/Contable** para PyMEs en general.
- **Discrepancia Crítica:** No se localizó un producto independiente o "vertical" llamado «Alegra Dental» en el portal de Argentina. Las funciones mencionadas en el informe (odontograma) no aparecen en la oferta general de facturación.
- **Pendiente:** Confirmar si "Alegra Dental" es un módulo específico para otros países (Colombia/México) o si fue un error de interpretación de la marca.

### C. AgendaPro Dental
- **URL Consultada:** [agendapro.com/es/dental/software-odontologico](https://agendapro.com/es/dental/software-odontologico)
- **Funcionalidades Respaldadas:**
    - Ficha clínica digital personalizable con anexado de archivos.
    - Agenda online 24/7 vinculada a redes sociales.
    - Recordatorios automáticos (WhatsApp/Email) para reducir inasistencias.
    - Control de inventarios y órdenes de laboratorio.
- **Conclusión del Proyecto:** AgendaPro se presenta como un fuerte competidor en "automatización de la agenda", pero su odontograma parece menos "gráfico/interactivo" que el de Dentalink en la documentación pública.

### D. Doctoralia PRO Argentina
- **URL Consultada:** [pro.doctoralia.com/ar/agenda-doctoralia-para-especialistas](https://pro.doctoralia.com/ar/agenda-doctoralia-para-especialistas)
- **Funcionalidades Respaldadas:**
    - Disminución del ausentismo mediante recordatorios por WhatsApp (afirma hasta un 65%).
    - Chat seguro entre médico y paciente para compartir documentos.
    - Integración con Google My Business (alianza oficial).
    - "Episodios clínicos" digitales en la nube (AWS).
- **Limitación Confirmada:** Su fuerte es la visibilidad y el motor de búsqueda (directorio médico), no tanto la gestión profunda de insumos o nomencladores de obras sociales complejos.

### E. TurnoApp (Argentina)
- **URL Consultada:** [turnoapp.com.ar/](https://turnoapp.com.ar/)
- **Funcionalidades Respaldadas:**
    - **Cobro de señas online con Mercado Pago** (funcionalidad core de nuestro MVP).
    - Envío de recordatorios por WhatsApp integrados.
    - Página de reserva personalizada ("Landing") sin que el cliente instale apps.
    - Manejo de ausencias y "lista de espera" automática para huecos liberados.
- **Conclusión del Proyecto:** Es el referente más directo para nuestro "Diferenciador Clave" (seña + Mercado Pago).

---

## 3. Limitaciones y Preguntas Pendientes

1.  **Alegra Dental:** ¿Existe realmente para Argentina o debemos descartarlo como competidor de nicho clínico (odontograma) y tratarlo solo como competidor de facturación?
2.  **WhatsApp Business API:** Todos mencionan "WhatsApp", pero no todos aclaran si usan la API oficial o automatizaciones de terceros (Grey Market). Esto impacta en los costos y estabilidad de nuestro futuro desarrollo.
3.  **Costos AFIP:** Se confirma que la integración con AFIP es un "superpoder" (en palabras de Alegra), lo que refuerza que para el MVP de nuestro proyecto, una *simulación* o estructura modular para AFIP es el camino correcto.

---
**Nota:** Este documento actúa como anexo técnico de verificación. No modifica el informe original.
