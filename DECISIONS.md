# DECISIONS.md

Decision and change log for this repo.

## Format
- Date - Title
- Context
- Decision
- Consequences

## 2026-01-15 - Create continuity docs (AGENTS/DECISIONS/PROJECT_CONTEXT)
Context: The user requested persistent context across chats and explicit continuity tracking.
Decision: Add AGENTS.md, DECISIONS.md, and PROJECT_CONTEXT.md and maintain them on every Codex change.
Consequences: All future edits must update these docs to stay in sync.

## 2026-01-15 - Add detailed rules reference in Rules folder
Context: The Rules folder contains the official rulebook PDF and an online-game source repo; the user requested a detailed rules doc.
Decision: Create `Rules/Secret_Hitler_Rules_Detailed.md` as a precise rules reference derived from the PDF.
Consequences: Future rule updates should modify this file and keep it in sync with the official rulebook.

## 2026-01-15 - Normalize game tokens and rules enforcement
Context: Core logic compared English tokens against Farsi card data, and several rule/robustness gaps existed.
Decision: Introduce canonical role/policy/action constants, align logic and callbacks, enforce single-use inspections, shuffle before chaos, and add stats/logs robustness.
Consequences: Localization is now consistent across rules logic, tests reflect Farsi output, and stats/log files are auto-managed.

## 2026-01-15 - Add runtime version reporting
Context: Need to identify the exact running build/version on Fly.io deployments.
Decision: Add `/version` command that reports `APP_VERSION`, `GIT_SHA` (or `SOURCE_VERSION`/`GITHUB_SHA`), and optionally `FLY_IMAGE_REF`; include a Docker build arg to populate `GIT_SHA`.
Consequences: Operators can see the running build from the bot, and deployments can surface commit IDs.

## 2026-01-15 - Improve compatibility and ping output
Context: `python-telegram-bot==12.8` is not a good match for Python 3.13, and `/ping` exposed a stale version string.
Decision: Downgrade the Docker base image to Python 3.10 and simplify `/ping` to a plain "pong"; add `/ping` to help and docs.
Consequences: Runtime is more compatible with the bot's Telegram library, and versioning is centralized in `/version`.

## 2026-01-15 - Stabilize tests with Mockbot
Context: `ptbtest.Mockbot` lacks a `request` attribute expected by `telegram.ext.Updater`.
Decision: Add a minimal `request` stub in test setup to satisfy `Updater` initialization.
Consequences: Unit tests can run without modifying external dependencies.

## 2026-01-15 - Patch Mockbot for User signature
Context: `ptbtest.Mockbot.getMe` uses an old `telegram.User` constructor signature and fails on PTB 12.8.
Decision: Patch `getMe` per test instance to provide the required `is_bot` argument.
Consequences: Test suite is compatible with current `python-telegram-bot`.

## 2026-01-15 - Patch ptbtest helpers for polling
Context: `ptbtest` helpers lack `delete_webhook` and still use the old `telegram.User` signature.
Decision: Add a `delete_webhook` stub on `Mockbot` and patch `UserGenerator.get_user` in tests to pass `is_bot`.
Consequences: Updater polling can run in tests without thread failures.

## 2026-01-15 - Patch MessageGenerator user creation
Context: `ptbtest.MessageGenerator` owns its own `UserGenerator`, which still used the old `telegram.User` signature.
Decision: Patch `MessageGenerator.ug.get_user` in test setup to pass `is_bot`.
Consequences: Message generation works under PTB 12.8 during tests.

## 2026-01-15 - Make tests synchronous
Context: Polling threads in `Updater.start_polling` caused timeouts and webhook calls in tests.
Decision: Use `dispatcher.process_update` directly instead of polling and `insertUpdate`.
Consequences: Tests run deterministically without background threads.

## 2026-01-15 - Ensure command entities in tests
Context: `CommandHandler` requires `bot_command` entities; ptbtest messages defaulted to none.
Decision: Pass `parse_mode="Markdown"` in test messages to generate command entities.
Consequences: Command handlers fire in tests.

## 2026-01-15 - Patch UserGenerator globally in tests
Context: `ChatGenerator` creates new `UserGenerator` instances internally, bypassing instance-level patches.
Decision: Override `UserGenerator.get_user` at the class level to pass the `is_bot` argument.
Consequences: All ptbtest-created users are compatible with PTB 12.8.

## 2026-01-15 - Ignore Python bytecode artifacts
Context: `.pyc` files and `__pycache__/` directories were showing up as modified artifacts in the working tree.
Decision: Add `__pycache__/` and `*.pyc` to `.gitignore`.
Consequences: New bytecode files will be ignored, but already-tracked artifacts still need to be removed manually if desired.

## 2026-01-15 - Ignore external rules source tree
Context: The `Rules/Secret-Hitler-Online-development/` folder is only a reference source tree and can be noisy in the repo.
Decision: Add `Rules/Secret-Hitler-Online-development/` to `.gitignore` while keeping `Rules/Secret_Hitler_Rules_Detailed.md` tracked.
Consequences: Reference sources stay untracked; the detailed rules doc remains versioned.

## 2026-01-15 - Simplify /version output
Context: The user only needs the bot version and does not want image refs or commit IDs in the `/version` response.
Decision: Make `/version` report only `APP_VERSION` (with a fallback if unset) and update the tests/docs accordingly.
Consequences: Deploy metadata like commit SHA or image ref is no longer shown in the bot response.

## 2026-01-15 - Use a single version label
Context: `/version` showed both "bot" and "app" labels, which was redundant.
Decision: Collapse `/version` to a single line that reports one version value.
Consequences: Users see one clear version string instead of multiple labels.

## 2026-01-15 - Localize vote output and stabilize RTL/LTR names
Context: Vote results were shown as "voted Ja/Nein" and mixed LTR names inside RTL sentences swapped order.
Decision: Map Ja/Nein to Persian labels for display and wrap LTR-ish names with Unicode isolates in key vote/nomination messages.
Consequences: Voting output is fully Persian and mixed-direction name order stays consistent in Telegram.

## 2026-01-15 - Use dynamic bot username in join fallback
Context: The join error message still pointed to the old bot username.
Decision: Resolve the current bot username at runtime and inject it into the join fallback message.
Consequences: Users are directed to the correct bot when private messages are blocked.

## 2026-01-15 - Update board track icons
Context: The board needed clearer, color-coded progress markers while keeping other icons unchanged.
Decision: Use white squares for empty slots, blue squares for liberal progress, and red squares for fascist progress.
Consequences: Board tracks read more clearly without changing action icons or vote markers.

## 2026-01-15 - Add temporary testboard command
Context: The user wanted to preview a sample board without starting a game.
Decision: Add a `/testboard` command that renders a sample board with dummy players and sample track progress.
Consequences: Users can preview board formatting before a game; command should be removed when no longer needed.
