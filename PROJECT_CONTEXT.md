# PROJECT_CONTEXT.md

Living overview of the project for continuity across chats.

## Purpose
- Telegram bot implementation of the Secret Hitler card game.
- This repo is a Persian/Farsi-oriented fork with RTL text and localized strings (visible in source, but currently garbled in this view).

## Runtime entry point
- `MainController.py` is the bot entry point and runs a polling loop using `python-telegram-bot` 12.8.

## Configuration
- `Constants/Config.py` loads `BOT_TOKEN`, `ADMIN_ID`, and `STATS_PATH` from env or `.env` (via `python-dotenv`).
- `BOT_TOKEN` is required; startup raises if missing.
- `STATS_PATH` defaults to `stats.json` at the repo root; `Constants/Config.py` resolves relative paths and exposes `load_stats`/`save_stats` helpers.
- `Commands.py` configures logging to `logs/logging.log` and now creates the `logs/` directory on startup.
- Optional runtime version env var used by `/version`: `APP_VERSION` (single-line version output).

## Architecture overview
- `Commands.py`: Telegram command handlers (help, start, join, board, votes, etc).
- `MainController.py`: game flow and callback query handlers (nomination, voting, policy enactment, executive actions).
- `GamesController.py`: holds the global `games` dict, initialized via `init()`.
- `Boardgamebox/`: core game data structures (`Board`, `Game`, `Player`, `State`).
- `Constants/Cards.py`: role sets, policy deck definitions, and canonical constants for roles, policies, and track actions.

## State and data
- Game state is in-memory only (`GamesController.games`); no persistence beyond stats JSON.
- Stats are read/written as JSON via `STATS_PATH`; file is not tracked in the repo.

## Tests
- `tests/test_Commands.py` uses `ptbtest` with a `Mockbot`.
- Tests assert localized Persian output via Unicode-escape substrings.
- Test setup injects a minimal `request` stub into `Mockbot` for `Updater` compatibility.
- Test setup patches `Mockbot.getMe` to pass the required `is_bot` argument to `telegram.User`.
- Test setup stubs `Mockbot.delete_webhook` and patches `UserGenerator.get_user` at the class level for the updated `telegram.User` signature.
- Tests call `dispatcher.process_update` directly (no polling threads).
- Tests pass `parse_mode="Markdown"` to generate `bot_command` entities.

## Deployment
- `Dockerfile` uses `python:3.10-slim`, installs build tools for `cryptography`, and runs `MainController.py`.
- `Dockerfile` accepts `GIT_SHA` as a build arg and sets it as a runtime env var (currently unused by `/version`).
- `fly.toml` builds from the Dockerfile and defines a `bot` process.

## Repo map
- `README.md`: user-facing overview, contains encoding artifacts in this view.
- `requirements.txt`: pinned dependencies including `python-telegram-bot==12.8` and `ptbtest`.
- `Commands.py`, `MainController.py`, `GamesController.py`: core bot logic.
- `Constants/`: config and card definitions.
- `Boardgamebox/`: game state classes.
- `Rules/Secret_Hitler_Rules.pdf`: official rulebook source.
- `Rules/Secret_Hitler_Rules_Detailed.md`: detailed internal rules reference derived from the rulebook.
- `Rules/Secret-Hitler-Online-development/`: external online-game source tree for reference; now ignored by `.gitignore`.
- `tests/test_Commands.py`: command tests with mock Telegram bot.
- `Dockerfile`, `fly.toml`: deployment configuration.
- `.gitignore`: ignores `.env`, `logs/`, `stats.json`, `__pycache__/`, `*.pyc`, and `Rules/Secret-Hitler-Online-development/`.
- `logs/`, `stats.json`: generated at runtime and ignored by `.gitignore`.
- `__pycache__/`, `Boardgamebox/__pycache__/`, `Constants/__pycache__/`: compiled `.pyc` files are currently tracked in the repo; new ones are now ignored.

## Encoding notes
- Many source files include non-ASCII and RTL strings; they appear garbled in this view.
- Avoid touching localized strings unless intentionally updating localization, and preserve file encoding.
