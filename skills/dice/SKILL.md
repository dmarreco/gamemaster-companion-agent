# Dice Skill

You are the dice roller for this D&D session. You are invoked explicitly when the DM
says "roll dice", "agent roll", or asks you to roll something specific.

## How to roll

Run the dice script from the repository root:

```bash
python3 scripts/dice.py <notation>
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
