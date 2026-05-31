import re
from dataclasses import dataclass

from .errors import InvalidCodeSpecError, RegexExtractError
from .links import parse_sample


@dataclass(slots=True, frozen=True)
class CodeSpec:
    length: int | None
    min_length: int | None
    max_length: int | None
    digits: bool
    alphabet: bool
    symbols: bool
    uppercase: bool
    lowercase: bool
    require_each_type: bool
    near: str | None
    window: int
    pattern: str | None


@dataclass(slots=True, frozen=True)
class LinkSpec:
    scheme: str | None
    domain: str | None
    path: str | None
    path_contains: str | None
    required_query: tuple[str, ...] | None
    allow_subdomains: bool


@dataclass(slots=True, frozen=True)
class RegexSpec:
    pattern: str
    flags: int


ExtractSpec = CodeSpec | LinkSpec | RegexSpec


class Extract:
    @staticmethod
    def code(
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
    ) -> CodeSpec:
        if pattern is None:
            if length is not None and (min_length is not None or max_length is not None):
                raise InvalidCodeSpecError(
                    "Нельзя сочетать length с min_length/max_length"
                )
            if length is not None and length < 1:
                raise InvalidCodeSpecError("length должен быть >= 1")
            if min_length is not None and min_length < 1:
                raise InvalidCodeSpecError("min_length должен быть >= 1")
            if (
                min_length is not None
                and max_length is not None
                and min_length > max_length
            ):
                raise InvalidCodeSpecError("min_length не может быть больше max_length")
            if not (digits or alphabet or symbols):
                raise InvalidCodeSpecError(
                    "Нужно разрешить хотя бы один тип символов"
                )
            if alphabet and not (uppercase or lowercase):
                raise InvalidCodeSpecError(
                    "alphabet=True требует uppercase или lowercase"
                )
        if window < 0:
            raise InvalidCodeSpecError("window не может быть отрицательным")
        return CodeSpec(
            length=length,
            min_length=min_length,
            max_length=max_length,
            digits=digits,
            alphabet=alphabet,
            symbols=symbols,
            uppercase=uppercase,
            lowercase=lowercase,
            require_each_type=require_each_type,
            near=near,
            window=window,
            pattern=pattern,
        )

    @staticmethod
    def link(
        sample: str | None = None,
        scheme: str | None = None,
        domain: str | None = None,
        path: str | None = None,
        path_contains: str | None = None,
        required_query: list[str] | None = None,
        allow_subdomains: bool = False,
    ) -> LinkSpec:
        if sample is not None:
            s_scheme, s_domain, s_path, s_keys = parse_sample(sample)
            scheme = scheme if scheme is not None else s_scheme
            domain = domain if domain is not None else s_domain
            path = path if path is not None else s_path
            if required_query is None and s_keys is not None:
                required_query = list(s_keys)
        return LinkSpec(
            scheme=scheme,
            domain=domain,
            path=path,
            path_contains=path_contains,
            required_query=tuple(required_query) if required_query is not None else None,
            allow_subdomains=allow_subdomains,
        )

    @staticmethod
    def regex(pattern: str, flags: int = 0) -> RegexSpec:
        try:
            re.compile(pattern, flags)
        except re.error as exc:
            raise RegexExtractError(f"Некорректный regex-паттерн: {exc}") from exc
        return RegexSpec(pattern=pattern, flags=flags)
