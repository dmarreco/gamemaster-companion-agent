# Dark Sun — Campaign Setting

Athas is a savage, post-apocalyptic world where arcane magic drains life from the land,
water is precious, metal is rare, and slavery is common. City-states are ruled by immortal
Sorcerer-Kings who crush dissent through their Templar bureaucracies.

## Compatible rulesets

- `dnd5e-2014` (primary — this setting was converted with Dark Sun 5E homebrew classes)
- `dnd5e-2024`

## Source material

`source/` contains text extracted from *Dark Sun Campaign Setting 5E* (homebrew PDF, 526 pages).
These files are gitignored. Regenerate with:

```bash
python3 scripts/pdf_to_campaign.py "/path/to/Dark Sun Campaign Setting 5E.pdf" settings/dark-sun/source/ --min-heading-size 22.5
```

## World canon

`world/` contains canonical setting lore shared across all Dark Sun campaigns:
- `locations.md` — major cities, landmarks, regions of Athas
- `npcs.md` — Sorcerer-Kings, notable figures, recurring characters
- `factions.md` — Templars, Veiled Alliance, merchant houses, slave tribes
