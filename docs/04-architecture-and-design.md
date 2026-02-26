# Architecture and Design

Claude Code is not just a code generator -- it is a design partner that can explore codebases, evaluate tradeoffs, and help you make better architectural decisions. The key is engaging Claude at the design stage, before you commit to an implementation path. This guide covers practical techniques for using Claude Code in architecture work, from initial exploration through to documenting the decisions you make.

## Using Plan Mode for Design

Start complex features in plan mode. Claude will explore your codebase, understand existing patterns, and propose an approach -- all before writing a single line of code. This is where Claude provides the most architectural value.

**Practical example:**

```
You (plan mode): I need to add WebSocket support to our Express REST
API for real-time order status updates. Currently clients poll
GET /orders/:id/status every 10 seconds. We're running Express 4 with
TypeScript, PostgreSQL for persistence, and Redis for caching. Deployed
on AWS ECS behind an ALB with 2-4 tasks.
```

Claude will typically:

1. Read your Express app setup, middleware configuration, and existing route structure
2. Check your `package.json` for relevant dependencies and your `tsconfig.json` for compilation targets
3. Look at how your existing `OrderService` handles status updates
4. Examine your Redis configuration and usage patterns
5. Review your deployment config (Dockerfile, ECS task definitions) for infrastructure constraints

Then Claude proposes a concrete plan:

```
Claude: Here's my proposed approach:

1. Use the `ws` library integrated with your existing Express HTTP
   server -- your ALB already supports WebSocket upgrade requests.

2. Create a WebSocketManager service in src/services/ that:
   - Maintains client connections keyed by orderId
   - Subscribes to Redis pub/sub channels for order status changes
   - Broadcasts updates to connected clients

3. Modify OrderService.updateStatus() to publish status changes to
   Redis after the database write (line 87 in order.service.ts
   already has the transaction -- we'll publish after commit).

4. Add a new route handler in src/routes/orders.ts for the WebSocket
   upgrade at /orders/:id/ws.

5. Redis pub/sub handles multi-instance fan-out so any ECS task can
   receive the update regardless of which task the client connected to.

Files to create: src/services/websocket-manager.service.ts
Files to modify: src/routes/orders.ts, src/services/order.service.ts,
                 src/app.ts (attach WebSocket server)

Tradeoffs: Redis pub/sub is fire-and-forget, so if a client
disconnects and reconnects, they'll need to fetch current status via
the existing REST endpoint. We could add a brief message buffer if
that becomes a problem.
```

**Your move:** Review the plan. Push back on specifics. Ask questions.

```
You: Good approach. Two adjustments: (1) Use a connection authentication
step -- clients should send a JWT in the first message after connecting,
not in the URL query string. (2) Add a heartbeat/ping interval to clean
up stale connections. Then go ahead and implement.
```

This back-and-forth before any code is written saves significant rework. You caught a security concern (token in URL gets logged) and an operational concern (stale connections) before implementation started.

**When plan mode is most valuable:**

- Features that span multiple services or layers
- Changes to shared infrastructure (database schemas, message queues, caching layers)
- Anything involving concurrency, state management, or distributed systems
- Migrations from one pattern to another (polling to WebSocket, REST to GraphQL, monolith to services)

## Codebase Exploration with Subagents

The Task tool spawns subagents that can do deep research without bloating your main conversation context. This is essential for architecture work on large or unfamiliar codebases.

**Understanding existing patterns:**

```
Use the Task tool to explore how authentication works in this project.
I want to understand: where tokens are issued, how they're validated
on each request, how refresh tokens work, and where the auth middleware
is applied. Summarize the full auth flow.
```

The subagent reads through auth-related files, traces the request flow, and returns a summary. Your main context stays clean for the actual design work that follows.

**Mapping a subsystem before changing it:**

```
Use the Task tool to map out the payment processing flow. Start from
the checkout endpoint in src/controllers/checkout.controller.ts and
trace through to the Stripe integration. I need to understand every
service, repository, and external call in that path before I refactor it.
```

**Comparing patterns across the codebase:**

```
Use the Task tool to find all the different approaches to error handling
in our API controllers in src/controllers/. Some use try-catch, some
use middleware, some throw custom errors. Catalog the different patterns
with file references so we can standardize.
```

**Tips for effective subagent exploration:**

- Give the subagent a clear starting point (a specific file, directory, or entry point)
- Tell it what you need to learn, not just where to look
- Use it before you start designing -- the information it finds will shape your approach
- Ask it to include file paths and function names in its summary so you can reference them later
- Run multiple subagent explorations in parallel if you need to understand several subsystems

