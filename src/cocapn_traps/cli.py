#!/usr/bin/env python3
"""cocapn-traps — CLI for managing and evaluating crab traps.

Usage:
    cocapn-traps list --target scholar
    cocapn-traps eval --trap traps/scholar.md --tiles tiles.jsonl
    cocapn-traps run --trap traps/scholar.md --agent http://agent:8080/run
    cocapn-traps stats
"""
import argparse
import json
import sys
from pathlib import Path

from cocapn_traps.trap import TrapRegistry
from cocapn_traps.loader import load_from_directory, load_from_file
from cocapn_traps.runner import run_trap


def main():
    parser = argparse.ArgumentParser(prog="cocapn-traps", description="Crab trap manager")
    parser.add_argument("--traps-dir", default="./traps", help="Directory containing trap .md files")
    sub = parser.add_subparsers(dest="cmd")

    # list
    ls = sub.add_parser("list", help="List traps")
    ls.add_argument("--target", help="Filter by target agent type")
    ls.add_argument("--tag", help="Filter by tag")
    ls.add_argument("--min-difficulty", type=int, help="Minimum difficulty")

    # eval
    ev = sub.add_parser("eval", help="Evaluate tiles against a trap")
    ev.add_argument("--trap", required=True, help="Path to trap .md file")
    ev.add_argument("--tiles", required=True, help="Path to tiles JSONL file")
    ev.add_argument("--output", help="Output file for result (default: stdout)")

    # run
    run = sub.add_parser("run", help="Run a trap against an agent")
    run.add_argument("--trap", required=True, help="Path to trap .md file")
    run.add_argument("--agent-url", help="Agent endpoint URL")
    run.add_argument("--tiles", help="Local tiles JSONL file (instead of agent)")

    # stats
    st = sub.add_parser("stats", help="Trap statistics")
    st.add_argument("--trap-id", help="Show stats for specific trap")

    args = parser.parse_args()

    registry = TrapRegistry()
    trap_dir = Path(args.traps_dir)
    if trap_dir.exists():
        for t in load_from_directory(str(trap_dir)):
            registry.register(t)

    if args.cmd == "list":
        traps = registry.list(target=args.target, tag=args.tag, min_difficulty=args.min_difficulty)
        print(f"{len(traps)} traps")
        for t in traps:
            rate = registry.success_rate(t.id) * 100
            print(f"  {t.id:20} target={t.target:10} diff={t.difficulty} tags={','.join(t.tags)} success={rate:.0f}%")

    elif args.cmd == "eval":
        trap = load_from_file(args.trap)
        tiles = []
        with open(args.tiles) as f:
            for line in f:
                if line.strip():
                    tiles.append(json.loads(line))
        result = run_trap(trap, local_tiles=tiles)
        out = sys.stdout if not args.output else open(args.output, "w")
        json.dump(result, out, indent=2)
        if args.output:
            out.close()
        print(f"\nScore: {result['score']}/1.0 | Passed: {result['passed']} | {result['feedback']}")

    elif args.cmd == "run":
        trap = load_from_file(args.trap)
        if args.tiles:
            tiles = []
            with open(args.tiles) as f:
                for line in f:
                    if line.strip():
                        tiles.append(json.loads(line))
            result = run_trap(trap, local_tiles=tiles)
        else:
            result = run_trap(trap, agent_url=args.agent_url)
        print(json.dumps(result, indent=2))

    elif args.cmd == "stats":
        if args.trap_id:
            trap = registry.get(args.trap_id)
            if trap:
                print(f"Trap: {trap.name}")
                print(f"Stats: {json.dumps(trap.stats, indent=2)}")
                print(f"Success rate: {registry.success_rate(trap.id)*100:.1f}%")
            else:
                print(f"Trap {args.trap_id} not found")
        else:
            print(f"Total traps: {len(registry.traps)}")
            print(f"Targets: {', '.join(registry.targets())}")
            print(f"Tags: {', '.join(registry.tags())}")
            for t in registry.list():
                if t.stats:
                    print(f"  {t.id}: {t.stats.get('runs', 0)} runs, {registry.success_rate(t.id)*100:.0f}% success")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
