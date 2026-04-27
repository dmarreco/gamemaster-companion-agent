#!/usr/bin/env python3
"""
Downloads SRD ruleset data from the Open5e API and formats it as local markdown files.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA SOURCE & LICENSE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

dnd5e-2014 content originates from the D&D 5e System Reference Document (SRD
5.1), published by Wizards of the Coast LLC.

dnd5e-2024 content originates from the D&D System Reference Document 5.2
(SRD 5.2), published by Wizards of the Coast LLC.

  License:  Creative Commons Attribution 4.0 International (CC BY 4.0)
            https://creativecommons.org/licenses/by/4.0/

  Source:   https://dnd.wizards.com/resources/systems-reference-document
            Served via Open5e (https://open5e.com) — an open-source project
            that provides a free JSON API over the SRD content.
            v1 API used for SRD 5.1 (2014); v2 API used for SRD 5.2 (2024).

  Notice:   "Dungeons & Dragons" and "D&D" are trademarks of Wizards of the
            Coast LLC. This script is not affiliated with or endorsed by
            Wizards of the Coast.

The downloaded files are intentionally excluded from this repository's git
history (see .gitignore). They are reference-only local copies for use by the
AI skills in this project. Do not redistribute them as standalone files without
retaining this attribution.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
    python3 scripts/download_ruleset.py dnd5e-2014   # SRD 5.1 via Open5e v1 API
    python3 scripts/download_ruleset.py dnd5e-2024   # SRD 5.2 via Open5e v2 API

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

BASE_URL_V1 = "https://api.open5e.com/v1"
BASE_URL_V2 = "https://api.open5e.com/v2"
SRD_SLUG_V1 = "wotc-srd"
SRD_SLUG_V2 = "srd-2024"

SUPPORTED = ["dnd5e-2014", "dnd5e-2024"]


def fetch(url: str) -> dict:
    """Fetch a URL and return parsed JSON."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all_v1(endpoint: str, params: str = "") -> list:
    """Fetch all pages from the v1 API."""
    results = []
    url = f"{BASE_URL_V1}/{endpoint}/?limit=200{params}"
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


def fetch_all_v2(endpoint: str, extra: str = "") -> list:
    """Fetch all pages from the v2 API filtered to srd-2024."""
    results = []
    url = f"{BASE_URL_V2}/{endpoint}/?document__key={SRD_SLUG_V2}&limit=200{extra}"
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


# ── v1 Formatters (dnd5e-2014) ────────────────────────────────────────────────

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


# ── v2 Formatters (dnd5e-2024) ────────────────────────────────────────────────

def fmt_spells_v2(spells: list) -> str:
    lines = ["# Spells\n"]
    lines.append("SRD spells from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")
    by_level: dict[int, list] = {}
    for s in spells:
        lvl = s.get("level", 0)
        by_level.setdefault(lvl, []).append(s)

    level_names = {0: "Cantrips (Level 0)", **{i: f"Level {i}" for i in range(1, 10)}}
    for lvl in sorted(by_level):
        lines.append(f"## {level_names.get(lvl, f'Level {lvl}')}\n")
        for spell in sorted(by_level[lvl], key=lambda x: x["name"]):
            lines.append(f"### {spell['name']}")
            school = spell.get("school") or {}
            school_name = school.get("name", "") if isinstance(school, dict) else str(school)
            if lvl == 0:
                meta = f"{school_name.lower()} cantrip"
            else:
                meta = f"Level {lvl} {school_name.lower()}"
            if spell.get("ritual"):
                meta += " (ritual)"
            lines.append(f"*{meta}*\n")
            lines.append(f"**Casting Time:** {spell.get('casting_time', '—')}")
            lines.append(f"**Range:** {spell.get('range_text') or spell.get('range', '—')}")
            components = []
            if spell.get("verbal"):
                components.append("V")
            if spell.get("somatic"):
                components.append("S")
            if spell.get("material"):
                mat = spell.get("material_specified") or ""
                components.append(f"M ({mat})" if mat else "M")
            lines.append(f"**Components:** {', '.join(components) or '—'}")
            lines.append(f"**Duration:** {spell.get('duration', '—')}" +
                         (" (concentration)" if spell.get("concentration") else ""))
            classes = spell.get("classes") or []
            class_names = ", ".join(c.get("name", c) if isinstance(c, dict) else str(c) for c in classes)
            lines.append(f"**Classes:** {class_names or '—'}\n")
            if spell.get("desc"):
                lines.append(spell["desc"].strip())
            if spell.get("higher_level"):
                lines.append(f"\n**At Higher Levels.** {spell['higher_level'].strip()}")
            lines.append("")
    return "\n".join(lines)


