# Code Review and Quality

## Overview

Claude Code can serve as a thorough, tireless code reviewer that catches bugs, security issues, and standards violations before they reach your team's PR queue. This document covers patterns for automated review, enforcing project-specific standards, security-focused analysis, and building quality gates that run continuously as you develop. These techniques work best when combined — standards in CLAUDE.md inform reviews, hooks enforce checks automatically, and custom commands codify your team's review process.

## Automated Code Review

The simplest way to use Claude for code review is to ask it to review changes before you open a pull request. This catches issues when they are cheapest to fix.

### Reviewing Staged Changes

From within a Claude Code session, you can ask Claude to review what you are about to commit:

```
Review my staged changes for bugs, security issues, and anything that
deviates from our project conventions. Pay close attention to error
handling and edge cases.
```

Claude has access to the `Bash` tool and will run `git diff --cached` to see your staged changes, then examine the surrounding code for context.

### Reviewing a Full Branch Diff

For a broader review before opening a PR, ask Claude to compare your branch against main:

```
Review the full diff between this branch and main. Focus on:
- Logic errors and off-by-one mistakes
- Missing error handling
- API contract changes that could break clients
- Test coverage gaps for new code paths
```

### Piping Diffs in Headless Mode

You can run reviews non-interactively for scripting or CI use:

```bash
git diff main...HEAD | claude --print \
  "Review this diff for bugs, security issues, and style problems. \
   Our conventions: we use early returns, avoid nested ternaries, \
   and require error handling on all async operations."
```

### Making Reviews Effective

Generic "review this code" prompts produce generic feedback. Provide context about what matters in your project:

```
Review this diff. Context:
- This is a payment processing service — correctness matters more than performance
- We use the Result pattern for error handling (no throwing in business logic)
- All database operations must go through the repository layer
- Public API responses must not leak internal field names
```

The more specific your review criteria, the more useful the feedback. Claude will not waste your time pointing out subjective style preferences if you tell it what actually matters.

## Enforcing Project Standards

The most effective way to maintain consistency is to put your standards in CLAUDE.md so Claude applies them in every interaction — both when writing code and when reviewing it.

### Defining Standards in CLAUDE.md

```markdown
# Coding Standards

## Naming Conventions
- React components: PascalCase (`UserProfile`, not `userProfile`)
- Hooks: camelCase prefixed with `use` (`useAuth`, `usePagination`)
- Constants: UPPER_SNAKE_CASE for true constants, camelCase for derived values
- Database columns: snake_case — the ORM maps to camelCase in application code

## Error Handling
- Use `Result<T, E>` for all service-layer functions — never throw from business logic
- Controllers catch errors at the boundary and map to HTTP status codes
- Always include a correlation ID in error logs
- Never swallow errors silently — at minimum, log and re-throw

## Import Ordering
1. Node.js built-ins (`node:fs`, `node:path`)
2. External packages (`express`, `zod`)
3. Internal aliases (`@/services`, `@/models`)
4. Relative imports (`./utils`, `../shared`)
- Blank line between each group

## Test Structure
- One test file per module, colocated: `foo.ts` → `foo.test.ts`
- Use `describe` blocks matching the function/class name
- Test names follow: "should [expected behavior] when [condition]"
- No test should depend on another test's state
```

When these standards are in CLAUDE.md, Claude follows them when generating code and flags violations when reviewing code. You do not need to repeat them in every prompt.

### Reviewing Against Standards

With standards defined, a simple prompt is enough:

```
Review this file against our project standards. Flag any violations
and suggest fixes.
```

Claude will check against the conventions in CLAUDE.md automatically. If it finds violations, it will cite the specific standard and show the corrected code.

### Graduating Standards from Reviews

When you notice Claude repeatedly flagging the same issue in reviews, that is a signal to either:

1. **Add a linter rule** if the check can be automated (import ordering, naming patterns)
2. **Update CLAUDE.md** if the pattern is not yet documented
3. **Create a code snippet/template** if the pattern is complex (error handling boilerplate, test setup)

