# AGENTS.md

Guidance for AI coding agents working in this repository. Human-facing usage
docs live in `docs/` (Mintlify).

## What this is

`textseek` is a zero-dependency Python library that searches and extracts
structured data — confirmation codes, links, arbitrary regex matches — from a
plain string the caller supplies.

**Hard invariants — do not break:**
- No runtime dependencies. Standard library only.
- No I/O and no network. The caller fetches text (email, SMS, HTTP, OCR…);
  textseek only operates on the string it is given.
- Python 3.12+ (uses `slots=True` dataclasses, `X | Y` unions, `@overload`).
- Public API is fully typed; `Any` is avoided in public signatures.

## Package map

| Path | Responsibility |
|---|---|
| `textseek/seek.py` | `TextSeek` facade. Dispatches a spec to its extractor; exposes `extract_one` / `extract_first` / `extract_all` / `contains`. |
| `textseek/specs.py` | `Extract` factory + frozen spec dataclasses (`CodeSpec`/`LinkSpec`/`RegexSpec`). All validation happens here, at spec-creation time. |
| `textseek/extractors/` | One extractor per kind (`code.py`, `link.py`, `regex.py`), each with `find_all(text) -> list[...]`. `base.py` is the `Extractor` protocol. |
| `textseek/links.py` | URL discovery (`http`/`https` only) and parsing into `LinkResult`; sample-URL parsing. |
| `textseek/patterns.py` | Builds the code-matching regex from a `CodeSpec`. |
| `textseek/results.py` | Frozen result dataclasses (`CodeResult`/`LinkResult`/`RegexResult`). |
| `textseek/errors.py` | Exception hierarchy, all rooted at `TextSeekError`. |

## Conventions

- **Dispatch by spec type.** `TextSeek._extractor` maps spec class → extractor.
- **Adding an extraction kind** means four edits: a frozen spec dataclass in
  `specs.py`, an `Extract.<name>` factory method (with validation) in `specs.py`,
  an extractor class with `find_all` in `textseek/extractors/`, and a branch in
  `TextSeek._extractor`. Export new public names from `textseek/__init__.py`.
- **Validation is eager.** Contradictory settings raise from the `Extract`
  factory before any search runs (e.g. `InvalidCodeSpecError`).
- **Exception messages are written in Russian** (see `errors.py`, `specs.py`).
  Keep that convention when adding messages.
- **Results are frozen dataclasses** with `slots=True`. Keep them immutable.

## Build / test

```bash
uv run pytest            # full suite (fast, no network)
uv run pytest -q         # quiet
```

Tests live in `tests/`; `tests/corpus.py` holds shared sample text. There is no
separate lint/format step configured.

## Documentation rule

Docs are bilingual. Every page under `docs/<page>.mdx` has a mirror at
`docs/ru/<page>.mdx`, wired in `docs/docs.json`. **Any change to public
behavior must update both the English page and its Russian mirror in the same
change.** Code blocks are identical across languages; only prose differs.
