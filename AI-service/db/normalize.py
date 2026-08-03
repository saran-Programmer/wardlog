import re

_HONORIFIC_PATTERN = re.compile(
    r"^(mr|mrs|ms|miss|master|dr|prof)\.?\s+", re.IGNORECASE
)


def strip_honorifics(name: str) -> str:
    """Strip a leading honorific/title (Mr., Mrs., Dr., ...) from a name."""
    cleaned = _HONORIFIC_PATTERN.sub("", name).strip()
    return cleaned or name


def normalize_key(text: str) -> str:
    """Normalize a name into a stable matching key: lowercase, no spaces."""
    return text.lower().replace(" ", "")
