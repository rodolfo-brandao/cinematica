# Subagents

A `code-reviewer` agent is configured in `.claude/agents/code-reviewer.md`.
It performs quality, security, and best-practices review of changed
files, grouping findings by severity (critical / major / minor). It is
read-only (`Read`, `Grep`, `Glob`).

A `git-ops` agent is configured in `.claude/agents/git-ops.md`. It
handles basic Git operations — commit, push, and pull — writing
meaningful, logically-split commit messages and always using the
machine's configured Git identity (never hardcoded). It never
force-pushes or discards work without explicit confirmation, and it adds
no `Co-Authored-By` trailer.