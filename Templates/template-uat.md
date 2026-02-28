# [Functional Area Name] — User Acceptance Testing Guide

**Version:** [X.X]
**Last Updated:** [YYYY-MM-DD]
**Status:** [Draft | Review | Approved | Executed]

---

## Source Documents

| Document | File | Version |
|---|---|---|
| [Primary PRD name] | `[filename].md` | [X.X] |
| [TDD if applicable] | `[filename].md` | [X.X] |
| [Additional PRDs covered] | `[filename].md` | [X.X] |

> This UAT guide verifies that the implementation satisfies the requirements defined in the source documents listed above. Every requirement ID and TDD decision in those documents must appear at least once in the Traceability Matrix below. If a source document requirement has no corresponding UAT test, that is a coverage gap to be resolved.

---

## Requirement Traceability Matrix

This table maps every testable requirement and technical decision from the source documents to its UAT test(s). The Status column is updated during test execution.

| Source | Requirement ID | Description | UAT Test ID(s) | Status |
|---|---|---|---|---|
| [PRD filename] | [REQ-01] | [Brief description of the requirement] | [UAT-01] | [ ] |
| [PRD filename] | [REQ-02] | [Brief description] | [UAT-02, UAT-03] | [ ] |
| [TDD filename] | [Decision 2.1] | [Brief description of the TDD decision] | [UAT-04] | [ ] |

**Coverage summary:** [X] requirements mapped / [Y] total requirements = [Z]% coverage

> **Traceability rules:**
> - Every requirement with an ID (e.g., IDENT-01, ADMIN-04) in the source PRD must have at least one UAT test
> - Every TDD decision with testable behavior must have at least one UAT test
> - Key Processes defined in Entity Base PRDs must each have at least one end-to-end UAT scenario
> - † cached sort fields must have a performance verification test
> - Field metadata (Editable/Sortable/Filterable) must have tests confirming each declared capability works

---

## Acceptance Test Scenarios

Tests are grouped by the source document section they verify. Each test describes a user-level verification — what a user does and what they should observe — not a unit test.

### [Source Document Section Name]

#### UAT-[XX]: [Test Name]

**Traces to:** [Requirement ID(s) and/or TDD Decision reference]
**Preconditions:** [What must be true before this test runs — data state, user role, configuration]
**Steps:**
1. [Action the user or tester takes]
2. [Next action]
3. [Continue as needed]

**Expected Result:** [What the user should observe. Be specific — exact values, UI state, system behavior]
**Pass/Fail:** [ ]
**Notes:** [Optional — edge cases to watch for, known limitations, links to related tests]

---

#### UAT-[XX]: [Test Name]

[Repeat the format above for each test scenario. Group tests under headings that match the source document's section structure for easy cross-referencing.]

---

### [Next Source Document Section]

[Continue with test scenarios for the next logical group of requirements.]

---

## Edge Cases & Boundary Conditions

These tests target behaviors that are easy to miss during implementation — boundary values, error paths, race conditions, and constraint enforcement. These often correspond to design decisions and cross-cutting concerns in the PRD rather than explicit requirement IDs.

#### UAT-E[XX]: [Edge Case Name]

**Traces to:** [Requirement ID or design decision reference, or "Implicit — [brief explanation]"]
**Preconditions:** [Setup required to trigger the edge case]
**Steps:**
1. [Action that triggers the boundary condition]

**Expected Result:** [Specific expected behavior at the boundary]
**Pass/Fail:** [ ]

[Repeat for each edge case. Common categories to check:

- **Boundary values:** Thresholds, limits, empty states, maximum lengths
- **Constraint enforcement:** Uniqueness violations, referential integrity, role restrictions
- **Concurrency:** Simultaneous edits, race conditions in auto-merge or sync
- **Error recovery:** Network failures mid-operation, invalid data handling, partial completion
- **Permission boundaries:** Actions at the edge of a user's role (e.g., last admin demotion)
- **Data volume:** Behavior with zero records, one record, and at scale thresholds defined in TDD]

---

## Cross-Cutting Verification

These tests verify that this functional area integrates correctly with other parts of the system. They test the boundaries between PRDs — where one functional area's output becomes another's input.

#### UAT-X[XX]: [Integration Test Name]

**Traces to:** [Requirement IDs from both this PRD and the related PRD]
**Related PRD:** `[other-prd-filename].md`
**Preconditions:** [State required in both systems]
**Steps:**
1. [Action in this functional area]
2. [Verification in the related functional area]

**Expected Result:** [What should be observable across both areas]
**Pass/Fail:** [ ]

[Common cross-cutting verifications:

- **Audit trail:** Admin actions produce audit log entries (Admin ↔ Audit PRD)
- **Enrichment triggers:** New entity creation triggers enrichment pipeline (Entity ↔ Enrichment PRD)
- **Notification generation:** Status changes generate expected notifications (Entity ↔ Notification PRD)
- **Permission enforcement:** Role changes propagate to all dependent features (Admin ↔ Permissions PRD)
- **Search indexing:** Entity changes appear in search results (Entity ↔ Search/Views PRD)]

---

## Execution Log

| Date | Tester | Environment | Tests Run | Passed | Failed | Blocked | Notes |
|---|---|---|---|---|---|---|---|
| [YYYY-MM-DD] | [Name] | [Dev/Staging/Prod] | [N] | [N] | [N] | [N] | [Summary] |
