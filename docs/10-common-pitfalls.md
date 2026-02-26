# Common Pitfalls

Even experienced developers fall into predictable traps when working with Claude Code. This guide catalogs the most common anti-patterns — what they look like in practice, why they happen, and concrete strategies to avoid them. Recognizing these patterns early saves hours of rework and prevents subtle bugs from reaching production.

Most pitfalls stem from a mismatch between how Claude Code works and how developers assume it works. Understanding these failure modes is as important as knowing the best practices.

## Over-Relying on Claude Without Reviewing Output

**What it looks like:** You accept Claude's output, commit it, and move on without reading the diff carefully. The code compiles, maybe the tests pass, and it looks reasonable at a glance. Weeks later, someone discovers a subtle bug — an edge case that silently returns wrong data, a security check that's almost right but bypassable, or business logic that handles 90% of cases but fails on the ones that matter most.

**Why it happens:** Claude produces fluent, well-structured code that reads like it was written by a competent developer. This creates a false sense of confidence. The output looks so plausible that your brain skips from "does this look right?" to "this looks right" without actually verifying.

**How to avoid it:**

Run the tests. Every time. If there aren't tests for the changed code, that's a signal to write them before committing.

```
# After Claude makes changes, always check what actually changed
git diff

# Run the relevant tests
npm test -- --related

# For critical paths, manually verify the behavior
```

Train yourself to look for these specific risks in Claude's output:

- **Incorrect business logic:** Claude may implement a reasonable interpretation that isn't your interpretation. Does the discount apply before or after tax? Does "inactive" mean soft-deleted or just deactivated? Claude will pick one — make sure it picked right.
- **Missing edge cases:** Empty arrays, null values, concurrent access, Unicode in string handling, timezone-related date logic. Claude often handles the happy path well and the edge cases poorly.
- **Security gaps that look fine at a glance:** Input validation that misses one field, an auth check that verifies the token but not the permissions, an SQL query that's parameterized except for one dynamic table name.

**The habit to build:** Treat Claude's output the way you'd treat a junior developer's PR. Read it with the same attention you'd give code you're responsible for — because you are.

## Context Window Exhaustion

**What it looks like:** Midway through a long session, Claude starts:

- Forgetting instructions you gave earlier ("I thought I said to use Result types, not exceptions")
- Suggesting changes that contradict its own earlier work
- Losing track of which files it already modified
- Giving generic responses instead of project-specific ones
- Repeating information you already discussed

**Why it happens:** Claude's context window is large but finite. Every message, every file read, every tool output consumes context. In a long session with many file reads and edits, earlier context gets pushed out to make room for newer content. Claude doesn't "forget" intentionally — the earlier information literally isn't available to it anymore.

The most common triggers:

- Reading many files to explore the codebase without a focused goal
- Large tool outputs (big test results, verbose logs, huge diffs)
- Sessions that span multiple unrelated tasks without resetting
- Repeatedly pasting large blocks of code or documentation

**How to avoid it:**

**Start fresh for new tasks.** If you've finished one feature and are starting another, open a new conversation. There's no benefit to carrying over context from unrelated work, and significant cost.

**Use /compact proactively.** Don't wait until Claude starts behaving oddly. If you've been working for a while and are about to start a different phase of work, compact the conversation:

```
/compact Focus on the billing service changes we've agreed on.
Discard the earlier exploration of authentication.
```

**Use subagents for research.** When you need Claude to explore the codebase to answer a question, use a focused subagent prompt rather than reading dozens of files into your main conversation:

```
Look at how the notification service works — specifically how it decides
which channel (email vs. SMS vs. push) to use for a given notification type.
Summarize the logic without reading every file.
```

**Keep tool outputs focused.** Instead of asking Claude to read an entire 2000-line file, point it at the specific section:

```
Read the processPayment function in src/services/billing.ts
(around lines 145-210).
```

**Watch for the warning signs.** If Claude gives a response that contradicts something you established earlier in the conversation, that's your signal that context is getting stale. Compact or restart.

## Over-Engineering and Gold-Plating

**What it looks like:** You ask Claude to add a feature and get back code with:

- An abstract base class and interface for something that has one implementation
- A configuration system for values that will never change
- A plugin architecture for a component that doesn't need extensibility
- Elaborate error handling for conditions that can't occur in practice
- Generic type parameters on a function called from exactly one place

Example — you ask for a function to format a user's display name:

```typescript
// What Claude might produce
interface NameFormatterConfig {
  includeMiddleName: boolean;
  lastNameFirst: boolean;
  titleCase: boolean;
  maxLength?: number;
  truncationSuffix?: string;
}

class NameFormatter {
  private config: NameFormatterConfig;

  constructor(config: Partial<NameFormatterConfig> = {}) {
    this.config = {
      includeMiddleName: false,
      lastNameFirst: false,
      titleCase: true,
      truncationSuffix: '...',
      ...config,
    };
  }

  format(user: User): string {
    // 40 lines of implementation covering every possible combination
  }
}

// What you actually needed
function formatDisplayName(user: User): string {
  return `${user.firstName} ${user.lastName}`;
}
```

