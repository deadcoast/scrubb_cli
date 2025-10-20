from __future__ import annotations
import re
from pathlib import Path
from typing import Dict, Iterable, Tuple

from .ignore import should_ignore

EMOJI_REGEX = re.compile(
    r"["
    "\U0001f600-\U0001f64f"  # Emoticons
    "\U0001f300-\U0001f5ff"  # Symbols & Pictographs
    "\U0001f680-\U0001f6ff"  # Transport & Map
    "\U0001f1e0-\U0001f1ff"  # Flags
    "\U00002702-\U000027b0"  # Dingbats
    "\U000024c2-\U0001f251"  # Enclosed chars
    "\U0001f900-\U0001f9ff"  # Supplemental
    "\U00002600-\U000026ff"  # Misc symbols
    "\U00002700-\U000027bf"  # Dingbats extended
    "\U0001f3fb-\U0001f3ff"  # Skin tones
    "\U0001f9b0-\U0001f9b3"  # Hair components
    r"]+",
    flags=re.UNICODE,
)

class RunStats:
    """Ephemeral per-run stats (printed at end of run)."""
    def __init__(self) -> None:
        self.files_processed = 0
        self.files_modified  = 0
        self.files_skipped   = 0
        self.errors          = 0
        self.emojis_removed  = 0
        self.scoped_scrub: Dict[str, int] = {}  # emoji -> count
        self.processed_files: list[str] = []    # list of files that were processed
        self.modified_files: list[str] = []     # list of files that were modified
        self.skipped_files: list[str] = []      # list of files that were skipped
        self.error_files: list[str] = []        # list of files that had errors

    def bump_emoji(self, token: str, n: int) -> None:
        # token may contain multiple emojis (e.g., consecutive); attribute n to the token
        self.scoped_scrub[token] = self.scoped_scrub.get(token, 0) + n

    def to_dict(self) -> Dict[str, int]:
        return {
            "files_processed": self.files_processed,
            "files_modified":  self.files_modified,
            "files_skipped":   self.files_skipped,
            "errors":          self.errors,
            "emojis_removed":  self.emojis_removed,
        }

class Scrubber:
    def __init__(self, ignore_patterns: Iterable[str], text_extensions: Iterable[str]) -> None:
        self.ignore_patterns = set(ignore_patterns)
        self.text_exts = set(x.lower() for x in text_extensions)
        self.run = RunStats()

    def _is_textish(self, p: Path) -> bool:
        if p.is_dir():
            return False
        suf = p.suffix.lower()
        name = p.name.lower()
        return (suf in self.text_exts) or (name in self.text_exts)

    def _remove_emojis(self, text: str) -> Tuple[str, int, Dict[str, int]]:
        # Count length delta for total removed; also tally token sequences
        matches = list(EMOJI_REGEX.finditer(text))
        token_counts: Dict[str, int] = {}
        for m in matches:
            token = m.group(0)
            token_counts[token] = token_counts.get(token, 0) + len(token)
        cleaned = EMOJI_REGEX.sub("", text)
        removed = len(text) - len(cleaned)
        return cleaned, removed, token_counts

    def scrub_file(self, file_path: Path) -> None:
        file_path_str = str(file_path)
        try:
            if should_ignore(file_path, self.ignore_patterns) or not self._is_textish(file_path):
                self.run.files_skipped += 1
                self.run.skipped_files.append(file_path_str)
                return
            content = file_path.read_text(encoding="utf-8")
            cleaned, removed, token_counts = self._remove_emojis(content)
            self.run.files_processed += 1
            self.run.processed_files.append(file_path_str)
            if removed > 0:
                file_path.write_text(cleaned, encoding="utf-8")
                self.run.files_modified += 1
                self.run.modified_files.append(file_path_str)
                self.run.emojis_removed += removed
                for tok, cnt in token_counts.items():
                    self.run.bump_emoji(tok, cnt)
            else:
                self.run.files_skipped += 1
                self.run.skipped_files.append(file_path_str)
        except Exception:
            self.run.errors += 1
            self.run.error_files.append(file_path_str)

    def scrub_dir(self, root: Path) -> None:
        for p in root.rglob("*"):
            if p.is_file():
                self.scrub_file(p)