#!/usr/bin/env python3
"""
Dice roller for D&D and Pathfinder.

Supports:
  XdY           — roll X dice with Y sides
  XdY+Z         — roll with positive modifier
  XdY-Z         — roll with negative modifier
  2d20 advantage    — roll 2d20, keep highest
  2d20 disadvantage — roll 2d20, keep lowest
  4d6kh3        — roll 4d6, keep highest 3 (character gen)
  4d6kl3        — roll 4d6, keep lowest 3

Usage (CLI):
  python scripts/dice.py 3d6
  python scripts/dice.py 1d20+5
  python scripts/dice.py 2d20 advantage
  python scripts/dice.py 4d6kh3
"""

import random
import re
import sys
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class DiceResult:
    notation: str
    rolls: List[int]
    kept: List[int]
    modifier: int
    total: int
    breakdown: str


# Regex patterns
_NOTATION_RE = re.compile(
    r"^(\d+)d(\d+)"          # XdY (required)
    r"([+-]\d+)?"             # optional modifier
    r"(?:\s*(advantage|disadvantage))?"   # optional advantage/disadvantage
    r"(?:k([hl])(\d+))?$",   # optional kh/kl keep
    re.IGNORECASE,
)


def parse_notation(
    notation: str,
) -> Tuple[int, int, int, Optional[str], Optional[Tuple[str, int]]]:
    """
    Parses dice notation string.

    Returns:
        (count, sides, modifier, mode, keep)
        - mode: "advantage" | "disadvantage" | None
        - keep: ("highest", N) | ("lowest", N) | None
    """
    cleaned = notation.strip()
    m = _NOTATION_RE.match(cleaned)
    if not m:
        raise ValueError(f"Invalid dice notation: '{notation}'")

    count = int(m.group(1))
    sides = int(m.group(2))
    modifier = int(m.group(3)) if m.group(3) else 0
    mode = m.group(4).lower() if m.group(4) else None

    keep = None
    if m.group(5) and m.group(6):
        direction = "highest" if m.group(5).lower() == "h" else "lowest"
        keep = (direction, int(m.group(6)))

    return count, sides, modifier, mode, keep


def roll(notation: str) -> DiceResult:
    """
    Rolls dice according to the given notation and returns a DiceResult.

    Args:
        notation: Dice expression (e.g. "3d6", "1d20+5", "2d20 advantage", "4d6kh3")

    Returns:
        DiceResult with rolls, kept dice, modifier, total, and breakdown string
    """
    count, sides, modifier, mode, keep = parse_notation(notation)

    rolls = [random.randint(1, sides) for _ in range(count)]

    if mode == "advantage":
        kept = [max(rolls)]
    elif mode == "disadvantage":
        kept = [min(rolls)]
    elif keep is not None:
        direction, n = keep
        sorted_rolls = sorted(rolls, reverse=(direction == "highest"))
        kept = sorted_rolls[:n]
    else:
        kept = rolls[:]

    total = sum(kept) + modifier

    # Build human-readable breakdown
    rolls_str = ", ".join(str(r) for r in rolls)
    kept_str = ", ".join(str(r) for r in kept)

    if mode:
        breakdown = f"Rolls: [{rolls_str}] → {mode}: {kept[0]}"
    elif keep is not None:
        direction, n = keep
        breakdown = f"Rolls: [{rolls_str}] → kept {direction} {n}: [{kept_str}]"
    else:
        breakdown = f"Rolls: [{rolls_str}]"

    if modifier > 0:
        breakdown += f" + {modifier}"
    elif modifier < 0:
        breakdown += f" - {abs(modifier)}"

    breakdown += f" = **{total}**"

    return DiceResult(
        notation=notation,
        rolls=rolls,
        kept=kept,
        modifier=modifier,
        total=total,
        breakdown=breakdown,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python dice.py <notation>")
        print("Examples:")
        print("  python dice.py 3d6")
        print("  python dice.py 1d20+5")
        print("  python dice.py 2d20 advantage")
        print("  python dice.py 4d6kh3")
        sys.exit(1)

    notation = " ".join(sys.argv[1:])
    try:
        result = roll(notation)
        print(result.breakdown)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