**Why it happens:** Claude's training data is full of well-engineered libraries and frameworks where abstraction is appropriate. It pattern-matches toward "production-quality" code, which in library contexts means flexible, configurable, and extensible. But most application code benefits from the opposite: specific, direct, and simple.

**How to avoid it:**

Be explicit about simplicity in your prompts:

```
Add a function to format the user's display name as "First Last".
Keep it simple — just a plain function, no classes or configuration.
Only handle the cases we actually have (firstName and lastName are
always present strings).
```

When reviewing Claude's output, ask yourself:

- Would I accept this in a code review from a colleague? Or would I ask them to simplify?
- Is there a configuration option here that we'll never actually use?
- Does this abstraction have more than one concrete implementation? Will it ever?
- Could I delete half of this code and still meet the requirements?

If Claude produces something over-engineered, don't just accept it. Push back:

```
This is more complex than needed. Simplify it:
- Remove the config object, just hardcode the behavior we need
- Use a plain function instead of a class
- Remove the error handling for empty names — our schema enforces they're always present
```

## Not Leveraging Existing Project Context

**What it looks like:** Claude writes code that works but feels off:

- Uses `console.log` when your project uses a structured logger
- Creates a new utility function when an identical one exists in your shared library
- Uses raw SQL when your project uses an ORM
- Follows different naming conventions than the rest of the codebase
- Implements error handling differently from every other file in the project

You spend more time adjusting Claude's output to match your project than you'd spend writing it yourself.

**Why it happens:** Without CLAUDE.md, Claude has no way to know your project's conventions beyond what it can infer from files it happens to read. It defaults to common patterns from its training data, which may not match your specific choices. Claude doesn't know that your team chose Zod over Joi for validation, or that your error types follow a specific discriminated union pattern, unless you tell it.

**How to avoid it:**

Invest time in CLAUDE.md upfront. The sections that save the most time:

```markdown
## Coding Standards
- Use the `logger` from `src/lib/logger.ts`, never `console.log`.
- Error handling: return `Result<T, E>` types, don't throw exceptions in
  service layer code. See `src/lib/result.ts` for the type definition.
- Validation: use Zod schemas. Define them in the same file as the route handler.
- Database: always go through the service layer. Never import Prisma directly
  in route handlers or components.
- Naming: camelCase for functions/variables, PascalCase for types/components,
  SCREAMING_SNAKE_CASE for constants. File names are kebab-case.
```

Point Claude at existing examples when asking for new code:

```
Add a new API route for listing invoices. Follow the same pattern as
src/app/api/orders/route.ts — same validation approach, error handling,
and response format.
```

When Claude writes code that doesn't match your conventions, correct it and then update CLAUDE.md so it doesn't happen again:

```
That's close, but we use our custom Result type for error handling here,
not try/catch. See src/services/order-service.ts for the pattern.

Also, I'm adding a note about this to CLAUDE.md so it gets it right next time.
```

## Ignoring Claude's Uncertainty Signals

**What it looks like:** Claude says something like "I believe this API accepts a `format` parameter, but you may want to verify in the documentation" and you skip the verification step. Or Claude hedges with "this should work, though I'm not certain about the behavior when the input is empty" and you deploy without testing that case.

Later, the API doesn't accept a `format` parameter. Or the empty input case throws an unhandled exception in production.

**Why it happens:** Two complementary biases at work. First, developers under time pressure treat hedging language as boilerplate — just Claude being politely cautious. Second, when you've seen Claude be right ten times in a row, you start assuming the eleventh time is no different.

**How to avoid it:**

Treat Claude's hedging language as actionable information, not filler. Common signals and what to do:

| Claude says                       | What it means                          | What to do                             |
| --------------------------------- | -------------------------------------- | -------------------------------------- |
| "I believe..." / "I think..."     | Genuine uncertainty about a fact       | Verify in documentation or source code |
| "You may want to verify..."       | Something is unverifiable from context | Actually verify it                     |
| "This should work..."             | Untested reasoning                     | Test it                                |
| "I'm not sure about the exact..." | Specific knowledge gap                 | Look it up                             |
| "Based on my understanding..."    | Possibly outdated information          | Check for current behavior             |

Be equally wary of the opposite: confident-sounding statements about things Claude can't actually know. Claude may state with apparent confidence:

