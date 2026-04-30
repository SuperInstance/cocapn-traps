"""cocapn-traps — Crab trap management for the Cocapn Fleet."""
from .trap import Trap, TrapRegistry
from .evaluator import evaluate_trap, update_trap_stats
from .loader import load_from_file, load_from_directory
from .runner import run_trap

__version__ = "1.0.0"
