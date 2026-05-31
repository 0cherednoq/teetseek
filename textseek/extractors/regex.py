import re

from ..results import RegexResult
from ..specs import RegexSpec


class RegexExtractor:
    def __init__(self, spec: RegexSpec) -> None:
        # Pattern validity is guaranteed by Extract.regex; recompile here.
        self.pattern = re.compile(spec.pattern, spec.flags)

    def find_all(self, text: str) -> list[RegexResult]:
        results: list[RegexResult] = []
        has_groups = self.pattern.groups > 0
        for m in self.pattern.finditer(text):
            value = m.group(1) if has_groups else m.group(0)
            results.append(
                RegexResult(
                    value=value if value is not None else "",
                    start=m.start(),
                    end=m.end(),
                    groups=m.groups(),
                    groupdict=m.groupdict(),
                )
            )
        return results
