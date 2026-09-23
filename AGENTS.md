# AGENTS.md

This is a lightweight exercise repository for practicing agentic coding. Favor clear, working changes over production-scale process or abstraction.

## Agent playbook

- Agent tasks should specify the desired outcome, constraints, acceptance criteria, and verification—not implementation instructions.
- Before autonomous implementation, turn ambiguous requirements into explicit decisions, constraints, and testable acceptance criteria. Identify unresolved assumptions before coding.
- Separate planning from execution. An agent should explore the repository, expose assumptions and produce a reviewable implementation plan before being authorized to modify code.
- The agent that implements a change should not be the only reviewer of that change. Use a fresh context or independent reviewer for meaningful verification.

## Working principles

- Understand the existing behavior and conventions before editing.
- Make the smallest coherent change that fully satisfies the request.
- Keep domain logic in `src/` and Telegram-specific behavior in `src/chat/`.
- Keep user-facing text in both `src/locale/en.py` and `src/locale/zh.py`.
- Preserve backward compatibility for persisted data in `data/` when practical.
- Avoid unrelated refactors, new frameworks, and speculative abstractions.
- Never commit secrets, `.env`, logs, PID files, virtual environments, or generated caches.

## Code quality

- Prefer straightforward Python with descriptive names and short functions.
- Validate external input at the domain boundary, not only in command handlers.
- Keep persistence formats readable and changes backward compatible.
- Preserve existing ordering and behavior unless the feature explicitly changes them.
- Log failures with enough context to diagnose them; do not expose secrets to users or logs.
- Add comments only when they explain a non-obvious decision.

## Tests and verification

- Add focused tests for new behavior, validation, persistence, and regressions.
- Use temporary paths and mocks; tests must not modify real files or call external services.
- Run the full suite with:

  ```bash
  venv/bin/python -m pytest -q
  ```

- Run `git diff --check` before finishing.
- Keep tests proportionate to this exercise; extensive production infrastructure is unnecessary.

## Documentation

- Update `/start`, `/help`, Telegram command registration, and the README when commands or user-visible behavior change.
- Keep English and Chinese documentation aligned.
- Document defaults and accepted values where users need them.

## Git hygiene

- Preserve unrelated user changes.
- Use concise commit messages that describe the outcome.
- Do not rewrite history or use destructive Git commands unless explicitly requested.
- Only commit or push when the user asks.
