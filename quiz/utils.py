import re


def normalise_name(name: str) -> str:
    """
    Pure function: trims whitespace and collapses multiple spaces.
    Example: "  Nazish   Jujara " -> "Nazish Jujara"
    """
    return " ".join((name or "").strip().split())


def is_valid_name(name: str) -> bool:
    """
    Pure function: validates a user name.

    Rules:
    - 2 to 40 characters
    - letters/spaces/hyphen/apostrophe allowed
    - must start with a letter
    """
    cleaned = normalise_name(name)
    if not (2 <= len(cleaned) <= 40):
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z\s'\-]*", cleaned))


def score_percentage(score: int, total: int) -> int:
    """
    Pure function: returns score as a percentage (0-100).
    Raises ValueError if inputs are invalid.
    """
    if total <= 0:
        raise ValueError("Total must be greater than 0.")
    if score < 0 or score > total:
        raise ValueError("Score must be between 0 and total.")
    return round((score / total) * 100)