def fmt_creatures_v2(creatures: list) -> str:
    lines = ["# Creatures\n"]
    lines.append("SRD creature stat blocks from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")
    for m in sorted(creatures, key=lambda x: x["name"]):
        lines.append(f"## {m['name']}")
        size = m.get("size") or {}
        size_name = size.get("name", "") if isinstance(size, dict) else str(size)
        ctype = m.get("type") or {}
        type_name = ctype.get("name", "") if isinstance(ctype, dict) else str(ctype)
        lines.append(f"*{size_name} {type_name}, {m.get('alignment', '')}*\n")
        ac = m.get("armor_class", "—")
        ac_detail = m.get("armor_detail", "")
        lines.append(f"**Armor Class:** {ac} {ac_detail}".strip())
        lines.append(f"**Hit Points:** {m.get('hit_points', '—')} ({m.get('hit_dice', '')})")
        speed = m.get("speed") or {}
        if isinstance(speed, dict):
            unit = speed.pop("unit", "ft") if "unit" in speed else "ft"
            speed_str = ", ".join(f"{k} {v} {unit}" for k, v in speed.items() if v)
        else:
            speed_str = str(speed)
        lines.append(f"**Speed:** {speed_str}\n")

        ab = m.get("ability_scores") or {}
        def mod(v): return f"+{(v-10)//2}" if (v-10)//2 >= 0 else str((v-10)//2)
        score_parts = []
        for stat in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            v = ab.get(stat, 10)
            score_parts.append(f"{stat[:3].upper()} {v} ({mod(v)})")
        lines.append(" | ".join(score_parts) + "\n")

        ri = m.get("resistances_and_immunities") or {}
        if ri.get("damage_immunities_display"):
            lines.append(f"**Damage Immunities:** {ri['damage_immunities_display']}")
        if ri.get("damage_resistances_display"):
            lines.append(f"**Damage Resistances:** {ri['damage_resistances_display']}")
        if ri.get("damage_vulnerabilities_display"):
            lines.append(f"**Damage Vulnerabilities:** {ri['damage_vulnerabilities_display']}")
        if ri.get("condition_immunities_display"):
            lines.append(f"**Condition Immunities:** {ri['condition_immunities_display']}")

        senses = []
        if m.get("darkvision_range"):
            senses.append(f"Darkvision {m['darkvision_range']} ft")
        if m.get("blindsight_range"):
            senses.append(f"Blindsight {m['blindsight_range']} ft")
        if m.get("truesight_range"):
            senses.append(f"Truesight {m['truesight_range']} ft")
        if m.get("tremorsense_range"):
            senses.append(f"Tremorsense {m['tremorsense_range']} ft")
        if m.get("passive_perception"):
            senses.append(f"passive Perception {m['passive_perception']}")
        if senses:
            lines.append(f"**Senses:** {', '.join(senses)}")
        if m.get("languages"):
            lines.append(f"**Languages:** {m['languages']}")
        lines.append(f"**Challenge:** {m.get('challenge_rating', '—')}\n")

        for trait in m.get("traits") or []:
            lines.append(f"***{trait['name']}.*** {trait.get('desc', '')}\n")

        action_types = [
            ("ACTION", "Actions"),
            ("BONUS_ACTION", "Bonus Actions"),
            ("REACTION", "Reactions"),
            ("LEGENDARY_ACTION", "Legendary Actions"),
        ]
        actions_by_type: dict[str, list] = {}
        for a in m.get("actions") or []:
            atype = a.get("action_type", "ACTION")
            actions_by_type.setdefault(atype, []).append(a)

        for atype, header in action_types:
            if atype in actions_by_type:
                lines.append(f"### {header}\n")
                for action in sorted(actions_by_type[atype],
                                     key=lambda x: x.get("order_in_statblock", 99)):
                    lines.append(f"***{action['name']}.*** {action.get('desc', '')}\n")

        lines.append("")
    return "\n".join(lines)


def fmt_classes_v2(classes: list) -> str:
    lines = ["# Classes\n"]
    lines.append("Class features from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")
    for cls in sorted(classes, key=lambda x: x["name"]):
        lines.append(f"## {cls['name']}\n")
        if cls.get("desc"):
            lines.append(cls["desc"].strip())
            lines.append("")
        for feature in sorted(
            cls.get("features") or [],
            key=lambda f: min((g["level"] for g in f.get("gained_at", [{"level": 99}])), default=99)
        ):
            levels = sorted(g["level"] for g in feature.get("gained_at") or [])
            level_str = "/".join(str(l) for l in levels) if levels else "?"
            lines.append(f"### {feature['name']} (Level {level_str})\n")
            if feature.get("desc"):
                lines.append(feature["desc"].strip())
            lines.append("")
    return "\n".join(lines)