- What an external API returns (it may be remembering an older version)
- How a library behaves in edge cases (it may be extrapolating)
- What your production environment configuration looks like (it's guessing)

When Claude makes claims about external APIs, library behavior, or runtime characteristics, verify them — regardless of how confident Claude sounds. Claude's confidence level does not correlate reliably with correctness for these categories.

```
# After Claude suggests an API call, verify the specifics
Can you show me where in the codebase we've used this API endpoint before?
If we haven't, I'll check the API docs before we proceed.
```

## Asking for Too Much at Once

**What it looks like:** You give Claude a prompt like:

```
Refactor the user service to use the new database layer, add pagination
support to all list endpoints, update the tests, add the new filtering
options from the PRD, and make sure the OpenAPI docs are updated.
```

Claude produces a large changeset. Some parts are right, some are half-finished, and some misinterpret the requirements. The pagination works but the filtering is wrong. The tests are updated for the refactor but don't cover the new filtering. The OpenAPI docs are partially updated.

You now have a messy diff that's hard to review, hard to partially accept, and hard to roll back.

**Why it happens:** Claude tries to address everything in one pass. With multiple competing concerns, it makes trade-offs and compromises without telling you. It may also lose track of earlier requirements as it works through later ones — especially if the combined task pushes against context limits.

**How to avoid it:**

For features with a PRD or spec, use the spec-driven workflow: point Claude at the spec in plan mode, let it propose the staged decomposition, and implement one stage at a time with reviews between stages. Claude does the decomposition work — you don't need to manually break it into prompts. See [Prompting Strategies](03-prompting-strategies.md) and [Implementation Patterns](05-implementation-patterns.md) for this workflow.

```
Read the user service overhaul spec in docs/specs/user-service-v2.md.
Propose a staged implementation plan. Each stage should be reviewable
and testable independently.
```

Claude proposes stages (refactor data layer → add pagination → add filtering → update docs), you review and adjust, then it implements stage by stage.

For ad-hoc tasks without a spec, keep each prompt focused on one concern:

```
Refactor the user service to use the new database layer.
Don't change any endpoint behavior — just swap the data access code.
The existing tests should still pass.
```

**How to judge if a task needs staging:** If you can't describe "done" in one or two sentences, it needs a plan. Other signals:

- The task involves more than 3-4 files
- It mixes refactoring with new features
- It requires multiple unrelated design decisions
- You'd break it into multiple tickets in a sprint

**The exception:** If the task is genuinely atomic — all the pieces must change together or nothing works — then a single prompt is fine. A database migration plus the service layer changes plus the type updates often need to happen together. But "together" is different from "together with three other unrelated features."

## Not Using Plan Mode for Complex Changes

**What it looks like:** You ask Claude to implement a complex feature and it starts writing code immediately. Three files in, you realize it's building on an approach you wouldn't have chosen — maybe it's adding a new database table when you'd prefer to extend an existing one, or it's using polling when you'd want WebSockets. Now you have to either accept the suboptimal approach or throw away the work and start over.

**Why it happens:** By default, Claude jumps into implementation because that's usually what people want. For straightforward tasks, this is efficient. But for complex changes, the first approach Claude picks isn't necessarily the best one, and course-correcting after code is written is expensive.

**How to avoid it:**

Use plan mode (Shift+Tab twice from default mode, or `--permission-mode plan`) when:

- The change spans multiple files or modules
- There are meaningful architectural choices to make
- You're working in an unfamiliar part of the codebase
- The task is ambiguous enough that two competent developers might approach it differently
- The wrong approach would be expensive to undo

For features with a PRD, point Claude at the spec in plan mode:

```
Read the notification system spec at docs/specs/notifications.md.
Propose a staged implementation plan considering our existing architecture.
```

For ad-hoc complex work without a spec, describe the scope and ask for a plan:

```
Plan how to add real-time notifications to the order tracking system.
Consider:
- Where does the notification logic live?
- How do we deliver notifications to the client? (WebSocket, SSE, polling)
- What changes to the database schema, if any?
- How does this interact with the existing email notification system?

Don't write code yet — just outline the approach.
```

Either way, review the plan. Push back on parts you disagree with. Ask about alternatives:

```
I'd rather use SSE than WebSockets here since we only need server-to-client.
How would that change the plan?
```

Once you've aligned on the approach, then move to implementation. Claude implements stage by stage, pausing for review between each one.

This plan-then-implement approach — whether driven by a PRD or an ad-hoc description — adds a few minutes upfront but avoids the scenario where you throw away 20 minutes of Claude's work because the approach was wrong.

**Quick reference for when to plan vs. just implement:**

| Scenario                                          | Mode           |
| ------------------------------------------------- | -------------- |
| Fix a bug with a clear cause                      | Just implement |
| Add a field to an existing form                   | Just implement |
| Build a new feature spanning multiple services    | Plan first     |
| Refactor a module's architecture                  | Plan first     |
| Anything where you'd sketch on a whiteboard first | Plan first     |
| You're not sure where the code should live        | Plan first     |

## See Also

- [Context Management](02-context-management.md) — Strategies for managing Claude's context window effectively
- [Prompting Strategies](03-prompting-strategies.md) — Writing clear, focused prompts that get better results
- [Implementation Patterns](05-implementation-patterns.md) — Proven patterns for building features with Claude Code
