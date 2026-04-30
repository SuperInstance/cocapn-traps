"""Load traps from markdown files.

Parses simple key: value frontmatter without external dependencies.
"""
import re
from pathlib import Path
from typing import List, Any
from .trap import Trap


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_value(val: str) -> Any:
    """Parse a frontmatter value string."""
    val = val.strip()
    if val.startswith("[") and val.endswith("]"):
        # List: [a, b, c]
        return [v.strip().strip('"\'') for v in val[1:-1].split(",") if v.strip()]
    if val.isdigit():
        return int(val)
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    return val


def _parse_frontmatter(text: str) -> dict:
    """Parse simple key: value frontmatter."""
    meta = {}
    for line in text.split("\n"):
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = _parse_value(val)
    return meta


def load_from_file(path: str) -> Trap:
    """Load a single trap from a markdown file."""
    with open(path) as f:
        content = f.read()
    
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError(f"No frontmatter found in {path}")
    
    meta = _parse_frontmatter(match.group(1))
    body = match.group(2).strip()
    
    # Extract ID from filename or frontmatter
    trap_id = meta.get("id") or Path(path).stem
    
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    
    return Trap(
        id=trap_id,
        name=meta.get("name", trap_id),
        prompt=body,
        target=meta.get("target", "general"),
        difficulty=meta.get("difficulty", 3),
        tags=tags,
        expected_output=meta.get("expected_output"),
        min_tiles=meta.get("min_tiles", 1),
        max_tiles=meta.get("max_tiles", 10),
    )


def load_from_directory(path: str) -> List[Trap]:
    """Load all traps from a directory."""
    traps = []
    for f in Path(path).glob("*.md"):
        try:
            traps.append(load_from_file(str(f)))
        except Exception as e:
            print(f"Warning: failed to load {f}: {e}")
    return traps
