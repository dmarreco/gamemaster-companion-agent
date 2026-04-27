# D&D AI — DM Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a four-skill Cursor DM assistant (rules, story, characters, dice) backed by plain markdown/JSON files in git, supporting multiple campaigns with a single active-campaign pointer.

**Architecture:** Four independent SKILL.md files live in `skills/` and are wired as Cursor rules for auto-attachment. Shared state lives in `campaigns/<name>/` directories; `active-campaign.txt` declares the active one. Python utility scripts handle computation (dice rolling, campaign scaffolding) that the skills invoke via shell.

**Tech Stack:** Python 3.11+, Cursor Skills (SKILL.md), Cursor Rules (.cursor/rules/), Markdown, JSON, Git

---

## File Map

| File | Purpose |
|------|---------|
| `active-campaign.txt` | Single-line pointer to the active campaign folder name |
| `README.md` | Project overview and DM quick-reference |
| `.gitignore` | Ignore Python cache, editor files |
| `scripts/new_campaign.py` | Scaffolds a new campaign directory with all required files |
| `scripts/dice.py` | Dice roller: parses notation, returns result + breakdown |
| `scripts/tests/test_dice.py` | Unit tests for dice.py |
| `scripts/tests/test_new_campaign.py` | Unit tests for new_campaign.py |
| `skills/dice/SKILL.md` | Dice skill — invokes dice.py, no campaign context |
| `skills/characters/SKILL.md` | Character tracking skill — reads/writes characters/ JSON |
| `skills/rules/SKILL.md` | Rules adjudication skill — reads rulesets/ files |
| `skills/story/SKILL.md` | Story/narrative skill — reads campaign files |
| `.cursor/rules/dnd-rules.mdc` | Auto-attaches rules skill on rules questions |
| `.cursor/rules/dnd-story.mdc` | Auto-attaches story skill on narrative requests |
| `.cursor/rules/dnd-characters.mdc` | Auto-attaches characters skill on tracking requests |
| `.cursor/rules/dnd-dice.mdc` | Auto-attaches dice skill on explicit roll requests |
| `rulesets/dnd5e-2024/README.md` | Instructions for populating 5e 2024 SRD data |
| `rulesets/dnd5e-2014/README.md` | Instructions for populating 5e 2014 SRD data |
| `rulesets/pathfinder2e/README.md` | Instructions for populating PF2e SRD data |
| `campaigns/example/` | Example campaign files for reference |

---

## Task 1: Repository Scaffold

**Files:**
- Create: `active-campaign.txt`
- Create: `README.md`
- Create: `.gitignore`
- Create: `rulesets/dnd5e-2024/README.md`
- Create: `rulesets/dnd5e-2014/README.md`
- Create: `rulesets/pathfinder2e/README.md`
- Create directory tree: `rulesets/`, `campaigns/`, `scripts/tests/`, `skills/`, `.cursor/rules/`

- [ ] **Step 1: Create all directories**

```bash
mkdir -p rulesets/dnd5e-2024 rulesets/dnd5e-2014 rulesets/pathfinder2e
mkdir -p campaigns
mkdir -p scripts/tests
mkdir -p skills/dice skills/characters skills/rules skills/story
mkdir -p .cursor/rules
```

- [ ] **Step 2: Create `active-campaign.txt`**

```
example
```

