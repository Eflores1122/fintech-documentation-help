"""Accent-insensitive search and evidence snippets."""

from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Flatten whitespace so PDF/DOCX line breaks do not hide phrases."""
    cleaned = text.replace("\x00", " ")
    return _WS.sub(" ", cleaned).strip()


def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def fold_with_map(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    mapping: list[int] = []
    for index, ch in enumerate(text):
        for piece in unicodedata.normalize("NFD", ch.casefold()):
            if unicodedata.category(piece) == "Mn":
                continue
            chars.append(piece)
            mapping.append(index)
    return "".join(chars), mapping


def _is_acronym(phrase: str) -> bool:
    letters = [ch for ch in phrase if ch.isalpha()]
    return (
        bool(letters)
        and all(ch.isupper() for ch in letters)
        and bool(re.fullmatch(r"[A-Z0-9]{2,8}", phrase))
    )


def locate_phrase(text: str, phrase: str) -> tuple[int, int] | None:
    """Return a span in ``text`` where ``phrase`` occurs, ignoring accents/case.

    Short all-caps tokens (INAI, UNE, ARCO, PLD) match on word boundaries so
    they do not fire inside unrelated words.
    """
    if not phrase.strip():
        return None
    folded, mapping = fold_with_map(text)
    needle = fold(phrase)
    if _is_acronym(phrase.strip()):
        match = re.search(rf"\b{re.escape(needle)}\b", folded)
        if match is None:
            return None
        start, end = match.start(), match.end()
    else:
        start = folded.find(needle)
        if start < 0:
            return None
        end = start + len(needle)
    if end == 0 or end - 1 >= len(mapping):
        return None
    return mapping[start], mapping[end - 1] + 1


def phrase_in(text: str, phrase: str) -> bool:
    return locate_phrase(text, phrase) is not None


def snippet(text: str, start: int, end: int, window: int = 90) -> str:
    left = max(0, start - window)
    right = min(len(text), end + window)
    chunk = text[left:right].strip()
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(text) else ""
    return f"{prefix}{chunk}{suffix}"


def quote_grounded(quote: str, documents: list[str], min_len: int = 12) -> bool:
    """True when ``quote`` is a verbatim span of some document (accents ignored)."""
    collapsed = normalize_text(quote)
    if len(fold(collapsed)) < min_len:
        return False
    return any(locate_phrase(document, collapsed) is not None for document in documents)