## Architecture Reviews

Claude can review architectural decisions with a level of thoroughness that is hard to match in a quick team discussion. Give it the full context and ask for honest feedback.

**Reviewing a proposed design:**

```
I'm planning to add multi-tenancy to our SaaS app. Current approach:
add a tenant_id column to every table, enforce tenant isolation at the
repository layer with a TenantContext that automatically filters queries.

Our stack: Node.js, PostgreSQL, Prisma ORM. We have about 40 tables
and 200 queries across the codebase.

Review this approach. What are the risks? What will we get wrong?
What alternatives should we consider?
```

Claude will typically identify concerns you haven't considered:

- Row-level security in PostgreSQL as an alternative to application-level filtering
- The risk of missing a query and leaking data across tenants
- Migration complexity for 40 tables with existing data
- Performance implications of adding an index to every table
- Whether Prisma middleware can centralize the tenant filtering

**Reviewing existing architecture for a new requirement:**

```
We need to support file uploads up to 500MB. Currently our API runs on
Express with a 10MB body limit, and we store everything in PostgreSQL.
Review our current architecture in the context of this new requirement.
What needs to change?
```

**Asking for specific review angles:**

```
Review the database schema in db/migrations/ with an eye toward
performance at scale. We currently have 50K users and expect to grow
to 1M in the next year. Which queries will become problematic? Which
indexes are missing?
```

**What makes a good architecture review prompt:**

- State what you're building and why
- Describe your current approach or proposed approach
- Include relevant constraints (team size, timeline, existing tech stack, scale)
- Ask specific questions rather than just "review this"
- Mention what tradeoffs you've already considered

## Documenting Decisions

Architecture decisions that live only in people's heads are architecture decisions that will be reversed or forgotten. Use Claude to document them while the context is fresh.

**Generating an ADR after a design session:**

```
We just decided to use event sourcing for the order management system
instead of direct state mutations. Document this as an ADR in
docs/adr/. Include:
- The context: we need audit trails and the ability to replay order
  state for debugging
- The decision: event sourcing with PostgreSQL as the event store
- Alternatives we rejected: audit log table (doesn't support replay),
  Change Data Capture (too much infrastructure overhead for our scale)
- Consequences: more complex write path, need to build projection
  logic, but full auditability and debugging capability
```

**Updating CLAUDE.md with architectural context:**

After making a significant design decision, update your project's `CLAUDE.md` so that Claude (and future developers) understand the architecture:

```
Add to CLAUDE.md under an Architecture section: we use the repository
pattern for all database access. Repositories live in src/repositories/
and are the only code that imports from Prisma. Services never access
the database directly. This is enforced by the eslint-plugin-boundaries
rules in .eslintrc.
```

This creates a positive feedback loop: Claude makes better suggestions in future sessions because it understands the architectural constraints from `CLAUDE.md`.

**Documenting integration points:**

```
Document the Stripe integration architecture in CLAUDE.md. Cover:
- Webhook handling in src/webhooks/stripe.ts (idempotency via event ID)
- The StripeService wrapper in src/services/stripe.service.ts
- How we map Stripe events to internal domain events
- The test doubles in src/__mocks__/stripe.ts and when to use them
```

**When to document:**

- After any design session that produced a decision
- When you discover undocumented conventions in an existing codebase
- When a decision has non-obvious reasoning ("we chose X because of Y constraint")
- When onboarding the next developer would require explaining something verbally

## Working with Existing Architecture

Most work happens within an existing architecture, not on greenfield projects. Helping Claude understand your existing patterns is critical for getting implementations that fit naturally into the codebase.

**CLAUDE.md as architectural documentation:**

The most impactful thing you can put in `CLAUDE.md` is a description of your architectural patterns and the reasoning behind them:

```markdown
## Architecture

### Layered Architecture
- Controllers handle HTTP concerns (request parsing, response formatting, status codes)
- Services contain business logic and orchestrate between repositories
- Repositories handle all database access via Prisma
- Controllers never import repositories directly

### Event System
- Domain events are defined in src/events/definitions/
- Events are dispatched synchronously via EventBus (src/lib/event-bus.ts)
- Event handlers live in src/events/handlers/
- Never dispatch events inside a database transaction -- dispatch after commit

### Error Handling
- Business rule violations throw AppError subclasses (src/errors/)
- The global error handler in src/middleware/error-handler.ts maps these to HTTP responses
- Never catch errors in controllers -- let them propagate to the error handler
```

With this in `CLAUDE.md`, Claude will follow these patterns automatically instead of you having to repeat them in every prompt.

