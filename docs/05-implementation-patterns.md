# Implementation Patterns

## Overview

Writing code with Claude Code is most effective when you treat it as a collaborative process rather than a one-shot generation task. The patterns in this document help you break work into manageable steps, coordinate changes across files, refactor safely, and recover when things go sideways. Each pattern has been tested on real codebases where the cost of mistakes is high.

## From Spec to Implementation

The most effective pattern for large features is to start from a spec or PRD, let Claude propose the implementation stages, and then execute those stages with review checkpoints between each one. The developer's role is steering and reviewing, not manually decomposing the work into prompts.

### The Workflow

**1. Point Claude at the spec in plan mode:**

```
Read the payment retry PRD in docs/specs/payment-retry.md and propose an
implementation plan. Consider our existing payment processing flow in
services/payment_processor.py and the task queue in utils/task_queue.py.
```

**2. Claude explores and proposes stages:**

Claude reads the spec, examines your codebase, and proposes something like:

```
Stage 1: Core retry logic — PaymentRetryService with retry eligibility,
         exponential backoff, and max retry limits
Stage 2: Error handling — specific exception types, validation of payment
         objects, guard against missing fields
Stage 3: Integration — wire into payment_processor.py, enqueue retries
         via task_queue, add structured logging
Stage 4: Tests — unit tests for retry logic, integration tests for the
         full flow
```

**3. You review the plan and adjust:**

```
Good, but combine stages 1 and 2 — error handling should be part of the core
logic, not a separate pass. And add a stage for the monitoring dashboard
metrics the spec mentions.
```

**4. Claude implements stage by stage, pausing between stages.** You review the diff, run tests, and approve before continuing.

This is more effective than writing four hand-crafted prompts because Claude has the full context from the spec and can make better decomposition decisions than you'd make upfront. If the spec mentions that retry metrics feed into a dashboard, Claude accounts for that in the data model from stage 1 — something you'd miss if you were manually writing prompts without re-reading the whole spec.

### Keeping the Big Picture

A common concern with incremental implementation is losing coherence — each stage works in isolation but the pieces don't fit together well. The PRD-driven approach avoids this because Claude has the full spec as context throughout. Each stage is implemented with awareness of what comes next.

To reinforce this, CLAUDE.md should document cross-cutting architectural patterns:

```markdown
## Architecture
- Services emit domain events via EventBus after state changes
- All new features must expose Prometheus metrics via the metrics service
- Database changes require both up and down migrations
```

These standing instructions keep every implementation stage aligned with the system's architecture, regardless of which specific feature is being built.

### When a Spec Isn't Needed

Not everything needs a PRD. For small, well-defined changes — adding a field, fixing a bug, implementing a utility function — a clear prompt is sufficient. The spec-driven workflow is for features with enough scope that you'd write a spec anyway: multi-file changes, new subsystems, features that span multiple layers of the stack.

## Multi-File Changes

Claude handles multi-file changes well, but it needs you to set up the context. Without clear guidance, Claude may make assumptions about file structure, naming conventions, or relationships between components that don't match your codebase.

**Tell Claude which files are involved, how they relate, and what needs to change in each one.**

```
I need to add a "last_login_ip" field to the user system. This touches three files:

1. models/user.py — Add a last_login_ip field (nullable string, max 45 chars for IPv6)
2. api/serializers.py — Include last_login_ip in UserSerializer (read-only)
3. migrations/ — Generate the migration for the new field

The User model uses SQLAlchemy. The serializer uses marshmallow. Follow the patterns
already established in those files for how fields are declared.
```

This works because Claude can read all three files, understand the existing patterns, and make consistent changes across them.

**For larger multi-file changes, specify the order:**

```
I'm adding webhook support to the notification system. Make these changes in order:

1. First, create models/webhook.py with a Webhook model (url, secret, events list,
   active boolean, created_at). Follow the same base class and conventions as
   models/notification.py.

2. Then create services/webhook_service.py with methods: register_webhook,
   deregister_webhook, and dispatch_event. dispatch_event should send an HTTP POST
   with an HMAC signature in the X-Webhook-Signature header.

3. Then add webhook API endpoints in api/routes/webhooks.py following the same
   pattern as api/routes/notifications.py — CRUD endpoints plus a test endpoint
   that sends a ping event.

4. Finally, update services/notification_service.py to call
   webhook_service.dispatch_event when a notification is created.
```