Over time, the number of review findings should decrease as standards become enforced earlier in the workflow.

## Security Review Patterns

Claude is effective at spotting common security vulnerabilities, especially when you direct its attention to specific threat categories.

### OWASP-Focused Review

```
Review this API endpoint for OWASP top 10 vulnerabilities. Specifically check:
- Injection flaws (SQL, NoSQL, command injection)
- Broken authentication or session management
- Sensitive data exposure in responses or logs
- Missing rate limiting or input validation
- Security misconfiguration
```

### Targeted Security Reviews

For specific concern areas, narrow the review scope:

**SQL Injection:**
```
Review all database queries in src/repositories/ for SQL injection
vulnerabilities. Check that every query uses parameterized statements
and that no user input is concatenated into query strings.
```

**Authentication and Authorization:**
```
Review the authentication flow in src/auth/. Check for:
- Token expiration and refresh handling
- Secure password hashing (bcrypt with sufficient rounds)
- Authorization checks on every protected route (not just authentication)
- CSRF protection on state-changing endpoints
- Secure cookie settings (httpOnly, secure, sameSite)
```

**Secrets and Configuration:**
```
Scan the codebase for hardcoded secrets, API keys, or credentials.
Check that all sensitive values come from environment variables and
that .env files are in .gitignore. Also check for sensitive data
in log statements.
```

### Security Review for Specific Changes

When reviewing a PR that touches security-sensitive areas, combine the diff review with targeted checks:

```
This PR modifies our authentication middleware. Review the changes and also:
1. Check that the JWT validation is complete (signature, expiration, issuer)
2. Verify that role-based access control is enforced, not just authentication
3. Look for any timing vulnerabilities in token comparison
4. Confirm error messages don't leak information about valid usernames
```

### Limitations

Claude is good at spotting common vulnerability patterns in code it can see, but it cannot replace a full security audit. It does not analyze running infrastructure, test for configuration issues in deployment environments, or verify cryptographic implementations at a mathematical level. Use Claude's security reviews as one layer in a defense-in-depth approach, not as the only layer.

## Using Skills and Hooks for Quality Gates

Hooks let you run automated checks every time Claude edits a file, catching problems immediately rather than during later review.

### Post-Edit Linting with Hooks

Configure a hook in `.claude/settings.json` that runs your linter after Claude edits any file:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'npx eslint --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null || true'"
      }
    ]
  }
}
```

This runs ESLint with auto-fix on every file Claude writes or edits. The `|| true` prevents hook failures from interrupting the workflow for non-critical lint issues.

### Running Tests After Changes

For a tighter feedback loop, run relevant tests after code changes:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'if [[ \"$CLAUDE_FILE_PATH\" == *.ts ]]; then npx jest --findRelatedTests \"$CLAUDE_FILE_PATH\" --passWithNoTests 2>&1 | tail -5; fi'"
      }
    ]
  }
}
```

This runs only the tests related to the changed file, keeping the feedback loop fast. Claude sees the test output and can fix failures immediately.

### Type Checking After Edits

For TypeScript projects, run the type checker to catch type errors as they are introduced:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'if [[ \"$CLAUDE_FILE_PATH\" == *.ts ]]; then npx tsc --noEmit --pretty 2>&1 | head -20; fi'"
      }
    ]
  }
}
```

### Combining Multiple Checks

You can chain multiple quality checks in a single hook:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "bash -c 'FILE=\"$CLAUDE_FILE_PATH\"; if [[ \"$FILE\" == *.ts ]]; then echo \"--- Lint ---\" && npx eslint --fix \"$FILE\" 2>&1 | tail -3; echo \"--- Types ---\" && npx tsc --noEmit 2>&1 | grep error | head -5; fi'"
      }
    ]
  }
}
```

### When to Use Hooks vs. Manual Checks

**Use hooks for:**
- Fast checks (linting, formatting) that complete in under a few seconds
- Checks that should always run — no exceptions
- Feedback that helps Claude self-correct during a session

