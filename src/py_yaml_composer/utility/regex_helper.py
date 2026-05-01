import re


class RegexHelper:
    @staticmethod
    def match(pattern: str, string: str) -> list[str]:
        match: re.Match[str] | None = re.match(pattern, string)
        if not match:
            return []

        arguments: list[str] = []
        for g in match.groups():
            arguments.append(g)
        return arguments