(Content is just `example` — points at the example campaign we'll create in Task 3.)

- [ ] **Step 3: Create `.gitignore`**

```
__pycache__/
*.pyc
*.pyo
.DS_Store
.env
*.egg-info/
dist/
build/
.pytest_cache/
```

- [ ] **Step 4: Create `README.md`**

```markdown
# D&D AI — DM Assistant

A Cursor-based AI assistant for Dungeon Masters. Four skills cover rules adjudication,
story/narrative, character tracking, and dice rolling.

## Quick Reference

| Goal | Skill | How to invoke |
|------|-------|--------------|
| Rules question | `rules` | Ask naturally — the rules rule auto-attaches |
| Story / NPC / plot | `story` | Ask naturally — the story rule auto-attaches |
| HP / XP / conditions | `characters` | Ask naturally — the characters rule auto-attaches |
| Roll dice | `dice` | Say "roll dice" or "agent roll" explicitly |

## Active Campaign

The file `active-campaign.txt` contains the name of the currently active campaign folder
under `campaigns/`. To switch campaigns, update this file and commit.

## Starting a New Campaign

```bash
python scripts/new_campaign.py <campaign-name> <ruleset>
# Example:
python scripts/new_campaign.py curse-of-strahd dnd5e-2024
```

Then update `active-campaign.txt` to the new campaign name and commit.

## Supported Rulesets

- `dnd5e-2024` — D&D 5e Revised (2024), primary
- `dnd5e-2014` — D&D 5e Original (2014)
- `pathfinder2e` — Pathfinder 2nd Edition

See each `rulesets/<edition>/README.md` for instructions on populating SRD data.

## Session Workflow

1. Start session: ask the story skill for a recap
2. During play: invoke whichever skill fits the moment
3. End of session: review story skill's proposed session log and world updates
4. Commit all changes — this is your session save point
```

- [ ] **Step 5: Create ruleset README files**

`rulesets/dnd5e-2024/README.md`:
```markdown
# D&D 5e 2024 Ruleset Data

Populate this directory with SRD content for D&D 5th Edition Revised (2024).

## Recommended sources

- [D&D 5e 2024 Free Rules SRD](https://www.dndbeyond.com/sources/dnd/free-rules) — export or copy key sections as markdown
- [5e.tools](https://5e.tools) — community data in JSON format (check license)
- Your own purchased PDFs — convert to markdown using Pandoc: `pandoc input.pdf -o output.md`

## Suggested file structure

- `classes.md` — all class features and subclass options
- `spells.md` — full spell list with descriptions
- `monsters.md` — monster stat blocks
- `conditions.md` — condition definitions
- `equipment.md` — weapons, armor, gear
- `rules.md` — core rules (actions, combat, rests, etc.)
- `tables/` — random tables (roll20 encounter tables, wild magic, etc.)
```

`rulesets/dnd5e-2014/README.md`:
```markdown
# D&D 5e 2014 Ruleset Data

Populate this directory with SRD content for D&D 5th Edition (2014).

## Recommended sources

- [D&D 5e SRD 5.1 (official, CC)](https://dnd.wizards.com/resources/systems-reference-document) — free, legal, downloadable PDF
- Convert with Pandoc: `pandoc SRD-CC-v5.1.pdf -o srd.md`
- [5e.tools](https://5e.tools) — community JSON data

## Suggested file structure (same as dnd5e-2024)

- `classes.md`, `spells.md`, `monsters.md`, `conditions.md`, `equipment.md`, `rules.md`, `tables/`
```

`rulesets/pathfinder2e/README.md`:
```markdown
# Pathfinder 2e Ruleset Data

Populate this directory with SRD content for Pathfinder 2nd Edition.

## Recommended sources

- [Archives of Nethys (official, free)](https://2e.aonprd.com/) — full rules online; use browser-to-markdown tools
- [Pathfinder 2e SRD JSON](https://github.com/foundryvtt/pf2e) — FoundryVTT community data
- Your own PDFs converted with Pandoc

## Suggested file structure

- `classes.md`, `spells.md`, `monsters.md`, `conditions.md`, `equipment.md`, `rules.md`, `tables/`
```

- [ ] **Step 6: Commit scaffold**

```bash
git add .
git commit -m "feat: scaffold repository structure and READMEs"
```

Expected: commit succeeds, all dirs and files tracked.

---

## Task 2: Character Sheet JSON Schema + Example Campaign

**Files:**
- Create: `campaigns/example/campaign.md`
- Create: `campaigns/example/ruleset.txt`
- Create: `campaigns/example/sessions/session-001.md`
- Create: `campaigns/example/world/npcs.md`
- Create: `campaigns/example/world/locations.md`
- Create: `campaigns/example/world/factions.md`
- Create: `campaigns/example/characters/thorin.json`
- Create: `campaigns/example/characters/thorin.md`

- [ ] **Step 1: Create `campaigns/example/ruleset.txt`**

```
dnd5e-2024
```

- [ ] **Step 2: Create `campaigns/example/campaign.md`**

```markdown
# The Lost Mines of Example

## Premise
A band of adventurers is hired to investigate the disappearance of a dwarven explorer
in the foothills of the Sword Mountains.

## Arc
- **Act 1:** Investigate Phandalin, gather leads
- **Act 2:** Explore the Cragmaw stronghold
- **Act 3:** Delve into the Wave Echo Cave

## World Notes
The region is tense: goblin raids have increased, and rumors of a dark mage persist.

## Tone
Heroic adventure with mystery elements. Combat-moderate.
```

- [ ] **Step 3: Create `campaigns/example/sessions/session-001.md`**

```markdown
# Session 001 — 2026-04-27

## What Happened
The party arrived in Phandalin after escorting a supply wagon. They met Sildar Hallwinter,
who revealed that Gundren Rockseeker had been captured by goblins.

## Decisions Taken
- Party chose to rescue Gundren before exploring the mines
- Thorin intimidated the town bully Harbin Wester — he now distrusts the party

## XP Awarded
- 150 XP each (goblin ambush + social encounter)

## State at End of Session
- Party is at the Stonehill Inn, Phandalin
- Next lead: Cragmaw Hideout, one day's travel east
```

- [ ] **Step 4: Create world files**

`campaigns/example/world/npcs.md`:
```markdown
# NPCs

## Sildar Hallwinter
- **Role:** Former soldier, companion of Gundren
- **Status:** Alive, in Phandalin
- **Motivation:** Rescue Gundren, restore order to Phandalin
- **Relationship to party:** Friendly, grateful

## Harbin Wester
- **Role:** Town master of Phandalin
- **Status:** Alive, distrusts party (Thorin's intimidation, session 001)
- **Motivation:** Keep the peace, avoid trouble
- **Relationship to party:** Wary
```

`campaigns/example/world/locations.md`:
```markdown
# Locations

## Phandalin (visited)
- Small frontier town, scarred by past bandit raids
- Key locations: Stonehill Inn, Barthen's Provisions, Town Master's Hall
- Secrets revealed: Redbrand bandits are terrorizing locals

## Cragmaw Hideout (known, not visited)
- Goblin stronghold one day east of Phandalin
- Gundren Rockseeker is believed to be held here
```

`campaigns/example/world/factions.md`:
```markdown
# Factions

## Redbrands
- **Type:** Bandit gang
- **Goal:** Control Phandalin's trade
- **Leader:** Unknown (rumored to be a dark mage called the Black Spider)
- **Status:** Active, hostile to party

## Lords' Alliance
- **Type:** Political coalition of northern cities
- **Goal:** Stability in the region
- **Contact:** Sildar Hallwinter
- **Status:** Neutral, potentially allied
```

- [ ] **Step 5: Create `campaigns/example/characters/thorin.json`**

This is the canonical character sheet schema. All character sheets must conform to this structure.

```json
{
  "name": "Thorin Ironforge",
  "player": "Daniel",
  "class": "Fighter",
  "subclass": "Battle Master",
  "level": 3,
  "race": "Mountain Dwarf",
  "background": "Soldier",
  "alignment": "Lawful Good",
  "xp": 900,
  "xp_next_level": 2700,
  "ability_scores": {
    "strength": 17,
    "dexterity": 12,
    "constitution": 16,
    "intelligence": 10,
    "wisdom": 13,
    "charisma": 9
  },
  "proficiency_bonus": 2,
  "hp": {
    "current": 28,
    "max": 34,
    "temp": 0
  },
  "hit_dice": {
    "total": 3,
    "remaining": 2,
    "die": "d10"
  },
  "armor_class": 18,
  "speed": 25,
  "initiative": 1,
  "saving_throws": {
    "proficient": ["strength", "constitution"]
  },
  "skills": {
    "proficient": ["athletics", "intimidation", "perception", "survival"],
    "expertise": []
  },
  "conditions": [],
  "death_saves": {
    "successes": 0,
    "failures": 0
  },
  "spell_slots": {},
  "class_resources": {
    "action_surge": { "max": 1, "remaining": 1 },
    "second_wind": { "max": 1, "remaining": 0 },
    "superiority_dice": { "max": 4, "remaining": 3, "die": "d8" }
  },
  "attacks": [
    {
      "name": "Battleaxe",
      "type": "melee",
      "attack_bonus": 5,
      "damage": "1d8+3",
      "damage_type": "slashing",
      "properties": ["versatile (1d10)"]
    },
    {
      "name": "Hand Crossbow",
      "type": "ranged",
      "attack_bonus": 3,
      "damage": "1d6+1",
      "damage_type": "piercing",
      "range": "30/120",
      "properties": ["light", "loading"]
    }
  ],
  "equipment": [
    "Battleaxe",
    "Hand crossbow (20 bolts)",
    "Chain mail",
    "Shield",
    "Explorer's pack",
    "50 gp"
  ],
  "features": [
    "Fighting Style: Defense",
    "Second Wind",
    "Action Surge (1/rest)",
    "Battle Master: Combat Superiority (4d8)",
    "Maneuvers: Disarming Attack, Menacing Attack, Trip Attack",
    "Know Your Enemy"
  ],
  "proficiencies": {
    "armor": ["light", "medium", "heavy", "shields"],
    "weapons": ["simple", "martial"],
    "tools": ["playing card set"],
    "languages": ["Common", "Dwarvish"]
  },
  "personality": {
    "traits": "I face problems head-on. A simple, direct solution is best.",
    "ideals": "Responsibility. I do what I must and face consequences.",
    "bonds": "Those who fight beside me are worth dying for.",
    "flaws": "I obey the law even if it causes misery."
  },
  "notes": "Thorin has a scar over his left eye from the Battle of Greenfields."
}
```

- [ ] **Step 6: Create `campaigns/example/characters/thorin.md`**

```markdown
# Thorin Ironforge — Fighter 3 (Battle Master)

**Player:** Daniel | **Race:** Mountain Dwarf | **Background:** Soldier

## Current Status
- **HP:** 28 / 34 | **AC:** 18 | **Speed:** 25 ft
- **Conditions:** None
- **Action Surge:** ✅ available | **Second Wind:** ❌ used | **Superiority Dice:** 3/4

## Quick Stats
STR 17 (+3) | DEX 12 (+1) | CON 16 (+3) | INT 10 (+0) | WIS 13 (+1) | CHA 9 (-1)

## Attacks
- Battleaxe: +5 to hit, 1d8+3 slashing (versatile 1d10)
- Hand Crossbow: +3 to hit, 1d6+1 piercing, 30/120 ft

## Notes
Scar over left eye. Intimidated Harbin Wester in session 001 — he now distrusts the party.
```

- [ ] **Step 7: Commit example campaign**

```bash
git add campaigns/ active-campaign.txt
git commit -m "feat: add example campaign with character sheet schema"
```

---

## Task 3: New Campaign Initializer Script

**Files:**
- Create: `scripts/new_campaign.py`
- Create: `scripts/tests/test_new_campaign.py`

- [ ] **Step 1: Write failing tests**

`scripts/tests/test_new_campaign.py`:
```python
import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from new_campaign import create_campaign, VALID_RULESETS


def test_creates_required_directories(tmp_path):
    create_campaign("test-campaign", "dnd5e-2024", campaigns_dir=tmp_path)
    base = tmp_path / "test-campaign"
    assert (base / "sessions").is_dir()
    assert (base / "world").is_dir()
    assert (base / "characters").is_dir()


def test_creates_required_files(tmp_path):
    create_campaign("test-campaign", "dnd5e-2024", campaigns_dir=tmp_path)
    base = tmp_path / "test-campaign"
    assert (base / "ruleset.txt").exists()
    assert (base / "campaign.md").exists()
    assert (base / "world" / "npcs.md").exists()
    assert (base / "world" / "locations.md").exists()
    assert (base / "world" / "factions.md").exists()


def test_ruleset_txt_contains_correct_value(tmp_path):
    create_campaign("my-adventure", "pathfinder2e", campaigns_dir=tmp_path)
    content = (tmp_path / "my-adventure" / "ruleset.txt").read_text().strip()
    assert content == "pathfinder2e"


def test_rejects_invalid_ruleset(tmp_path):
    with pytest.raises(ValueError, match="Unknown ruleset"):
        create_campaign("bad", "dnd3e", campaigns_dir=tmp_path)


def test_rejects_existing_campaign(tmp_path):
    create_campaign("existing", "dnd5e-2024", campaigns_dir=tmp_path)
    with pytest.raises(FileExistsError):
        create_campaign("existing", "dnd5e-2024", campaigns_dir=tmp_path)


def test_valid_rulesets_list():
    assert "dnd5e-2024" in VALID_RULESETS
    assert "dnd5e-2014" in VALID_RULESETS
    assert "pathfinder2e" in VALID_RULESETS
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd scripts && python -m pytest tests/test_new_campaign.py -v
```

Expected: `ModuleNotFoundError: No module named 'new_campaign'`

- [ ] **Step 3: Implement `scripts/new_campaign.py`**

```python
#!/usr/bin/env python3
"""
Scaffolds a new campaign directory under campaigns/.

Usage:
    python scripts/new_campaign.py <campaign-name> <ruleset>

Example:
    python scripts/new_campaign.py curse-of-strahd dnd5e-2024
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import date

VALID_RULESETS = ["dnd5e-2024", "dnd5e-2014", "pathfinder2e"]

CAMPAIGN_MD_TEMPLATE = """\
# {title}

## Premise
[Describe the campaign premise here.]

## Arc
- **Act 1:** [First act description]
- **Act 2:** [Second act description]
- **Act 3:** [Third act description]

## World Notes
[Key world details, tone, themes.]

## Tone
[Describe the tone: gritty, heroic, mystery, horror, etc.]
"""

NPCS_MD_TEMPLATE = """\
# NPCs

<!-- Template:
## NPC Name
- **Role:** What they do in the world
- **Status:** Alive / Dead / Unknown
- **Motivation:** What they want
- **Relationship to party:** Friendly / Hostile / Neutral / Unknown
-->
"""

LOCATIONS_MD_TEMPLATE = """\
# Locations

<!-- Template:
## Location Name (visited / known / rumored)
- Description
- Key features
- Secrets revealed: [list anything the party has uncovered]
-->
"""

FACTIONS_MD_TEMPLATE = """\
# Factions

<!-- Template:
## Faction Name
- **Type:** Guild / Military / Political / Criminal / Religious / etc.
- **Goal:** What they want
- **Leader:** Name (if known)
- **Status:** Active / Dormant / Destroyed
- **Relationship to party:** Allied / Neutral / Hostile
-->
"""


def create_campaign(name: str, ruleset: str, campaigns_dir: Path = None) -> Path:
    """
    Creates a new campaign directory structure.

    Args:
        name: Campaign folder name (kebab-case recommended)
        ruleset: One of VALID_RULESETS
        campaigns_dir: Override for campaigns directory (used in tests)

    Returns:
        Path to the created campaign directory

    Raises:
        ValueError: If ruleset is not in VALID_RULESETS
        FileExistsError: If campaign directory already exists
    """
    if ruleset not in VALID_RULESETS:
        raise ValueError(
            f"Unknown ruleset '{ruleset}'. Valid options: {', '.join(VALID_RULESETS)}"
        )

    if campaigns_dir is None:
        repo_root = Path(__file__).parent.parent
        campaigns_dir = repo_root / "campaigns"

    campaign_path = campaigns_dir / name

    if campaign_path.exists():
        raise FileExistsError(f"Campaign '{name}' already exists at {campaign_path}")

    # Create directory tree
    (campaign_path / "sessions").mkdir(parents=True)
    (campaign_path / "world").mkdir()
    (campaign_path / "characters").mkdir()

    # Write files
    (campaign_path / "ruleset.txt").write_text(ruleset + "\n")

    title = name.replace("-", " ").title()
    (campaign_path / "campaign.md").write_text(CAMPAIGN_MD_TEMPLATE.format(title=title))

    (campaign_path / "world" / "npcs.md").write_text(NPCS_MD_TEMPLATE)
    (campaign_path / "world" / "locations.md").write_text(LOCATIONS_MD_TEMPLATE)
    (campaign_path / "world" / "factions.md").write_text(FACTIONS_MD_TEMPLATE)

    return campaign_path


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new D&D campaign directory."
    )
    parser.add_argument("name", help="Campaign folder name (e.g. curse-of-strahd)")
    parser.add_argument(
        "ruleset",
        help=f"Ruleset to use. Options: {', '.join(VALID_RULESETS)}",
    )
    args = parser.parse_args()

    try:
        path = create_campaign(args.name, args.ruleset)
        print(f"✓ Campaign created at {path}")
        print(f"\nNext steps:")
        print(f"  1. Edit campaigns/{args.name}/campaign.md with your premise and arc")
        print(f"  2. Update active-campaign.txt to '{args.name}'")
        print(f"  3. git add . && git commit -m 'feat: start campaign {args.name}'")
    except (ValueError, FileExistsError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd scripts && python -m pytest tests/test_new_campaign.py -v
```

Expected output:
```
PASSED tests/test_new_campaign.py::test_creates_required_directories
PASSED tests/test_new_campaign.py::test_creates_required_files
PASSED tests/test_new_campaign.py::test_ruleset_txt_contains_correct_value
PASSED tests/test_new_campaign.py::test_rejects_invalid_ruleset
PASSED tests/test_new_campaign.py::test_rejects_existing_campaign
PASSED tests/test_new_campaign.py::test_valid_rulesets_list
6 passed
```

- [ ] **Step 5: Commit**

```bash
git add scripts/new_campaign.py scripts/tests/test_new_campaign.py
git commit -m "feat: add new campaign initializer script"
```

---

## Task 4: Dice Roller Script

**Files:**
- Create: `scripts/dice.py`
- Create: `scripts/tests/test_dice.py`

- [ ] **Step 1: Write failing tests**

`scripts/tests/test_dice.py`:
```python
import sys
import os
import re
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dice import roll, parse_notation, DiceResult


def test_single_die_returns_value_in_range():
    result = roll("1d6")
    assert 1 <= result.total <= 6


def test_multiple_dice_returns_value_in_range():
    result = roll("3d6")
    assert 3 <= result.total <= 18
    assert len(result.rolls) == 3


def test_modifier_added_correctly():
    result = roll("1d1+5")
    assert result.total == 6
    assert result.rolls == [1]
    assert result.modifier == 5


def test_negative_modifier():
    result = roll("1d1-3")
    assert result.total == -2


def test_advantage_returns_higher_of_two():
    # With 1d1 both rolls are 1, so advantage total == 1
    result = roll("2d1 advantage")
    assert result.total == 1
    assert len(result.rolls) == 2
    assert result.kept == [1]


def test_disadvantage_returns_lower_of_two():
    result = roll("2d1 disadvantage")
    assert result.total == 1
    assert len(result.rolls) == 2


def test_keep_highest(monkeypatch):
    # Mock random to return predictable values
    import dice as dice_module
    call_count = [0]
    values = [3, 5, 1, 6]
    def mock_randint(a, b):
        val = values[call_count[0] % len(values)]
        call_count[0] += 1
        return val
    monkeypatch.setattr(dice_module.random, "randint", mock_randint)
    result = roll("4d6kh3")
    assert result.kept == sorted([3, 5, 1, 6], reverse=True)[:3]
    assert result.total == sum(sorted([3, 5, 1, 6], reverse=True)[:3])


def test_invalid_notation_raises():
    with pytest.raises(ValueError, match="Invalid dice notation"):
        roll("banana")


def test_result_has_breakdown_string():
    result = roll("1d1+2")
    assert "1" in result.breakdown
    assert "2" in result.breakdown
    assert "3" in result.breakdown


def test_d20_range():
    for _ in range(20):
        result = roll("1d20")
        assert 1 <= result.total <= 20


def test_parse_notation_basic():
    count, sides, modifier, mode, keep = parse_notation("3d8+2")
    assert count == 3
    assert sides == 8
    assert modifier == 2
    assert mode is None


def test_parse_notation_advantage():
    count, sides, modifier, mode, keep = parse_notation("2d20 advantage")
    assert mode == "advantage"


def test_parse_notation_keep_highest():
    count, sides, modifier, mode, keep = parse_notation("4d6kh3")
    assert keep == ("highest", 3)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd scripts && python -m pytest tests/test_dice.py -v
```

Expected: `ModuleNotFoundError: No module named 'dice'`

- [ ] **Step 3: Implement `scripts/dice.py`**

```python
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
from dataclasses import dataclass, field
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd scripts && python -m pytest tests/test_dice.py -v
```

Expected:
```
PASSED tests/test_dice.py::test_single_die_returns_value_in_range
PASSED tests/test_dice.py::test_multiple_dice_returns_value_in_range
PASSED tests/test_dice.py::test_modifier_added_correctly
PASSED tests/test_dice.py::test_negative_modifier
PASSED tests/test_dice.py::test_advantage_returns_higher_of_two
PASSED tests/test_dice.py::test_disadvantage_returns_lower_of_two
PASSED tests/test_dice.py::test_keep_highest
PASSED tests/test_dice.py::test_invalid_notation_raises
PASSED tests/test_dice.py::test_result_has_breakdown_string
PASSED tests/test_dice.py::test_d20_range
PASSED tests/test_dice.py::test_parse_notation_basic
PASSED tests/test_dice.py::test_parse_notation_advantage
PASSED tests/test_dice.py::test_parse_notation_keep_highest
13 passed
```

- [ ] **Step 5: Quick smoke test from CLI**

```bash
python scripts/dice.py 3d6
python scripts/dice.py 1d20+5
python scripts/dice.py 2d20 advantage
python scripts/dice.py 4d6kh3
```

Expected: each command prints a breakdown line ending in `= **N**` with a valid number.

- [ ] **Step 6: Commit**

```bash
git add scripts/dice.py scripts/tests/test_dice.py
git commit -m "feat: add dice roller utility with full notation support"
```

---

## Task 5: `dice` Skill

**Files:**
- Create: `skills/dice/SKILL.md`
- Create: `.cursor/rules/dnd-dice.mdc`

- [ ] **Step 1: Create `skills/dice/SKILL.md`**

```markdown
# Dice Skill

You are the dice roller for this D&D session. You are invoked explicitly when the DM
says "roll dice", "agent roll", or asks you to roll something specific.

## How to roll

Run the dice script from the repository root:

```bash
python scripts/dice.py <notation>
```

## Supported notations

| Expression | Meaning |
|-----------|---------|
| `3d6` | Roll 3 six-sided dice |
| `1d20+5` | Roll d20, add 5 |
| `1d20-2` | Roll d20, subtract 2 |
| `2d20 advantage` | Roll 2d20, keep the higher result |
| `2d20 disadvantage` | Roll 2d20, keep the lower result |
| `4d6kh3` | Roll 4d6, keep highest 3 (character generation) |
| `4d6kl3` | Roll 4d6, keep lowest 3 |

## After rolling

- Report the full breakdown (rolls shown, modifier, final total)
- If the DM asked for a specific check (e.g. "roll Perception"), note that the result
  needs to be compared against a DC — ask the DM what the DC is if not stated
- Do NOT narrate the outcome — that is the DM's job

## Roll tables

If the DM asks you to roll on a named table (e.g. "roll on the wild magic surge table"),
look for the table in `rulesets/<active-ruleset>/tables/`. Read the active ruleset from
`active-campaign.txt` → `campaigns/<name>/ruleset.txt`. Roll the appropriate die, then
read the corresponding table entry and report it.

## What you do NOT do

- Do not interpret dice results narratively — just report numbers
- Do not roll unless explicitly asked — physical table rolls are the default
```

- [ ] **Step 2: Create `.cursor/rules/dnd-dice.mdc`**

```
---
description: Attach the dice skill when the DM explicitly asks the agent to roll dice
globs:
alwaysApply: false
---

Attach and follow `skills/dice/SKILL.md` when the user says any of:
- "roll dice", "agent roll", "you roll"
- "roll [notation]" (e.g. "roll 3d6", "roll for initiative")
- "roll on the [table name] table"

Do NOT attach this skill for physical table rolls that the DM is just reporting.
```

- [ ] **Step 3: Verify skill works — manual smoke test**

In Cursor chat, type: `roll 2d20 advantage for a Perception check`

Expected: Agent runs `python scripts/dice.py 2d20 advantage`, reports both roll values and the higher one, does not narrate the narrative outcome.

- [ ] **Step 4: Commit**

```bash
git add skills/dice/SKILL.md .cursor/rules/dnd-dice.mdc
git commit -m "feat: add dice skill and cursor rule"
```

---

## Task 6: `characters` Skill

**Files:**
- Create: `skills/characters/SKILL.md`
- Create: `.cursor/rules/dnd-characters.mdc`

- [ ] **Step 1: Create `skills/characters/SKILL.md`**

````markdown
# Characters Skill

You track all player characters for the active campaign. Your source of truth is the
JSON file for each character in `campaigns/<active>/characters/`.

## Finding the active campaign

1. Read `active-campaign.txt` to get the campaign name
2. The characters directory is `campaigns/<name>/characters/`

## Your responsibilities

- Update HP (damage taken, healing received, temp HP)
- Update spell slots and class resources (used/restored on rest)
- Add/remove conditions and status effects
- Track XP and handle level-up prompts
- Update inventory (items gained/lost/used)
- Produce a party status summary on request

## How to update a character

1. Read the character's JSON file
2. Apply the change
3. Write the updated JSON back to the file
4. Also update the corresponding `.md` file's "Current Status" section to reflect the new state

Always update BOTH the `.json` (source of truth) and the `.md` (human-readable summary).

## Handling a DM narration

When the DM tells you what happened (e.g. "Thorin took 12 piercing damage"), translate
that into a JSON update:

- Damage: subtract from `hp.current` (apply resistance/vulnerability if DM specifies)
- Healing: add to `hp.current`, never exceeding `hp.max`
- Temp HP: set `hp.temp` (does not stack — take higher value)
- Conditions: add to `conditions` array (e.g. `"poisoned"`, `"prone"`)
- Condition removed: remove from `conditions` array
- Spell slot used: decrement the appropriate slot level in `spell_slots`
- Short rest: restore `hit_dice` usage per DM instruction; restore short-rest resources
- Long rest: restore `hp.current` to `hp.max`, restore all `spell_slots`, restore all class resources

## Leveling up

When the DM says a character levels up:
1. Increment `level`
2. Update `xp_next_level` to the next threshold (see table below)
3. Prompt the DM for: new HP roll result, new class features, new spells if applicable
4. Apply changes once DM provides them

XP thresholds (D&D 5e):
Level 1→2: 300 | 2→3: 900 | 3→4: 2700 | 4→5: 6500 | 5→6: 14000
Level 6→7: 23000 | 7→8: 34000 | 8→9: 48000 | 9→10: 64000
Level 10→11: 85000 | 11→12: 100000 | 12→13: 120000 | 13→14: 140000
Level 14→15: 165000 | 15→16: 195000 | 16→17: 225000 | 17→18: 265000
Level 18→19: 305000 | 19→20: 355000

## Party status summary

When asked for a party status summary, produce a compact markdown table:

```
| Character | HP | Conditions | Key Resources |
|-----------|-----|-----------|---------------|
| Thorin (Fighter 3) | 28/34 | — | Action Surge ✅, Sup. Dice 3/4 |
```

## What you do NOT do

- Do not make rulings on what damage type applies — that is the rules skill's job
- Do not narrate events — that is the story skill's job
- Do not create characters from scratch — ask the DM for the full character sheet first
````

- [ ] **Step 2: Create `.cursor/rules/dnd-characters.mdc`**

```
---
description: Attach the characters skill for HP, XP, conditions, and character tracking
globs:
alwaysApply: false
---

Attach and follow `skills/characters/SKILL.md` when the user mentions any of:
- damage taken, healing, hit points, HP
- conditions (poisoned, stunned, prone, etc.)
- spell slots, class resources, second wind, action surge
- experience points, XP, leveling up
- inventory changes, items, equipment
- party status, character status summary
- short rest, long rest
```

- [ ] **Step 3: Verify — manual smoke test**

In Cursor chat, type: `Thorin took 8 fire damage and is now poisoned`

Expected: Agent reads `active-campaign.txt`, reads `campaigns/example/characters/thorin.json`, decrements `hp.current` by 8 (28 → 20), adds `"poisoned"` to conditions array, writes both files back, confirms the update.

- [ ] **Step 4: Commit**

```bash
git add skills/characters/SKILL.md .cursor/rules/dnd-characters.mdc
git commit -m "feat: add characters skill and cursor rule"
```

---

## Task 7: `rules` Skill

**Files:**
- Create: `skills/rules/SKILL.md`
- Create: `.cursor/rules/dnd-rules.mdc`

- [ ] **Step 1: Create `skills/rules/SKILL.md`**

```markdown
# Rules Skill

You are the rules adjudicator. Your job is to answer rules questions and resolve
edge cases accurately, citing sources.

## Finding the active ruleset

1. Read `active-campaign.txt` to get the campaign name
2. Read `campaigns/<name>/ruleset.txt` to get the ruleset ID (e.g. `dnd5e-2024`)
3. Your rulebook files are in `rulesets/<ruleset-id>/`

## How to answer a rules question

1. Check the relevant file in `rulesets/<ruleset-id>/` (e.g. `rules.md`, `spells.md`, `conditions.md`)
2. Quote or paraphrase the relevant passage with a reference (e.g. "Per the 2024 PHB, Grappling:")
3. If the rulebook files don't cover it, say so, then use your training knowledge for 5e/PF2e
4. If you find a conflict between local files and your training knowledge, **local files win**

## Precedence rules

Local ruleset files > your training knowledge > web search (last resort)

## Common question types

**Actions in combat:** Check `rules.md` → Combat section
**Spell effects:** Check `spells.md` for the specific spell
**Condition effects:** Check `conditions.md` (e.g. what does Poisoned actually do?)
**Class feature interactions:** Check `classes.md`
**Grappling, shoving, special attacks:** Check `rules.md` → Special Attacks

## Format your answer

- Lead with the ruling (one sentence)
- Follow with the rules text or paraphrase
- Note any common edge cases or DM rulings that apply
- If a table or die roll is involved, suggest using the dice skill

## What you do NOT do

- Do not update campaign files
- Do not track HP or character state — that is the characters skill's job
- Do not make up rules that aren't in the source material — say "the SRD doesn't cover this" if needed
```

- [ ] **Step 2: Create `.cursor/rules/dnd-rules.mdc`**

```
---
description: Attach the rules skill for D&D/PF2e rules questions and adjudication
globs:
alwaysApply: false
---

Attach and follow `skills/rules/SKILL.md` when the user asks about:
- How a spell, ability, or action works
- Combat rules (actions, reactions, bonus actions, movement)
- Conditions and their effects
- Grapple, shove, or special attack rules
- Class features, racial traits, feats
- Saving throws, skill checks, DCs
- Any "can I do X?" or "what happens when Y?" question about rules
- Edge cases, rule interactions, or clarifications
```

- [ ] **Step 3: Verify — manual smoke test**

In Cursor chat, type: `Can a grappled creature still cast spells?`

Expected: Agent reads `active-campaign.txt`, finds the ruleset, checks `rulesets/dnd5e-2024/` (or falls back to training knowledge if files not yet populated), gives a clear ruling with citation.

- [ ] **Step 4: Commit**

```bash
git add skills/rules/SKILL.md .cursor/rules/dnd-rules.mdc
git commit -m "feat: add rules skill and cursor rule"
```

---

## Task 8: `story` Skill

**Files:**
- Create: `skills/story/SKILL.md`
- Create: `.cursor/rules/dnd-story.mdc`

- [ ] **Step 1: Create `skills/story/SKILL.md`**

````markdown
# Story Skill

You are the narrative brain of this campaign. You help the DM with storytelling,
NPC dialogue, session recaps, encounter hooks, and world continuity.

## Loading campaign context

On every invocation, read these files in order:

1. `active-campaign.txt` → get campaign name
2. `campaigns/<name>/campaign.md` → premise, arc, tone
3. `campaigns/<name>/ruleset.txt` → which game system (affects tone/setting norms)
4. The **last 2 session logs** in `campaigns/<name>/sessions/` (most recent first)
5. `campaigns/<name>/world/npcs.md`
6. `campaigns/<name>/world/locations.md`
7. `campaigns/<name>/world/factions.md`

Loading all 7 gives you the context window you need. Do not skip any.

## What you help with

### NPC dialogue and behavior
When asked "what does [NPC] say/do?":
- Read the NPC's entry in `npcs.md`
- Stay consistent with their motivation, relationship to the party, and any prior interactions
- Write dialogue in their voice; include body language and tone notes

### Encounter hooks and plot twists
Generate hooks that connect to existing campaign threads. Prefer organic connections to
established NPCs, factions, and locations over new elements.

### Session recaps ("previously on...")
Summarize the last session in 3-5 sentences, written as a dramatic "previously on..."
narrator voice. Pull key events, decisions, and unresolved threads from the session log.

### Surfacing past decisions
When the DM asks "did they ever meet X?" or "what did the party decide about Y?", scan
all session logs and quote the relevant passage with the session number.

### Story arc development
Help build Act structure, foreshadowing, and consequences of player choices. Suggest
how past decisions could echo forward in the campaign.

## End-of-session workflow

At the end of a session, when the DM says "end session" or "write session log":

1. Ask the DM: "What were the key events, decisions, and XP awarded this session?"
2. Write a session log in this format:

```markdown
# Session NNN — YYYY-MM-DD

## What Happened
[3-5 sentence narrative summary of events]

## Decisions Taken
- [Decision 1 and its immediate consequence]
- [Decision 2 and its immediate consequence]

## XP Awarded
- [Amount] XP each ([reason])

## State at End of Session
- Party location
- Any immediate next leads or hooks
```

3. Propose updates to world files if anything changed:
   - New NPCs met → add to `npcs.md`
   - New locations visited or revealed → add to `locations.md`
   - Faction relationships changed → update `factions.md`

4. Present all proposed changes to the DM for review. Do NOT write to files until
   the DM confirms.

5. Once the DM confirms, write the session log and update the world files.

## What you do NOT do

- Do not track HP, XP, or mechanical state — that is the characters skill's job
- Do not answer rules questions — that is the rules skill's job
- Do not write to files without DM confirmation
- Do not invent major plot elements that contradict established campaign facts
````

- [ ] **Step 2: Create `.cursor/rules/dnd-story.mdc`**

```
---
description: Attach the story skill for narrative, NPC, session, and plot requests
globs:
alwaysApply: false
---

Attach and follow `skills/story/SKILL.md` when the user asks about:
- NPC dialogue, reactions, motivations, or behavior
- "What happens next?", plot hooks, encounter ideas
- Session recap or "previously on..."
- World-building: locations, factions, lore
- End of session log writing
- Story arc development, foreshadowing, consequences
- "Did the party ever...?" or "What did we decide about...?"
```

- [ ] **Step 3: Verify — manual smoke test**

In Cursor chat, type: `Give me a recap of the last session`

Expected: Agent reads `active-campaign.txt`, loads the example campaign files, reads `sessions/session-001.md`, produces a "previously on..." style 3-5 sentence recap.

- [ ] **Step 4: Commit**

```bash
git add skills/story/SKILL.md .cursor/rules/dnd-story.mdc
git commit -m "feat: add story skill and cursor rule"
```

---

## Task 9: Final Integration Check

- [ ] **Step 1: Run all tests**

```bash
cd scripts && python -m pytest tests/ -v
```

Expected: all tests pass with 0 failures.

- [ ] **Step 2: Verify directory structure matches spec**

```bash
find . -not -path './.git/*' -not -path './__pycache__/*' | sort
```

Expected output should include all files from the File Map at the top of this plan.

- [ ] **Step 3: Test active campaign switching**

```bash
python scripts/new_campaign.py test-switch dnd5e-2014
echo "test-switch" > active-campaign.txt
```

Then in Cursor chat, ask: `Who are the current NPCs in this campaign?`

Expected: Agent reads `active-campaign.txt`, loads `campaigns/test-switch/`, finds empty `world/npcs.md`, and reports that no NPCs have been added yet (not the example campaign's NPCs).

Then restore:
```bash
echo "example" > active-campaign.txt
```

- [ ] **Step 4: Clean up test campaign**

```bash
rm -rf campaigns/test-switch
```

- [ ] **Step 5: Final commit**

```bash
git add .
git commit -m "chore: final integration check and cleanup"
```

---

## Post-Build: Populate Ruleset Data

The skills are functional but will fall back to training knowledge until you add actual SRD files. Follow the instructions in each `rulesets/<edition>/README.md` to populate content.

**Quickest start for 5e 2024:**
- The [D&D Free Rules (2024)](https://www.dndbeyond.com/sources/dnd/free-rules) are available online
- Use a browser-to-markdown converter or copy key sections manually
- Start with `conditions.md` and `rules.md` — these cover 80% of table adjudication questions
