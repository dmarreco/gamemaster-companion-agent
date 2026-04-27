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
