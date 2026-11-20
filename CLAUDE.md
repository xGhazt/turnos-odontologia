# turnos-odontologia — Instrucciones para Agentes

> Este archivo (y su copia `AGENTS.md`) es lo PRIMERO que todo agente lee al entrar al repo.
> Generado a partir de `knowledge-base/` y `CHANGES.md`. No editar a mano sin re-sincronizar ambos archivos.

---

## Stack Tecnológico

| Capa | Tecnología | Versión |
|------|------------|---------|
| Frontend | React + TypeScript / Vite / Tailwind CSS | ^18.x / ^5.x |
| Backend | Python / FastAPI / SQLAlchemy (Alembic) / Pydantic v2 | ^3.11 / ^0.100+ |
| Persistencia / Cola | PostgreSQL / Redis | ^15 / ^7 |
| Infraestructura | Docker / Docker Compose | — |

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md)

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. **Leé el archivo relevante ANTES de implementar.**

| Archivo | Cuándo leerlo |
|---------|---------------|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Entender propósito y alcance |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Auth, RBAC, permisos |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, ERD, migraciones |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas codificadas (RN-XX) |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario por épica |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, estructura, env vars |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | Preguntas abiertas y discrepancias; revisá las PA que afectan al change que vas a implementar |

> Antes de implementar un change, revisá en CHANGES.md su sección "Leer antes". PA-01 → C-05; PA-02/03 → C-08; PA-05 → C-09; PA-07 → C-13. PA-04 está resuelta y C-01 ya está archivado. PA-06 es una corrección documental del Discovery, no un bloqueante de código.

---

## Skills Disponibles

| Agente | Rol | Skills que carga |
|--------|-----|------------------|
| **Backend Core** | FastAPI / SQLAlchemy / UoW / migraciones | `fastapi`, `async-python-patterns` |
| **Backend Aux** | Servicios, integraciones, seguridad | `fastapi`, `async-python-patterns` (base) |
| **Frontend** | React / TypeScript / Vite / Tailwind | `vercel-react-best-practices` |
| **Orquestación** | SDD / OPSX / docs | `active-orchestrator`, `discovery-research`, `kb-creator`, `roadmap-generator`, `find-skill`, `skill-registry`, `agent-instruction` |

Cargá la skill correspondiente al contexto ANTES de escribir código.

> Skills instaladas actualmente: esas 10. `python-testing-patterns`, `api-security-best-practices`, `postgresql-optimization` y `typescript-advanced-types` son previstas y se incorporarán cuando el change que las necesite las requiera.

---

## Roadmap de Changes

El plan de implementación completo está en [CHANGES.md](CHANGES.md). Resumen:

- **Total**: 13 changes en 7 fases (`C-01` a `C-13`).
- **Camino crítico**: `C-01 → C-02 → C-03 → C-05 → C-07 → C-08 → C-11`.
- **Primer change**: `C-01` (Configuración inicial del repositorio backend y FastAPI).

**Antes de cualquier `/opsx:propose`**: leé [CHANGES.md](CHANGES.md), identificá las dependencias del change y los archivos de "Leer antes".

---

## Reglas Duras

- **NUNCA almacenar datos reales de pacientes en el repositorio ni en los ejemplos** — utilizar exclusivamente datos ficticios/mock generados para pruebas.
- **NUNCA schema Pydantic sin validación estricta** — rechazar campos no declarados y tipar estrictamente en Python y TypeScript.
- **NUNCA commitear secretos ni credenciales** — utilizar variables de entorno y `.env.example`.

---

## Flujo de Trabajo

```
1. Leer la KB relevante (knowledge-base/)        → entender el dominio
2. Identificar el change en CHANGES.md           → respetar dependencias
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Implementar las tasks (cargando skills)       → respetando las reglas duras
5. /opsx:archive C-NN-nombre + marcar [x]        → cerrar el change
```

Aplicar TODAS las reglas duras en cada paso. Ante conflicto entre la KB y este archivo, las reglas duras prevalecen.
