from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class CodeResult:
    value: str
    start: int
    end: int


@dataclass(slots=True, frozen=True)
class LinkResult:
    value: str
    start: int
    end: int

    scheme: str
    domain: str
    host: str
    port: int | None
    path: str
    query: str
    fragment: str

    query_params: dict[str, list[str]]


@dataclass(slots=True, frozen=True)
class RegexResult:
    value: str
    start: int
    end: int
    groups: tuple[str, ...]
    groupdict: dict[str, str]


ExtractResult = CodeResult | LinkResult | RegexResult
