# Team Workflows

Effective teams don't just use Claude Code individually — they build shared conventions, prompts, and knowledge that make everyone more productive. This guide covers how to establish team-wide practices that compound over time, from shared CLAUDE.md files to custom slash commands that encode institutional knowledge.

When a team aligns on how they use Claude Code, the tool becomes significantly more powerful. New members onboard faster, code reviews are more consistent, and hard-won knowledge persists instead of living in one person's head.

## Shared CLAUDE.md Conventions

CLAUDE.md is version controlled alongside your code. Treat it as living documentation that the whole team maintains — not a personal config file. When CLAUDE.md is well-structured, every team member gets the same high-quality context when working with Claude.

Establish clear sections so team members know where to add information:

```markdown
# CLAUDE.md

## Build & Development
- `npm run dev` — start development server on port 3000
- `npm test` — run full test suite
- `npm run test:unit -- path/to/file` — run tests for a specific file
- `npm run lint` — run ESLint and Prettier checks
- `npm run db:migrate` — run pending database migrations

## Architecture Overview
This is a Next.js 14 app using the App Router. Key structure:
- `src/app/` — routes and page components
- `src/lib/` — shared utilities, database client, auth helpers
- `src/components/` — React components organized by feature
- `src/services/` — business logic layer (not in components)
- `prisma/` — database schema and migrations

API routes follow REST conventions in `src/app/api/`.
Business logic lives in `src/services/`, not in route handlers or components.

## Coding Standards
- Use TypeScript strict mode. No `any` types without a comment explaining why.
- React components use named exports, not default exports.
- Database queries go through the service layer, never called directly from components.
- Error handling: use Result types from `src/lib/result.ts`, not try/catch in business logic.
- Tests: colocate test files next to source (`foo.ts` → `foo.test.ts`).

## Common Gotchas
- The `users` table has soft deletes. Always filter by `deleted_at IS NULL` unless
  you specifically need deleted records. The service layer handles this automatically.
- Auth middleware runs on all `/api/` routes except those in `/api/public/`.
- The `order.total` field is stored in cents, not dollars.
- Never import from `@prisma/client` directly. Use the wrapped client in `src/lib/db.ts`
  which adds logging and soft-delete filtering.

## Deployment
- `main` branch deploys to production automatically via GitHub Actions.
- PRs get preview deployments on Vercel.
- Environment variables are managed in Vercel dashboard (production) and `.env.local` (local).
- Database migrations run automatically on deploy. Never modify a migration after it ships.
```

### Keeping CLAUDE.md Current

Treat CLAUDE.md updates like code changes — include them in PRs when relevant:

- **Adding a new service?** Update the architecture section.
- **Changed the build command?** Update build & development.
- **Hit a weird bug caused by a non-obvious behavior?** Add it to common gotchas.
- **Established a new team convention?** Add it to coding standards.

A good rule of thumb: if you'd tell a new team member about it during pairing, it belongs in CLAUDE.md.

### Layered CLAUDE.md for Monorepos

For larger projects, use CLAUDE.md files at multiple levels:

```
repo-root/
├── CLAUDE.md              # Repo-wide: monorepo tooling, shared conventions
├── packages/
│   ├── api/
│   │   └── CLAUDE.md      # API-specific: route patterns, auth, middleware
│   ├── web/
│   │   └── CLAUDE.md      # Frontend-specific: component patterns, state management
│   └── shared/
│       └── CLAUDE.md      # Shared library: what it exports, versioning rules
```

Claude reads all CLAUDE.md files from the root to the current working directory, so information naturally layers — specific context builds on top of general context.

## Onboarding New Team Members

Claude Code dramatically accelerates onboarding when CLAUDE.md and the codebase are well-organized. Instead of spending days tracing code paths, new developers can have a guided conversation with the codebase.

### Effective Onboarding Questions

New team members can ask Claude questions like these right away:

```
How does the authentication system work? Walk me through a login request
from the frontend to the database.
```

```
Where are API routes defined and what middleware runs on them?
```

```
How does the billing service calculate subscription renewals?
Show me the relevant code.
```

```
What's the testing strategy for this project? Show me an example of a
well-written test file.
```

The quality of Claude's answers depends directly on two things:

