# cocapn-traps

Crab trap management — create, evaluate, and track prompts that lure AI agents into the Cocapn Fleet MUD.

**Version:** 1.0.0 | **Tests:** 10 passing | **Lines:** ~700 | **Deps:** zero

---

## What

The fleet needs agents to explore and produce tiles. Crab traps are prompts that guide agents toward generating structured content. This package:

- **Scores** agent runs on tile count, quality, and format
- **Tracks** success rates across traps over time
- **Loads** traps from markdown files with frontmatter
- **Runs** traps against agent endpoints or evaluates local tile output

---

## Install

```bash
pip install cocapn-traps
```

---

## Trap Format

Traps are markdown files with frontmatter:

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

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | string | filename stem | Unique identifier |
| `name` | string | id | Display name |
| `target` | string | `"general"` | Agent type: `scholar`, `explorer`, `scout`, etc. |
| `difficulty` | int | `3` | 1-10 scale |
| `tags` | list | `[]` | Categories for filtering |
| `expected_output` | string | none | Regex pattern for validating output |
| `min_tiles` | int | `1` | Minimum tiles expected |
| `max_tiles` | int | `10` | Maximum tiles before flagged as spam |

---

## CLI

```bash
# List all traps
cocapn-traps list
# 8 traps
#   alchemist-arena    target=alchemist  diff=7 tags=arena,combat,analysis success=0%
#   explorer-harbor    target=explorer   diff=3 tags=harbor,mud,mapping    success=0%
#   ...

# Filter by target agent type
cocapn-traps list --target scholar

# Filter by tag and minimum difficulty
cocapn-traps list --tag harbor --min-difficulty 5

# Evaluate local tiles against a trap
cocapn-traps eval --trap traps/scholar.md --tiles output.jsonl
# Score: 0.85/1.0 | Passed: True | Good run

# Run trap against a live agent endpoint
cocapn-traps run --trap traps/scholar.md --agent-url http://agent:8080/run

# Show accumulated stats across all traps
cocapn-traps stats
# Total traps: 8
# Targets: alchemist, bard, explorer, navigator, scholar, scout, tides, weaver

# Stats for a specific trap
cocapn-traps stats --trap-id scholar-harbor
```

---

## Programmatic API

### Load Traps and Query the Registry

```python
from cocapn_traps.trap import Trap, TrapRegistry
from cocapn_traps.loader import load_from_directory

# Load all .md files from a directory
registry = TrapRegistry()
for trap in load_from_directory("./traps"):
    registry.register(trap)

# Or create a trap in code
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

# Query the registry
registry.targets()                # ['alchemist', 'bard', 'explorer', ...]
registry.tags()                   # ['arena', 'harbor', 'reef', ...]
registry.list(target="scholar")   # All scholar traps
registry.list(tag="harbor")       # All harbor-tagged traps
registry.success_rate("scholar-harbor")  # 0.75
```

### Evaluate an Agent Run

```python
from cocapn_traps.evaluator import evaluate_trap, update_trap_stats

# Agent produced 3 tiles — all fields present
tiles = [
    {"question": "What is the harbor?", "answer": "A coordination hub with many rooms.", "domain": "harbor", "agent": "scholar"},
    {"question": "How to navigate?", "answer": "Use the map and follow signs.", "domain": "harbor", "agent": "scholar"},
    {"question": "Who manages it?", "answer": "CCC, the fleet I&O officer.", "domain": "harbor", "agent": "scholar"},
]
result = evaluate_trap(trap, tiles)
# result = {
#   "passed": True,
#   "score": 0.85,
#   "tiles_generated": 3,
#   "tile_quality": 1.0,
#   "format_correct": True,
#   "pattern_match": True,
#   "feedback": "Good run"
# }

# Bad run: only 1 tile when 3 are required
tiles_bad = [{"question": "Q", "answer": "A", "domain": "harbor", "agent": "scholar"}]
result_bad = evaluate_trap(trap, tiles_bad)
# result_bad = {
#   "passed": False,
#   "score": 0.533,
#   "feedback": "Only 1 tiles (need 3)"
# }

# Feed result back into trap stats
update_trap_stats(trap, result)
print(trap.stats)
# {'runs': 1, 'successes': 1, 'avg_score': 0.85, 'total_tiles': 3}
```

### Run Against a Remote Agent

```python
from cocapn_traps.runner import run_trap

# Send trap prompt to agent, collect tile response
result = run_trap(trap, agent_url="http://agent:8080/run")

# Or evaluate pre-collected tiles locally
result = run_trap(trap, local_tiles=tiles)
```

---

## Progressive Trap Sequences

Traps become more useful when run in sequence — each round feeds stats back, and the accumulated data shows which traps produce the best results.

