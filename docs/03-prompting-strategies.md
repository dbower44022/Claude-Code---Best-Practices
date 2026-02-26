# Prompting Strategies

Writing effective prompts is the single biggest lever you have for getting good results from Claude Code. The difference between a vague request and a well-structured prompt is the difference between spending ten minutes on revisions and getting it right the first time. This guide covers practical techniques for writing prompts that produce reliable, high-quality output on real codebases.

## PRD-Driven Development

On large applications, teams work from PRDs, design docs, and specs — not ad-hoc prompts. The most effective workflow with Claude Code is to provide the PRD and let Claude handle the decomposition, rather than manually breaking features into small prompts yourself.

### Store Specs in Your Repository

Keep PRDs and feature specs where Claude can read them:

```
docs/
  specs/
    notifications.md       # PRD for notification system
    team-management.md     # PRD for teams feature
    billing-v2.md          # PRD for billing overhaul
```

Reference them from CLAUDE.md so Claude knows they exist:

```markdown
## Feature Specs
PRDs and feature specs live in docs/specs/. Read the relevant spec before
implementing any feature work.
```

### Let Claude Decompose the Work

Instead of manually writing four sequential prompts, point Claude at the spec and use plan mode:

```
Read the notification system PRD in docs/specs/notifications.md and propose
an implementation plan. Break it into stages that can be implemented and
reviewed incrementally. Consider our existing patterns — the EventBus in
src/lib/event-bus.ts, the existing EmailService, and our standard
service/repository/controller layers.
```

Claude reads the PRD, explores your codebase, and proposes something like:

```
Stage 1: Database schema — notification and preference tables, migrations
Stage 2: NotificationService — create, mark read, query with filters
Stage 3: API endpoints — list (paginated), mark read, mark all read
Stage 4: Email integration — connect to existing EmailService
Stage 5: Weekly digest — scheduled job using existing task queue
Stage 6: Tests — unit tests for service, integration tests for endpoints
```

You review the plan, adjust the staging ("move preferences to stage 2, we need them before the API layer"), and approve. Then Claude implements stage by stage, and you review at each checkpoint.

**Why this works better than manual decomposition:**

- Claude sees the full picture from the PRD, so each stage accounts for what comes next
- The decomposition reflects your actual codebase structure, not a generic guess
- You steer at the plan level, not at the prompt level
- It scales — the same workflow works for a 2-page spec or a 20-page PRD

### Encode the Workflow as a Slash Command

Once you've established this pattern, make it repeatable:

```markdown
<!-- .claude/commands/implement-spec.md -->
Read the feature spec at: $ARGUMENTS

Before writing any code:
1. Understand the full scope of the feature from the spec
2. Explore the codebase to understand existing patterns that apply
3. Propose an implementation plan broken into stages
4. Each stage should be independently reviewable and testable
5. Call out any ambiguities or decisions not covered by the spec

Present the plan and wait for my approval before implementing any stage.
After approval, implement one stage at a time, pausing for review between stages.
```

Now any team member runs `/project:implement-spec docs/specs/notifications.md` and gets a structured implementation workflow driven by the PRD.

### When Manual Decomposition Still Makes Sense

For smaller tasks that don't warrant a full spec — bug fixes, small enhancements, adding a field — you don't need a PRD. Just give Claude a clear, focused prompt. The PRD workflow is for features with enough scope that you'd write a spec anyway.

## Specificity vs. Ambiguity

Knowing when to be precise and when to leave room for Claude's judgment is a key skill.

### Be Specific When...

You have exact requirements, naming conventions, or implementation details that matter.

```
Refactor the calculateShipping function in src/orders/shipping.ts to use
a strategy pattern. Each shipping method (standard, express, overnight)
should be its own class implementing a ShippingStrategy interface with a
calculate(weight: number, distance: number): Money method. Keep the
existing test cases passing.
```