def fmt_species(species_list: list) -> str:
    lines = ["# Species\n"]
    lines.append("Species (races) from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")
    base = [s for s in species_list if not s.get("is_subspecies")]
    subs = [s for s in species_list if s.get("is_subspecies")]

    for sp in sorted(base, key=lambda x: x["name"]):
        lines.append(f"## {sp['name']}\n")
        if sp.get("desc"):
            lines.append(sp["desc"].strip())
            lines.append("")
        for trait in sp.get("traits") or []:
            lines.append(f"**{trait['name']}:** {trait.get('desc', '').strip()}\n")
        lines.append("")

    if subs:
        lines.append("## Subspecies\n")
        for sp in sorted(subs, key=lambda x: x["name"]):
            parent = sp.get("subspecies_of") or {}
            parent_name = parent.get("name", "") if isinstance(parent, dict) else str(parent)
            lines.append(f"### {sp['name']}" + (f" ({parent_name})" if parent_name else "") + "\n")
            if sp.get("desc"):
                lines.append(sp["desc"].strip())
                lines.append("")
            for trait in sp.get("traits") or []:
                lines.append(f"**{trait['name']}:** {trait.get('desc', '').strip()}\n")
            lines.append("")
    return "\n".join(lines)


def fmt_backgrounds_v2(backgrounds: list) -> str:
    lines = ["# Backgrounds\n"]
    lines.append("Backgrounds from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")
    for bg in sorted(backgrounds, key=lambda x: x["name"]):
        lines.append(f"## {bg['name']}\n")
        if bg.get("desc"):
            lines.append(bg["desc"].strip())
            lines.append("")
        for benefit in bg.get("benefits") or []:
            btype = benefit.get("type", "")
            bname = benefit.get("name", btype.replace("_", " ").title())
            lines.append(f"**{bname}:** {benefit.get('desc', '').strip()}\n")
        lines.append("")
    return "\n".join(lines)


def fmt_feats_v2(feats: list) -> str:
    lines = ["# Feats\n"]
    lines.append("Feats from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")
    for feat in sorted(feats, key=lambda x: x["name"]):
        lines.append(f"## {feat['name']}\n")
        if feat.get("prerequisite"):
            lines.append(f"*Prerequisite: {feat['prerequisite']}*\n")
        if feat.get("desc"):
            lines.append(feat["desc"].strip())
            lines.append("")
        for benefit in feat.get("benefits") or []:
            if benefit.get("desc"):
                lines.append(f"- {benefit['desc'].strip()}")
        lines.append("")
    return "\n".join(lines)


def fmt_rules_v2(rules: list) -> str:
    lines = ["# Rules\n"]
    lines.append("Core rules from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")
    for rule in sorted(rules, key=lambda x: x.get("index") or x["name"]):
        header = "#" * min(rule.get("initialHeaderLevel", 2) + 1, 4)
        lines.append(f"{header} {rule['name']}\n")
        if rule.get("desc"):
            lines.append(rule["desc"].strip())
        lines.append("")
    return "\n".join(lines)


def fmt_equipment_v2(weapons: list, armor: list) -> str:
    lines = ["# Equipment\n"]
    lines.append("Weapons and armor from D&D SRD 5.2 (CC BY 4.0 — Wizards of the Coast).\n")

    lines.append("## Weapons\n")
    lines.append("| Name | Cost | Damage | Weight | Properties |")
    lines.append("|------|------|--------|--------|------------|")
    for w in sorted(weapons, key=lambda x: x["name"]):
        name = w.get("name", "—")
        cost = w.get("cost", "—")
        dmg = f"{w.get('damage_dice', '—')} {w.get('damage_type', '')}".strip()
        weight = w.get("weight", "—")
        props = w.get("properties") or []
        prop_parts = []
        for p in props:
            if isinstance(p, dict):
                prop_obj = p.get("property") or p
                pname = prop_obj.get("name", "") if isinstance(prop_obj, dict) else str(prop_obj)
                detail = p.get("detail")
                prop_parts.append(f"{pname} ({detail})" if detail else pname)
            else:
                prop_parts.append(str(p))
        props_str = ", ".join(prop_parts)
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


