# D&D AI — DM Assistant Design Spec

*Date: 2026-04-27*

## Overview

A set of four Cursor AI skills that assist a Dungeon Master during play and session prep. All state is persisted as plain markdown/JSON files in a git repository. One campaign is active at a time. The system is ruleset-agnostic and extensible to new editions.

## Interface

Cursor agent/chat. No custom UI. The DM invokes skills by name in conversation. Dice rolling is physical by default; the `dice` skill is available on explicit request only. Players manage nothing in this system — it is a DM-only tool.

## Repository Structure

```
dnd-ai/
├── active-campaign.txt      # Single line: name of the active campaign folder
├── rulesets/
│   ├── dnd5e-2014/          # SRD markdown/JSON for 5e 2014
│   ├── dnd5e-2024/          # SRD markdown/JSON for 5e 2024 (primary)
│   └── pathfinder2e/        # SRD markdown/JSON for PF2e
├── campaigns/
│   ├── <active-campaign>/
│   │   ├── campaign.md      # Premise, world lore, arc overview
│   │   ├── ruleset.txt      # Single line: e.g. "dnd5e-2024"
│   │   ├── sessions/
│   │   │   └── session-NNN.md   # Append-only narrative log per session
│   │   ├── world/
│   │   │   ├── npcs.md          # NPC roster, motivations, current status
│   │   │   ├── locations.md     # Places visited, secrets revealed
│   │   │   └── factions.md      # Factions, their goals, relationships
│   │   └── characters/
│   │       ├── <name>.json      # Machine-readable character sheet (source of truth)
│   │       └── <name>.md        # Human-readable companion / flavor notes
│   └── <other-campaign>/    # Paused or completed campaigns coexist here
├── skills/
│   ├── rules/SKILL.md
│   ├── story/SKILL.md
│   ├── characters/SKILL.md
│   └── dice/SKILL.md
└── docs/
    └── superpowers/specs/
```

## Active Campaign & Multi-Campaign Support

Multiple campaigns can coexist under `campaigns/` in any state (active, paused, completed). The file `active-campaign.txt` at the repo root contains a single line — the folder name of the currently active campaign (e.g., `curse-of-strahd`). All four skills read this file on invocation to know which campaign directory to load. Campaign contexts are fully isolated; switching never contaminates state.

**Starting a new campaign:**
1. Create `campaigns/<new-name>/` with `campaign.md`, `ruleset.txt`, and empty `sessions/`, `world/`, `characters/` directories.
2. Update `active-campaign.txt` to the new campaign name.
3. Commit.

**Switching to a paused campaign:**
1. Update `active-campaign.txt` to the target campaign name.
2. Commit.

The git log on each campaign folder is its independent history. Switching is a single-line file change.

## The Four Skills

### `rules`

Loads rulebook content from `rulesets/<edition>/` based on the active campaign's `ruleset.txt`. Answers rules questions and adjudicates edge cases with citations to the source material. Falls back to web search when local docs don't cover something; local always wins on conflict. Read-only — never writes campaign files.

### `story`

Loads `campaign.md`, recent session logs, `world/npcs.md`, `world/locations.md`, and `world/factions.md` on invocation to build its context window. Assists with:

- NPC dialogue, personality, and reactions
- Encounter hooks and plot twists
- Session recaps and "previously on…" summaries
- Surfacing past decisions when they become relevant again
- Building story arcs and foreshadowing

Proposes updates to world files when new information is revealed (NPCs discovered, locations unlocked, faction dynamics changed). The DM reviews and confirms before anything is written. Session logs are append-only; each end-of-session git commit is the save point.

### `characters`

Owns all files in `characters/` for the active campaign. Tracks:

- Hit points (current / max / temp)
- Experience points and level progression
- Spell slots and other limited resources
- Conditions and status effects
- Inventory and equipment
- Class features and abilities

The DM narrates what happened ("Lira took 8 fire damage, concentration broken") and the skill updates the JSON accordingly. Can produce a compact party status summary for combat situations. JSON is the machine-readable source of truth; the markdown companion is human-readable flavor.

### `dice`

Pure utility — no campaign context required. Accepts standard dice notation:

- `XdY`, `XdY+Z`, `XdY-Z`
- `2d20 advantage` / `2d20 disadvantage`
- `4d6kh3` (keep highest 3, for character generation)
- Named roll tables (e.g., random encounter, wild magic surge) — table definitions stored in `rulesets/<edition>/tables/`

Invoked explicitly by the DM when they want the agent to roll instead of the physical table. Results are returned with a full breakdown and fed back into session narrative manually.

## Rules Sourcing

**Base layer:** Community SRD data (5e 2014, 5e 2024, Pathfinder 2e) as structured markdown/JSON stored in `rulesets/`. Freely and legally available.

**Supplement layer:** DM-owned PDFs (non-SRD subclasses, adventure modules, homebrew) converted to markdown and added to the relevant ruleset folder.

**V1 approach:** Direct file reads — the agent reads relevant ruleset files directly. No vector/RAG search. This is sufficient given Cursor's context window. RAG is a future upgrade if rulebook volume becomes unmanageable.

**Extensibility:** Adding a new ruleset = adding a folder to `rulesets/` and declaring it in a campaign's `ruleset.txt`.

## Supported Rulesets (v1)

| ID | Description |
|----|-------------|
| `dnd5e-2014` | D&D 5th Edition (2014 Player's Handbook) |
| `dnd5e-2024` | D&D 5th Edition Revised (2024, primary) |
| `pathfinder2e` | Pathfinder 2nd Edition |

## Session Workflow

1. **Start of session:** DM invokes `story` — it reads campaign files and produces a recap of where things stand.
2. **During play:** DM invokes whichever skill is relevant:
   - Rules question → `rules`
   - HP update / level up → `characters`
   - NPC dialogue / plot hook → `story`
   - Agent-rolled check → `dice` (explicit only)
3. **End of session:** DM reviews `story`'s proposed session log, world file updates, and any character changes. Adjusts as needed.
4. **Commit:** DM commits all changes to git. That commit is the canonical session save point and full history is preserved.

## Persistence Contract

- Session logs are **append-only** — never retroactively edited.
- Character JSON is the **single source of truth** for mechanical state.
- World markdown files are **living documents** — updated as the story evolves.
- `campaign.md` is **stable** — it describes the premise and arc, not session-by-session state.
- Git history is the **complete campaign record** — any prior state is recoverable.

## Out of Scope (v1)

- Dice rolling UI or automation (physical table; `dice` skill is opt-in only)
- Parallel multi-campaign state (multiple campaigns can exist, but only one is active at a time)
- Vector / RAG semantic search over rulebooks
- Custom web UI or player-facing interface
- Online sync or multiplayer state sharing
