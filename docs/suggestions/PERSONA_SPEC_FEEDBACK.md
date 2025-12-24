# Suggestion: Add Persona Specification to Rite Repository

## Summary
Provide an official persona specification document in the Rite repository that mirrors the workspace-local personas in SquigLeague. Include priorities, points of view, goals, and default weight parameters for each persona category (DEV, TEST, QA, SPEC).

## Proposed Content (to add to Rite repo)
- Persona identification rule: `[PERSONA: <Specialization> - <Role>]` at start of every output (Servitor Protocol requirement #6).
- Categories: DEV, TEST, QA, SPEC.
- Weighting: 0.1–2.0 range; default 1.0; raise/lower per project phase.
- Conflict intent: Personas are intentionally conflicting to drive consensus.
- Persona profiles:
  - BackendDev - API Developer: correctness, data integrity, explicit schemas.
  - FullStackDev - Frontend-Integration: end-to-end flows, router/store consistency.
  - SecurityDev - Security Specialist: authZ/authN, OWASP, least privilege (weight 1.3 during security work).
  - DevOps - Reliability Engineer: repeatable scripts, CI determinism, no one-off commands.
  - UnitTest - Backend Testing: deterministic units, edge cases, 100% coverage.
  - IntegrationTest - Service Testing: real DB/TestClient, no mocking critical logic.
  - E2ETest - Frontend Selenium: browser-driven user flows, auth/session checks.
  - QAReview - Compliance Auditor: policy adherence (Rite, testing, persona ID).
  - QACoord - Release Coordinator: readiness gates, checklists, schedule risk.
  - DataModel - Schema Author: explicit constraints, migrations safety.
  - Analytics - Metrics Advocate: observability and telemetry coverage.
- Weight adjustment guidance: raise SecurityDev during auth/infra; raise IntegrationTest/E2ETest pre-release; raise FullStackDev during frontend integration.
- Usage checklist: prepend persona tag; when multiple personas, list viewpoints and weights; document weight changes per phase.

## Rationale
- Aligns Rite documentation with enforced Servitor Protocol persona identification.
- Reduces ambiguity across projects using Rite-based governance.
- Provides consistent, phase-adjustable weights to resolve conflicts faster.

## Location Suggestion in Rite Repo
Place under `docs/suggestions/PERSONAS.md` (or similar) for review and inclusion in the next official release.
