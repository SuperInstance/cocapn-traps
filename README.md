# cocapn-traps

Crab trap management — create, evaluate, and track prompts that lure AI agents.

## Install

```bash
pip install cocapn-traps
```

## What

The fleet needs agents to explore and produce tiles. Crab traps are carefully crafted prompts that guide agents toward generating valuable content.

This package makes traps:
- **Measurable**: score agent runs on tile count, quality, format
- **Comparable**: track success rates across traps
- **Loadable**: define traps in simple markdown files

## Trap Format

```markdown
---
id: scholar-harbor
target: scholar
difficulty: 5
tags: [harbor, exploration]
expected_output: "explored|visited|found"
min_tiles: 3
max_tiles: 8
---

You are a scholar exploring the Harbor room of the Cocapn Fleet MUD.
Your task: examine every object, map every exit, and document what you find.
Submit your findings as structured tiles.
```

## Usage

### CLI

```bash
# List traps
cocapn-traps list --target scholar

# Evaluate tiles against a trap
cocapn-traps eval --trap traps/scholar.md --tiles output.jsonl

# Run trap against agent endpoint
cocapn-traps run --trap traps/scholar.md --agent-url http://agent:8080/run

# Stats
cocapn-traps stats
```

### Programmatic

```python
from cocapn_traps.trap import Trap, TrapRegistry
from cocapn_traps.loader import load_from_directory
from cocapn_traps.evaluator import evaluate_trap

registry = TrapRegistry()
for trap in load_from_directory("./traps"):
    registry.register(trap)

# Evaluate a run
trap = registry.get("scholar-harbor")
tiles = [{"question": "Q", "answer": "A", "domain": "harbor", "agent": "scholar"}]
result = evaluate_trap(trap, tiles)
print(result["passed"], result["score"])  # True, 0.85
```

## Version

1.0.0

## Fleet

Built by CCC (🦀) for the Cocapn Fleet.
