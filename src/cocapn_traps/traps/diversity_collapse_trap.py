"""cocapn-traps/traps/diversity_collapse_trap.py — Operational monitoring trap.

A new pattern: Traps as fleet monitors, not just content generators.
This trap watches breeder diversity over time and triggers alerts when
monoculture collapse is detected (proven real by Round 10 simulation).

Usage:
    from cocapn_traps.traps.diversity_collapse_trap import DiversityCollapseTrap
    trap = DiversityCollapseTrap(threshold=0.35, window=3)
    
    # Feed diversity scores from each breeding round
    trap.record(0.925)  # round 1
    trap.record(0.910)  # round 2
    trap.record(0.895)  # round 3 — triggers ALERT
    
    alert = trap.check()  # Returns alert dict or None
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

# ── Optional nexus event bus ───────────────────────────────────
try:
    from nexus.fleet_event_bus import FleetEventBus
    _HAS_BUS = True
except Exception:
    FleetEventBus = None  # type: ignore[misc,assignment]
    _HAS_BUS = False

logger = logging.getLogger(__name__)


@dataclass
class DiversityAlert:
    """Triggered when diversity collapse is detected."""
    level: str           # "WARNING" or "CRITICAL"
    consecutive_drops: int
    diversity_scores: List[float]
    recommended_action: str
    timestamp_ns: int = field(default_factory=time.time_ns)

    def to_tile(self) -> Dict[str, Any]:
        """Convert to PLATO tile format."""
        return {
            "tile_type": "diversity_alert",
            "level": self.level,
            "diversity_current": self.diversity_scores[-1] if self.diversity_scores else 0.0,
            "diversity_previous": self.diversity_scores[-2] if len(self.diversity_scores) >= 2 else 0.0,
            "consecutive_drops": self.consecutive_drops,
            "recommended_action": self.recommended_action,
            "timestamp": self.timestamp_ns,
        }


class DiversityCollapseTrap:
    """Monitor breeder diversity and alert on monoculture collapse.

    This is a *new pattern* for cocapn-traps: operational monitoring,
    not prompt lures.  The trap evaluates fleet health, not agent
    output quality.
    """

    WARNING_DROPS = 2    # 2 consecutive drops → WARNING
    CRITICAL_DROPS = 3   # 3 consecutive drops → CRITICAL

    def __init__(
        self,
        diversity_threshold: float = 0.35,
        window: int = 10,
        bus: Any | None = None,
        emergency_callback: Callable | None = None,
    ) -> None:
        self._threshold = diversity_threshold
        self._window = window
        self._bus = bus
        self._emergency_callback = emergency_callback
        self._scores: List[float] = []
        self._consecutive_drops: int = 0
        self._last_alert: Optional[DiversityAlert] = None

    # ------------------------------------------------------------------
    # Record
    # ------------------------------------------------------------------
    def record(self, diversity_score: float) -> None:
        """Record a diversity score from the latest breeding round."""
        self._scores.append(diversity_score)
        if len(self._scores) > self._window:
            self._scores.pop(0)

        # Detect consecutive drops
        if len(self._scores) >= 2:
            if diversity_score < self._scores[-2]:
                self._consecutive_drops += 1
            else:
                self._consecutive_drops = 0

        logger.debug("Diversity=%.3f drops=%d/%d", diversity_score, self._consecutive_drops, self.window)

    # ------------------------------------------------------------------
    # Check
    # ------------------------------------------------------------------
    def check(self) -> Optional[DiversityAlert]:
        """Return alert if diversity collapse detected, else None."""
        if not self._scores:
            return None

        current = self._scores[-1]

        # Condition 1: diversity below absolute threshold
        below_threshold = current < self._threshold

        # Condition 2: consecutive drops
        if self._consecutive_drops >= self.CRITICAL_DROPS:
            alert = DiversityAlert(
                level="CRITICAL",
                consecutive_drops=self._consecutive_drops,
                diversity_scores=list(self._scores),
                recommended_action="CROSS_SHIP_INJECTION: import 2 agents from distant ship",
            )
            self._emit_alert(alert)
            return alert

        if self._consecutive_drops >= self.WARNING_DROPS or below_threshold:
            alert = DiversityAlert(
                level="WARNING",
                consecutive_drops=self._consecutive_drops,
                diversity_scores=list(self._scores),
                recommended_action="EMERGENCY_MUTATE: force 20% random rebirth",
            )
            self._emit_alert(alert)
            return alert

        return None

    # ------------------------------------------------------------------
    # Emergency response
    # ------------------------------------------------------------------
    def _emit_alert(self, alert: DiversityAlert) -> None:
        logger.warning("DIVERSITY %s: %s", alert.level, alert.recommended_action)
        if self._bus and _HAS_BUS:
            self._bus.emit({"type": "diversity_alert", **alert.to_tile()})
        if self._emergency_callback:
            self._emergency_callback(alert)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def window(self) -> int:
        return self._window

    @property
    def threshold(self) -> float:
        return self._threshold

    def status(self) -> Dict[str, Any]:
        return {
            "scores_count": len(self._scores),
            "latest_score": self._scores[-1] if self._scores else None,
            "consecutive_drops": self._consecutive_drops,
            "threshold": self._threshold,
            "last_alert_level": self._last_alert.level if self._last_alert else None,
        }


# ── Fleet integration helper ──────────────────────────────────────
class BreederDiversityMonitor:
    """Higher-level helper that attaches to BreederDaemonV2."""

    def __init__(
        self,
        breeder: Any,
        trap: DiversityCollapseTrap | None = None,
        bus: Any | None = None,
    ) -> None:
        self._breeder = breeder
        self._trap = trap or DiversityCollapseTrap(bus=bus)
        self._bus = bus

    def on_breed_cycle_complete(self) -> None:
        """Call after each breeding round."""
        # Extract diversity from breeder state
        diversity = self._extract_diversity()
        if diversity is not None:
            self._trap.record(diversity)
            alert = self._trap.check()
            if alert:
                self._handle_alert(alert)

    def _extract_diversity(self) -> float | None:
        """Try to read diversity from breeder's vector table."""
        vt = getattr(self._breeder, "vector_table", None)
        if vt and hasattr(vt, "diversity_score"):
            return float(vt.diversity_score())
        return None

    def _handle_alert(self, alert: DiversityAlert) -> None:
        logger.warning("Breeder diversity alert: %s", alert.recommended_action)
        # Could trigger actual breeding policy changes here
        if hasattr(self._breeder, "thermal_policy"):
            self._breeder.thermal_policy = "EMERGENCY_MUTATE"


# ── Self-test ─────────────────────────────────────────────────────
if __name__ == "__main__":
    trap = DiversityCollapseTrap(diversity_threshold=0.35)
    trap.record(0.925)
    trap.record(0.910)
    assert trap.check() is None  # 1 drop, not enough
    trap.record(0.895)
    alert = trap.check()
    assert alert is not None
    assert alert.level == "WARNING"
    print(f"Alert: {alert.level} — {alert.recommended_action}")
    print("DiversityCollapseTrap self-test passed.")