```
Add rate limiting to the /api/auth/login endpoint. Use a sliding window
of 5 attempts per 15 minutes, keyed by IP address. Return 429 with a
Retry-After header. Use our existing Redis instance for storage -- see
the connection in src/config/redis.ts.
```

Specificity matters most for:

- Database schema changes (column names, types, constraints)
- API contracts (routes, status codes, response shapes)
- Error handling behavior (what to catch, how to report)
- Performance requirements (caching strategy, query optimization)

### Be Open-Ended When...

You want to explore approaches or leverage Claude's ability to analyze tradeoffs.

```
We need to add real-time updates to our dashboard. The current setup
polls every 30 seconds. What are our options given that we're running
on Express with a PostgreSQL backend? Consider our current
infrastructure -- we're on a single server behind nginx.
```

```
The test suite for src/services/payment.service.ts takes 45 seconds to
run. Look at the tests and suggest how we could speed them up without
reducing coverage.
```

Open-endedness works for:

- Evaluating architectural approaches
- Finding performance improvements
- Identifying potential issues with a design
- Learning how an unfamiliar part of the codebase works

## Referencing Files and Code

Claude Code can read your project files directly. Pointing it at specific locations is far more effective than pasting code into your prompt.

**Direct file references:**

```
In src/auth/middleware.ts, the validateToken function on line 45 needs
to handle expired tokens. Right now it throws a generic AuthError -- it
should return a 401 with a specific "token_expired" error code so the
client can trigger a refresh.
```

**Referencing patterns to follow:**

```
Add a new CacheService following the same patterns as
src/services/session.service.ts -- same constructor injection style,
same error handling approach, same logging conventions.
```

**Pointing at related code for context:**

```
The UserRepository in src/repositories/user.repository.ts has a
findByEmail method. Add a similar findByUsername method, but note
that usernames have a unique index (see the migration in
db/migrations/003_add_username_index.sql) so we can optimize the query.
```

**Tips for file references:**

- Use full paths from the project root -- `src/services/auth.ts` not just `auth.ts`
- Mention function or class names when the file is large
- Reference line numbers for specific code blocks, but know they shift as code changes
- Point to test files when you want Claude to understand expected behavior
- Reference configuration files when they affect implementation (tsconfig, eslint, etc.)

## Using Plan Mode

Plan mode tells Claude to analyze and propose an approach before writing any code. Enter it with Shift+Tab (press twice from default mode to cycle through Auto-Accept → Plan) or start Claude with `--permission-mode plan`. This is valuable when the cost of going in the wrong direction is high.

**When to use plan mode:**

- Multi-file refactors where the approach matters
- Features that touch unfamiliar parts of the codebase
- Architecture decisions with multiple viable approaches
- Any change where you want to review the strategy before seeing code

**Example plan mode interaction:**

```
You (plan mode): I need to add WebSocket support to our Express REST API
for real-time order status updates. The current flow is: client polls
GET /orders/:id every 10 seconds. We're on Express 4 with TypeScript,
deployed on AWS ECS behind an ALB.

Claude (plan response):
- Explores your existing Express setup, middleware chain, and deployment config
- Identifies that ALB supports WebSocket connections natively
- Proposes using ws library with Express, creating a WebSocketManager
  service that integrates with your existing OrderService
- Outlines the files to create/modify and the migration path from
  polling to WebSocket
- Notes that you'll need sticky sessions or a pub/sub layer for
  multi-instance support

You: Good plan, but we're about to move to multiple ECS tasks, so
let's include Redis pub/sub from the start. Skip the polling fallback
for now -- we'll add that later if needed.

Claude: Updates the plan with Redis pub/sub integration, references
your existing Redis config, and proceeds to implementation.
```

**Tips for better plans:**

- Give Claude the full context: what you're building, why, and what constraints exist
- Mention infrastructure and deployment details -- they affect architecture
- Review the plan carefully and push back on anything that doesn't fit
- Ask about tradeoffs if the plan makes a choice you don't understand
- Once you approve, exit plan mode (Shift+Tab to cycle back to default mode) and tell Claude to proceed with the plan — plan mode is read-only, so Claude cannot write code until you switch out of it