1. **CLAUDE.md quality** — If your architecture overview explains where things live and why, Claude gives accurate, contextualized answers instead of generic guesses.
2. **Codebase organization** — Clear naming, consistent patterns, and good directory structure help Claude navigate and explain the code.

### Creating an Onboarding Slash Command

Encode your onboarding flow as a custom command so new team members get a consistent experience:

```markdown
<!-- .claude/commands/onboard.md -->
Give me an onboarding walkthrough of this codebase. Cover:

1. High-level architecture: what are the main components and how do they interact?
2. How to run the project locally (build, test, dev server)
3. The directory structure and where to find things
4. Key patterns and conventions the team uses
5. How a typical feature gets built, from route to database

Keep explanations concrete — reference specific files and functions.
After the overview, ask me what area I'd like to explore deeper.
```

A new developer runs `/onboard` and gets a tailored walkthrough based on the actual codebase, not outdated wiki pages.

## Consistent Prompting Patterns

When someone on the team discovers an effective prompt pattern, share it. The best mechanism is custom slash commands in `.claude/commands/`, which are version controlled and available to everyone who clones the repo.

### Team Review Command

```markdown
<!-- .claude/commands/review.md -->
Review the staged changes (git diff --cached) against our team standards:

**Correctness**
- Does the logic handle edge cases? Check for null/undefined, empty arrays, boundary values.
- Are database queries filtering soft-deleted records appropriately?
- Do error paths return proper Result types, not thrown exceptions?

**Style & Conventions**
- Named exports for React components (no default exports).
- Business logic in services, not in route handlers or components.
- TypeScript strict: no untyped `any` without a justifying comment.

**Testing**
- Are new functions covered by tests?
- Do tests follow the existing patterns (colocated, using our test helpers)?

**Security**
- Are user inputs validated before reaching the service layer?
- Do new API routes have appropriate auth middleware?

Flag issues by severity: 🔴 must fix, 🟡 should fix, 🟢 suggestion.
```

### Feature Implementation from Specs

For teams that work from PRDs or feature specs, encode the spec-to-implementation workflow:

```markdown
<!-- .claude/commands/implement-spec.md -->
Read the feature spec at: $ARGUMENTS

Before writing any code:
1. Read and understand the full scope from the spec
2. Explore the codebase to understand existing patterns that apply
3. Propose a staged implementation plan — each stage independently
   reviewable and testable
4. Flag any ambiguities or gaps in the spec
5. Wait for plan approval before implementing

After approval, implement one stage at a time. Run tests after each stage.
Pause for review between stages.
```

This gives the team a consistent workflow: write a spec, run `/project:implement-spec docs/specs/feature-name.md`, review the plan, then let Claude implement stage by stage. The spec carries the big picture so individual stages stay coherent.

For smaller features that don't have a formal spec:

```markdown
<!-- .claude/commands/implement-feature.md -->
I need to implement the following feature: $ARGUMENTS

Before writing any code, create a plan:
1. Which existing files need to change?
2. What new files need to be created?
3. What's the data flow from the user action to the database and back?
4. What tests should be written?

Present the plan and wait for my approval before implementing.
Follow our project conventions in CLAUDE.md.
```

### Test Generation Command

```markdown
<!-- .claude/commands/add-tests.md -->
Write tests for: $ARGUMENTS

Follow these project conventions:
- Colocate test files next to the source file.
- Use our test helpers from `src/lib/test-utils.ts` for database setup/teardown.
- Name test files as `[source-name].test.ts`.
- Structure tests with describe blocks matching the function/component name.
- Test the happy path first, then edge cases, then error cases.
- For service layer tests, mock the database client from `src/lib/db.ts`.
- For API route tests, use our `createTestRequest` helper.

Look at existing test files nearby for patterns to follow.
```

### Sharing and Evolving Commands

Treat `.claude/commands/` like a shared toolbox:

- **Add commands through PRs** so the team can review and refine them.
- **Include comments** explaining when to use each command.
- **Iterate based on feedback** — if a command's output consistently needs manual adjustment, update the command.
- **Keep commands focused** — a command that tries to do everything does nothing well.

## Knowledge Sharing Through Commands and Memory

The combination of `.claude/commands/` and CLAUDE.md creates a persistent knowledge base that grows smarter over time. When you solve a hard problem, encode that knowledge so Claude handles similar situations better in the future.

