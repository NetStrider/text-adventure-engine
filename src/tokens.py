"""Token extraction utilities.

Narrative text can contain interactive/highlight tokens in the form [[token_name]].
This module exposes a helper to extract those for future UI layers or validation.
"""
from __future__ import annotations

from typing import List
import re

TOKEN_PATTERN = re.compile(r"\[\[([A-Za-z0-9_\-]+)\]\]")

def extract_tokens(text: str) -> List[str]:
    """Return list of unique token strings in order of first appearance."""
    seen: List[str] = []
    for match in TOKEN_PATTERN.finditer(text):
        tok = match.group(1)
        if tok not in seen:
            seen.append(tok)
    return seen

__all__ = ["extract_tokens", "TOKEN_PATTERN"]
