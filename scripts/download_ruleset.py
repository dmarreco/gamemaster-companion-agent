#!/usr/bin/env python3
"""
Downloads SRD ruleset data from the Open5e API and formats it as local markdown files.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA SOURCE & LICENSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All content downloaded by this script originates from the D&D 5e System
Reference Document (SRD 5.1), published by Wizards of the Coast LLC.

  License:  Creative Commons Attribution 4.0 International (CC BY 4.0)
            https://creativecommons.org/licenses/by/4.0/

  Source:   https://dnd.wizards.com/resources/systems-reference-document
            Served via Open5e (https://open5e.com) — an open-source project
            that provides a free JSON API over the SRD content.

  Notice:   "Dungeons & Dragons" and "D&D" are trademarks of Wizards of the
            Coast LLC. This script is not affiliated with or endorsed by
            Wizards of the Coast.

The downloaded files are intentionally excluded from this repository's git
history (see .gitignore). They are reference-only local copies for use by the
AI skills in this project. Do not redistribute them as standalone files without
retaining this attribution.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
    python3 scripts/download_ruleset.py dnd5e-2014
    python3 scripts/download_ruleset.py dnd5e-2024  # same SRD base; add 2024-specific
                                                    # content manually as supplements

Requirements:
    pip install requests
"""

import argparse
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests not found. Install with: python3 -m pip install requests", file=sys.stderr)
    sys.exit(1)

BASE_URL = "https://api.open5e.com/v1"
SRD_SLUG = "wotc-srd"

SUPPORTED = ["dnd5e-2014", "dnd5e-2024"]