### Pattern: Solving a Problem, Then Teaching Claude

Suppose your team spent hours debugging an issue where Prisma's `findMany` returned stale data because of connection pooling in serverless environments. After fixing it:

**Step 1:** Add the context to CLAUDE.md:

```markdown
## Common Gotchas
...
- Prisma connection pooling in serverless: always use the `prismaClient` from
  `src/lib/db.ts`, which configures the connection pool for serverless. Do not
  instantiate `new PrismaClient()` directly — this causes connection exhaustion
  and stale reads under concurrent Lambda invocations.
```

**Step 2:** If it's a recurring workflow, make a command:

```markdown
<!-- .claude/commands/debug-db.md -->
Help me debug a database-related issue: $ARGUMENTS

Check these common causes first:
1. Are we using the shared Prisma client from `src/lib/db.ts`?
   (Direct `new PrismaClient()` causes connection issues in serverless.)
2. Is soft-delete filtering applied? Check for `deleted_at` conditions.
3. Are we inside a transaction where we need to be, or outside one where we shouldn't be?
4. Check for N+1 queries — are we using `include` where needed?

Look at the relevant service file and its tests to understand the expected behavior.
```

Now the entire team benefits from that debugging session — Claude will check for the connection pooling issue first when anyone reports stale database reads.

### Building Institutional Knowledge Incrementally

Good CLAUDE.md files aren't written in one sitting. They accumulate knowledge over time:

```
Week 1:  Basic build commands and project structure
Week 3:  Added coding standards after first few PR reviews revealed inconsistencies
Week 6:  Added gotchas section after a production bug caused by soft-delete oversight
Week 10: Added architecture decisions after onboarding a new team member revealed gaps
Week 15: Added deployment notes after a migration ordering issue
```

Make it a team habit: when a PR fixes a non-obvious bug, ask "should we add something to CLAUDE.md so Claude catches this pattern in the future?"

## Code Review with Claude Across a Team

Claude Code is an effective first-pass reviewer, but establishing clear team norms about its role prevents both over-reliance and under-utilization.

### The Two-Pass Review Model

**Pass 1 — Claude (automated or manual):**
- Style and convention compliance
- Common bug patterns (null checks, off-by-one, resource cleanup)
- Security basics (input validation, auth checks, SQL injection)
- Test coverage gaps
- Documentation consistency

**Pass 2 — Human reviewer:**
- Architectural fit (does this belong here? is this the right abstraction?)
- Business logic correctness (does this match the requirements?)
- Design trade-offs (performance vs. readability, flexibility vs. simplicity)
- Cross-cutting concerns (how does this interact with other features?)
- Naming and API design (will this make sense to future developers?)

### Setting Up Claude-Assisted PR Review

Create a CI step or a team slash command for PR review:

```markdown
<!-- .claude/commands/pr-review.md -->
Review the changes in this PR (use git diff against the base branch).

Focus on:
1. **Bugs**: logic errors, missing edge cases, race conditions
2. **Security**: input validation, auth, data exposure
3. **Conventions**: does this follow our patterns in CLAUDE.md?
4. **Tests**: are the changes adequately tested?

Do NOT comment on:
- Subjective style preferences already handled by our linter
- Minor naming choices unless genuinely confusing
- Things that are clearly intentional design decisions

Format findings as a list with severity and file location.
```

### Team Norms Worth Establishing

Document these decisions so the team stays aligned:

- **"Claude reviewed" is not "reviewed."** Claude's review is a tool for the human reviewer, not a substitute. PRs still need human approval.
- **Use Claude review to prepare for human review.** Authors can run `/pr-review` before requesting human review to catch obvious issues early, making the human reviewer's job easier.
- **Don't argue with Claude's review in the PR.** If Claude flags something that's actually fine, either fix the review command to be smarter or just move on. The human reviewer makes the call.
- **Share review findings.** If Claude consistently catches a particular mistake, add a note to CLAUDE.md so it helps prevent the issue at authoring time, not just review time.

## See Also

- [Project Setup](01-project-setup.md) — Setting up CLAUDE.md and project configuration from scratch
- [CI/CD and Automation](08-cicd-and-automation.md) — Integrating Claude Code into automated pipelines, including PR review
- [Prompting Strategies](03-prompting-strategies.md) — Writing effective prompts and building custom slash commands
