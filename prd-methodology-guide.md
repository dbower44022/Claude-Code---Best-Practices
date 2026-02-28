# PRD Methodology Guide

## Using Claude.ai and Claude Code for Large Project Development

**Version:** 5.0
**Date:** 2026-02-28
**Purpose:** This guide defines the standard methodology for developing large software projects using Claude.ai for product requirements and design, and Claude Code for implementation. It establishes document types, templates, workflows, and rationale for each decision.

See [Appendix A: Version History](#appendix-a-version-history) for the complete changelog.

---

## 1. Philosophy

### 1.1 Why This Methodology Exists

Large software projects collapse when product requirements live in a single monolithic document. A single PRD quickly becomes too large for effective human review and too large for Claude Code to hold in context without losing focus. Implementation details get mixed with product requirements. Tracking what's been built versus what's planned becomes guesswork.

This methodology solves these problems by:

- Separating *what* the product does (PRDs) from *how* it's built (TDDs)
- Decomposing requirements into focused, self-contained documents that Claude Code can work from without losing context
- Embedding implementation tracking directly into the requirements documents
- Establishing a consistent plan-execute-verify-test cycle between you and Claude Code

### 1.2 Core Principles

**Separation of What and How.** Product Requirements Documents define what the system does and why. Technical Design Documents define how it's built. This separation keeps PRDs focused on user-facing behavior and business rules, while TDDs capture technology choices with their rationale. Neither contaminates the other.

**Self-Contained Documents.** Each document Claude Code works from should contain enough context to implement from without requiring multiple document loads. Action Sub-PRDs extract relevant context from their parent Entity Base PRD. The instruction to Claude Code is always: "Read this document, focus on this section."

**Hierarchical Decomposition.** Requirements are organized in a hierarchy — product, entity, action — where each level adds detail. Higher levels provide the map; lower levels provide the directions. Someone reading only the Product PRD understands the entire system. Someone reading an Action Sub-PRD understands exactly how to build one piece.

**Living Documents.** PRDs are not static specifications. They include task lists and test plans that track implementation progress. Documents evolve as decisions are made, but changes are always reviewed and approved by the product owner before being written.

**Human Approval.** Claude Code proposes; you decide. All document modifications — task list changes, test plans, technical decisions — are presented for discussion and approval before being written. The PRDs always reflect your decisions, not Claude Code's assumptions.

---

## 2. Document Hierarchy

The methodology uses a three-level hierarchy of documents, with supporting documents at each level.

### 2.1 Product Level

These documents describe the entire product and apply globally.

| Document | Purpose | Contains |
|---|---|---|
| Product PRD | What the product is and why it exists | Vision, competitive landscape, target users, product scope, principles |
| Product TDD | Global technology and deployment decisions | Technology stack, database choices, API patterns, design principles, deployment infrastructure, with rationale. The foundation that all entity and action TDDs inherit from. |
| GUI Standards | Reusable UI patterns and conventions | Design philosophy, color system, typography, spacing, component patterns, layout conventions, interaction behaviors, data display conventions |
| PRD Index | Document registry and navigation | Hierarchical status of all documents, retired document history, workflow notes |
| Glossary | Single authoritative source of terminology | Flat alphabetical term list with definitions and source PRD references. All PRDs reference this document rather than maintaining independent term definitions. |
| Implementation Guides | What Claude Code actually built for each product-level document | Files created/modified, requirement-to-code mapping, deviations and rationale, edge cases discovered, integration points, technical debt |

### 2.2 Entity Level

These documents describe a single data entity (Contact, Company, Communication, etc.) and everything users can do with it.

| Document | Purpose | Contains |
|---|---|---|
| Entity Base PRD | Complete description of the entity | Definition, field-level metadata (editable/sortable/filterable), relationships, lifecycle, key processes, action catalog, cross-cutting concerns |
| Entity UI PRD | Screen layouts and navigation for the entity | Screen descriptions, interaction flows, simple action UI, task lists, test plans |
| Entity TDD | Entity-specific technical decisions (only if needed) | Decisions with rationale that deviate from or extend the Product TDD. Starts with your architectural decisions; grows as Claude Code adds implementation decisions. |
| Implementation Guides | What Claude Code actually built for each entity-level document | 1:1 companion for each Entity Base PRD, Entity UI PRD, and Entity TDD. Maps requirements and decisions to codebase reality. |

### 2.3 Action Level

These documents describe a single complex action or group of related actions on an entity.

| Document | Purpose | Contains |
|---|---|---|
| Action Sub-PRD | Detailed requirements for a complex action | Overview, extracted context, key processes, requirements, UI specs, task lists, test plans |
| Action TDD | Action-specific technical decisions (only if needed) | Decisions with rationale that apply only to this action. Same living document approach — you write initial decisions, Claude Code adds implementation decisions. |
| Implementation Guides | What Claude Code actually built for each action-level document | 1:1 companion for each Action Sub-PRD and Action TDD. Maps requirements and decisions to codebase reality. |

### 2.4 Functional Area Level

These documents describe a cross-cutting functional area that doesn't center on a single data entity. Examples: System Administration, Notifications, Audit Logging, Search Infrastructure.

| Document | Purpose | Contains |
|---|---|---|
| Functional Area PRD | Complete description of a cross-cutting capability | Scope, actors, capabilities, configuration, key processes, action catalog, cross-cutting concerns, task lists, test plans |
| Action Sub-PRD | Detailed requirements for a complex action within the area | Same template as entity action sub-PRDs |
| Functional Area TDD | Area-specific technical decisions (only if needed) | Same living document approach as entity TDDs |
| Implementation Guides | What Claude Code actually built for each functional-area-level document | 1:1 companion for each Functional Area PRD, Action Sub-PRD, and Functional Area TDD. Maps requirements and decisions to codebase reality. |

### 2.5 Cross-Entity Workflows

If a workflow genuinely spans multiple entities without a natural owner, it follows the same pattern as an entity — base PRD, sub-PRDs, UI PRD, and TDD as needed. In practice, most workflows have a natural owning entity, and the action sub-PRD simply references other entity base PRDs.

### 2.6 Inheritance

Each level inherits from above. An Action Sub-PRD inherits the product principles, the entity's data model and lifecycle, and any technical decisions from the Product TDD and Entity TDD. The self-containment principle means relevant inherited context is extracted into the document rather than requiring Claude Code to load parent documents.

### 2.7 Implementation Guides

Every document that Claude Code works from — every PRD and every TDD — gets a companion Implementation Guide. This is a strict 1:1 mapping: `contact-entity-base-prd.md` gets `contact-entity-base-prd-impl.md`, `contact-entity-tdd.md` gets `contact-entity-tdd-impl.md`, and so on.

**Why this exists:** PRDs define what to build. TDDs capture key technical decisions. But neither tells a future Claude Code session what was actually implemented — which files were created, how requirements mapped to code, what deviations occurred and why, what edge cases were discovered. Without this record, a Claude Code session starting an iteration must reverse-engineer the codebase to understand what's already there. The Implementation Guide eliminates that reverse-engineering step.

**The handoff set:** When directing Claude Code to iterate on a feature, you hand it three documents: the PRD (what we want), the TDD (how we decided to build it), and the Implementation Guide (what was actually built). Together these give Claude Code complete context for the iteration — intent, decisions, and codebase reality.

---

## 3. Document Templates

Each document type has a defined template. Templates provide structure and consistency but are not rigid — the author decides what level of detail is appropriate for each section. The following sections reference the separate template files.

### Template Registry

All templates are stored in `Templates/`. This is the complete list:

| Template | Document Type | Level |
|---|---|---|
| `template-product-prd.md` | Product PRD | Product |
| `template-product-tdd.md` | Product TDD | Product |
| `template-gui-standards.md` | GUI Standards | Product |
| `template-prd-index.md` | PRD Index | Product |
| *(no template)* | Glossary | Product |
| `template-entity-base-prd.md` | Entity Base PRD | Entity |
| `template-entity-ui-prd.md` | Entity UI PRD | Entity |
| `template-tdd.md` | Entity TDD / Action TDD | Entity or Action |
| `template-action-sub-prd.md` | Action Sub-PRD | Action |
| `template-functional-area-prd.md` | Functional Area PRD | Functional Area |
| `template-implementation-guide.md` | Implementation Guide | All Levels |
| `skill-templates/` | Skill starter kits (GUI Standards, Design Principles, Glossary, PRD Templates) | Project |

### 3.1 Product PRD

**Template file:** `template-product-prd.md`

The Product PRD is the root document. It answers: what is this product, why does it exist, who is it for, and what does it encompass? Someone reading only this document should understand the entire product at a conceptual level.

**When to create:** Once, at the start of the project. Updated when the product scope changes.

**Key principle:** The Product PRD is lean. It summarizes features and entities — it does not describe them in detail. Detailed requirements live in entity and action PRDs. Business metrics, roadmap, and phasing are separate concerns managed outside the PRD system.

### 3.2 Product TDD

**Template file:** `template-product-tdd.md`

The Product TDD captures global technology decisions that apply across the entire system. It answers: what technologies are we using, and why?

**When to create:** Early in the project, alongside the Product PRD. Updated as major technical decisions are made.

**Key principle:** Every decision includes rationale and rejected alternatives. This prevents revisiting settled decisions and helps Claude Code understand the constraints it's working within. Entity or action-specific technology choices do not belong here — they go in entity or action TDDs.

**The Product TDD as foundation:** The Product TDD establishes the defaults that all entity and action TDDs inherit from. When an entity TDD is silent on a topic, the Product TDD applies. This means the Product TDD should cover: language and framework choices, database strategy, API conventions, authentication patterns, UI architecture patterns, design principles that constrain all implementation, testing patterns, configuration approach, and project structure. Entity TDDs only document decisions that deviate from or extend these defaults.

**Design Principles section:** The Product TDD should include a Design Principles section that captures global constraints Claude Code must follow. These are not suggestions — they are rules. Examples include: "display speed is paramount" (denormalize for read speed), "idempotent writes" (all sync uses UPSERT), "editability is explicit" (Claude Code must not make fields editable unless the PRD says so). These principles save time by preventing Claude Code from making decisions that violate architectural intent.

### 3.3 GUI Standards

**Template file:** `template-gui-standards.md`

The GUI Standards document defines the visual design system and interaction conventions used across the entire product. It is the single source of truth for how the product looks and behaves.

**When to create:** Early in the project, before any entity UI work begins. Updated as new component patterns are established.

**Key principle:** This document has task lists and test plans because building the design system is real implementation work — shared component libraries, color systems, and layout patterns must be built and tested. Once stable, this document is a strong candidate for promotion to a Claude Code skill (see Section 4.7).

### 3.4 PRD Index

**Template file:** `template-prd-index.md`

The PRD Index is the navigation hub for the entire document set. It is the first document read at the start of any session.

**When to create:** Once, at the start of the project. Updated after every PRD session.

**Key principle:** The index is lean. It tracks document status and provides navigation. Cross-PRD decisions belong in TDDs. Priority sequencing and work tracking belong in your project management tool.

### 3.5 Glossary

The Glossary is the single authoritative source of terminology for the product. All PRDs reference this document for term definitions rather than maintaining independent glossary sections that drift out of sync.

**When to create:** Early in the project, alongside the first Entity Base PRDs. Updated whenever a new PRD introduces terminology or when existing terms are refined.

**Key principle:** The glossary uses a flat alphabetical table with three columns: Term, Definition, and Source PRD(s). The Source PRD column traces each term back to the document where it is defined in detail, creating a two-way navigation path — PRDs reference the glossary for definitions, and the glossary references PRDs for full context. No template is needed; the structure is a simple markdown table.

**Why this matters for Claude Code:** Without a shared glossary, Claude Code may use inconsistent terminology across implementation — calling the same concept by different names in different files, or misunderstanding a domain term that has a specific meaning in your product. When the glossary is loaded as context, Claude Code uses your exact terms in code, comments, UI labels, and documentation.

### 3.6 Entity Base PRD

**Template file:** `template-entity-base-prd.md`

The Entity Base PRD is the complete map of a single entity. It defines what the entity is, how it relates to other entities, its lifecycle, and everything you can do with it.

**When to create:** One per entity, when the entity is first designed. Updated when new actions are added or the data model changes.

**Key principle:** The Entity Base PRD is the map, not the directions. Someone reading it understands the full scope of the entity without reading any sub-PRDs. Simple actions are fully described in the action catalog. Complex actions are summarized with enough detail to understand what they do, with pointers to their sub-PRDs for implementation detail. No implementation or technology specifics appear here.

**Key Processes:** Between the entity lifecycle and the action catalog, the Entity Base PRD defines Key Processes — end-to-end user journeys through the entity's core workflows. Each Key Process has a unique ID (e.g., KP-CONT-01), a name, a trigger, and a step-by-step walkthrough of the user experience from start to finish. Key Processes tie together multiple simple actions, UI interactions, and system behaviors into coherent workflows. Simple actions in the action catalog reference the Key Process IDs they participate in ("Supports processes: KP-CONT-01, KP-CONT-03"). This creates a two-way link: processes show how actions combine, and actions show which processes they serve.

**Field-Level Metadata:** The Core Fields table in the Entity Base PRD includes three metadata columns beyond the field's description and valid values:

- **Editable** — Declares how (or if) the user can modify the field. Values: `Direct` (inline edit), `Override` (computed with manual override), `Via [sub-entity]` (edit through related record), `Computed` (derived, not editable), `System` (never user-editable). This prevents Claude Code from making non-editable fields editable or routing edits through the wrong UI.
- **Sortable** — Whether the field appears in sort options in list views. Fields backed by correlated subqueries that would be expensive to sort are marked with † and a note that the Entity TDD must define a caching or denormalization strategy. Fields without † are expected to sort at negligible cost (direct columns or JOINs).
- **Filterable** — Whether the field appears in filter options in list views.

These are product decisions, not technical decisions. The PRD declares the intended behavior; the TDD documents how to achieve it performantly.

### 3.7 Entity UI PRD

**Template file:** `template-entity-ui-prd.md`

The Entity UI PRD describes the standard screens and navigation flows for an entity — list views, detail views, and UI for simple actions. It does not cover UI for complex actions that have their own sub-PRDs.

**When to create:** One per entity, after the Entity Base PRD is established. Updated when new screens are added or layouts change.

**Key principle:** Organized by screen, not by feature. Each screen section contains the layout description, interaction behaviors, and associated task lists and test plans. References the GUI Standards for component patterns but does not duplicate them. The level of UI detail is the author's choice — from a sentence for trivial screens to wireframes for critical layouts.

### 3.8 Entity TDD

**Template file:** `template-entity-tdd.md` (uses the same template as Action TDD)

Entity TDDs are optional. They capture technical decisions that apply only to this entity and deviate from or extend the Product TDD.

**When to create:** Only when the entity requires technical decisions not covered by the Product TDD. Many entities will not need one. However, for core entities with complex data models (e.g., contacts with multi-identifier resolution, denormalized display fields, and event sourcing), an Entity TDD is strongly recommended.

**TDD structure:** The Entity TDD mirrors the Product TDD's decision format — each decision has a title, the decision itself, rationale, alternatives rejected, and constraints/tradeoffs. The TDD does not include table schemas, full SQL, or implementation code. It captures decisions and their reasoning, not the implementation details that follow from those decisions.

**Living document approach:** The Entity TDD is written in two phases:

1. **You write the decisions you care about** as the product/architecture owner. These are decisions where you have opinions and Claude Code should not freelance — caching strategies, denormalization choices, algorithm design, data model patterns. Write only what you know needs to be decided. Leave areas where you don't have a strong opinion for Claude Code to resolve.

2. **Claude Code writes its decisions back** during implementation. When Claude Code encounters technical decisions not covered by the TDD — index placement, query patterns, error handling approaches, adapter interfaces — it records those decisions with rationale in the appropriate section of the TDD. This creates a complete record of all technical decisions, not just the ones you anticipated.

The result is a TDD that starts lean (only your architectural decisions) and grows organically as implementation proceeds. Future Claude Code sessions read the TDD and understand the existing codebase without re-deriving decisions or accidentally contradicting them.

**Placeholder section:** The Entity TDD should end with a section titled "Decisions to Be Added by Claude Code" that lists the areas where Claude Code will likely need to make decisions. This serves as a roadmap and a reminder to document those decisions when they're made.

### 3.9 Action Sub-PRD

**Template file:** `template-action-sub-prd.md`

The Action Sub-PRD is the document Claude Code works from most directly. It contains the detailed requirements, UI specifications, task lists, and test plans for a complex action.

**When to create:** One per complex action or group of related actions. Created when the action is too complex to describe fully in the Entity Base PRD's action catalog. Simple actions do not need sub-PRDs.

**Key principle:** Self-contained. The document extracts relevant context from the Entity Base PRD so Claude Code can work from it without loading multiple documents. Requirements are organized into functional sections, each with their own task lists and test plans. The format of requirements (sequential workflow, business rules, or a mix) is the author's choice based on what best fits the action.

**Key Processes in Action Sub-PRDs:** Complex actions define their own Key Processes using the same KP-ID pattern (e.g., KP-MERGE-01). These describe the end-to-end user journeys specific to that action. Functional sections within the Sub-PRD reference which Key Processes they support, creating the same two-way linkage as in the Entity Base PRD. This ensures Claude Code understands not just what to build, but how the pieces fit into complete user experiences.

### 3.10 Action TDD

**Template file:** `template-action-tdd.md` (uses the same template as Entity TDD)

Action TDDs are optional. They capture technical decisions specific to an action, including deployment requirements. They follow the same living document approach as Entity TDDs — you write the decisions you care about, Claude Code writes back the decisions it makes during implementation.

**When to create:** Only when the action requires technology or deployment decisions not covered by the Product TDD or Entity TDD. For example, an Email Import action requiring AWS Lambda would have its own TDD. Simple actions that follow standard patterns typically don't need a TDD. Complex actions with non-obvious algorithm design, transaction semantics, or external service integration benefit from one.

**TDD hierarchy:** When Claude Code works on an action, it reads the Product TDD (platform defaults), the Entity TDD (entity-specific decisions), and the Action TDD (action-specific decisions), in that order. Each level overrides the one above for its specific scope.

### 3.11 Functional Area PRD

**Template file:** `template-functional-area-prd.md`

The Functional Area PRD describes a cross-cutting capability that doesn't center on a single data entity. It governs system-level functionality like administration, notifications, audit logging, or search infrastructure — areas where the requirements span multiple entities or involve configuration and operations rather than entity CRUD.

**When to create:** When a capability needs structured requirements but doesn't fit the Entity Base PRD pattern. The distinguishing characteristic is that the functional area operates *on* entities and system resources rather than *being* an entity itself. For example, System Administration manages users, provider accounts, and settings — but "admin" is not a data entity with its own fields and lifecycle.

**Key principle:** The Functional Area PRD borrows the proven patterns from Entity Base PRDs — Key Processes, action catalog (simple vs. complex), task lists, test plans — but replaces the entity definition and field tables with a scope/capabilities definition and a configuration table. This ensures Claude Code gets the same structured, implementable requirements regardless of whether the work is entity-centric or cross-cutting.

**Structure comparison:**

| Entity Base PRD | Functional Area PRD |
|---|---|
| Entity Definition (fields, metadata) | Scope & Boundaries (purpose, actors, boundaries) |
| Relationships | Related Documents |
| Lifecycle | Capabilities (what the area provides) |
| Key Processes | Key Processes (same pattern) |
| Action Catalog | Action Catalog (same pattern) |
| Cross-Cutting Concerns | Cross-Cutting Concerns (same pattern) |
| — | Configuration (settings, parameters, defaults) |

**Sub-PRDs and TDDs:** Functional areas use the same Action Sub-PRD and TDD templates as entities. A complex admin action (like GDPR data purge) gets its own Sub-PRD following the standard template. A functional area TDD follows the same living document approach as an entity TDD.

### 3.12 Implementation Guide

**Template file:** `template-implementation-guide.md`

The Implementation Guide is the record of what Claude Code actually built. It is the bridge between requirements (PRDs) and codebase reality — the document that prevents future Claude Code sessions from having to reverse-engineer existing code to understand what's already in place.

**When to create:** Claude Code creates or updates the Implementation Guide during the Document stage of the Plan-Execute-Verify-Test-Document cycle (Section 4.2). The first implementation pass creates the guide; subsequent iterations update it.

**Who writes it:** Claude Code. It is the only actor that knows exactly what was built, which files were touched, and what implementation choices were made. You review and approve it, but Claude Code authors it.

**Key principle:** The Implementation Guide maps requirements to code. It does not repeat the PRD's requirements or the TDD's decisions — it references them and explains how they were realized in the codebase. Someone reading the PRD, TDD, and Implementation Guide together understands intent, technical approach, and codebase reality without reading any source code.

**Naming convention:** The companion guide uses the source document's filename with `-impl` appended before the extension. Examples:
- `contact-entity-base-prd.md` → `contact-entity-base-prd-impl.md`
- `contact-entity-tdd.md` → `contact-entity-tdd-impl.md`
- `contact-merge-split-prd.md` → `contact-merge-split-prd-impl.md`
- `product-tdd.md` → `product-tdd-impl.md`

**Content scope:** Each Implementation Guide covers:

- **Files and components.** Which files were created or modified, organized by functional area. Not an exhaustive file listing — a meaningful map of where the implementation lives in the codebase.
- **Requirement-to-code mapping.** How specific PRD requirements or TDD decisions were realized. References task list IDs (e.g., CONT-01) and maps them to the code structures that implement them.
- **Deviations from requirements.** Where the implementation diverged from the PRD or TDD, and why. This is critical for iterations — if a requirement was modified during implementation, the next Claude Code session needs to know that before re-implementing the original spec.
- **Edge cases discovered.** Edge cases, boundary conditions, or interaction effects that weren't anticipated in the PRD but were handled in implementation.
- **Integration points.** How this implementation connects to other entities, services, or shared infrastructure. What it depends on and what depends on it.
- **Technical debt and known limitations.** Workarounds, performance compromises, incomplete implementations, or areas flagged for future improvement. Includes context on why the debt was accepted (e.g., "deferred pagination optimization pending real usage data").

**Iteration handling:** When Claude Code iterates on a previously implemented feature:

- **Minor changes** (bug fixes, small enhancements, adding a field): Claude Code appends to the existing Implementation Guide with a dated changelog entry describing what changed and why.
- **Major changes** (significant rework, architectural changes, large new feature areas): Claude Code writes a new comprehensive Implementation Guide reflecting the current state of the implementation, with a changelog section at the top summarizing the evolution from prior versions.

The threshold between minor and major is a judgment call. The guiding question is: would a future Claude Code session be better served by reading the existing guide plus an appendix, or by reading a fresh comprehensive guide? If the accumulated changes make the original guide misleading or hard to follow, it's time for a rewrite.

---

## 4. The Implementation Workflow

### 4.1 Phase Split: Claude.ai vs. Claude Code

**Claude.ai** is used for thinking, planning, and designing. All PRD creation and refinement happens here. Claude.ai helps you define requirements, identify edge cases, and structure documents. The PRD Index is the starting context for every Claude.ai session.

**Claude Code** is used for building and verifying. Claude Code reads PRDs and TDDs, plans implementation, writes code, and reports status. Claude Code proposes changes to documents but never modifies them without your approval.

### 4.2 The Plan-Execute-Verify-Test-Document Cycle

When you direct Claude Code to implement a section of a PRD, the workflow follows five stages:

**Plan.** Claude Code reads the document section and its task list. It presents a proposed implementation plan, which may include suggested additions or modifications to the task list. You discuss the plan and approve it before any code is written. This is where Claude Code might identify tasks you hadn't thought of or suggest splitting a task that's too large.

**Execute.** Claude Code implements the approved plan, working through the task list. It updates task checkboxes as it completes each item.

**Verify.** After implementation, Claude Code verifies each completed task against the approved plan and reports status. This is a self-check — Claude Code confirms it actually implemented what was planned.

**Test.** Claude Code generates a test plan for the completed section. You review and approve the test plan before it's added to the document. Claude Code then runs the tests and reports results.

**Document.** Claude Code writes or updates the Implementation Guide for the document it worked from (Section 3.12). This captures what was actually built — files created, requirement-to-code mapping, deviations from the PRD, edge cases discovered, integration points, and any technical debt introduced. You review and approve the Implementation Guide before the cycle is complete.

The Document stage is not optional. Without it, the next Claude Code session working on this feature starts from a knowledge deficit — it knows what was intended (PRD) and what decisions were made (TDD), but not what actually exists in the codebase. The Implementation Guide closes that gap.

### 4.3 Session Management

Claude Code does not maintain state between sessions. At the start of each session:

1. Direct Claude Code to read the relevant document
2. If iterating on previously implemented work, also load the corresponding Implementation Guide
3. Tell it which section to focus on
4. Claude Code reviews the task list and reports what's done versus remaining
5. You confirm the starting point and direct it to proceed

This prevents Claude Code from losing track of where it is in a larger implementation effort. The Implementation Guide is especially important for iteration sessions — it tells Claude Code what's already built so it doesn't re-derive or contradict existing implementation.

### 4.4 Technical Decision Capture

During implementation, Claude Code will make technical decisions not covered by existing TDDs — a library choice, an architectural pattern, a query optimization, an index strategy. The methodology requires that these decisions are captured, not lost.

**The write-back workflow:**

1. **Claude Code encounters a decision point** not covered by the Product TDD or Entity TDD — for example, which indexes to create on a table, how to structure an FTS virtual table, or how to handle a concurrency edge case.
2. **Claude Code implements its chosen approach** and documents the decision in the appropriate TDD using the standard format (decision, rationale, alternatives rejected, constraints/tradeoffs).
3. **You review the additions** during your next TDD review pass. You may approve, modify, or override Claude Code's decisions. The TDD always reflects the final approved state.

**Where decisions go:**
- Platform-wide decisions (e.g., "we use FTS5 for all full-text search") → Product TDD
- Entity-specific decisions (e.g., "the contacts table uses these specific indexes") → Entity TDD
- Action-specific decisions (e.g., "the merge transaction uses this locking strategy") → Action TDD

**Why this matters:** Without write-back, Claude Code's implementation decisions exist only in the code. A future Claude Code session reading the TDD sees gaps and may make different decisions, creating inconsistencies. Write-back ensures the TDD is the authoritative record of both what was intended and what was actually built.

**Detecting PRD-to-implementation gaps:** Claude Code may discover during implementation that a PRD requirement has performance or feasibility implications the PRD didn't account for. For example, a PRD may state "all fields are sortable" when some fields require expensive subqueries to sort. When this happens:

1. Claude Code documents the gap and the technical constraint in the TDD
2. Claude Code proposes a resolution (e.g., mark subquery fields non-sortable, or implement caching)
3. You review and may update the PRD to reflect the corrected product decision
4. The TDD documents the technical rationale for the PRD change

This feedback loop — PRD states intent → Claude Code discovers constraint → TDD captures rationale → PRD is updated — keeps the documents honest and aligned with reality.

### 4.5 High-Level Tracking

The PRD task lists and test plans track detailed implementation status within each document. High-level priorities, sequencing across entities and features, and cross-entity dependencies are tracked in your project management tool (e.g., ClickUp). This avoids duplicating tracking information in two places.

### 4.6 Prompt Templates for Claude Code

The Plan-Execute-Verify-Test-Document cycle described in Section 4.2 requires specific prompts at each stage. These templates are not rigid scripts — adapt them to your project's conventions and the specific task. They encode the patterns that reliably produce good results.

#### Session Start: New Implementation

Use this when Claude Code is implementing a feature for the first time — no prior implementation exists.

```
Read the following documents:
1. [path/to/entity-base-prd.md] — the requirements
2. [path/to/entity-tdd.md] — the technical decisions
3. [path/to/product-tdd.md] — the global technical decisions (if not already loaded as a skill)
4. [path/to/gui-standards.md] — the UI standards (if this task involves UI work)
5. [path/to/glossary.md] — the project glossary for consistent terminology

Focus on Section [X]: [section name]. Review the task list in that section
and report which tasks are completed vs. remaining. Then propose an
implementation plan for the remaining tasks.

Do not write any code yet — present the plan for review first.
```

#### Session Start: Iteration on Existing Implementation

Use this when Claude Code is returning to a feature that was previously implemented — bug fixes, enhancements, or continuing incomplete work.

```
Read the following documents:
1. [path/to/entity-base-prd.md] — the requirements
2. [path/to/entity-tdd.md] — the technical decisions
3. [path/to/entity-base-prd-impl.md] — the Implementation Guide for what was already built

Focus on Section [X]: [section name]. The Implementation Guide describes
what was previously implemented. Review it to understand the current state
of the codebase for this feature.

[Describe what needs to change: "We need to add filtering to the contact
list view" or "The merge preview is not showing related records correctly"
or "Continue with the remaining tasks in this section."]

Propose a plan before making any changes.
```

#### Plan Stage

After Claude Code has read the documents and proposes a plan, review it carefully. Common adjustments:

```
Good plan, but two changes:
1. Move [task X] before [task Y] — we need [reason]
2. Split [task Z] into two steps: [first part] then [second part]
3. Skip [task W] for now — we'll handle that in a separate session

Proceed with the approved plan.
```

If the plan is missing something:

```
The plan doesn't account for [concern — e.g., "the † cached fields that
need denormalization" or "the Key Process KP-CONT-03 flow" or "the
Override editability pattern on display_name"]. Add that to the plan
and re-present.
```

#### Execute Stage

Once the plan is approved, direct Claude Code to implement. For large task lists, implement in batches rather than all at once:

```
Implement tasks [CONT-01 through CONT-05] from the approved plan.
Update the task checkboxes as you complete each one.
```

If Claude Code gets stuck or asks a question that the PRD should answer:

```
Check the Entity Base PRD Section [X] — the answer is in the [field
metadata table / action catalog / key process KP-CONT-02]. If the PRD
doesn't cover this, flag it as an open question and move on.
```

If Claude Code proposes a deviation from the PRD:

```
Do not deviate from the PRD without discussing it first. If you've found
a technical constraint that makes a requirement impractical, document
the constraint and propose alternatives — but don't implement the
alternative until I approve it.
```

#### Verify Stage

After implementation is complete, trigger verification:

```
Verify the implementation against the approved plan. For each completed
task, confirm:
1. The task is actually implemented (not just the checkbox marked)
2. The implementation matches the PRD requirements for that task
3. No PRD requirements were skipped or modified without discussion

Report any gaps or deviations you find.
```

#### Test Stage

After verification passes, trigger test generation:

```
Generate a test plan for the tasks you just completed. Organize tests
by the Key Processes they exercise (reference KP IDs from the PRD).
Include:
- Happy path tests for each Key Process flow
- Edge cases from the PRD's business rules
- Validation tests for field metadata constraints (Editable, Sortable, Filterable)
- Integration tests for cross-entity interactions

Present the test plan for review before writing test code.
```

After approving the test plan:

```
Implement the approved test plan. Run the tests and report results.
If any tests fail, fix the implementation (not the test) unless the
test itself is wrong.
```

#### Document Stage

After tests pass, trigger Implementation Guide creation or update:

```
Write the Implementation Guide for this work. Create [or update]
[path/to/entity-base-prd-impl.md] following the template in
[path/to/template-implementation-guide.md].

Cover:
- Files created or modified, organized by functional area
- How each completed task (reference task IDs) maps to code
- Any deviations from the PRD and why
- Edge cases you discovered during implementation
- Integration points with other entities or shared infrastructure
- Technical debt or known limitations introduced

This is a record for the next Claude Code session that works on this
feature — write it for that audience.
```

#### TDD Write-Back

This can happen during or after the Execute stage, depending on how many decisions accumulated:

```
Review the technical decisions you made during this implementation that
are not already documented in the TDD. For each decision:

1. Determine the right TDD level:
   - Platform-wide decisions → Product TDD
   - Entity-specific decisions → Entity TDD
   - Action-specific decisions → Action TDD

2. Document each decision using the standard format:
   - Decision title
   - The decision itself
   - Rationale
   - Alternatives rejected
   - Constraints/tradeoffs

Present the proposed TDD additions for review before writing them.
```

#### Slash Commands

These prompts can be encoded as reusable slash commands in `.claude/commands/`. Examples:

**`.claude/commands/implement-section.md`**

```markdown
Read the PRD and TDD for the feature being implemented.
If an Implementation Guide exists for this feature, read that too.

Focus on the section specified by the user. Review the task list and
report status. Propose an implementation plan for remaining tasks.
Do not write code until the plan is approved.

After implementation: verify against the plan, generate a test plan,
run tests, and update the Implementation Guide.

Document any technical decisions in the appropriate TDD.

The user will specify the document and section: $ARGUMENTS
```

**`.claude/commands/write-impl-guide.md`**

```markdown
Write or update the Implementation Guide for the document specified.
Follow the template in docs/templates/template-implementation-guide.md.

Map completed tasks to code, document deviations, edge cases,
integration points, and technical debt. Write for the audience of a
future Claude Code session that needs to understand what was built.

The user will specify the source document: $ARGUMENTS
```

**`.claude/commands/tdd-writeback.md`**

```markdown
Review all technical decisions made in the current session that are not
already documented in a TDD. For each decision, determine the correct
TDD level (Product, Entity, or Action) and document it using the
standard format: Decision, Rationale, Alternatives Rejected,
Constraints/Tradeoffs.

Present proposed additions for review before writing.

The user will specify the scope: $ARGUMENTS
```

### 4.7 Promoting Documents to Claude Code Skills

As your project matures, certain methodology documents become stable reference material that Claude Code needs repeatedly. Rather than loading these documents manually each session or duplicating their content in CLAUDE.md, you can promote them to Claude Code skills — packaged capabilities that Claude Code discovers and loads automatically when they're relevant to the current task.

#### How Skills Differ from CLAUDE.md and Session Prompts

Three mechanisms put context in front of Claude Code, each suited to different content:

- **CLAUDE.md** — always loaded, every session. Best for: permanent rules, file locations, build commands, conventions. Keep it lean (under 150 lines) because it consumes context window in every conversation.
- **Session prompts** (Section 4.6) — loaded once per session by the user. Best for: specifying which documents to read and which section to focus on. This is the mission briefing.
- **Skills** — loaded on-demand when Claude Code determines they're relevant based on the skill's description. Best for: reference material that's needed sometimes but not always. Skills don't consume context window until they're activated.

The key insight: skills are the right home for stable methodology documents that are too large for CLAUDE.md but too frequently needed to rely on session prompts alone.

#### Which Documents to Promote

**Good candidates for skills** — documents that are stable, referenced across many tasks, and can be loaded contextually:

| Document | Skill Type | When Claude Code Loads It |
|---|---|---|
| GUI Standards | Reference | Any task involving UI components, layouts, styling, or interaction patterns |
| Product TDD (design principles section) | Reference | Any implementation task — the principles constrain all code |
| Glossary | Reference | Any task where consistent terminology matters — UI labels, code identifiers, comments, documentation |
| Templates | Task | When creating a new PRD, TDD, or Implementation Guide |

**Poor candidates for skills** — documents that change frequently or are session-specific:

| Document | Why Not a Skill | Where It Belongs |
|---|---|---|
| Entity Base PRDs | Change with each decomposition session; session-specific | Session prompt — load the relevant one |
| Action Sub-PRDs | Same — active work products, not stable reference | Session prompt |
| Implementation Guides | Updated every implementation cycle | Session prompt |
| TDDs (full document) | Living documents that grow during implementation | Session prompt; extract stable design principles into a skill |

#### Creating Methodology Skills

Skills live in `.claude/skills/` (project-level, shared via git) or `~/.claude/skills/` (personal, across all projects). Each skill is a directory containing a `SKILL.md` file with YAML frontmatter and markdown content, plus optional supporting files.

Starter templates for each of these skills are provided in `Templates/skill-templates/`. Copy the relevant template directory into your project's `.claude/skills/` and customize the content for your project.

**GUI Standards skill:**

```
.claude/skills/gui-standards/
├── SKILL.md
└── gui-standards-reference.md
```

`SKILL.md`:
```yaml
---
name: gui-standards
description: UI design system and component patterns for this project. Use when implementing any user interface — list views, detail views, forms, modals, navigation, or any visual component. Covers typography, spacing, color system, component architecture, interaction behaviors, and data display conventions.
---

# GUI Standards

This skill provides the project's UI design system. Load it whenever you're
building or modifying user interface components.

For the complete specification, see [gui-standards-reference.md](gui-standards-reference.md).

## Key Rules (always apply)
- [Your primary font and spacing grid, e.g., "Inter font, 4px spacing grid"]
- [Your component architecture pattern, e.g., "Props-first data flow with composable components"]
- [Your loading state rule, e.g., "Immediate loading states — never show empty screens"]
- [Your theme rule, e.g., "Support both light and dark modes"]
- [Your animation policy, e.g., "No animations or visual flourishes"]
- [Your density preference, e.g., "Compact spacing — information density over whitespace"]
```

The `gui-standards-reference.md` file contains the full GUI Standards document. Claude Code reads `SKILL.md` first (the summary), then loads the reference file only if it needs the detailed specification. This is progressive disclosure — the skill's summary helps Claude Code decide if it needs the full document.

**Design Principles skill:**

```
.claude/skills/design-principles/
└── SKILL.md
```

`SKILL.md`:
```yaml
---
name: design-principles
description: Global design principles and technical constraints that govern all implementation. Use when writing any code, making architectural decisions, or reviewing implementation approaches. These are rules, not suggestions.
---

# Design Principles

These principles are extracted from the Product TDD and apply to all
implementation work. They are non-negotiable constraints.

- [Your performance principle, e.g., "Display speed is paramount — denormalize for read speed"]
- [Your data integrity principle, e.g., "Idempotent writes — all sync uses UPSERT"]
- [Your editability principle, e.g., "Editability is explicit — never make fields editable unless the PRD says so"]
- [Your caching principle, e.g., "Fields marked with † require a caching/denormalization strategy in the TDD"]
- [Add your project's design principles here]
```

This skill is intentionally small. It extracts just the design principles from the Product TDD — the rules that apply to every implementation task. The full Product TDD stays in the repo and is loaded via session prompt when Claude Code needs the complete technical decisions.

**Glossary skill:**

```
.claude/skills/project-glossary/
├── SKILL.md
└── glossary.md
```

`SKILL.md`:
```yaml
---
name: project-glossary
description: Authoritative project terminology. Use when naming variables, writing UI labels, creating comments, writing documentation, or any time consistent terminology matters. Contains all domain terms with definitions.
---

# Project Glossary

Use these terms exactly as defined. Do not invent synonyms or abbreviations.

For the complete term list, see [glossary.md](glossary.md).
```

**Template skill:**

```
.claude/skills/prd-templates/
├── SKILL.md
├── template-entity-base-prd.md
├── template-action-sub-prd.md
├── template-tdd.md
├── template-implementation-guide.md
└── [other templates]
```

`SKILL.md`:
```yaml
---
name: prd-templates
description: Templates for creating PRD methodology documents — Entity Base PRDs, Action Sub-PRDs, TDDs, Implementation Guides, Functional Area PRDs, and other document types. Use when creating a new methodology document or when asked to generate a PRD, TDD, or implementation guide.
---

# PRD Document Templates

When creating a new methodology document, use the appropriate template:

- Entity Base PRD → [template-entity-base-prd.md](template-entity-base-prd.md)
- Action Sub-PRD → [template-action-sub-prd.md](template-action-sub-prd.md)
- Entity/Action TDD → [template-tdd.md](template-tdd.md)
- Implementation Guide → [template-implementation-guide.md](template-implementation-guide.md)
- Functional Area PRD → [template-functional-area-prd.md](template-functional-area-prd.md)
- Entity UI PRD → [template-entity-ui-prd.md](template-entity-ui-prd.md)
- GUI Standards → [template-gui-standards.md](template-gui-standards.md)
- Product PRD → [template-product-prd.md](template-product-prd.md)
- Product TDD → [template-product-tdd.md](template-product-tdd.md)
- PRD Index → [template-prd-index.md](template-prd-index.md)

Read the template before creating the document. Follow its structure exactly.
```

#### Skill Activation and Reliability

Skills are model-invoked — Claude Code decides when to load them based on the description matching the current task. Activation is not guaranteed; it depends on how well the description matches the user's request.

**Writing effective descriptions:** The `description` field in the YAML frontmatter is what Claude Code uses to decide whether to load the skill. Include both what the skill does and specific trigger words that would appear in relevant prompts. For example, "Use when implementing any user interface" is better than "UI stuff" because it matches prompts like "implement the contact list view."

**When activation matters most:** For design principles and glossary, inconsistent activation means inconsistent code. If you find that a skill isn't activating reliably for tasks where it should apply, you have two options:

1. **Improve the description** — add more trigger words and make the "when to use" clause more specific.
2. **Move critical rules to CLAUDE.md** — if a rule must apply to every task without exception, CLAUDE.md (always loaded) is more reliable than a skill (loaded on match). Extract the most critical rules into CLAUDE.md and keep the full reference in the skill.

These are complementary strategies, not alternatives. CLAUDE.md carries the rules Claude Code must never forget; skills carry the detailed reference it needs when working in a specific area.

**Explicit invocation as a fallback:** If Claude Code doesn't load a skill automatically, you can reference it in your session prompt: "Use the gui-standards skill for this task." This forces activation regardless of description matching.

#### Sharing Skills via Git

Project skills in `.claude/skills/` are checked into version control and automatically available to all team members when they pull. This makes skills the right distribution mechanism for methodology documents — update the glossary or GUI Standards in the skill, push to git, and every developer's Claude Code instance picks up the change.

Update the skill files directly when the source documents change. Unlike project knowledge in Claude.ai (which requires manual re-upload), skills in the repo stay in sync with git automatically.

**Symlinks vs. copies for reference files:** Skills reference documents that already exist in your project (GUI Standards, glossary, templates). Rather than copying these files into the skill directory (creating a maintenance problem with two copies), use symbolic links: `ln -s ../../../PRDs/glossary.md glossary.md`. Git preserves symlinks, so the skill's reference file always points to the canonical source. When the source document is updated, the skill picks up the change automatically.

---

## 5. Writing Effective PRDs

### 5.1 Abstraction Level

PRDs describe *what* the system does in terms of user-facing behavior and business rules. They do not specify implementation details. Examples:

**PRD (correct):** "Contact display name is required. It is computed from first name and last name unless manually overridden by the user."

**PRD (too technical):** "display_name TEXT NOT NULL DEFAULT computed via COALESCE(first_name || ' ' || last_name)."

The second example belongs in a TDD if the specific implementation matters.

### 5.2 Action Catalog Granularity

In the Entity Base PRD, simple actions are fully described in the action catalog. An action is "simple" when it can be fully specified in a few sentences — its trigger, inputs, outcome, and business rules. Once an action involves multi-step workflows, conditional logic, interactions with multiple entities, or complex UI, it graduates to its own sub-PRD.

The author makes this call. The methodology provides a structure to capture the information consistently regardless of where the boundary falls.

### 5.3 Task List Granularity

Each task list item should be small enough that Claude Code can implement it in a focused pass and you can verify it clearly, but not so granular that the list becomes unmanageable. Items are prefixed with an entity code and number for tracking:

```
- [ ] CONT-01: Contact list view with sortable columns (name, company, email, phone)
- [ ] CONT-02: Add Contact form with field validation
- [ ] CONT-03: Edit Contact form with pre-populated fields
```

The right granularity will emerge through practice. Start at the level of one discrete behavior or UI element and adjust as you learn.

### 5.4 UI Specifications

The level of UI detail is always the author's choice:

- A sentence for trivial UI ("standard edit form per GUI Standards")
- A written description for moderate complexity (field layout, conditional visibility, navigation flow)
- A wireframe for critical layouts where visual precision matters

The GUI Standards document handles reusable patterns. Entity and action PRDs handle specific screens and workflows.

### 5.5 Cross-Entity References

When an action sub-PRD crosses entity boundaries (e.g., email import touches Communications, Contacts, and Companies), it references the other entity base PRDs by name but extracts the specific context it needs into its own document. This maintains self-containment while acknowledging dependencies.

### 5.6 Field-Level Metadata in Entity Base PRDs

Every field in an Entity Base PRD's Core Fields table must declare three behavioral attributes beyond its description and valid values: **Editable**, **Sortable**, and **Filterable**. These are product decisions that directly control what Claude Code builds.

**Why this matters:** Without explicit field metadata, Claude Code makes assumptions. It may make a computed field editable (e.g., allowing inline editing of a display name that's derived from first + last name). It may add sort options to fields that require expensive subqueries. It may omit filter options for fields that users need to filter by. Each of these is a bug that traces back to an ambiguous PRD.

**The Editable taxonomy:**
- **Direct** — User edits this field inline. Claude Code renders an input or select control.
- **Override** — Computed by default, but user can manually override. Claude Code needs to track whether the current value is computed or overridden, and provide a "reset to computed" action.
- **Via [sub-entity]** — The displayed value summarizes a related record. Clicking it opens the sub-entity's editor, not an inline edit. This is the most common source of Claude Code bugs — it sees a field on the detail page and makes it editable when it should navigate to a different editor.
- **Computed** — Derived from other data. Not editable at all. Claude Code renders it as read-only.
- **System** — Set by the system. Never rendered with any edit affordance.

**The † caching convention for sortable fields:** When a field is marked Sortable but is backed by a correlated subquery (e.g., primary email is resolved from a join on contact_identifiers), the PRD marks it with † and includes a note: "The Entity TDD must define a caching or denormalization strategy." This creates a clear contract:
- The PRD says "users should be able to sort by this field" (product decision)
- The TDD says "we cache this value in column X, kept in sync by Y" (technical decision)
- Claude Code reads both and implements accordingly

Without this convention, Claude Code either makes expensive subquery fields sortable (degrading performance) or silently makes them non-sortable (violating the PRD). The † makes the intent explicit and the responsibility clear.

### 5.7 Entity vs. Functional Area: Where System Admin Functions Belong

System administration is the most common case where functionality doesn't fit neatly into a single entity. The challenge is that admin work touches multiple entities (users, provider accounts, settings) while also including system-level operations (backups, health monitoring, GDPR purge) that don't belong to any entity. Getting the boundary wrong creates either a bloated entity PRD or scattered requirements that Claude Code can't find.

**The decision rule:** If the functionality *is* a data object with its own fields, lifecycle, and CRUD operations, it's an entity. If the functionality *operates on* entities and system resources, it's a functional area. Some things that feel like "admin" are actually entities:

| Looks like admin... | Actually is... | Why |
|---|---|---|
| "User management" | User entity + admin actions on it | Users have fields (name, email, role), a lifecycle (invited → active → suspended → deactivated), and CRUD. The data model belongs in a User Entity Base PRD. |
| "Tenant management" | Customer/Tenant entity + admin actions | Tenants have fields, configuration, and lifecycle. The data model belongs in its own Entity Base PRD. |
| "Provider account management" | Provider Account entity + admin actions | Provider accounts have fields (email, type, tokens, sync state), a lifecycle (connected → syncing → paused → needs_reauth → disconnected), and CRUD. |
| "Settings page" | Admin functional area (configuration) | Settings don't have an independent lifecycle — they're configuration knobs. They belong in the Functional Area PRD's Configuration section. |
| "GDPR purge" | Admin functional area (data operations) | A cross-entity workflow that touches contacts, communications, relationships, and the event store. No single entity owns it. |
| "System health dashboard" | Admin functional area (monitoring) | Aggregates status from sync, database, and background jobs. Not an entity. |

**The recommended split for system administration:**

1. **Entity Base PRDs** for User, Customer/Tenant, and Provider Account — each defines the data model, fields (with editable/sortable/filterable metadata), relationships, and lifecycle. Simple CRUD actions live in their action catalogs.

2. **System Administration Functional Area PRD** for everything that operates across entities or at the system level — the admin actions performed on those entities (invite user, suspend user, connect account, disconnect account), settings management, data operations, system health monitoring, and onboarding workflows. The Functional Area PRD references the entity PRDs for data model context but owns the administrative actions and processes.

3. **Action Sub-PRDs** for complex admin operations — GDPR data purge, schema migration execution, and similar high-consequence workflows that need detailed requirements, confirmation gates, and audit trails.

**Why this split works:** Claude Code gets clear, focused documents. When building the user profile page, it reads the User Entity Base PRD. When building the admin user management screen, it reads the Admin Functional Area PRD. When building the GDPR purge workflow, it reads the GDPR Sub-PRD. Each document is self-contained for its purpose.

**Generalizing beyond admin:** This same pattern applies to any functional area. Notifications, audit logging, search infrastructure, and reporting are all functional areas that operate across entities. Each gets its own Functional Area PRD when the requirements are substantial enough to warrant it. Small cross-cutting concerns (like "all entities support soft delete") can live in the Product PRD or the relevant Entity Base PRDs without needing a separate document.

---

## 6. Evolving the Methodology

This methodology is a starting framework, not a rigid specification. As you use it:

- Adjust task list granularity based on what works with Claude Code
- Add new document types if cross-entity workflows need their own home
- Promote stable reference documents (Product TDD, GUI Standards, Glossary) to Claude Code skills (see Section 4.7)
- Refine templates based on what information Claude Code actually needs versus what's noise

The structure is designed to be extensible. Any new document type follows the same patterns — self-contained, hierarchically organized, with task lists and test plans where implementation work is tracked.

---

## Appendix A: Version History

### V5.0 — 2026-02-28

**Consolidated methodology into a single canonical document.** Two divergent copies (CRMExtender V4 and Best Practices V3) were merged. All content now lives in this document in the Best Practices repository. The CRMExtender copy was retired.

**New document type: Glossary (Section 3.5).** Recognized the glossary as a product-level document type. Added to the Product Level table (Section 2.1) and the Template Registry. The glossary provides a single authoritative source of terminology — all PRDs reference it rather than maintaining independent term definitions. No formal template needed; the structure is a flat alphabetical term table.

**New section: Prompt Templates for Claude Code (Section 4.6).** Added stage-by-stage prompt templates for the Plan-Execute-Verify-Test-Document cycle: session start (new implementation and iteration variants), plan stage, execute stage, verify stage, test stage, document stage, and TDD write-back. Added three reusable slash command examples (`implement-section`, `write-impl-guide`, `tdd-writeback`).

**New section: Skills Integration (Section 4.7).** Added guidance on promoting stable methodology documents to Claude Code skills. Covers which documents are good candidates (GUI Standards, Design Principles, Glossary, Templates) vs. poor candidates (active PRDs, TDDs, Implementation Guides). Provides four complete skill examples with progressive disclosure pattern. Covers activation reliability, the relationship between CLAUDE.md/session prompts/skills, sharing via git, and symlinks for reference files.

**Added skill starter templates to Template Registry.** Four starter kits in `Templates/skill-templates/` for GUI Standards, Design Principles, Glossary, and PRD Templates skills.

**Section renumbering.** All Section 3 subsections renumbered (3.5–3.12) to accommodate the Glossary insertion. Cross-references in version history and Section 4.2 updated accordingly.

### V4.0 — 2026-02-23

**New: Template Registry (Section 3).** Added a centralized registry listing all template files with their document types and hierarchy levels. This provides a single reference for which template to use when creating each document type.

**New: Entity vs. Functional Area framework (Section 5.7).** Added decision guidance for when functionality should be treated as an entity (with its own data models, lifecycle, and document set) versus a functional area (cross-cutting operations that work across entities). Includes the Admin System as a worked example demonstrating the three-document pattern: Functional Area PRD for the admin workspace, Entity Base PRDs for administrable entities, and Action Sub-PRDs for complex admin operations.

### V3.0 — 2026-02-23 / 2026-02-27

This version was created in two stages across different documents, later consolidated in V5.0.

**New document type: Functional Area PRD (Sections 2.4, 3.11).** Added a new hierarchy level for cross-cutting functionality that doesn't center on a single data entity — administration, notifications, audit logging, search infrastructure, and similar concerns that span multiple entities. Includes inheritance rules and a dedicated template.

**New document type: Implementation Guide (Sections 2.1–2.3, 3.12).** Added as a 1:1 companion for every PRD and TDD that Claude Code works from. Purpose: capture what was actually built — files created, requirement-to-code mapping, deviations from the PRD, edge cases discovered, integration points, and technical debt. The handoff set for Claude Code iterations is now three documents: PRD + TDD + Implementation Guide.

**Extended implementation workflow (Section 4.2).** The cycle expanded from Plan-Execute-Verify-Test to Plan-Execute-Verify-Test-Document. The Document stage is mandatory — Claude Code writes or updates the Implementation Guide after completing work.

**New template:** `template-implementation-guide.md` added to the Templates directory.

### V2.0 — 2026-02-23

**New PRD component: Key Processes (Sections 3.6, 3.9).** Key Processes document the critical multi-step workflows for each entity — the flows that must work correctly for the entity to deliver its value. Each Key Process has a unique ID (e.g., KP-CONT-01), a descriptive name, and step-by-step flow. Test plans reference Key Process IDs to ensure coverage.

**New PRD component: Field Metadata (Section 5.6).** Entity Base PRD field registries now require three metadata columns: Editable (Direct, Override, Via sub-entity, Computed, System), Sortable (Yes, Yes†, No), and Filterable (Yes, No). This creates explicit contracts between the PRD and the implementation — Claude Code knows exactly which fields to make editable, sortable, and filterable without guessing.

**Expanded TDD methodology (Sections 3.2, 3.8, 4.4).** TDDs are now described as living documents where both the product owner and Claude Code record decisions. The write-back workflow allows Claude Code to document technical decisions it makes during implementation, using the standard format: Decision, Rationale, Alternatives Rejected, Constraints/Tradeoffs.

**New convention: † caching symbol.** When a field's Sortable column shows "Yes†", it means the field is backed by a correlated subquery that is expensive to sort. The PRD states the product intent; the TDD must define a caching or denormalization strategy to make it performant.

### V1.0 — 2026-02-21

**Initial methodology.** Established the core framework: three-level document hierarchy (Product, Entity, Action), document types (Product PRD, Product TDD, Entity Base PRD, Entity UI PRD, Entity TDD, Action Sub-PRD, Action TDD), the phase split between Claude.ai and Claude Code, session management guidance, and the Plan-Execute-Verify-Test implementation cycle. Created initial templates for all document types.
