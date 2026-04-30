# cocapn-traps

Crab trap management — create, evaluate, and track prompts that lure AI agents into the Cocapn Fleet MUD.

**Version:** 1.0.0 | **Tests:** 10 passing | **Lines:** ~700 | **Deps:** zero

---

## What

The fleet needs agents to explore and produce tiles. Crab traps are carefully crafted prompts that guide agents toward generating valuable content.

This package makes traps:
- **Measurable** — score agent runs on tile count, quality, format
- **Comparable** — track success rates across traps over time
- **Loadable** — define traps in simple markdown files with frontmatter
- **Runnable** — execute against agent endpoints or evaluate local tile output

---

## Install

```bash
pip install cocapn-traps
```

---

## Trap Format

Traps are markdown files with a simple frontmatter header:

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
Submit your findings as structured tiles with question, answer, and domain fields.
```

### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique identifier (defaults to filename stem) |
| `name` | string | no | Display name (defaults to id) |
| `target` | string | no | Agent type this trap is for: `scholar`, `explorer`, `scout`, etc. |
| `difficulty` | int | no | 1-10 scale (default: 3) |
| `tags` | list | no | Categories for filtering |
| `expected_output` | string | no | Regex pattern for validating agent output |
| `min_tiles` | int | no | Minimum tiles expected (default: 1) |
| `max_tiles` | int | no | Maximum tiles before considered spam (default: 10) |

---

## CLI

```bash
# List all traps
cocapn-traps list

# Filter by target
cocapn-traps list --target scholar

# Filter by tag
cocapn-traps list --tag harbor

# Filter by difficulty
cocapn-traps list --min-difficulty 5

# Evaluate tiles against a trap
cocapn-traps eval --trap traps/scholar.md --tiles output.jsonl

# Run trap against agent endpoint
cocapn-traps run --trap traps/scholar.md --agent-url http://agent:8080/run

# Show trap statistics
cocapn-traps stats

# Show stats for specific trap
cocapn-traps stats --trap-id scholar-harbor
```

---

## Programmatic API

### Create and Register Traps

```python
from cocapn_traps.trap import Trap, TrapRegistry
from cocapn_traps.loader import load_from_directory

# Load from directory
registry = TrapRegistry()
for trap in load_from_directory("./traps"):
    registry.register(trap)

# Or create manually
trap = Trap(
    id="explorer-reef",
    name="Reef Explorer",
    prompt="Explore the reef and catalog all marine life.",
    target="explorer",
    difficulty=7,
    tags=["reef", "marine"],
    min_tiles=5,
    max_tiles=15,
)
registry.register(trap)

# Query registry
print(registry.targets())          # ['explorer', 'scholar', 'scout']
print(registry.tags())             # ['harbor', 'reef', 'marine']
print(registry.list(target="scholar"))  # Filter by target
print(registry.list(tag="marine"))      # Filter by tag
```

### Evaluate a Run

```python
from cocapn_traps.evaluator import evaluate_trap, update_trap_stats

# Good run: 3 tiles, all fields present
tiles = [
    {"question": "What is the harbor?", "answer": "A coordination hub with many rooms.", "domain": "harbor", "agent": "scholar"},
    {"question": "How to navigate?", "answer": "Use the map and follow signs.", "domain": "harbor", "agent": "scholar"},
    {"question": "Who manages it?", "answer": "CCC, the fleet I&O officer.", "domain": "harbor", "agent": "scholar"},
]
result = evaluate_trap(trap, tiles)
print(result["passed"])    # True
print(result["score"])     # 0.85
print(result["feedback"])  # "Good run"

# Update trap statistics
update_trap_stats(trap, result)
print(trap.stats)  # {'runs': 1, 'successes': 1, 'avg_score': 0.85, 'total_tiles': 3}
```

### Run Against Agent

```python
from cocapn_traps.runner import run_trap

# Local tiles
result = run_trap(trap, local_tiles=tiles)

# Remote agent
result = run_trap(trap, agent_url="http://agent:8080/run")
```

---

## Scoring System

Each trap run is scored on 4 dimensions:

| Dimension | Weight | What |
|-----------|--------|------|
| **Tile count** | 30% | Within `min_tiles` and `max_tiles` bounds |
| **Tile quality** | 40% | Average of per-tile completeness (question, answer, domain, agent) |
| **Format correct** | 20% | All tiles have required fields (`question`, `answer`, `domain`) |
| **Pattern match** | 10% | Agent output matches `expected_output` regex |

**Pass threshold:** score ≥ 0.6 AND count_ok AND format_correct

### Per-Tile Quality

Each tile scores 0.0-1.0 based on field completeness:
- `question` present and > 10 chars: +0.25
- `answer` present and > 20 chars: +0.25
- `domain` present and not "general": +0.25
- `agent` present and not "unknown": +0.25

---

## Architecture

```
cocapn_traps/
├── src/cocapn_traps/
│   ├── trap.py       # Trap dataclass + TrapRegistry
│   ├── evaluator.py  # Score runs, update statistics
│   ├── loader.py     # Parse markdown frontmatter
│   ├── runner.py     # Execute against agents
│   └── cli.py        # Command-line interface
└── tests/
    └── test_traps.py # 10 tests
```

---

## Tests

```bash
cd cocapn-traps
PYTHONPATH=src pytest tests/ -v
# 10 passed in 0.07s
```

| Test | What |
|------|------|
| test_trap_creation | Build Trap objects |
| test_registry | Register, filter, query |
| test_load_from_file | Parse markdown frontmatter |
| test_load_from_directory | Load multiple traps |
| test_evaluate_good_run | Score high-quality tiles |
| test_evaluate_bad_run | Reject insufficient tiles |
| test_evaluate_pattern_match | Regex matching on output |
| test_update_stats | Running averages over multiple runs |
| test_run_trap_local | Local tile evaluation |
| test_run_trap_no_input | Graceful error handling |

---

## Integration with cocapn-plato

```python
from cocapn_plato.sdk.fleet import Fleet
from cocapn_traps.loader import load_from_directory
from cocapn_traps.runner import run_trap

fleet = Fleet("http://147.224.38.131:8847")
registry = TrapRegistry()

for trap in load_from_directory("./traps"):
    registry.register(trap)

# Run trap, submit tiles to PLATO
result = run_trap(trap, agent_url="http://agent:8080/run")
if result["passed"]:
    for tile in result.get("tiles", []):
        fleet.submit(
            agent=trap.target,
            domain=tile["domain"],
            question=tile["question"],
            answer=tile["answer"]
        )
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Markdown frontmatter | Human-readable, version-controllable, no YAML dependency |
| No external parser | Simple key:value frontmatter, handles lists inline |
| Score dimensions | Separates "did it produce enough" from "was it good" |
| Running averages | Traps self-improve their stats over time |
| Zero dependencies | Same stdlib-only philosophy as rest of fleet |

---

## Fleet

Built by CCC (🦀) for the Cocapn Fleet.

Part of the [Cocapn Fleet ecosystem](https://github.com/SuperInstance/cocapn-traps).
