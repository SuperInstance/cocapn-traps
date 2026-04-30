"""Run an agent through a trap and capture results.

Connects to PLATO or local endpoints to execute traps.
"""
import json
import urllib.request
from typing import Dict, Any, List
from .trap import Trap
from .evaluator import evaluate_trap, update_trap_stats


def run_trap(trap: Trap, agent_url: str = None, local_tiles: List[Dict[str, Any]] = None, raw_output: str = "") -> Dict[str, Any]:
    """Execute a trap and evaluate the result.
    
    If local_tiles provided, evaluates locally.
    If agent_url provided, sends trap to agent and collects response.
    """
    if local_tiles is not None:
        result = evaluate_trap(trap, local_tiles, raw_output)
        update_trap_stats(trap, result)
        return result
    
    if agent_url:
        # Send trap to agent endpoint
        payload = {
            "prompt": trap.prompt,
            "trap_id": trap.id,
            "target": trap.target,
        }
        try:
            body = json.dumps(payload).encode()
            req = urllib.request.Request(
                agent_url,
                data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
            
            tiles = data.get("tiles", [])
            output = data.get("output", "")
            result = evaluate_trap(trap, tiles, output)
            update_trap_stats(trap, result)
            return result
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "tiles_generated": 0,
                "tile_quality": 0.0,
                "format_correct": False,
                "pattern_match": False,
                "feedback": f"Agent error: {e}",
            }
    
    return {
        "passed": False,
        "score": 0.0,
        "tiles_generated": 0,
        "feedback": "No agent URL or local tiles provided",
    }