The ordering matters because each step builds on the previous one. Claude can make all these changes in a single pass, but specifying the order helps it maintain consistency.

**Common mistake:** Asking Claude to "update all the relevant files" without specifying which files. This works sometimes, but on large codebases, Claude may miss files or change files you did not intend. Be explicit.

## Refactoring with Confidence

Refactoring is one of Claude's strongest use cases because refactoring has a clear success criterion: behavior stays the same while structure improves. The key is being explicit about the boundary between what should change and what should not.

**The standard refactoring prompt pattern:**

```
Extract the validation logic from the createOrder function in services/order.py
into a separate validateOrder function in the same file. The new function should
take an OrderRequest and return a ValidationResult. All existing behavior must be
preserved — no functional changes. The createOrder function should call
validateOrder and handle the result the same way the inline validation currently does.
```

Notice three elements: what to extract, where to put it, and the explicit constraint that behavior must not change.

**Always run tests after each refactoring step.** If tests pass before the refactoring and fail after, the refactoring introduced a bug. This is the simplest way to verify correctness, and it is the reason you want good test coverage before starting a refactoring effort.

**For larger refactoring efforts, break them into phases:**

```
I want to refactor the monolithic ReportGenerator class (services/reports.py, ~400 lines)
into smaller, focused classes. Let's do this in stages:

Phase 1: Extract data fetching into a ReportDataFetcher class. Move fetch_sales_data,
fetch_inventory_data, and fetch_customer_data. ReportGenerator should instantiate
ReportDataFetcher and delegate to it. Tests should still pass.

Phase 2: Extract formatting into a ReportFormatter class. Move format_as_pdf,
format_as_csv, and format_as_excel. Same approach — delegate from ReportGenerator.

Phase 3: Extract scheduling logic into ReportScheduler. Move schedule_report,
cancel_scheduled_report, and get_pending_reports.

After all three phases, ReportGenerator should be an orchestrator that coordinates
the three new classes. Run tests after each phase.
```

Ask Claude to do one phase at a time. Review and test between phases.

**Rename refactoring across a codebase:**

```
Rename the "customer" concept to "client" across the codebase. This affects:
- models/customer.py → models/client.py (rename file and class)
- All imports referencing Customer or customer
- Database table name stays as "customers" — don't change the migration
- API endpoints stay as /customers for backward compatibility — only internal names change
- Update tests to use the new names

List all files you plan to change before making changes so I can confirm.
```

The instruction to list files first is important for large-scale renames. It lets you catch files Claude might miss or files it should not touch.

## Handling Large PRs

When a change touches many files, a single large commit is hard to review and hard to revert if something goes wrong. Break the work into logical commits that each represent a coherent step.

**Ask Claude to make changes in layers:**

```
I'm adding a new "teams" feature. Let's build it in stages, and I'll commit after each one:

Stage 1 — Data layer: Create the Team model, TeamMembership model, and migrations.
Stage 2 — Business logic: Create TeamService with create_team, add_member,
          remove_member, and transfer_ownership.
Stage 3 — API layer: Add REST endpoints for team CRUD and membership management.
Stage 4 — Tests: Unit tests for TeamService, integration tests for the API endpoints.
Stage 5 — Documentation: Update the API docs with the new endpoints.
```

After each stage, review the changes, run relevant tests, and commit. This produces a clean commit history that tells the story of the change.

**For changes that need to land atomically but are still large:**

If you cannot split the change into independent commits (for example, a database schema change that requires simultaneous code changes), you can still break the work into reviewable steps within a single branch. Ask Claude to make changes in an order that lets you review incrementally, then squash or keep the commits depending on your team's convention.

**Useful habit:** After Claude completes a large set of changes, ask it to summarize what it changed:

```
Summarize the changes you just made: which files were modified, what was added
or removed in each, and any decisions you made that I should be aware of.
```

This helps you catch changes you might otherwise miss during review.

## Using Worktrees for Parallel Work

Git worktrees let you have multiple branches checked out simultaneously in separate directories. Claude Code supports worktrees natively, making it practical to work on multiple tasks in parallel without stashing or switching branches.

**When worktrees are useful:**

- **Comparing approaches:** You want to try two different implementations of a feature and compare them side by side.
- **Hotfix while a feature is in progress:** You are mid-feature on a branch but need to fix something on main. Create a worktree for the fix instead of stashing your work.
- **Parallelizing independent tasks:** Two changes that do not conflict can proceed simultaneously in separate worktrees with separate Claude sessions.

