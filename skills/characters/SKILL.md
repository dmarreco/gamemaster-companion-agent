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

| Character | HP | Conditions | Key Resources |
|-----------|-----|-----------|---------------|
| Thorin (Fighter 3) | 28/34 | — | Action Surge ✅, Sup. Dice 3/4 |

## What you do NOT do

- Do not make rulings on what damage type applies — that is the rules skill's job
- Do not narrate events — that is the story skill's job
- Do not create characters from scratch — ask the DM for the full character sheet first
