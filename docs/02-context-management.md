# Context Management

Claude Code operates within a finite context window — the total amount of text Claude can "see" at once. On large codebases, managing this window is the difference between Claude staying sharp through a complex task and Claude losing track of what it was doing halfway through. This guide covers practical techniques for keeping context under control.

## How the Context Window Works

Every conversation with Claude has a context window measured in tokens (roughly 3/4 of a word per token). Everything in the conversation counts toward this limit: your prompts, Claude's responses, file contents Claude reads, tool outputs, and the CLAUDE.md file loaded at the start.

Here is what makes context management critical on large codebases:

- **Tool results are often large.** A single file read can add hundreds or thousands of lines. A grep across a big directory can return pages of results. A test run might dump a full stack trace. Each of these consumes context that cannot be reclaimed.
- **Context is cumulative.** The fifth file Claude reads sits on top of the first four. By mid-task, Claude may have consumed most of its window just on research.
- **When context fills up, Claude loses earlier information.** The auto-compaction mechanism summarizes older parts of the conversation to make room, but summarization is lossy. Specific details — exact line numbers, variable names, error messages — can be lost in the summary.

The practical implication: you need to be intentional about what goes into the context window and when to reset it.

## Keeping CLAUDE.md Concise

The CLAUDE.md file is loaded into every single conversation. A 500-line CLAUDE.md means every conversation starts with 500 lines of context already consumed, whether or not that information is relevant to the task at hand.

### Guidelines

- **Target under 200 lines.** This is not a hard limit, but if your CLAUDE.md is significantly longer, you are almost certainly including things that do not belong there.
- **Link instead of embedding.** Instead of pasting your entire API design guide into CLAUDE.md, write "API design conventions are documented in docs/api-conventions.md — read it when working on API routes." Claude will read the file when it needs it, and only when it needs it.
- **Focus on action, not explanation.** "Use Zod for validation" is better than a paragraph explaining what Zod is and why the team chose it.
- **Use nested CLAUDE.md files for package-specific details.** The root CLAUDE.md should contain only what applies to every task in the repo. Package-specific build commands, conventions, and gotchas belong in a CLAUDE.md inside that package directory.

### Before and After

**Too verbose (root CLAUDE.md):**

```markdown
## API Error Handling

We use a custom error handling system based on the AppError class defined in
packages/shared/src/errors.ts. This class extends the native JavaScript Error
class and adds a `code` property (string enum), a `statusCode` property (HTTP
status code), and an optional `details` property (arbitrary metadata).

When throwing errors in route handlers, always use a specific AppError subclass
rather than the base AppError. Available subclasses include:
- NotFoundError (404) — use when a requested resource doesn't exist
- ValidationError (400) — use when request data fails validation
- AuthenticationError (401) — use when the user is not authenticated
- AuthorizationError (403) — use when the user lacks permission
[... 30 more lines ...]
```

**Concise (root CLAUDE.md):**

```markdown
## Error Handling
- Throw AppError subclasses (NotFoundError, ValidationError, etc.), never raw Error
- Error classes defined in packages/shared/src/errors.ts — read that file for the full list
```

The concise version gives Claude enough to follow the convention. If Claude needs the full error class hierarchy, it can read the source file, and that cost is only paid when relevant.

## Using .claudeignore Effectively

The `.claudeignore` file prevents Claude from reading or searching through files that match the specified patterns. This matters for context management in two ways:

1. **Prevents accidental reads.** If Claude is exploring the codebase and encounters a 10,000-line generated file, reading it wastes a massive amount of context for zero value.
2. **Reduces search noise.** When Claude greps for a pattern, matches in generated or vendored files produce irrelevant results that consume context and distract from the actual code.

### High-Impact Patterns to Exclude

| Pattern                               | Why                                               |
| ------------------------------------- | ------------------------------------------------- |
| `node_modules/`                       | Thousands of files, never relevant to edit        |
| `dist/`, `build/`, `.next/`           | Generated output, not source of truth             |
| `*.min.js`, `*.min.css`               | Minified code is unreadable and huge              |
| `*.pb.ts`, `src/generated/`           | Generated code that should not be manually edited |
| `package-lock.json`, `pnpm-lock.yaml` | Lock files can be tens of thousands of lines      |
| `*.sql.gz`, `fixtures/large/`         | Large data files that consume context quickly     |
| `coverage/`                           | Test coverage reports, not useful for development |

Lock files deserve special attention. A `package-lock.json` in a mid-size project can easily be 20,000+ lines. If Claude reads it — even partially — that is a significant chunk of context spent on content that is almost never useful.

## When to Start Fresh vs. Continue

One of the most impactful context management decisions is knowing when to start a new conversation versus continuing the current one.

### Start a New Conversation When:

- **You are switching tasks.** If you just finished implementing a feature and now want to fix an unrelated bug, start fresh. The feature implementation context is just dead weight for the bug fix.
- **Context has been heavily compacted.** If you see the "conversation was compacted" indicator multiple times, Claude has lost the specifics of earlier work. Starting fresh with a clear prompt often gets better results than working on top of lossy summaries.
- **Claude seems confused or repetitive.** If Claude is re-reading files it already read, contradicting earlier statements, or going in circles, the context has likely degraded. A fresh start with a clear problem statement is faster than debugging Claude's confusion.
- **The task is done.** Do not reuse a conversation for "one more thing" after a task is complete. The completed task's context just adds noise for the new task.

