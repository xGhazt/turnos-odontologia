# Skill Registry

**Delegator use only.** Any agent that launches sub-agents reads this registry to resolve compact rules, then injects them directly into sub-agent prompts. Sub-agents do NOT read this registry or individual SKILL.md files.

See `_shared/skill-resolver.md` for the full resolution protocol.

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| active-orchestrator:init, /active-orchestrator:kb, /active-orchestrator:rules, /active-orchestrator:discovery, /active-orchestrator:openspec, /active-orchestrator:devops, /active-orchestrator:find-skill | active-orchestrator | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/active-orchestrator/SKILL.md |
| discovery-research | discovery-research | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/discovery-research/SKILL.md |
| kb-creator | kb-creator | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/kb-creator/SKILL.md |
| roadmap-generator | roadmap-generator | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/roadmap-generator/SKILL.md |
| find-skill | find-skill | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/find-skill/SKILL.md |
| agent-instruction | agent-instruction | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/agent-instruction/SKILL.md |
| fastapi | fastapi | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/fastapi/SKILL.md |
| vercel-react-best-practices | vercel-react-best-practices | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/vercel-react-best-practices/SKILL.md |
| async-python-patterns | async-python-patterns | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/.agents/skills/async-python-patterns/SKILL.md |

## Compact Rules

Pre-digested rules per skill. Delegators copy matching blocks into sub-agent prompts as `## Project Standards (auto-resolved)`.

### active-orchestrator
- Thin orchestrator for project foundation flow
- Runs openspec init, discovery, kb, roadmap, find-skill, registry, agent-instruction in order
- Owns .active-orchestrator-state.json and step field

### discovery-research
- Scrapes competitor URLs and guides Q&A checklist
- Captures problem, users, constraints, risks
- Never simulates external validation or sources

### kb-creator
- Builds 10 canonical markdown files in knowledge-base/
- Dual mode: silent from docs/ or interactive Q&A
- Stack-aware generation

### roadmap-generator
- Generates CHANGES.md operational index
- Defines dependency tree, parallelism gates, critical path
- Pointers to knowledge-base

### find-skill
- Recommends skills based on stack/domain
- Requires one-line justification per recommendation

### agent-instruction
- Generates AGENTS.md and CLAUDE.md in project root
- Interactive review of rules
- Enforces domain rules (e.g. no PII/real patient data in repo)

### fastapi
- Use dependency injection for DB sessions and auth
- Pydantic v2 for validation and schemas
- Async route handlers for I/O bound operations

### vercel-react-best-practices
- Server components by default, use client only when needed
- Modern hooks and state management patterns

### async-python-patterns
- Use asyncio, async/await for concurrency
- Handle connection pools and non-blocking I/O

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| AGENTS.md | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/AGENTS.md | Index / Global & Project Instructions |
| CLAUDE.md | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/CLAUDE.md | Project instructions |
| openspec/config.yaml | /home/gaston/Desktop/Programacion III/Metodología/turnos-odontologia/openspec/config.yaml | OpenSpec configuration & context stack |

Read the convention files listed above for project-specific patterns and rules. All referenced paths have been extracted — no need to read index files to discover more.