def _print_summary(out_dir: Path) -> None:
    sizes = {
        f.name: f"{f.stat().st_size // 1024}KB"
        for f in out_dir.iterdir()
        if f.suffix == ".md" and f.name != "README.md"
    }
    print("\n✅ Done! Files written:\n")
    for fname, size in sorted(sizes.items()):
        print(f"  {fname:20s} {size}")


def download_v1(out_dir: Path) -> None:
    """Download SRD 5.1 (2014) data via Open5e v1 API."""
    out_dir.mkdir(parents=True, exist_ok=True)

    print("📖 Conditions...")
    conditions = fetch_all_v1("conditions")
    (out_dir / "conditions.md").write_text(fmt_conditions(conditions))
    print(f"  ✓ {len(conditions)} conditions → conditions.md")

    print("\n📖 Rules sections...")
    sections = fetch_all_v1("sections")
    (out_dir / "rules.md").write_text(fmt_sections(sections))
    print(f"  ✓ {len(sections)} sections → rules.md")

    print("\n📖 Spells (SRD only)...")
    spells = fetch_all_v1("spells", f"&document__slug={SRD_SLUG_V1}")
    (out_dir / "spells.md").write_text(fmt_spells(spells))
    print(f"  ✓ {len(spells)} spells → spells.md")

    print("\n📖 Monsters (SRD only)...")
    monsters = fetch_all_v1("monsters", f"&document__slug={SRD_SLUG_V1}")
    (out_dir / "monsters.md").write_text(fmt_monsters(monsters))
    print(f"  ✓ {len(monsters)} monsters → monsters.md")

    print("\n📖 Classes...")
    classes = fetch_all_v1("classes")
    (out_dir / "classes.md").write_text(fmt_classes(classes))
    print(f"  ✓ {len(classes)} classes → classes.md")

    print("\n📖 Equipment (weapons + armor)...")
    weapons = fetch_all_v1("weapons")
    armor = fetch_all_v1("armor")
    (out_dir / "equipment.md").write_text(fmt_equipment(weapons, armor))
    print(f"  ✓ {len(weapons)} weapons + {len(armor)} armor → equipment.md")

    _print_summary(out_dir)


def download_v2(out_dir: Path) -> None:
    """Download SRD 5.2 (2024) data via Open5e v2 API."""
    out_dir.mkdir(parents=True, exist_ok=True)

    print("📖 Rules...")
    rules = fetch_all_v2("rules")
    (out_dir / "rules.md").write_text(fmt_rules_v2(rules))
    print(f"  ✓ {len(rules)} rules → rules.md")

    print("\n📖 Spells...")
    spells = fetch_all_v2("spells")
    (out_dir / "spells.md").write_text(fmt_spells_v2(spells))
    print(f"  ✓ {len(spells)} spells → spells.md")

    print("\n📖 Creatures...")
    creatures = fetch_all_v2("creatures")
    (out_dir / "monsters.md").write_text(fmt_creatures_v2(creatures))
    print(f"  ✓ {len(creatures)} creatures → monsters.md")

    print("\n📖 Classes...")
    classes = fetch_all_v2("classes")
    (out_dir / "classes.md").write_text(fmt_classes_v2(classes))
    print(f"  ✓ {len(classes)} classes → classes.md")

    print("\n📖 Species...")
    species = fetch_all_v2("species")
    (out_dir / "species.md").write_text(fmt_species(species))
    print(f"  ✓ {len(species)} species → species.md")

    print("\n📖 Backgrounds...")
    backgrounds = fetch_all_v2("backgrounds")
    (out_dir / "backgrounds.md").write_text(fmt_backgrounds_v2(backgrounds))
    print(f"  ✓ {len(backgrounds)} backgrounds → backgrounds.md")

    print("\n📖 Feats...")
    feats = fetch_all_v2("feats")
    (out_dir / "feats.md").write_text(fmt_feats_v2(feats))
    print(f"  ✓ {len(feats)} feats → feats.md")

    print("\n📖 Equipment (weapons + armor)...")
    weapons = fetch_all_v2("weapons")
    armor = fetch_all_v2("armor")
    (out_dir / "equipment.md").write_text(fmt_equipment_v2(weapons, armor))
    print(f"  ✓ {len(weapons)} weapons + {len(armor)} armor → equipment.md")

    _print_summary(out_dir)


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

    if args.ruleset == "dnd5e-2024":
        print(ATTRIBUTION_NOTICE)
        print(f"Downloading SRD 5.2 data (2024) → {out_dir}\n")
        download_v2(out_dir)
    else:
        print(ATTRIBUTION_NOTICE)
        print(f"Downloading SRD 5.1 data (2014) → {out_dir}\n")
        download_v1(out_dir)


if __name__ == "__main__":
    main()