### Continue the Conversation When:

- **You are iterating on the same feature.** "Make that function async instead" or "add error handling to the endpoint we just built" benefits from the existing context.
- **You are debugging a specific issue.** The investigation builds on itself — each test run, log check, and code read narrows the problem. Starting over would mean re-reading all the same files.
- **Claude has important state.** If Claude has built up an understanding of a complex system through multiple file reads and you are still working within that system, preserving the context is valuable.
- **You are reviewing Claude's work.** "Actually, use a different approach for the validation" is better as a continuation than re-explaining the entire task in a new conversation.

### The General Rule

When in doubt, err toward starting fresh. A new conversation with a well-written prompt is almost always better than a continuation in degraded context. Conversations are cheap; bad context leads to bad output.

## Compact Mode and Summarization

The `/compact` command summarizes the current conversation, replacing the full history with a condensed version. This frees up context window space while preserving the key information Claude needs to continue working.

### How It Works

When you run `/compact` (or when auto-compaction triggers), Claude reviews the conversation history and produces a summary that captures:

- What task is being worked on
- What has been done so far
- What files have been modified
- Key decisions and their rationale
- What remains to be done

The full conversation is then replaced with this summary, freeing up significant context space.

### When to Use /compact Proactively

- **Before starting a new sub-task within the same conversation.** If you have been debugging and now want to implement the fix, compact first. The debugging details are no longer needed — just the conclusion.
- **After a large research phase.** If Claude just read 15 files to understand how the auth system works, compact before asking it to make changes. The summary will capture the understanding without keeping all the raw file contents.
- **When you notice the conversation getting long.** If you have been working for a while and the conversation feels like it has accumulated a lot of back-and-forth, compact to keep Claude focused.

### Auto-Compaction

Claude Code automatically triggers compaction when the context window fills to approximately 80-90% capacity. This happens transparently — you will see a brief indicator that compaction occurred. The behavior works well in most cases, but there are two things to be aware of:

1. **Auto-compaction is reactive, not predictive.** It fires when context is nearly full. If Claude is mid-thought on a complex task, the compaction can disrupt its chain of reasoning. Proactive `/compact` at natural break points avoids this.
2. **Compaction is lossy.** The summary is good but not perfect. Specific numbers, exact error messages, and detailed code snippets may be approximated rather than preserved verbatim. If you need Claude to retain a specific detail, restate it after compaction.

### Custom Compaction Prompts

You can pass a focus hint to `/compact`: for example, `/compact focus on the database migration changes`. This biases the summary toward retaining the details you care about and being more aggressive about discarding the rest.

## Subagents and Context Isolation

Claude Code's Task tool (also called subagents) spawns a separate Claude instance with its own context window. The subagent does its work — reading files, running commands, analyzing code — and returns a summary to the main conversation. Only the summary enters the main context, not the full contents of everything the subagent read.

### Why This Matters

Consider a task like: "Refactor all API routes to use the new validation middleware." Claude needs to:

1. Read the new middleware to understand its interface
2. Find all existing routes (maybe 30+ files)
3. Understand each route's current validation approach
4. Modify each route

Without subagents, steps 1-3 would fill a substantial portion of the context window before Claude even starts making changes. With subagents, Claude can delegate the research:

- **Subagent 1:** "Read the validation middleware and summarize its interface and usage patterns"
- **Subagent 2:** "Find all route files and categorize them by their current validation approach"

Each subagent reads as many files as it needs in its own context window. The main conversation receives two concise summaries instead of 30+ full file contents.

### When to Use Subagents

Claude decides when to use the Task tool on its own, but you can influence this by how you phrase your requests. Tasks that benefit from subagent delegation:

- **Research-heavy tasks** — "understand how X works across the codebase" before making changes
- **Multi-file analysis** — "find all places where Y pattern is used" when you expect many matches
- **Comparison tasks** — "compare the implementations in these three services" where each service requires reading several files

You can explicitly ask Claude to use subagents: "Use a subagent to research how the auth middleware works, then update the user routes to use it." This gives Claude permission to spend subagent context freely on research without worrying about consuming the main window.

### Subagent Limitations

- Subagents do not share context with each other. If two subagents need to coordinate, they cannot — the main conversation must do the coordination.
- Subagents can read files and run commands, but the main conversation does not see the raw results. If you need Claude to look at a specific file's exact contents, ask directly rather than through a subagent.
- There is overhead in spawning subagents. For simple tasks (read one file, run one command), a direct approach is faster.

## See Also

- [Project Setup](01-project-setup.md) — configure CLAUDE.md, .claudeignore, and project structure
- [Prompting Strategies](03-prompting-strategies.md) — write prompts that make efficient use of context
- [Common Pitfalls](10-common-pitfalls.md) — mistakes that waste context and how to avoid them
