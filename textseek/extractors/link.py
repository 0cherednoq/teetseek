from ..links import find_link_candidates
from ..results import LinkResult
from ..specs import LinkSpec


class LinkExtractor:
    def __init__(self, spec: LinkSpec) -> None:
        self.spec = spec

    def find_all(self, text: str) -> list[LinkResult]:
        return [l for l in find_link_candidates(text) if self._matches(l)]

    def _matches(self, link: LinkResult) -> bool:
        spec = self.spec
        if spec.scheme is not None and link.scheme != spec.scheme:
            return False
        if spec.domain is not None and not self._domain_ok(link.host):
            return False
        if spec.path is not None and link.path != spec.path:
            return False
        if spec.path_contains is not None and spec.path_contains not in link.path:
            return False
        if spec.required_query is not None:
            for key in spec.required_query:
                if key not in link.query_params:
                    return False
        return True

    def _domain_ok(self, host: str) -> bool:
        spec = self.spec
        assert spec.domain is not None
        if host == spec.domain:
            return True
        if spec.allow_subdomains and host.endswith("." + spec.domain):
            return True
        return False
