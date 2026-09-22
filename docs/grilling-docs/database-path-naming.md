# Database path naming decisions

Date: 2026-09-22

## Goal

Make the host seed/export database and the live container database impossible to confuse in code while preserving their existing roles and container locations.

## Decisions

- Callers will select explicit path constants. The code will not infer the intended database from its runtime environment.
- The host seed/export file will move from `data/database/chess.db` to `data/database/chess-seed.db`.
- The live backend and worker database will remain `/workspace/data/database/chess.db` in their containers.
- The live Datasette database will remain `/data/chess.db` in its container.
- `DEFAULT_DATABASE_PATH` will be removed, not retained as a compatibility alias and not reassigned to either role.
- The intended names are `HOST_SEED_DATABASE_PATH` and `LIVE_DATABASE_PATH`. Assessment may determine where each name should be owned and which callers require it, but it must preserve the explicit host-versus-live choice.

## Reasoning

The two files have different ownership and purposes. Explicit names make that distinction visible at every call site and in tests. Runtime detection would hide the choice, and retaining the old default name would continue to permit ambiguous code. Renaming the host file provides a filesystem-level distinction as well as a code-level distinction.

## Constraints and exclusions

- Host commands must continue to default to the host seed/export copy, now at its new name.
- Backend and worker containers must continue to resolve the live database to `/workspace/data/database/chess.db`.
- Datasette must continue to resolve the live database to `/data/chess.db`.
- Database behavior, data semantics, and service topology must not change.
- Existing literal-pinning tests, CLI help text, documentation, and Compose arguments must be updated deliberately.
- This record settles direction only. It is not an implementation Plan or authorization to edit product code.

## Remaining assessment question

Assessment must determine how the existing host file is represented or migrated in the checkout so that changing its default path does not strand the current host copy.
