# Implementation Guide: [Source Document Name]

**Source Document:** [filename of the PRD or TDD this guide documents]
**Entity/Feature:** [entity or feature name]
**Last Updated:** [date]
**Implementation Status:** [Initial | Iteration N]

---

## Changelog

| Date | Scope | Summary |
|---|---|---|
| [date] | Initial implementation | [brief description of what was built] |

---

## Files and Components

Organized by functional area. List the files created or significantly modified during implementation, grouped by purpose.

### [Functional Area 1, e.g., Data Model]

| File | Purpose |
|---|---|
| `path/to/file` | [what this file does in the context of this feature] |

### [Functional Area 2, e.g., API Layer]

| File | Purpose |
|---|---|
| `path/to/file` | [what this file does] |

### [Functional Area 3, e.g., UI Components]

| File | Purpose |
|---|---|
| `path/to/file` | [what this file does] |

---

## Requirement-to-Code Mapping

Maps task list items and key requirements from the source document to their implementation. Reference task IDs where available.

| Task / Requirement | Implementation | Notes |
|---|---|---|
| [ENTITY-01: requirement description] | [where/how it was implemented] | [any relevant context] |
| [ENTITY-02: requirement description] | [where/how it was implemented] | |

---

## Deviations from Requirements

Where the implementation diverged from the PRD or TDD, and why. If no deviations, state "None — implementation matches requirements as specified."

### [Deviation Title]

**Requirement:** [what the PRD/TDD specified]
**Implementation:** [what was actually built]
**Rationale:** [why the deviation was necessary or beneficial]

---

## Edge Cases Discovered

Edge cases, boundary conditions, or interaction effects not anticipated in the PRD that were handled during implementation. If none, state "None discovered during this implementation pass."

| Edge Case | How Handled | Discovered During |
|---|---|---|
| [description] | [implementation approach] | [which task or testing phase] |

---

## Integration Points

How this implementation connects to other entities, services, or shared infrastructure.

### Dependencies (what this implementation requires)

| Dependency | Type | Details |
|---|---|---|
| [entity/service/component] | [data / API / UI / shared component] | [how it's used] |

### Dependents (what relies on this implementation)

| Dependent | Type | Details |
|---|---|---|
| [entity/service/component] | [data / API / UI / shared component] | [how it uses this] |

---

## Technical Debt and Known Limitations

Workarounds, performance compromises, incomplete implementations, or areas flagged for future improvement. If none, state "No known technical debt from this implementation pass."

| Item | Context | Priority |
|---|---|---|
| [description] | [why the debt was accepted] | [Low / Medium / High] |
