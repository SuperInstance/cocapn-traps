"""Crab Trap — A prompt designed to lure an AI agent into generating valuable tiles.

Maximum capability in minimum lines.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class Trap:
    """A single crab trap."""
    id: str
    name: str
    prompt: str
    target: str  # What kind of agent this trap is for (e.g., "scholar", "explorer")
    difficulty: int = 3  # 1-10
    tags: List[str] = field(default_factory=list)
    expected_output: Optional[str] = None  # Regex or description of good output
    min_tiles: int = 1  # Minimum tiles expected from a good run
    max_tiles: int = 10  # Maximum tiles before considered spam
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "prompt": self.prompt,
            "target": self.target,
            "difficulty": self.difficulty,
            "tags": self.tags,
            "expected_output": self.expected_output,
            "min_tiles": self.min_tiles,
            "max_tiles": self.max_tiles,
            "stats": self.stats,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Trap":
        return cls(
            id=d["id"],
            name=d["name"],
            prompt=d["prompt"],
            target=d.get("target", "general"),
            difficulty=d.get("difficulty", 3),
            tags=d.get("tags", []),
            expected_output=d.get("expected_output"),
            min_tiles=d.get("min_tiles", 1),
            max_tiles=d.get("max_tiles", 10),
            stats=d.get("stats", {}),
        )


class TrapRegistry:
    """Store and query traps."""

    def __init__(self):
        self.traps: Dict[str, Trap] = {}

    def register(self, trap: Trap):
        self.traps[trap.id] = trap

    def get(self, trap_id: str) -> Optional[Trap]:
        return self.traps.get(trap_id)

    def list(self, target: str = None, tag: str = None, min_difficulty: int = None) -> List[Trap]:
        results = list(self.traps.values())
        if target:
            results = [t for t in results if t.target == target]
        if tag:
            results = [t for t in results if tag in t.tags]
        if min_difficulty is not None:
            results = [t for t in results if t.difficulty >= min_difficulty]
        return results

    def targets(self) -> List[str]:
        return sorted(set(t.target for t in self.traps.values()))

    def tags(self) -> List[str]:
        all_tags = []
        for t in self.traps.values():
            all_tags.extend(t.tags)
        return sorted(set(all_tags))

    def success_rate(self, trap_id: str) -> float:
        trap = self.traps.get(trap_id)
        if not trap or not trap.stats:
            return 0.0
        runs = trap.stats.get("runs", 0)
        successes = trap.stats.get("successes", 0)
        return successes / runs if runs > 0 else 0.0
