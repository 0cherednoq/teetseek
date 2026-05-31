import re
from urllib.parse import parse_qs, urlsplit

from .errors import InvalidSampleLinkError
from .results import LinkResult

_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_TRAILING = ".,;:!?)]}>\"'"


def _port_of(parts) -> int | None:
    try:
        return parts.port
    except ValueError:
        return None


def parse_link(url: str, start: int, end: int) -> LinkResult:
    parts = urlsplit(url)
    host = parts.hostname or ""
    return LinkResult(
        value=url,
        start=start,
        end=end,
        scheme=parts.scheme,
        domain=host,
        host=host,
        port=_port_of(parts),
        path=parts.path,
        query=parts.query,
        fragment=parts.fragment,
        query_params=parse_qs(parts.query),
    )


def find_link_candidates(text: str) -> list[LinkResult]:
    results: list[LinkResult] = []
    for m in _URL_RE.finditer(text):
        stripped = m.group().rstrip(_TRAILING)
        results.append(parse_link(stripped, m.start(), m.start() + len(stripped)))
    return results


def parse_sample(sample: str) -> tuple[str, str, str | None, tuple[str, ...] | None]:
    parts = urlsplit(sample)
    if not parts.scheme or not parts.hostname:
        raise InvalidSampleLinkError(f"Некорректный пример ссылки: {sample!r}")
    keys = tuple(parse_qs(parts.query).keys()) or None
    return parts.scheme, parts.hostname, (parts.path or None), keys
