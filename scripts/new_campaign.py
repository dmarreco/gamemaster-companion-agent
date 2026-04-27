#!/usr/bin/env python3
"""
Scaffolds a new campaign directory under campaigns/.

Usage:
    python scripts/new_campaign.py <campaign-name> <ruleset> [--setting <setting-name>]

Example:
    python scripts/new_campaign.py curse-of-strahd dnd5e-2024
    python scripts/new_campaign.py freedom-one-shot dnd5e-2014 --setting dark-sun
"""

import argparse
import sys
from pathlib import Path

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


def create_campaign(
    name: str,
    ruleset: str,
    setting: str = None,
    campaigns_dir: Path = None,
) -> Path:
    """
    Creates a new campaign directory structure.

    Args:
        name: Campaign folder name (kebab-case recommended)
        ruleset: One of VALID_RULESETS
        setting: Optional setting name (e.g. 'dark-sun'). Writes setting.txt if provided.
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

    if setting:
        (campaign_path / "setting.txt").write_text(setting + "\n")

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
    parser.add_argument(
        "--setting",
        default=None,
        help="Setting name (e.g. dark-sun). Creates setting.txt linking to settings/<name>/.",
    )
    args = parser.parse_args()

    try:
        path = create_campaign(args.name, args.ruleset, setting=args.setting)
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