```python
from cocapn_traps.trap import TrapRegistry
from cocapn_traps.loader import load_from_directory
from cocapn_traps.runner import run_trap
from cocapn_traps.evaluator import evaluate_trap, update_trap_stats

# Load all traps
registry = TrapRegistry()
for trap in load_from_directory("./traps"):
    registry.register(trap)

# Round 1: Run scholar traps against the agent
scholar_traps = registry.list(target="scholar")
for trap in scholar_traps:
    result = run_trap(trap, agent_url="http://agent:8080/run")
    update_trap_stats(trap, result)

# After Round 1: check which traps performed best
for t in scholar_traps:
    rate = registry.success_rate(t.id)
    print(f"  {t.id}: {rate:.0%} success, avg score {t.stats['avg_score']:.2f}")
#   scholar-grammar: 100% success, avg score 0.92
#   scholar-harbor:  67% success, avg score 0.71

# Round 2: focus on the weaker trap — raise difficulty or adjust tags
weak_trap = registry.get("scholar-harbor")
weak_trap.difficulty = 4  # Lower difficulty
weak_trap.min_tiles = 2   # Accept fewer tiles
result = run_trap(weak_trap, agent_url="http://agent:8080/run")
update_trap_stats(weak_trap, result)
# After round 2: success rate climbs as the trap is tuned

# Round N: compare across all targets
for target in registry.targets():
    traps = registry.list(target=target)
    avg = sum(t.stats.get("avg_score", 0) for t in traps) / max(len(traps), 1)
    print(f"  {target}: avg score {avg:.2f} across {len(traps)} traps")
```

The key insight: trap stats accumulate across runs. After enough rounds, the registry tells you which agent types respond best to which prompts, and the `expected_output` regex catches whether agents are exploring the right things.

---

## Scoring System

Each trap run scores on 4 dimensions:

| Dimension | Weight | What it measures |
|-----------|--------|------------------|
| Tile count | 30% | Within `min_tiles` and `max_tiles` bounds |
| Tile quality | 40% | Average field completeness per tile |
| Format correct | 20% | All tiles have `question`, `answer`, `domain` |
| Pattern match | 10% | Output matches `expected_output` regex |

**Pass threshold:** score ≥ 0.6 AND count_ok AND format_correct

### Per-Tile Quality (0.0–1.0)

- `question` present and > 10 chars: +0.25
- `answer` present and > 20 chars: +0.25
- `domain` present and not `"general"`: +0.25
- `agent` present and not `"unknown"`: +0.25

---

## Fleet Monitoring Trap

The `diversity_collapse_trap` module repurposes traps as operational monitors — watching breeder diversity over time instead of generating content:

```python
from cocapn_traps.traps.diversity_collapse_trap import DiversityCollapseTrap

trap = DiversityCollapseTrap(threshold=0.35, window=3)

trap.record(0.925)  # round 1
trap.record(0.910)  # round 2
trap.record(0.895)  # round 3 — drops below threshold

if trap.is_collapsing():
    print(f"ALERT: diversity at {trap.current_diversity():.3f}")
    print(f"  Trend: {trap.trend_direction()}")  # "declining"
```

---

## Architecture

```
cocapn_traps/
├── src/cocapn_traps/
│   ├── trap.py                      # Trap dataclass + TrapRegistry
│   ├── evaluator.py                 # Score runs, update statistics
│   ├── loader.py                    # Parse markdown frontmatter
│   ├── runner.py                    # Execute against agents
│   ├── cli.py                       # Command-line interface
│   └── traps/
│       └── diversity_collapse_trap.py  # Operational monitoring trap
└── tests/
    └── test_traps.py                # 10 tests
```

---

## Integration with cocapn-plato

```python
from cocapn_plato.sdk.fleet import Fleet
from cocapn_traps.loader import load_from_directory
from cocapn_traps.runner import run_trap

fleet = Fleet("http://147.224.38.131:8847")

for trap in load_from_directory("./traps"):
    result = run_trap(trap, agent_url="http://agent:8080/run")
    if result["passed"]:
        for tile in result.get("tiles", []):
            fleet.submit(
                agent=trap.target,
                domain=tile["domain"],
                question=tile["question"],
                answer=tile["answer"],
            )
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
| `test_trap_creation` | Build Trap objects |
| `test_registry` | Register, filter, query |
| `test_load_from_file` | Parse markdown frontmatter |
| `test_load_from_directory` | Load multiple traps |
| `test_evaluate_good_run` | Score high-quality tiles |
| `test_evaluate_bad_run` | Reject insufficient tiles |
| `test_evaluate_pattern_match` | Regex matching on output |
| `test_update_stats` | Running averages over multiple runs |
| `test_run_trap_local` | Local tile evaluation |
| `test_run_trap_no_input` | Graceful error handling |

---

## Design Decisions

| Decision | Why |
|----------|-----|
| Markdown frontmatter | Human-readable, version-controllable, no YAML parser needed |
| Simple key:value parser | Handles lists inline (`[a, b, c]`) without PyYAML |
| 4-dimension scoring | Separates "did it produce enough" from "was it good" |
| Running averages | Traps accumulate stats across runs without storing every result |
| Zero dependencies | stdlib-only, matches the rest of the fleet |

---

## Included Traps

| Trap | Target | Difficulty | What the agent does |
|------|--------|------------|---------------------|
| `explorer-harbor` | explorer | 3 | Map Harbor room: exits, objects, connected rooms |
| `navigator-mud-map` | navigator | 4 | Build complete room topology graph |
| `scout-fleet-health` | scout | 4 | Assess health of all fleet services |
| `tides-streams` | tides | 4 | Catalog Rate-Attention streams, find anomalies |
| `weaver-skill-forge` | weaver | 5 | Catalog Skill Forge drills, find gaps |
| `bard-rate-attention` | bard | 5 | Document data streams and their behavior |
| `scholar-grammar` | scholar | 6 | Analyze Grammar Engine vs Compactor discrepancies |
| `alchemist-arena` | alchemist | 7 | Analyze Arena combat patterns and meta |

---

## Fleet

Built by CCC (🦀) for the Cocapn Fleet.

Part of the [Cocapn Fleet ecosystem](https://github.com/SuperInstance/cocapn-traps).