**How to use worktrees with Claude Code:**

Tell Claude to create a worktree when you want to start parallel work:

```
Create a worktree for experimenting with a Redis-based caching approach.
```

Claude creates a new worktree in `.claude/worktrees/` with a new branch based on your current HEAD. You can then work in that worktree independently. When you are done, you can merge the branch or discard the worktree.

**Important:** Add `.claude/worktrees/` to your `.gitignore` to prevent worktree contents from appearing as untracked files in your main repository.

**Practical example — comparing two caching approaches:**

In your main worktree:
```
Implement an in-memory LRU cache for the product catalog lookups in
services/catalog.py. Use functools.lru_cache with a max size of 1000
and a TTL wrapper that expires entries after 5 minutes.
```

In a second worktree:
```
Implement a Redis-based cache for the product catalog lookups in
services/catalog.py. Use the existing Redis connection in config/redis.py.
Cache serialized Product objects with a 5-minute TTL. Include a cache
invalidation method that's called when a product is updated.
```

Now you can compare both implementations, run benchmarks on each, and choose the better approach with full working code for both options.

**Practical example — hotfix while a feature is in progress:**

You are in the middle of adding a teams feature when a production bug comes in. Instead of stashing your half-finished work:

```
Create a worktree for a hotfix on the login rate limiter.
```

Fix the bug in the new worktree, get it reviewed and merged, then return to your feature branch with no disruption.

## When Claude Gets Stuck

Claude is a powerful tool, but it has limits. Recognizing when Claude is struggling and knowing how to recover will save you significant time.

**Signs that Claude is struggling:**

- **Circular edits:** Claude changes something, breaks something else, fixes that, and breaks the original thing again. You are going in circles.
- **Increasing complexity:** Each iteration adds more special cases, flags, or workarounds instead of addressing the root issue.
- **Bug whack-a-mole:** Fixing one test breaks another. The fixes are not converging.
- **Contradictory changes:** Claude undoes changes it made two prompts ago.
- **Confident but wrong:** Claude asserts that a change fixes the issue, but it does not, and repeating the same prompt produces the same incorrect fix.

**What to do:**

**1. Step back and provide more context.** Claude may be missing information about how the system works. Instead of continuing to prompt for fixes, explain the architecture:

```
Let me step back and explain how this system works. The order processing pipeline
has three stages: validation, payment, and fulfillment. Each stage is a separate
service that communicates through an event bus. The bug we're seeing is in the
fulfillment stage, but the root cause might be in how events are serialized
between payment and fulfillment. Here's what I know: [details].
```

**2. Simplify the task.** If Claude is struggling with a complex change, break it into smaller pieces that are each straightforward:

```
Let's simplify. Forget the caching for now. Just get the basic query working
correctly against the database with no caching layer. Once that works, we'll
add caching as a separate step.
```

**3. Start a fresh conversation.** Context accumulates in long conversations, and sometimes that context includes wrong assumptions or failed approaches that bias future responses. A fresh conversation with a clear, well-framed prompt often succeeds where continuing a long thread fails:

```
I need to fix a bug in the order fulfillment pipeline. When an order has more
than 10 line items, the fulfillment event is not being processed. Here's the
relevant code: [paste or reference the key files]. The error in the logs is:
"Event payload exceeds maximum size." I think the fix is in the event
serialization, but I want you to investigate and confirm before making changes.
```

**4. Do the hard part yourself.** Sometimes the right move is to write the tricky logic yourself and hand Claude the straightforward parts. If Claude cannot figure out the correct algorithm for a complex business rule, write the algorithm and ask Claude to integrate it, add tests, and handle edge cases.

**5. Check if Claude has the right information.** If Claude keeps producing wrong code, it may be working with incorrect assumptions about your dependencies, your runtime environment, or your data shapes. Ask Claude what it thinks the relevant interfaces look like:

```
Before making any changes, tell me: what do you think the signature of
process_event looks like? What fields do you expect on the FulfillmentEvent object?
```

If the answer is wrong, you have found the problem. Provide the correct information and try again.

## See Also

- [Prompting Strategies](03-prompting-strategies.md) -- How to write prompts that set up these patterns for success
- [Testing and Debugging](06-testing-and-debugging.md) -- Testing workflows that complement incremental implementation
- [Architecture and Design](04-architecture-and-design.md) -- Designing systems that are easier to implement incrementally