def fetch(url: str) -> dict:
    """Fetch a URL and return parsed JSON."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all(endpoint: str, params: str = "") -> list:
    """Fetch all pages of a paginated endpoint."""
    results = []
    url = f"{BASE_URL}/{endpoint}/?limit=200{params}"
    page = 1
    while url:
        print(f"  Fetching {endpoint} page {page}...", end=" ", flush=True)
        data = fetch(url)
        results.extend(data["results"])
        print(f"({len(results)}/{data['count']})")
        url = data.get("next")
        page += 1
        if url:
            time.sleep(0.3)
    return results


# ── Formatters ────────────────────────────────────────────────────────────────

def fmt_conditions(conditions: list) -> str:
    lines = ["# Conditions\n"]
    lines.append(
        "Conditions alter a creature's capabilities in various ways, and can arise "
        "as a result of a spell, a class feature, a monster's attack, or other effect. "
        "Most conditions are defined below.\n"
    )
    for c in sorted(conditions, key=lambda x: x["name"]):
        lines.append(f"## {c['name']}\n")
        lines.append(c["desc"].strip())
        lines.append("")
    return "\n".join(lines)


def fmt_sections(sections: list) -> str:
    lines = ["# Rules\n"]
    lines.append(
        "Core rules from the D&D 5e SRD 5.1 (CC BY 4.0 — Wizards of the Coast).\n"
    )
    # All sections have a parent category name — group by that
    by_parent: dict[str, list] = {}
    for s in sections:
        parent = s.get("parent") or "General"
        by_parent.setdefault(parent, []).append(s)

    for parent in sorted(by_parent):
        lines.append(f"## {parent}\n")
        for section in sorted(by_parent[parent], key=lambda x: x["name"]):
            lines.append(f"### {section['name']}\n")
            if section.get("desc"):
                lines.append(section["desc"].strip())
            lines.append("")
    return "\n".join(lines)


def fmt_spells(spells: list) -> str:
    lines = ["# Spells\n"]
    lines.append(
        "SRD spells from D&D 5e SRD 5.1 (CC BY 4.0 — Wizards of the Coast).\n"
    )
    by_level: dict[int, list] = {}
    for s in spells:
        lvl = s.get("spell_level", 0)
        by_level.setdefault(lvl, []).append(s)

    level_names = {0: "Cantrips (Level 0)", **{i: f"Level {i}" for i in range(1, 10)}}
    for lvl in sorted(by_level):
        lines.append(f"## {level_names.get(lvl, f'Level {lvl}')}\n")
        for spell in sorted(by_level[lvl], key=lambda x: x["name"]):
            lines.append(f"### {spell['name']}")
            meta = []
            if lvl == 0:
                meta.append(f"{spell.get('school', '').title()} cantrip")
            else:
                meta.append(f"Level {lvl} {spell.get('school', '').lower()}")
            if spell.get("ritual"):
                meta.append("(ritual)")
            lines.append(f"*{', '.join(meta)}*\n")
            lines.append(f"**Casting Time:** {spell.get('casting_time', '—')}")
            lines.append(f"**Range:** {spell.get('range', '—')}")
            components = spell.get("components", "")
            if spell.get("material"):
                components += f" ({spell['material']})"
            lines.append(f"**Components:** {components}")
            lines.append(f"**Duration:** {spell.get('duration', '—')}")
            if spell.get("concentration"):
                lines[-1] += " (concentration)"
            lines.append(f"**Classes:** {spell.get('dnd_class', '—')}\n")
            if spell.get("desc"):
                lines.append(spell["desc"].strip())
            if spell.get("higher_level"):
                lines.append(f"\n**At Higher Levels.** {spell['higher_level'].strip()}")
            lines.append("")
    return "\n".join(lines)


def fmt_monsters(monsters: list) -> str:
    lines = ["# Monsters\n"]
    lines.append(
        "SRD monster stat blocks from D&D 5e SRD 5.1 (CC BY 4.0 — Wizards of the Coast).\n"
    )
    for m in sorted(monsters, key=lambda x: x["name"]):
        lines.append(f"## {m['name']}")
        lines.append(
            f"*{m.get('size', '')} {m.get('type', '')}, {m.get('alignment', '')}*\n"
        )
        lines.append(f"**Armor Class:** {m.get('armor_class', '—')} {m.get('armor_desc', '')}")
        hp = m.get("hit_points", "—")
        hd = m.get("hit_dice", "")
        lines.append(f"**Hit Points:** {hp} ({hd})")
        speed = m.get("speed", {})
        speed_str = ", ".join(f"{k} {v}" for k, v in speed.items()) if isinstance(speed, dict) else str(speed)
        lines.append(f"**Speed:** {speed_str}\n")

        # Ability scores
        scores = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        keys = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        def mod(v): return f"+{(v-10)//2}" if (v-10)//2 >= 0 else str((v-10)//2)
        score_row = " | ".join(f"{s} {m.get(k, '—')} ({mod(m.get(k, 10))})" for s, k in zip(scores, keys))
        lines.append(score_row + "\n")

        if m.get("saving_throws"):
            lines.append(f"**Saving Throws:** {m['saving_throws']}")
        if m.get("skills"):
            lines.append(f"**Skills:** {m['skills']}")
        if m.get("damage_vulnerabilities"):
            lines.append(f"**Damage Vulnerabilities:** {m['damage_vulnerabilities']}")
        if m.get("damage_resistances"):
            lines.append(f"**Damage Resistances:** {m['damage_resistances']}")
        if m.get("damage_immunities"):
            lines.append(f"**Damage Immunities:** {m['damage_immunities']}")
        if m.get("condition_immunities"):
            lines.append(f"**Condition Immunities:** {m['condition_immunities']}")
        if m.get("senses"):
            lines.append(f"**Senses:** {m['senses']}")
        if m.get("languages"):
            lines.append(f"**Languages:** {m['languages']}")
        cr = m.get("challenge_rating", "—")
        xp = m.get("cr", "")
        lines.append(f"**Challenge:** {cr}\n")

        for trait in m.get("special_abilities") or []:
            lines.append(f"***{trait['name']}.*** {trait.get('desc', '')}\n")

        if m.get("actions"):
            lines.append("### Actions\n")
            for action in m["actions"]:
                lines.append(f"***{action['name']}.*** {action.get('desc', '')}\n")

        if m.get("legendary_actions"):
            lines.append("### Legendary Actions\n")
            if m.get("legendary_desc"):
                lines.append(m["legendary_desc"] + "\n")
            for action in m["legendary_actions"]:
                lines.append(f"***{action['name']}.*** {action.get('desc', '')}\n")

        if m.get("reactions"):
            lines.append("### Reactions\n")
            for action in m["reactions"]:
                lines.append(f"***{action['name']}.*** {action.get('desc', '')}\n")

        lines.append("")
    return "\n".join(lines)


def fmt_classes(classes: list) -> str:
    lines = ["# Classes\n"]
    lines.append(
        "Class features from D&D 5e SRD 5.1 (CC BY 4.0 — Wizards of the Coast).\n"
    )
    for cls in sorted(classes, key=lambda x: x["name"]):
        lines.append(f"## {cls['name']}\n")
        if cls.get("desc"):
            lines.append(cls["desc"].strip())
            lines.append("")
        if cls.get("hit_dice"):
            lines.append(f"**Hit Dice:** 1d{cls['hit_dice']} per {cls['name']} level")
        if cls.get("hp_at_1st_level"):
            lines.append(f"**HP at 1st Level:** {cls['hp_at_1st_level']}")
        if cls.get("hp_at_higher_levels"):
            lines.append(f"**HP at Higher Levels:** {cls['hp_at_higher_levels']}")
        if cls.get("prof_armor"):
            lines.append(f"**Armor Proficiencies:** {cls['prof_armor']}")
        if cls.get("prof_weapons"):
            lines.append(f"**Weapon Proficiencies:** {cls['prof_weapons']}")
        if cls.get("prof_tools"):
            lines.append(f"**Tool Proficiencies:** {cls['prof_tools']}")
        if cls.get("prof_saving_throws"):
            lines.append(f"**Saving Throw Proficiencies:** {cls['prof_saving_throws']}")
        if cls.get("prof_skills"):
            lines.append(f"**Skill Proficiencies:** {cls['prof_skills']}")
        lines.append("")

        for feature in cls.get("features", []) or []:
            level = feature.get("level", "?")
            fname = feature.get("name", "Feature")
            lines.append(f"### {fname} (Level {level})\n")
            if feature.get("desc"):
                lines.append(feature["desc"].strip())
            lines.append("")

        for subclass in cls.get("archetypes", []) or []:
            lines.append(f"### Subclass: {subclass['name']}\n")
            if subclass.get("desc"):
                lines.append(subclass["desc"].strip())
                lines.append("")
            for feature in subclass.get("features", []) or []:
                level = feature.get("level", "?")
                fname = feature.get("name", "Feature")
                lines.append(f"#### {fname} (Level {level})\n")
                if feature.get("desc"):
                    lines.append(feature["desc"].strip())
                lines.append("")
    return "\n".join(lines)


def fmt_equipment(weapons: list, armor: list) -> str:
    lines = ["# Equipment\n"]
    lines.append(
        "Weapons and armor from D&D 5e SRD 5.1 (CC BY 4.0 — Wizards of the Coast).\n"
    )

    lines.append("## Weapons\n")
    lines.append("| Name | Cost | Damage | Weight | Properties |")
    lines.append("|------|------|--------|--------|------------|")
    for w in sorted(weapons, key=lambda x: x["name"]):
        name = w.get("name", "—")
        cost = w.get("cost", "—")
        dmg = f"{w.get('damage_dice', '—')} {w.get('damage_type', '')}".strip()
        weight = w.get("weight", "—")
        props = w.get("properties", [])
        if isinstance(props, list):
            props_str = ", ".join(p.get("name", p) if isinstance(p, dict) else str(p) for p in props)
        else:
            props_str = str(props)
        lines.append(f"| {name} | {cost} | {dmg} | {weight} | {props_str} |")
    lines.append("")

    lines.append("## Armor\n")
    lines.append("| Name | Cost | AC | Strength | Stealth | Weight |")
    lines.append("|------|------|----|----------|---------|--------|")
    for a in sorted(armor, key=lambda x: x["name"]):
        name = a.get("name", "—")
        cost = a.get("cost", "—")
        ac = a.get("base_ac", "—")
        if a.get("add_dex_modifier"):
            ac = f"{ac} + Dex"
            if a.get("max_dex_modifier"):
                ac += f" (max {a['max_dex_modifier']})"
        strength = a.get("strength_requirement") or "—"
        stealth = "Disadvantage" if a.get("stealth_disadvantage") else "—"
        weight = a.get("weight", "—")
        lines.append(f"| {name} | {cost} | {ac} | {strength} | {stealth} | {weight} |")
    lines.append("")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

ATTRIBUTION_NOTICE = """
Content: D&D 5e SRD 5.1 — Wizards of the Coast LLC
License: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
Source:  https://open5e.com / https://dnd.wizards.com/resources/systems-reference-document
Note:    Downloaded files are gitignored and for local AI skill use only.
"""


def download(ruleset: str, out_dir: Path) -> None:
    print(ATTRIBUTION_NOTICE)
    print(f"Downloading SRD data for '{ruleset}' → {out_dir}\n")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("📖 Conditions...")
    conditions = fetch_all("conditions")
    (out_dir / "conditions.md").write_text(fmt_conditions(conditions))
    print(f"  ✓ {len(conditions)} conditions → conditions.md")

    print("\n📖 Rules sections...")
    sections = fetch_all("sections")
    (out_dir / "rules.md").write_text(fmt_sections(sections))
    print(f"  ✓ {len(sections)} sections → rules.md")

    print("\n📖 Spells (SRD only)...")
    spells = fetch_all("spells", f"&document__slug={SRD_SLUG}")
    (out_dir / "spells.md").write_text(fmt_spells(spells))
    print(f"  ✓ {len(spells)} spells → spells.md")

    print("\n📖 Monsters (SRD only)...")
    monsters = fetch_all("monsters", f"&document__slug={SRD_SLUG}")
    (out_dir / "monsters.md").write_text(fmt_monsters(monsters))
    print(f"  ✓ {len(monsters)} monsters → monsters.md")

    print("\n📖 Classes...")
    classes = fetch_all("classes")
    (out_dir / "classes.md").write_text(fmt_classes(classes))
    print(f"  ✓ {len(classes)} classes → classes.md")

    print("\n📖 Equipment (weapons + armor)...")
    weapons = fetch_all("weapons")
    armor = fetch_all("armor")
    (out_dir / "equipment.md").write_text(fmt_equipment(weapons, armor))
    print(f"  ✓ {len(weapons)} weapons + {len(armor)} armor → equipment.md")

    sizes = {f.name: f"{f.stat().st_size // 1024}KB" for f in out_dir.iterdir() if f.suffix == ".md" and f.name != "README.md"}
    print(f"\n✅ Done! Files written:\n")
    for fname, size in sorted(sizes.items()):
        print(f"  {fname:20s} {size}")
    print(f"\nAdd rulesets to .gitignore if not already done, then they won't be committed.")


def main():
    parser = argparse.ArgumentParser(
        description="Download SRD ruleset data from Open5e API."
    )
    parser.add_argument(
        "ruleset",
        help=f"Ruleset ID. Options: {', '.join(SUPPORTED)}",
    )
    args = parser.parse_args()

    if args.ruleset not in SUPPORTED:
        print(f"Error: Unknown ruleset '{args.ruleset}'. Options: {', '.join(SUPPORTED)}", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).parent.parent
    out_dir = repo_root / "rulesets" / args.ruleset
    download(args.ruleset, out_dir)


if __name__ == "__main__":
    main()