## Multi-Turn Iteration

Real work happens across multiple turns. Effective iteration means giving Claude precise feedback rather than starting over.

**Effective iteration flow:**

```
Turn 1 - You: Add input validation to the CreateUserDTO in
src/dto/create-user.dto.ts using class-validator decorators. Email
should be validated, name should be 1-100 chars, password needs
minimum 8 chars with at least one number.

Turn 2 - Claude: [implements the validation]

Turn 3 - You: Good, but two changes: the password also needs at least
one uppercase letter, and add a @Transform decorator to trim whitespace
from the email and name fields.

Turn 4 - Claude: [makes targeted updates]

Turn 5 - You: Now add unit tests for this DTO in the same pattern as
src/dto/__tests__/update-user.dto.test.ts. Cover all the validation
rules including edge cases.
```

**Iteration principles:**

- **Be specific about what to change.** "The error message on line 23 should say 'Invalid email format' not 'Validation failed'" is better than "Fix the error messages."
- **Reference what Claude just did.** "In the function you just created, the retry logic needs a maximum backoff of 30 seconds" keeps context tight.
- **Don't start over for small fixes.** If 90% of the output is good, ask for targeted changes to the other 10%.
- **Build on previous turns.** Each prompt can assume Claude remembers what it just did in this session.
- **Ask for tests after implementation,** not simultaneously. Let Claude focus on one thing at a time.

**When to start a new session instead of iterating:**

- The conversation has gone on for many turns and context is getting large
- You've changed direction significantly from the original task
- Claude seems to be losing track of earlier changes (repeating mistakes you already corrected)

## Prompting Anti-Patterns

**Burying the request in backstory:**

```
Bad: "So we've been having this issue where users complain about slow
page loads and I think it might be related to how we fetch data in the
dashboard component because there are like 6 different API calls that
happen on mount and some of them depend on each other but some don't
and the product team wants us to fix it by next sprint. Can you help?"

Good: "The dashboard component in src/pages/Dashboard.tsx makes 6 API
calls on mount. Three of them are independent (user profile, recent
orders, notifications) and should run in parallel with Promise.all.
The other three depend on the user's org ID from the profile call.
Refactor the data fetching to parallelize the independent calls."
```

**Asking for too many things at once:**

```
Bad: "Add pagination, sorting, filtering, and full-text search to the
/api/products endpoint, update the frontend table component to use all
of these, and add tests."

Good: Start with pagination, verify it works, then add sorting, then
filtering. Each is a reviewable, testable increment.
```

**Being vague when precision matters:**

```
Bad: "Make the auth more secure."

Good: "Add CSRF protection to all state-changing endpoints (POST, PUT,
DELETE). Use the csurf middleware with cookie-based tokens. Exclude the
/api/webhooks/* routes since those use HMAC verification instead."
```

**Not mentioning project conventions:**

```
Bad: "Add a logger to the payment service."

Good: "Add logging to src/services/payment.service.ts using our Winston
logger (imported from src/lib/logger.ts). Follow the same pattern as
src/services/order.service.ts -- structured JSON logs with a service
name prefix and correlation ID from the request context."
```

**Over-constraining exploration prompts:**

```
Bad: "Use Redis Streams with consumer groups to build a job queue with
exactly-once delivery and priority levels 1-5."

Good (if you're exploring): "We need a background job queue for sending
emails and generating reports. We're already running Redis. What
approach would you recommend? We process about 10,000 jobs per day
and need retry logic for failures."
```

The fix for most anti-patterns is the same: be clear about what you want, give Claude the context it needs, and keep each prompt focused on one thing.

## See Also

- [Context Management](02-context-management.md) -- how to give Claude the right context for your prompts
- [Architecture and Design](04-architecture-and-design.md) -- using prompting strategies for design work
- [Implementation Patterns](05-implementation-patterns.md) -- prompting patterns for common implementation tasks