**Use manual prompts for:**
- Expensive checks (full test suites, integration tests)
- Judgment calls that require context (architecture review, design feedback)
- One-time reviews before opening a PR

## Review Checklists

Custom slash commands let you codify your team's review process into reusable, consistent checklists.

### Creating a Review Command

Create `.claude/commands/review.md`:

```markdown
Review the current staged changes (or the full branch diff from main if nothing is staged) against this checklist:

## Correctness
- [ ] No logic errors, off-by-one mistakes, or incorrect conditions
- [ ] Edge cases handled (empty inputs, null values, boundary conditions)
- [ ] Error handling is complete — no unhandled promise rejections or swallowed errors
- [ ] Concurrent access is safe where applicable (race conditions, deadlocks)

## Tests
- [ ] New code paths have corresponding tests
- [ ] Tests cover both success and failure cases
- [ ] No tests that always pass (check assertions are meaningful)
- [ ] Test descriptions clearly state what is being tested

## Security
- [ ] User input is validated and sanitized
- [ ] No SQL injection, XSS, or command injection vectors
- [ ] Authentication and authorization checks are present where needed
- [ ] Sensitive data is not logged or exposed in responses

## Performance
- [ ] No N+1 query patterns
- [ ] Large data sets are paginated
- [ ] No unnecessary blocking operations in async code
- [ ] Database queries use appropriate indexes (check query plans if unsure)

## Documentation
- [ ] Public API changes are reflected in documentation
- [ ] Complex logic has explanatory comments (why, not what)
- [ ] Breaking changes are called out clearly

For each item, mark it as passing, failing (with explanation), or not applicable. Provide a summary at the end with the most important findings.
```

Run it with `/project:review` in any Claude Code session.

### Domain-Specific Review Commands

Create specialized review commands for different areas of your codebase:

**`.claude/commands/review-api.md`** for API endpoint reviews:

```markdown
Review the current changes focused on API quality:

1. **Contract**: Do request/response schemas match the API documentation?
   Check for missing fields, incorrect types, or undocumented changes.
2. **Validation**: Is all input validated before processing? Check path
   params, query params, headers, and request bodies.
3. **Error Responses**: Do error responses follow our standard format?
   Are HTTP status codes correct? Do error messages help the caller
   without leaking internals?
4. **Backward Compatibility**: Will this change break existing clients?
   Check for removed fields, changed types, or new required parameters.
5. **Rate Limiting**: Are new endpoints covered by rate limiting?
6. **Authorization**: Does every endpoint check permissions, not just
   authentication?
```

**`.claude/commands/review-migration.md`** for database migration reviews:

```markdown
Review the database migration in the current changes:

1. **Reversibility**: Is there a down migration? Does it fully reverse
   the up migration?
2. **Data Safety**: Could this migration lose data? Check for column
   drops, type changes, and constraint additions on populated tables.
3. **Lock Duration**: Will this migration lock tables? For large tables,
   check if the operation can run without blocking reads/writes.
4. **Index Impact**: Are new indexes needed for new columns or query
   patterns? Will new indexes cause slow migration on large tables?
5. **Default Values**: Do new non-nullable columns have appropriate
   defaults or a backfill strategy?
```

### Parameterized Review Commands

You can create commands that accept arguments using the `$ARGUMENTS` placeholder:

**`.claude/commands/review-file.md`**:

```markdown
Perform a thorough review of $ARGUMENTS. Read the file, then:

1. Check it against our project standards in CLAUDE.md
2. Look for bugs, edge cases, and error handling gaps
3. Assess test coverage — find the corresponding test file and check
   whether all code paths are tested
4. Suggest specific improvements with code examples

Be direct. Skip praise. Focus on actionable findings.
```

Usage: `/project:review-file src/services/payment.ts`

## See Also

- [Testing and Debugging](06-testing-and-debugging.md) — Testing strategies that complement code review
- [CI/CD and Automation](08-cicd-and-automation.md) — Automate reviews in your CI pipeline
- [Project Setup](01-project-setup.md) — Configure CLAUDE.md where your standards live
