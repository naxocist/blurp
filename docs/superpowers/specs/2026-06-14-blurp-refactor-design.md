# Blurp Refactor Design (Pycord best-practices)

Date: 2026-06-14
Status: Approved

## Goal

Restructure the Blurp Discord bot (Pycord / py-cord 2.6.1) so it is easy to read
and develop further, following Discord bot best practices. External behavior (the
slash commands and their responses) stays identical. No user-visible change.

## Constraints

- `main.py` must remain at the repo root as the entrypoint. The Makefile runs
  `uv run main.py` and the Dockerfile runs `make run-prod`. The entrypoint command
  must not change.
- Generated MAL models (`models.py`) are produced by `model_gen.sh` and are not
  hand-edited. They move location, but their contents are left untouched.
- Same environment variable names and same dev/prod behavior as today.
- Python 3.12 (`requires-python = ">=3.12, <3.13"`).

## Target layout

```
main.py                      # thin entrypoint: build bot, run
blurp/
  __init__.py
  config.py                  # Settings: env load + validate (was credentials.py)
  logging_setup.py           # setup_logging() (was logging_config.py)
  bot.py                     # create_bot() factory + extension auto-loading
  cogs/
    __init__.py
    general.py               # /anime /expression /action /art (was cogs/anime.py)
    events.py                # listeners + global error handler
    games/
      __init__.py
      cycle.py               # AniCycle cog
      clues.py               # AniClues cog
      whatnum.py             # WhatNum cog
      ship.py                # Ship cog (stub kept)
  games/                     # game domain logic (was utils/customs)
    __init__.py
    state.py                 # Answer enum + GameRegistry (replaces global dicts)
    cycle/
      __init__.py
      game.py                # CycleClass
      views.py               # InviteView / TurnView / PickView
      flow.py                # init/random/pick/game phases (was logic.py)
    clues/
      __init__.py
      game.py                # ClueClass
      synopsis.py            # make_synopsis_clue (jikan + llm)
    whatnum/
      __init__.py
      game.py                # BinarySearch
  services/                  # external API clients (was utils/apis)
    __init__.py
    jikan.py
    mal.py
    nekos.py
    llm.py                   # gemini (was google.py); typhoon removed
  ui/
    __init__.py
    embeds.py                # make_anime_embed / make_timer_embed
    timers.py                # count_down_timer
  media.py                   # blur_image_from_url
  models/                    # generated MAL models (was utils/mal_model)
    __init__.py
    models.py
    jikan-openapi.json
    model_gen.sh
tests/
  test_whatnum.py
  test_cycle.py
  test_embeds.py
```

## Component responsibilities

- **`blurp/config.py`**: one `Settings` object loaded once from env. Loads the right
  `.env.*` file, validates required keys, computes `guild_ids` for dev/prod. Emits
  `logging` messages instead of `print`/emoji. Same var names and behavior.
  Since the Typhoon client is removed, `TYPHOON_API_KEY` is dropped from the
  required-keys list.
- **`blurp/logging_setup.py`**: `setup_logging()` configures the `discord` logger
  (file handler) plus a stream handler so application logs are visible. Equivalent
  to current behavior, extended to cover app logs.
- **`blurp/bot.py`**: `create_bot()` builds intents + activity and returns the
  `discord.Bot`. Extensions are discovered from `blurp.cogs` (and `blurp.cogs.games`)
  and loaded in a loop with logging, replacing the hardcoded list.
- **`blurp/games/state.py`**: `Answer` enum (unchanged) and `GameRegistry`, a small
  class wrapping the former module globals `players_games` and `minigame_objects`
  with `register(member, game)`, `get(member)`, `remove(game)` methods. A single
  shared instance is created and imported by the game cogs. Semantics identical.
- **`blurp/games/<game>/`**: each minigame gets a consistent shape: `game.py` for the
  game-state class, `views.py` for Discord UI views (cycle only), `flow.py` for
  multi-phase orchestration (cycle only), `synopsis.py` for clue text (clues only).
- **`blurp/services/`**: thin async wrappers over external APIs. `llm.py` exposes an
  async Gemini call. `typhoon.py` is removed.
- **`blurp/ui/`**: embed builders and the countdown-timer helper.
- **`blurp/media.py`**: image blur utility.
- **`blurp/models/`**: generated models, moved verbatim; `model_gen.sh` updated for
  the new path.

## Best-practice changes (internal only)

1. **Auto extension loading** with logging instead of a hardcoded list + `print`.
2. **Config as an object** with validation and logging, not top-level `print`s.
3. **`GameRegistry`** replaces two module-global mutable dicts. Same behavior,
   testable and explicit.
4. **No event-loop blocking**: the synchronous Gemini call and the
   `requests` + OpenCV blur run via `asyncio.to_thread` so they no longer block the
   gateway. (The Jikan wrapper already offloads to an executor; kept as-is.)
5. **Remove dead code / unused deps**: delete `typhoon.py`; remove `flask` from
   `pyproject.toml`. `ship.py` stays as a stub.
6. **No bare `except`**, no em-dashes, minimal comments (continues the prior pass).

## Testing

Pure-logic pytest only (I/O-bound Discord code is out of scope):

- `test_whatnum.py`: `BinarySearch.expected_guess_cnt` math across ranges; target is
  within `[low, high]`; `terminate(success)` sets the correct `Answer` status.
- `test_cycle.py`: `CycleClass.random_targets()` produces a derangement (no member
  targets themselves) and a valid one-to-one assignment; `given_by` inverts `targets`.
- `test_embeds.py`: `make_anime_embed` and `make_timer_embed` produce the expected
  titles/fields given a fake anime-like object.

`pytest` is added as a dev dependency.

## Migration safety

- No tests exist today, so validation per step: `ruff check`, byte-compile, and an
  import smoke test of the `blurp` package (with env stubbed) after each move.
- Imports are updated per moved module; old paths are removed only after all
  references are repointed and a re-grep shows zero stale imports.
- Verify the entrypoint import chain resolves at the end.

## Out of scope

- No changes to slash command names, options, descriptions, or response content.
- No changes to the generated `models.py` contents.
- No mocked-Discord or API integration tests (pure-logic only).
- No new features; `ship` remains a stub.
