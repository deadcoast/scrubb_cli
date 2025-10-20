from __future__ import annotations
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable

def should_ignore(path: Path, patterns: Iterable[str]) -> bool:
    s = str(path)
    name = path.name
    # quick contains or fnmatch on either full path or basename
    for pat in patterns:
        if "*" in pat or "?" in pat or "[" in pat:
            if fnmatch(name, pat) or fnmatch(s, pat):
                return True
        else:
            if pat in s or name == pat:
                return True
    return False