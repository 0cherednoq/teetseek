# Design: AI-friendly documentation for textseek

Date: 2026-06-01
Status: Approved (pending user spec review)

## Goal

Make textseek's documentation easier for AI to understand and use correctly —
both coding agents working *inside* the repository and assistants answering
questions *about* the library from its published docs. Concretely: an LLM
generating textseek code should pick the right call and not hit the surprises
that the current docs leave implicit.

## Scope (decided with user)

1. Add `AGENTS.md` at the repo root (cross-vendor agent instruction file).
2. Full pass over all 15 English `.mdx` pages + sync the 15 Russian pages.
3. Add a curated `docs/llms.txt` index (Mintlify also auto-generates one).

Out of scope: generating docs from docstrings; restructuring navigation;
changing library behavior or public API.

## Guiding principles

- **Page self-containment.** AI retrieves pages individually (RAG / llms.txt).
  Each usage page carries a full import, a runnable example with the expected
  output in a comment, and an explicit "boundaries / what it does NOT do" note.
- **API reference = full contract.** Every parameter gets type, default, and a
  one-line purpose; every result field gets a type; every raise is listed with
  its trigger.
- **Fix doc-vs-code gaps.** Document the six behaviors below where current docs
  are silent or misleading — this removes the main class of AI generation errors.

## Doc-vs-code gaps to fix (verified against source)

| # | Reality (source) | Where docs are wrong/silent | Fix |
|---|---|---|---|
| 1 | Only `http://`/`https://` are recognized (`links.py` `_URL_RE`). No ftp/mailto. | Silent; `scheme=` filter implies any scheme works. | State "recognised schemes: http, https only" on link pages + `Extract.link` reference. |
| 2 | Trailing punctuation `.,;:!?)]}>"'` is stripped from matched URLs (`find_link_candidates`). | Silent; affects `value`/`end`. | Note trailing-punctuation trimming on extract-links page + results reference. |
| 3 | `LinkResult.domain` and `.host` are identical (both = hostname). `domain=` filter compares to `host`. | `concepts/results.mdx`, `usage/extract-links.mdx` present them as distinct. | Clarify `domain` is an alias of `host`; both are the hostname. |
| 4 | `Extract.code()` with no args = digits only, length ≥ 1, strict token boundaries. | Not stated explicitly anywhere. | Add explicit "defaults" sentence to `extract.mdx` + extract-specs concept. |
| 5 | `near` takes `window` chars on BOTH sides of the phrase. | `usage/extract-code.mdx` says vague "window around it". | Make the two-sided window explicit; keep the after-then-before ranking note. |
| 6 | `query_params` uses `keep_blank_values=True`. | Silent. | Note blank query values are kept (`?a=` → `{"a": [""]}`). |

## Deliverables

### 1. `AGENTS.md` (repo root)

Sections:
- **Project.** Zero-dependency stdlib-only text extraction; Python 3.12+; the
  invariant "no runtime dependencies, no network/IO — caller supplies the text".
- **Package map.** `seek.py` (TextSeek facade, dispatches by spec type) ·
  `specs.py` (`Extract` factory + validation, frozen spec dataclasses) ·
  `extractors/` (per-kind `find_all` logic) · `links.py` (URL parsing) ·
  `patterns.py` (code regex builder) · `results.py` (frozen result dataclasses)
  · `errors.py` (exception hierarchy).
- **Commands.** `uv run pytest` to test; note tests live in `tests/` with a
  shared `corpus.py`. (Add lint/type commands only if present in the repo.)
- **Conventions.** Facade dispatches on spec type; adding an extractor =
  spec dataclass + `Extract` factory method + extractor class with `find_all` +
  register in `TextSeek._extractor`; exception messages are written in Russian;
  public API avoids `Any` and returns typed frozen dataclasses; methods are
  `@overload`-ed per spec type.
- **Docs.** Where docs live (`docs/`, Mintlify `docs.json`); rule: every change
  to public behavior updates the English page AND its `docs/ru/...` mirror.

Keep it concise (target ~1 screen). It states facts an agent cannot cheaply
derive, not a re-listing of the code.

### 2. English `.mdx` pass (15 pages)

- `api-reference/extract.mdx` — parameter tables (name · type · default ·
  purpose) for `code`/`link`/`regex`; add "Recognised URL schemes" and
  "Trailing punctuation" notes; list each raise with its trigger.
- `api-reference/results.mdx` + `concepts/results.mdx` — full field tables with
  types; clarify `domain == host`; note `keep_blank_values`.
- `api-reference/textseek.mdx` — confirm raises/return per method are complete.
- `usage/extract-code.mdx` — defaults of `code()`; two-sided `near` window with
  expected output.
- `usage/extract-links.mdx` — http/https-only + punctuation trimming;
  `domain`/`host` alias; expected output on the field example.
- `usage/link-by-sample.mdx`, `usage/regex-search.mdx`, `usage/error-handling.mdx`
  — full import + expected output + boundary note each.
- `concepts/extract-specs.mdx`, `concepts/textseek.mdx` — code defaults; near
  ranking; dispatch model.
- `introduction.mdx`, `quickstart.mdx` — consistency only (schemes caveat in
  intro's "what it does NOT do").

Style stays consistent with the existing terse, example-first voice. No
behavioral claims that aren't backed by source.

### 3. Russian `.mdx` sync (15 pages)

Mirror every English change into `docs/ru/...`. Same code blocks (code is
language-neutral); prose translated. Keep frontmatter `description` translated —
it feeds the language-specific llms.txt.

### 4. `docs/llms.txt`

Curated index in the llmstxt.org format: H1 title, blockquote summary, then
grouped links (Getting Started / Concepts / Usage / API / Advanced) with a
one-line gloss each. Note in the spec: Mintlify auto-serves `/llms.txt` and
`/llms-full.txt` from `docs.json` + page descriptions, so the highest leverage
is good frontmatter descriptions; the committed `docs/llms.txt` is a portable
fallback for non-Mintlify consumers. We do NOT hand-maintain `llms-full.txt`.

## Testing / verification

- `tests/test_examples.py` runs doc examples — any code block we change that is
  covered must still pass `uv run pytest`.
- Manually re-verify each of the six gap fixes against the cited source line so
  no note overstates behavior.
- Cross-check that en and ru page sets stay 1:1 (same pages, same sections).

## Risks

- Russian sync drift — mitigated by doing en+ru page-by-page in the same step.
- Overstating behavior in new notes — mitigated by citing source per claim.
- `docs/llms.txt` vs Mintlify auto-generation — documented; curated file is a
  fallback, not a competing source of truth.
