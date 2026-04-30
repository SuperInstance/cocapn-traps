"""Evaluate how well an agent performed on a trap.

Scores based on: tile count, output quality, format correctness, engagement.
"""
import re
from typing import Dict, Any, List
from .trap import Trap


def evaluate_trap(trap: Trap, tiles: List[Dict[str, Any]], raw_output: str = "") -> Dict[str, Any]:
    """Score an agent's run on a trap.
    
    Returns dict with:
        - passed: bool
        - score: float (0-1)
        - tiles_generated: int
        - tile_quality: float (avg quality of tiles)
        - format_correct: bool
        - feedback: str
    """
    tiles_count = len(tiles)
    
    # Check tile count
    count_ok = trap.min_tiles <= tiles_count <= trap.max_tiles
    
    # Check tile quality
    qualities = []
    for tile in tiles:
        q = 0.0
        if tile.get("question") and len(tile["question"]) > 10:
            q += 0.25
        if tile.get("answer") and len(tile["answer"]) > 20:
            q += 0.25
        if tile.get("domain") and tile["domain"] != "general":
            q += 0.25
        if tile.get("agent") and tile["agent"] != "unknown":
            q += 0.25
        qualities.append(q)
    
    avg_quality = sum(qualities) / len(qualities) if qualities else 0.0
    
    # Check format correctness (all tiles have required fields)
    format_correct = all(
        tile.get("question") and tile.get("answer") and tile.get("domain")
        for tile in tiles
    )
    
    # Check expected output pattern
    pattern_match = True
    if trap.expected_output and raw_output:
        try:
            pattern_match = bool(re.search(trap.expected_output, raw_output, re.IGNORECASE))
        except re.error:
            pattern_match = trap.expected_output.lower() in raw_output.lower()
    
    # Overall score
    score = 0.0
    if count_ok:
        score += 0.3
    score += avg_quality * 0.4
    if format_correct:
        score += 0.2
    if pattern_match:
        score += 0.1
    
    passed = score >= 0.6 and count_ok and format_correct
    
    # Feedback
    feedback_parts = []
    if not count_ok:
        if tiles_count < trap.min_tiles:
            feedback_parts.append(f"Only {tiles_count} tiles (need {trap.min_tiles})")
        else:
            feedback_parts.append(f"Too many tiles: {tiles_count} (max {trap.max_tiles})")
    if avg_quality < 0.5:
        feedback_parts.append("Tiles lack detail")
    if not format_correct:
        feedback_parts.append("Missing required fields")
    if not pattern_match and trap.expected_output:
        feedback_parts.append("Output doesn't match expected pattern")
    
    feedback = "; ".join(feedback_parts) if feedback_parts else "Good run"
    
    return {
        "passed": passed,
        "score": round(score, 3),
        "tiles_generated": tiles_count,
        "tile_quality": round(avg_quality, 3),
        "format_correct": format_correct,
        "pattern_match": pattern_match,
        "feedback": feedback,
    }


def update_trap_stats(trap: Trap, result: Dict[str, Any]):
    """Update a trap's stats with a new run result."""
    if "runs" not in trap.stats:
        trap.stats["runs"] = 0
        trap.stats["successes"] = 0
        trap.stats["avg_score"] = 0.0
        trap.stats["total_tiles"] = 0
    
    trap.stats["runs"] += 1
    if result["passed"]:
        trap.stats["successes"] += 1
    
    # Update running average
    n = trap.stats["runs"]
    old_avg = trap.stats["avg_score"]
    trap.stats["avg_score"] = round((old_avg * (n - 1) + result["score"]) / n, 3)
    trap.stats["total_tiles"] += result["tiles_generated"]
