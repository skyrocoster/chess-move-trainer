# opening_catalog

Opening classification and analysis scripts.

## Purpose

Classifies chess positions by opening, tracks preferred moves per position, analyzes recurrence patterns, and maps opening relationships.

## Domain modules

Each domain follows a three-layer pattern: `*_schema.py` (DDL), `*_contract.py` (interfaces), `*_persistence.py` (SQLite access).

| Domain | Files | Purpose |
|--------|-------|---------|
| classification | `classification.py`, `classification_schema.py`, `classification_contract.py`, `classification_persistence.py` | Assigns ECO codes and opening names to positions |
| preferred_move | `preferred_move.py`, `preferred_move_schema.py`, `preferred_move_contract.py`, `preferred_move_history.py` | Tracks which moves are most common per position |
| recurrence | `recurrence.py`, `recurrence_schema.py`, `recurrence_contract.py`, `recurrence_persistence.py` | Analyzes how often positions recur across games |
| relationships | `relationships.py`, `relationship_persistence.py` | Maps parent-child relationships between positions |
| tracked_player | `tracked_player.py`, `tracked_player_schema.py`, `tracked_player_contract.py`, `tracked_player_persistence.py` | Projections scoped to a specific tracked player |

## Shared

- `schema.py` — ensures all core tables exist
- `importer.py` — batch import of classified positions
