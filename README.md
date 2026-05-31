# textseek

**English** | [Русский](README.ru.md)

Zero-dependency Python library for searching and extracting structured data —
confirmation codes, links, and arbitrary regex matches — from plain text.

`textseek` is not tied to any source: the text may come from email, SMS, HTML,
an API response, logs, OCR, or anywhere else. Fetching text is your job; pulling
structured values out of it is `textseek`'s.

## Install

```bash
pip install textseek
```

Requires Python 3.12+. No runtime dependencies.

## Quickstart

```python
from textseek import TextSeek, Extract

text = "Your verification code is 123456"

seek = TextSeek(text)
result = seek.extract_one(Extract.code(length=6, digits=True))

print(result.value)  # 123456
```

### Extract a link and inspect its parts

```python
link = TextSeek(text).extract_one(
    Extract.link(domain="example.com")
)
print(link.domain)              # example.com
print(link.path)                # /auth/magic
print(link.query_params["token"][0])
```

### Find by example link

```python
link = TextSeek(text).extract_one(
    Extract.link(sample="https://example.com/auth/magic?token=abc&email=test@example.com")
)
```

### Arbitrary regex

```python
order = TextSeek(text).extract_one(Extract.regex(r"Order ID:\s*([A-Z0-9\-]+)"))
print(order.value)
```

## Methods

| Method | Returns |
|---|---|
| `extract_one(spec)` | one result, or raises `ExtractNotFoundError` |
| `extract_first(spec)` | first result, or `None` |
| `extract_all(spec)` | list of results (possibly empty) |
| `contains(spec)` | `bool` |

See full documentation in `docs/`.
