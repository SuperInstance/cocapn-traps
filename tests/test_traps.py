"""Tests for cocapn-traps."""
import json
import tempfile
import os
from pathlib import Path

from cocapn_traps.trap import Trap, TrapRegistry
from cocapn_traps.loader import load_from_file, load_from_directory
from cocapn_traps.evaluator import evaluate_trap, update_trap_stats
from cocapn_traps.runner import run_trap


def test_trap_creation():
    t = Trap(
        id="test-trap",
        name="Test Trap",
        prompt="Explore the harbor and report findings.",
        target="scholar",
        difficulty=5,
        tags=["harbor", "exploration"],
        min_tiles=2,
        max_tiles=5,
    )
    assert t.id == "test-trap"
    assert t.difficulty == 5
    assert t.tags == ["harbor", "exploration"]


def test_registry():
    registry = TrapRegistry()
    t1 = Trap(id="t1", name="Trap 1", prompt="P1", target="scholar", tags=["easy"])
    t2 = Trap(id="t2", name="Trap 2", prompt="P2", target="explorer", tags=["easy", "hard"])
    registry.register(t1)
    registry.register(t2)
    
    assert len(registry.list()) == 2
    assert len(registry.list(target="scholar")) == 1
    assert len(registry.list(tag="hard")) == 1
    assert registry.targets() == ["explorer", "scholar"]
    assert registry.tags() == ["easy", "hard"]


def test_load_from_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("""---
id: harbor-explorer
target: explorer
difficulty: 3
tags: [harbor, map]
min_tiles: 1
max_tiles: 3
---

Explore the Harbor room. List all objects and exits.
""")
        path = f.name
    try:
        trap = load_from_file(path)
        assert trap.id == "harbor-explorer"
        assert trap.target == "explorer"
        assert trap.difficulty == 3
        assert trap.tags == ["harbor", "map"]
        assert "Explore the Harbor" in trap.prompt
    finally:
        os.unlink(path)


def test_load_from_directory():
    with tempfile.TemporaryDirectory() as d:
        Path(d, "trap1.md").write_text("""---
id: t1
target: scholar
---

Prompt 1
""")
        Path(d, "trap2.md").write_text("""---
id: t2
target: explorer
---

Prompt 2
""")
        traps = load_from_directory(d)
        assert len(traps) == 2
        ids = {t.id for t in traps}
        assert ids == {"t1", "t2"}


def test_evaluate_good_run():
    trap = Trap(
        id="test",
        name="Test",
        prompt="P",
        target="scholar",
        min_tiles=1,
        max_tiles=5,
    )
    tiles = [
        {"question": "What is the harbor?", "answer": "A coordination hub with many rooms.", "domain": "harbor", "agent": "scholar"},
        {"question": "How to navigate?", "answer": "Use the map and follow signs.", "domain": "harbor", "agent": "scholar"},
    ]
    result = evaluate_trap(trap, tiles)
    assert result["passed"] is True
    assert result["score"] > 0.6
    assert result["tiles_generated"] == 2
    assert result["format_correct"] is True


def test_evaluate_bad_run():
    trap = Trap(
        id="test",
        name="Test",
        prompt="P",
        target="scholar",
        min_tiles=3,
        max_tiles=5,
    )
    tiles = [
        {"question": "Q", "answer": "A", "domain": "harbor", "agent": "scholar"},
    ]
    result = evaluate_trap(trap, tiles)
    assert result["passed"] is False
    assert result["score"] < 0.6
    assert "Only 1 tiles" in result["feedback"]


def test_evaluate_pattern_match():
    trap = Trap(
        id="test",
        name="Test",
        prompt="P",
        target="scholar",
        expected_output="explored|visited",
    )
    result = evaluate_trap(trap, [], raw_output="I explored the room and visited all exits.")
    assert result["pattern_match"] is True
    
    result2 = evaluate_trap(trap, [], raw_output="I did nothing.")
    assert result2["pattern_match"] is False


def test_update_stats():
    trap = Trap(id="test", name="Test", prompt="P", target="scholar")
    result = {"passed": True, "score": 0.8, "tiles_generated": 3}
    update_trap_stats(trap, result)
    assert trap.stats["runs"] == 1
    assert trap.stats["successes"] == 1
    assert trap.stats["avg_score"] == 0.8
    
    result2 = {"passed": False, "score": 0.3, "tiles_generated": 1}
    update_trap_stats(trap, result2)
    assert trap.stats["runs"] == 2
    assert trap.stats["successes"] == 1
    assert trap.stats["avg_score"] == 0.55  # (0.8 + 0.3) / 2


def test_run_trap_local():
    trap = Trap(id="test", name="Test", prompt="P", target="scholar")
    tiles = [{"question": "Q", "answer": "A", "domain": "harbor", "agent": "scholar"}]
    result = run_trap(trap, local_tiles=tiles)
    assert "passed" in result
    assert "score" in result


def test_run_trap_no_input():
    trap = Trap(id="test", name="Test", prompt="P", target="scholar")
    result = run_trap(trap)
    assert result["passed"] is False
    assert "No agent URL" in result["feedback"]