**Using exploration before modification:**

When you need to modify an unfamiliar subsystem, explore first:

```
Prompt 1: "Use the Task tool to explore the notification subsystem in
src/notifications/. I need to understand the class hierarchy, how
notifications are dispatched, and how new notification types are added.
I'm about to add a new notification type."

Prompt 2 (after reading the exploration results): "Add a new
InvoiceOverdue notification type following the patterns you found.
It should be triggered when an invoice is more than 30 days past due."
```

This two-step approach (explore, then implement) consistently produces better results than asking Claude to modify code it hasn't studied.

**Aligning with existing conventions:**

When existing patterns matter, point Claude at concrete examples:

```
Add a new ReportService. Follow exactly the same patterns as
src/services/analytics.service.ts for:
- Constructor dependency injection
- Method-level error handling with the logAndRethrow helper
- The way it uses the CacheService for expensive computations
- JSDoc comment style on public methods
```

Pointing at a specific reference file is more reliable than describing patterns in prose. Claude can read the file and replicate the patterns exactly.

**Identifying and addressing architectural drift:**

Codebases accumulate inconsistencies over time. Claude can help you find and fix them:

```
Use the Task tool to compare the patterns used across all files in
src/services/. I want to know: which services follow our standard
pattern (constructor injection, structured logging, error handling via
AppError) and which ones deviate. List the deviations with file
references so we can plan a cleanup.
```

This kind of systematic analysis across dozens of files is exactly the work that is tedious for humans but straightforward for Claude.

## PRD-Driven Design Workflow

On large applications, features are defined in PRDs or design docs before implementation begins. Claude Code integrates naturally into this workflow — the PRD becomes the primary input, and Claude handles the translation from requirements to implementation plan.

### The Full Cycle

```
PRD (written by team) → Plan Mode (Claude decomposes) → Review Plan → Implement by Stage → Review Each Stage
```

**Step 1: Store the PRD where Claude can read it.**

Keep feature specs in your repository — `docs/specs/`, `docs/prd/`, or wherever your team organizes them. Reference the directory in CLAUDE.md:

```markdown
## Feature Specs
PRDs and feature specs are in docs/specs/. Always read the relevant spec
before starting implementation work on a feature.
```

**Step 2: Feed the PRD to Claude in plan mode.**

```
Read the PRD at docs/specs/team-management.md. Based on our existing
architecture and patterns, propose an implementation plan broken into
stages. Each stage should be reviewable and testable independently.
Flag any ambiguities or missing details in the spec.
```

Claude will explore the codebase, understand your patterns, and propose a staged plan that accounts for your actual architecture — not a generic one.

**Step 3: Review and refine the plan with your team.**

The plan is a collaboration artifact. Push back on staging, add constraints, clarify ambiguities:

```
Move the invitation system to a later stage — we need basic team CRUD
first. Also, the spec doesn't mention it, but teams should have a
soft-delete lifecycle matching our user model. Plan for that from the
data layer.
```

**Step 4: Implement stage by stage.**

Once the plan is approved, Claude implements each stage with the full PRD as context. Because it has the whole spec, each stage naturally accounts for what comes later — data models include fields needed by later stages, services expose methods that future stages will call.

### Why This Scales

Manual prompt decomposition breaks down on large applications because:

- The developer has to hold the full spec in their head while writing prompts
- Individual prompts lose the big picture — stage 1 doesn't know about stage 5's needs
- It's tedious across dozens of features, and the decomposition itself is error-prone
- It doesn't match how teams actually work (from specs, not from prompt sequences)

The PRD-driven approach pushes the decomposition work to Claude, where it belongs. The developer's job is providing the requirements and steering the plan — the same role they play without AI.

### Encode It as a Team Workflow

Create a slash command so any team member can start this workflow:

```markdown
<!-- .claude/commands/implement-spec.md -->
Read the feature spec at: $ARGUMENTS

1. Read and understand the full scope of the feature
2. Explore the codebase to understand existing patterns and architecture
3. Propose a staged implementation plan where each stage is independently
   reviewable and testable
4. Flag ambiguities, missing details, or potential conflicts with existing code
5. Wait for plan approval before implementing

After approval, implement one stage at a time. Pause after each stage for
review. Run relevant tests after each stage.
```

## See Also

- [Prompting Strategies](03-prompting-strategies.md) -- techniques for writing effective prompts during design work
- [Implementation Patterns](05-implementation-patterns.md) -- translating architectural decisions into implementation
- [Project Setup](01-project-setup.md) -- configuring CLAUDE.md and project context for architectural guidance
