# AI-friendly documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make textseek's docs easy for AI to use correctly — add a repo-root `AGENTS.md`, rework all 15 English `.mdx` pages (with the 15 Russian mirrors) to be self-contained and contract-complete, fix six documented-vs-actual behavior gaps, and add a curated `docs/llms.txt`.

**Architecture:** Pure documentation change — no library code is touched. "Verification" for each doc claim is: run the snippet against real Python (values below are already captured from the live library) and keep `uv run pytest` green. English and Russian pages are edited page-by-page in lockstep to stay 1:1.

**Tech Stack:** Mintlify (`docs.json`), MDX, Python 3.12 / `uv`, pytest.

---

## Verified facts (captured from the live library — use these exact values)

All values below were produced by running the current source. Do NOT alter them.

- Link match strips trailing punctuation `.,;:!?)]}>"'`:
  `"Click https://example.com/auth/magic?token=abc123&email=test@example.com#top."`
  → `value == "https://example.com/auth/magic?token=abc123&email=test@example.com#top"` (trailing `.` dropped).
- `LinkResult.domain == LinkResult.host` (both are the hostname, e.g. `"example.com"`).
- `query_params` keeps blank values: `"...?flag=&q=1"` → `{"flag": [""], "q": ["1"]}`.
- Only `http://` / `https://` are recognized: `Extract.link()` on `"ftp://example.com/file"` → `[]`.
- `Extract.code()` (no args) = digits only, length ≥ 1; on `"id 42 and 1234 and ab12"` → `["42", "1234", "12"]`.
- Code boundaries are against the **allowed character class**, not word boundaries:
  `Extract.code(length=4, digits=True)` on `"user ab1234 here"` → `["1234"]` (the letters aren't digits, so the digit run is a valid token); on `"1234567890"` → `[]` (all digits, no 6-char token with non-digit borders).
- `near` window = `window` chars on BOTH sides of the phrase; after-phrase codes outrank before-phrase codes:
  - `"Ignore 111111. Your verification code is 654321."`, `Extract.code(length=6, digits=True, near="verification code")` → `extract_one` = `"654321"`; `extract_all` = `["654321", "111111"]`.
  - Fallback (only a code before the phrase): `"G-447103 is your verification code"` → `extract_one` = `"447103"`.
- `require_each_type`: `"token A1B2C3D4 next"`, `Extract.code(length=8, digits=True, alphabet=True, require_each_type=True)` → `"A1B2C3D4"`.

## File map

Create:
- `AGENTS.md` (repo root)
- `docs/llms.txt`

Modify (English, 15):
- `docs/introduction.mdx`, `docs/quickstart.mdx`
- `docs/concepts/textseek.mdx`, `docs/concepts/extract-specs.mdx`, `docs/concepts/results.mdx`
- `docs/usage/extract-code.mdx`, `docs/usage/extract-links.mdx`, `docs/usage/link-by-sample.mdx`, `docs/usage/regex-search.mdx`, `docs/usage/error-handling.mdx`
- `docs/api-reference/textseek.mdx`, `docs/api-reference/extract.mdx`, `docs/api-reference/results.mdx`, `docs/api-reference/errors.mdx`
- `docs/advanced/custom-extractors.mdx`, `docs/advanced/typing.mdx`

Modify (Russian mirrors, same 15 under `docs/ru/...`).

---

### Task 1: AGENTS.md (repo root)

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Write `AGENTS.md`**

```markdown
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
```

- [ ] **Step 2: Verify it reflects reality**

Confirm each claim against source: package map paths exist (`ls textseek textseek/extractors`); `uv run pytest` is the real command (run it, expect all pass/skip, 0 failures); messages in `errors.py`/`specs.py` are Russian.

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "docs: add AGENTS.md for AI coding agents"
```

---

### Task 2: API reference — `extract.mdx` (English)

**Files:**
- Modify: `docs/api-reference/extract.mdx`

- [ ] **Step 1: Replace the file body with parameter tables + behavior notes**

Replace the whole file (keep the frontmatter) with:

````markdown
---
title: Extract
description: API reference for the Extract factory — code, link, regex
---

`Extract` is a factory of immutable, eagerly validated spec objects. You never
construct `CodeSpec` / `LinkSpec` / `RegexSpec` directly.

## `Extract.code`

```python
Extract.code(
    length: int | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    digits: bool = True,
    alphabet: bool = False,
    symbols: bool = False,
    uppercase: bool = True,
    lowercase: bool = True,
    require_each_type: bool = False,
    near: str | None = None,
    window: int = 300,
    pattern: str | None = None,
) -> CodeSpec
```

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `length` | `int \| None` | `None` | Exact token length. Mutually exclusive with `min_length`/`max_length`. |
| `min_length` | `int \| None` | `None` | Minimum length (defaults to 1 when only `max_length` is set). |
| `max_length` | `int \| None` | `None` | Maximum length (unbounded if omitted). |
| `digits` | `bool` | `True` | Allow `0-9`. |
| `alphabet` | `bool` | `False` | Allow letters (see `uppercase`/`lowercase`). |
| `symbols` | `bool` | `False` | Allow the default symbol set `-` and `_`. |
| `uppercase` | `bool` | `True` | When `alphabet`, allow `A-Z`. |
| `lowercase` | `bool` | `True` | When `alphabet`, allow `a-z`. |
| `require_each_type` | `bool` | `False` | Require ≥1 char of every enabled class (post-filter). |
| `near` | `str \| None` | `None` | Anchor phrase; results are ranked by proximity (see below). |
| `window` | `int` | `300` | Chars scanned on **each** side of the `near` phrase. |
| `pattern` | `str \| None` | `None` | Raw regex; bypasses the builder and the validation above. |

**Defaults:** `Extract.code()` with no arguments matches digit-only tokens of
length ≥ 1.

**Token boundaries are class-relative.** A match must be bordered by characters
*outside the allowed class*, not by word boundaries. So with `digits=True`,
`length=4`, `"ab1234"` yields `"1234"` (letters aren't digits), but `"1234567890"`
yields nothing for `length=6` (every neighbour is also a digit).

**`require_each_type`** rejects tokens missing an enabled class: with
`digits=True, alphabet=True, require_each_type=True`, `"A1B2C3D4"` passes while
`"12345678"` and `"ABCDEFGH"` are rejected.

Raises `InvalidCodeSpecError` on contradictory settings: `length` together with
`min_length`/`max_length`; `length`/`min_length` < 1; `min_length > max_length`;
no character class enabled; `alphabet=True` with both `uppercase` and
`lowercase` off; negative `window`. (With `pattern` set, only `window` is
validated.)

## `Extract.link`

```python
Extract.link(
    sample: str | None = None,
    scheme: str | None = None,
    domain: str | None = None,
    path: str | None = None,
    path_contains: str | None = None,
    required_query: list[str] | None = None,
    allow_subdomains: bool = False,
) -> LinkSpec
```

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `sample` | `str \| None` | `None` | Example URL; its scheme, host, path, and query **keys** become filters (explicit args win). |
| `scheme` | `str \| None` | `None` | Exact scheme match (only `http`/`https` are ever discovered). |
| `domain` | `str \| None` | `None` | Exact hostname match (use `allow_subdomains` to widen). |
| `path` | `str \| None` | `None` | Exact path match. |
| `path_contains` | `str \| None` | `None` | Substring match on path. |
| `required_query` | `list[str] \| None` | `None` | Query keys that must be present (values not compared). |
| `allow_subdomains` | `bool` | `False` | Also match `*.domain`. |

**Recognised schemes:** link discovery only finds `http://` and `https://`
URLs. `ftp://`, `mailto:`, etc. are never returned, regardless of `scheme`.

Raises `InvalidSampleLinkError` if `sample` lacks a scheme or host.

## `Extract.regex`

```python
Extract.regex(pattern: str, flags: int = 0) -> RegexSpec
```

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `pattern` | `str` | — | Regular expression, compiled immediately. |
| `flags` | `int` | `0` | `re` flags (e.g. `re.IGNORECASE`). |

Raises `RegexExtractError` if `pattern` does not compile.
````

- [ ] **Step 2: Verify the documented behaviors**

Run: `uv run python -c "from textseek import TextSeek, Extract; print([c.value for c in TextSeek('user ab1234 here').extract_all(Extract.code(length=4, digits=True))])"`
Expected: `['1234']`

Run: `uv run python -c "from textseek import TextSeek, Extract; print(TextSeek('ftp://example.com/x').extract_all(Extract.link()))"`
Expected: `[]`

- [ ] **Step 3: Commit**

```bash
git add docs/api-reference/extract.mdx
git commit -m "docs: full parameter contract for Extract reference"
```

---

### Task 3: API reference — `results.mdx` and `textseek.mdx` (English)

**Files:**
- Modify: `docs/api-reference/results.mdx`
- Modify: `docs/api-reference/textseek.mdx`

- [ ] **Step 1: Replace `results.mdx` body with typed field tables**

````markdown
---
title: Results
description: Result dataclasses and their fields
---

All results are `@dataclass(slots=True, frozen=True)` and share `value`,
`start`, `end`.

| Field | Type | Meaning |
|---|---|---|
| `value` | `str` | The matched substring. For links, trailing punctuation `.,;:!?)]}>"'` is stripped. |
| `start` | `int` | Start index in the source text. |
| `end` | `int` | End index (exclusive) in the source text. |

## `CodeResult`

Adds nothing beyond `value`, `start`, `end`.

## `LinkResult`

| Field | Type | Notes |
|---|---|---|
| `scheme` | `str` | e.g. `"https"`. |
| `domain` | `str` | Hostname. **Alias of `host`** — same value. |
| `host` | `str` | Hostname. |
| `port` | `int \| None` | `None` if absent or invalid. |
| `path` | `str` | e.g. `"/auth/magic"`. |
| `query` | `str` | Raw query string. |
| `fragment` | `str` | Part after `#`. |
| `query_params` | `dict[str, list[str]]` | Parsed query; blank values are kept (`?a=` → `{"a": [""]}`). |

## `RegexResult`

| Field | Type | Notes |
|---|---|---|
| `groups` | `tuple[str, ...]` | Positional groups. |
| `groupdict` | `dict[str, str]` | Named groups. |

`value` is the first group if the pattern has groups, otherwise the whole match.
````

- [ ] **Step 2: Update `textseek.mdx` to complete the per-method contract**

Replace its body (keep frontmatter) with:

````markdown
---
title: TextSeek
description: API reference for the TextSeek class
---

`TextSeek(text: str)` wraps a string. Each method takes an `Extract` spec and is
`@overload`-ed per spec type, so the result type is narrowed automatically.

## `extract_one(spec) -> ExtractResult`

The single best match. Returns `CodeResult` / `LinkResult` / `RegexResult`
according to the spec.

Raises `ExtractNotFoundError` if there is no match; `InvalidExtractSpecError` if
the spec type is unrecognized.

## `extract_first(spec) -> ExtractResult | None`

The first match, or `None`. With `near`, "first" means best-ranked, not
source-order.

## `extract_all(spec) -> list[ExtractResult]`

All matches (empty list if none). For `code` with `near`, results are ordered by
proximity to the phrase (after-phrase first); otherwise in source-text order.

## `contains(spec) -> bool`

`True` if at least one match exists. Equivalent to `extract_first(spec) is not None`.
````

- [ ] **Step 3: Verify**

Run: `uv run python -c "from textseek import TextSeek, Extract; l=TextSeek('go https://example.com/a?t=1#x.').extract_one(Extract.link()); print(l.value, l.domain==l.host)"`
Expected: `https://example.com/a?t=1#x True`

- [ ] **Step 4: Commit**

```bash
git add docs/api-reference/results.mdx docs/api-reference/textseek.mdx
git commit -m "docs: complete result-field and TextSeek method contracts"
```

---

### Task 4: API reference — `errors.mdx` + Concepts pages (English)

**Files:**
- Modify: `docs/api-reference/errors.mdx`
- Modify: `docs/concepts/results.mdx`
- Modify: `docs/concepts/extract-specs.mdx`
- Modify: `docs/concepts/textseek.mdx`

- [ ] **Step 1: `errors.mdx` — add the trigger column** (replace body, keep frontmatter)

````markdown
---
title: Errors
description: Exception hierarchy and what triggers each
---

```text
TextSeekError                 # base — catch this for everything
├── ExtractNotFoundError      # extract_one found no match
├── InvalidExtractSpecError   # TextSeek got an unrecognized spec type
├── InvalidSampleLinkError    # Extract.link(sample=...) URL lacks scheme/host
├── InvalidCodeSpecError      # Extract.code(...) settings contradict each other
└── RegexExtractError         # Extract.regex(...) pattern failed to compile
```

| Exception | Raised by | When |
|---|---|---|
| `ExtractNotFoundError` | `extract_one` | No match in the text. |
| `InvalidExtractSpecError` | `TextSeek` dispatch | Spec is not a known type. |
| `InvalidSampleLinkError` | `Extract.link` | `sample` has no scheme or host. |
| `InvalidCodeSpecError` | `Extract.code` | Contradictory code settings (see Extract reference). |
| `RegexExtractError` | `Extract.regex` | Pattern does not compile. |

All inherit from `TextSeekError`, so one `except TextSeekError` catches every
library error. Validation errors are raised at `Extract.*` time, before any
search runs.
````

- [ ] **Step 2: `concepts/results.mdx` — fix the `domain`/`host` claim** (replace body, keep frontmatter)

````markdown
---
title: Results
description: Typed result objects
---

Every result is a frozen dataclass carrying `value`, `start`, and `end`:

| Field | Meaning |
|---|---|
| `value` | the matched value (for links, trailing punctuation is stripped) |
| `start` | start index in the source text |
| `end` | end index (exclusive) in the source text |

`CodeResult` adds nothing more.

`LinkResult` adds `scheme`, `domain`, `host`, `port`, `path`, `query`,
`fragment`, and `query_params`. **`domain` and `host` are the same hostname** —
`domain` is a convenience alias. `query_params` keeps blank values
(`?flag=` → `{"flag": [""]}`).

`RegexResult` adds `groups` (positional) and `groupdict` (named).

See the [results reference](/api-reference/results) for full types.
````

- [ ] **Step 3: `concepts/extract-specs.mdx` — add defaults + eager validation note** (replace body, keep frontmatter)

````markdown
---
title: Extract specs
description: How search rules are built
---

You never construct internal spec classes directly. Use the `Extract` factory:

```python
Extract.code(...)   # confirmation codes
Extract.link(...)   # http/https links
Extract.regex(...)  # arbitrary regex
```

Each returns an immutable spec object **validated at creation time** — invalid
settings raise immediately (e.g. `InvalidCodeSpecError`), before any search runs.

Defaults worth knowing:

- `Extract.code()` matches digit-only tokens of length ≥ 1, with class-relative
  boundaries (a token must be bordered by characters outside its allowed set).
- `Extract.link()` matches every `http`/`https` URL in the text; add filters to
  narrow it.
- `Extract.regex(pattern)` compiles `pattern` eagerly; a bad pattern raises
  `RegexExtractError` here, not during the search.
````

- [ ] **Step 4: `concepts/textseek.mdx` — clarify near ordering** (append the Note below to the existing body, after the code block)

```markdown
<Note>
`extract_all` returns matches in source-text order, **except** for
`Extract.code(near=...)`, where results are ranked by proximity to the phrase
(after-phrase codes first). `extract_one`/`extract_first` then return the
best-ranked match.
</Note>
```

- [ ] **Step 5: Verify**

Run: `uv run python -c "from textseek import TextSeek, Extract; print(TextSeek('a https://x.com/p?flag=&q=1 b').extract_one(Extract.link()).query_params)"`
Expected: `{'flag': [''], 'q': ['1']}`

- [ ] **Step 6: Commit**

```bash
git add docs/api-reference/errors.mdx docs/concepts/results.mdx docs/concepts/extract-specs.mdx docs/concepts/textseek.mdx
git commit -m "docs: fix domain/host, blank-query, defaults, and near-ordering in concepts/errors"
```

---

### Task 5: Usage pages (English)

**Files:**
- Modify: `docs/usage/extract-code.mdx`
- Modify: `docs/usage/extract-links.mdx`
- Modify: `docs/usage/link-by-sample.mdx`
- Modify: `docs/usage/regex-search.mdx`
- Modify: `docs/usage/error-handling.mdx`

Each page gets: a full `from textseek import ...` line in its first example,
expected-output comments using the verified values, and a boundary note.

- [ ] **Step 1: `extract-code.mdx` — replace the "Near a phrase" section** with the verified two-sided behavior:

````markdown
## Near a phrase

```python
from textseek import TextSeek, Extract

text = "Ignore 111111. Your verification code is 654321."
code = TextSeek(text).extract_one(
    Extract.code(length=6, digits=True, near="verification code")
)
print(code.value)  # 654321
```

`window` chars are scanned on **each side** of the phrase (300 by default). Codes
that appear **after** the phrase outrank codes before it (the usual "your code is
XXX"), and nearer outranks farther. If no code follows the phrase, the nearest
one before it is used:

```python
TextSeek("G-447103 is your verification code").extract_one(
    Extract.code(length=6, digits=True, near="verification code")
).value  # 447103
```

With `near`, `extract_all` returns matches ordered by rank (best first), so for
the first example it is `["654321", "111111"]`.
````

Also update the existing "Strict boundaries" section to state class-relative
boundaries explicitly:

````markdown
## Strict boundaries

A code is matched as a whole token, bordered by characters **outside its allowed
character class**. `Extract.code(length=6, digits=True)` does not match `123456`
inside `1234567890` (all neighbours are digits). But `Extract.code(length=4,
digits=True)` does match `1234` inside `ab1234`, because letters are not in the
digit class.
````

- [ ] **Step 2: `extract-links.mdx` — add boundary note + expected output**

Append after the fields example:

````markdown
<Note>
Only `http://` and `https://` URLs are discovered — `ftp://`, `mailto:`, etc.
are never returned. Trailing punctuation (`.,;:!?)]}>"'`) is stripped from each
match, so a URL ending a sentence keeps a clean `value`. `domain` and `host`
hold the same hostname.
</Note>
````

Ensure the first example has the import line:

```python
from textseek import TextSeek, Extract
links = TextSeek(text).extract_all(Extract.link())
```

- [ ] **Step 3: `link-by-sample.mdx`** — add the import line to the example and append:

```markdown
Only the query **keys** from the sample become filters, never the values, and
explicit `Extract.link(...)` arguments override anything derived from `sample`.
```

- [ ] **Step 4: `regex-search.mdx`** — add the import line and an expected-output comment:

```python
from textseek import TextSeek, Extract

result = TextSeek("Order ID: AB-9921").extract_one(
    Extract.regex(r"Order ID:\s*([A-Z0-9\-]+)")
)
print(result.value)  # AB-9921 (the first group, since the pattern has groups)
```

- [ ] **Step 5: `error-handling.mdx`** — make the example self-contained:

```python
from textseek import TextSeek, Extract
from textseek import ExtractNotFoundError, InvalidCodeSpecError

text = "no code here"
try:
    code = TextSeek(text).extract_one(Extract.code(length=6))
except ExtractNotFoundError:
    print("Code not found")        # printed for this text
except InvalidCodeSpecError:
    print("Bad code settings")
```

- [ ] **Step 6: Verify the new expected outputs**

Run: `uv run python -c "from textseek import TextSeek, Extract; print(TextSeek('Ignore 111111. Your verification code is 654321.').extract_one(Extract.code(length=6, digits=True, near='verification code')).value)"`
Expected: `654321`

Run: `uv run python -c "from textseek import TextSeek, Extract; print(TextSeek('Order ID: AB-9921').extract_one(Extract.regex(r'Order ID:\s*([A-Z0-9\-]+)')).value)"`
Expected: `AB-9921`

- [ ] **Step 7: Commit**

```bash
git add docs/usage
git commit -m "docs: self-contained usage examples with verified outputs and boundaries"
```

---

### Task 6: Intro, quickstart, advanced (English)

**Files:**
- Modify: `docs/introduction.mdx`
- Modify: `docs/quickstart.mdx`
- Modify: `docs/advanced/custom-extractors.mdx`
- Modify: `docs/advanced/typing.mdx`

- [ ] **Step 1: `introduction.mdx`** — in the "What it does" list, change the links bullet to name the scheme limit:

```markdown
- Extract `http`/`https` links as rich objects with `scheme`, `domain`,
  `path`, `query_params`
```

- [ ] **Step 2: `quickstart.mdx`** — the "Extract links" snippet currently reuses the code-only `text`, which yields nothing. Make it self-contained and truthful:

```python
text = "Open https://example.com/auth/magic?token=abc to continue."
links = TextSeek(text).extract_all(Extract.link())
for link in links:
    print(link.domain, link.path)  # example.com /auth/magic
```

- [ ] **Step 3: `advanced/custom-extractors.mdx`** — append the registration detail already used by built-ins:

```markdown
`TextSeek._extractor` dispatches by spec class, so your new spec type needs a
branch there. Export any new public names from `textseek/__init__.py`.
```

- [ ] **Step 4: `advanced/typing.mdx`** — no behavioral change; verify the example still type-narrows and the `Any`-avoidance claim holds (it does). Leave as-is unless an import line is missing; if so add `from textseek import Extract`.

- [ ] **Step 5: Verify quickstart links snippet**

Run: `uv run python -c "from textseek import TextSeek, Extract; [print(l.domain, l.path) for l in TextSeek('Open https://example.com/auth/magic?token=abc to continue.').extract_all(Extract.link())]"`
Expected: `example.com /auth/magic`

- [ ] **Step 6: Commit**

```bash
git add docs/introduction.mdx docs/quickstart.mdx docs/advanced
git commit -m "docs: fix quickstart links example and tighten intro/advanced"
```

---

### Task 7: Russian mirror sync (all 15 pages)

**Files:**
- Modify: every `docs/ru/<page>.mdx` corresponding to a page changed in Tasks 2–6.

- [ ] **Step 1: Port every change page-by-page**

For each English page edited above, apply the identical structural change to its
`docs/ru/...` mirror: copy the code blocks verbatim (code is language-neutral,
including the expected-output comments — keep the literal values, translate only
the comment words where they are prose), and translate the prose, tables, and
`<Note>` text into Russian. Match the existing Russian register in the repo
(e.g. compare against `README.ru.md`).

Key terms to keep consistent in Russian:
- "hostname / host alias" → «`domain` совпадает с `host` (это псевдоним)»
- "trailing punctuation is stripped" → «хвостовая пунктуация отрезается»
- "only http/https are discovered" → «находятся только ссылки `http`/`https`»
- "class-relative boundaries" → «границы по разрешённому классу символов»
- "after-phrase codes outrank before-phrase" → «коды после фразы важнее кодов перед ней»

- [ ] **Step 2: Verify 1:1 structure**

Run: `uv run python - <<'PY'`
```python
import re, pathlib
en = sorted(p.relative_to('docs') for p in pathlib.Path('docs').glob('*.mdx')) + \
     sorted(p.relative_to('docs') for p in pathlib.Path('docs').glob('*/*.mdx') if 'ru' not in p.parts and 'superpowers' not in p.parts)
ru = sorted(p.relative_to('docs/ru') for p in pathlib.Path('docs/ru').glob('**/*.mdx'))
missing = set(map(str, en)) - set(map(str, ru))
print("MISSING RU:", missing or "none")
PY
```
Expected: `MISSING RU: none`

Also confirm each RU page has the same number of `##` headings as its EN twin
(spot-check the four API-reference pages and `usage/extract-code`).

- [ ] **Step 3: Commit**

```bash
git add docs/ru
git commit -m "docs: sync Russian pages with reworked English docs"
```

---

### Task 8: `docs/llms.txt` + frontmatter descriptions

**Files:**
- Create: `docs/llms.txt`
- Modify: any `docs/*.mdx` whose frontmatter `description` is weak (it feeds the auto-generated llms.txt).

- [ ] **Step 1: Create `docs/llms.txt`**

```text
# textseek

> Zero-dependency Python library (3.12+) for extracting confirmation codes,
> http/https links, and arbitrary regex matches from plain text the caller
> supplies. No network, no I/O — you fetch the text, textseek pulls structured
> values out of it.

## Getting started
- [Introduction](/introduction): what textseek does and does not do
- [Quickstart](/quickstart): extract your first code and link

## Concepts
- [TextSeek](/concepts/textseek): the entry-point object and its four methods
- [Extract specs](/concepts/extract-specs): how validated search rules are built
- [Results](/concepts/results): typed frozen result objects

## Usage
- [Extract codes](/usage/extract-code): numeric, alphanumeric, symbol, and near-phrase codes
- [Extract links](/usage/extract-links): links as structured LinkResult objects (http/https only)
- [Find links by example](/usage/link-by-sample): build filters from a sample URL
- [Regex search](/usage/regex-search): arbitrary regex extraction with typed results
- [Error handling](/usage/error-handling): the TextSeekError hierarchy

## API reference
- [TextSeek](/api-reference/textseek): extract_one / extract_first / extract_all / contains
- [Extract](/api-reference/extract): full parameter contract for code/link/regex
- [Results](/api-reference/results): result dataclass fields and types
- [Errors](/api-reference/errors): exceptions and their triggers

## Advanced
- [Custom extractors](/advanced/custom-extractors): add a new extraction kind
- [Typing](/advanced/typing): how results stay statically typed
```

- [ ] **Step 2: Strengthen weak frontmatter descriptions**

Review each English page's `description:`. Ensure it is a specific one-liner
(Mintlify feeds these into the auto-generated `/llms.txt`). Concretely set:
- `usage/extract-links.mdx` → `description: Extract http/https links as structured LinkResult objects`
- `api-reference/extract.mdx` → `description: API reference for the Extract factory — code, link, regex`
- Leave others that are already specific.

Do NOT hand-write `llms-full.txt` — Mintlify generates it from page bodies.

- [ ] **Step 3: Verify llms.txt links resolve**

Run: `uv run python - <<'PY'`
```python
import re, pathlib
txt = pathlib.Path('docs/llms.txt').read_text(encoding='utf-8')
links = re.findall(r'\]\((/[^)]+)\)', txt)
missing = [l for l in links if not (pathlib.Path('docs') / (l.lstrip('/') + '.mdx')).exists()]
print("BROKEN:", missing or "none")
PY
```
Expected: `BROKEN: none`

- [ ] **Step 4: Commit**

```bash
git add docs/llms.txt docs/usage/extract-links.mdx docs/api-reference/extract.mdx
git commit -m "docs: add curated llms.txt index and tighten page descriptions"
```

---

### Task 9: Final verification

- [ ] **Step 1: Full suite stays green**

Run: `uv run pytest -q`
Expected: same pass/skip counts as before the change (76 passed, 9 skipped), 0 failures.

- [ ] **Step 2: Re-check every gap fix against source one more time**

Confirm each of the six gap notes (schemes, trailing punctuation, `domain==host`,
code defaults, two-sided `near`, blank query) cites behavior that the live
library still exhibits, using the one-liner commands embedded in Tasks 2–6.

- [ ] **Step 3: Confirm AGENTS.md + docs render**

Run: `uv run python -c "import json; json.load(open('docs/docs.json'))"` (valid JSON, navigation unchanged).
Spot-read `AGENTS.md` and `docs/llms.txt` for accuracy.

- [ ] **Step 4: Final commit if anything is outstanding**

```bash
git add -A
git commit -m "docs: finalize AI-friendly documentation pass"
```

---

## Self-review notes

- **Spec coverage:** AGENTS.md (Task 1) ✓; full English pass — API ref (Tasks 2–4),
  concepts (Task 4), usage (Task 5), intro/quickstart/advanced (Task 6) ✓;
  Russian sync (Task 7) ✓; llms.txt + descriptions (Task 8) ✓; all six gaps fixed
  and each cited to verified output ✓.
- **Placeholders:** none — every expected output is a captured real value.
- **Consistency:** field/term names (`domain`/`host`, `query_params`,
  `require_each_type`, `near`/`window`) match `results.py`/`specs.py` throughout.
```
