# Personal Opening Classification and Progressive Line Training — Confirmed Grilling Synthesis

**Recorded:** 2026-08-21
**Status:** Confirmed synthesis of the current conversation; conceptual and training-direction evidence only
**Implementation authority:** None
**Relationship:** Builds on the [opening position pattern discovery record](opening-position-pattern-discovery.md),
which settled exact-position identity, the transposition-aware repertoire graph, and manual preferred-move
authority. It also sits alongside the confirmed engine-analysis direction recorded in the
[MP-10 browser evaluation synthesis](mp10-browser-evaluation.md), where evaluation runs as a backend Stockfish
service that informs decisions but never makes them. This record is a focused concept record of the current
conversation; it is not a Plan, a specification, a schema, or an authorization to implement.

## Purpose

This record preserves the current conversation about how Chess Move Trainer should:

1. classify the openings a player actually reaches and cares about (personal opening classification);
2. decide which positions and routes belong to the player's active opening frontier (adaptive opening frontiers);
3. handle transpositions between openings without losing identity or membership;
4. weight recurrence so practice targets what matters to this player (recurrence weighting); and
5. train full opening lines progressively, reinforcing what is reliable before extending further (progressive
   line training).

The record states what is settled, what each settled idea means in plain terms, and what is explicitly deferred.
It does not invent thresholds, formulas, concrete schemas, taxonomy editing, or implementation actions. No part
of this record authorizes implementation, downloads, database changes, dependencies, edits to product source, or
a Plan or master plan.

## What this record is

This is a focused, coherent concept record — not a transcript of the conversation, not an append-only note, not
a Plan, not a specification, and not an implementation authority. It organizes the confirmed conceptual direction
by topic so later grilling or planning can start from a single readable account.

## Position identity and opening classification

### Exact board position is the primary training identity

The exact board position is the primary identity for training. Everything the trainer tracks — membership,
recurrence, progress, training moves — attaches to exact positions, consistent with the rule-aware identity
settled in the earlier pattern-discovery record. Opening labels do not replace positions; they organize practice.
A familiar name such as "the Caro" is a convenient handle for grouping and selecting practice, not a substitute
for knowing which exact position is being trained.

### Opening labels organize practice

Opening labels are organizational. Their job is to let the app gather the positions and lines that belong to a
familiar opening under one practice surface ("practice the Caro"), while the underlying training identity remains
the exact position. Labeling decisions therefore never change which exact positions are tracked or how they are
trained.

## Opening membership

### Neutral identity is separate from player-specific relationship

Opening identity and membership are neutral facts, separate from the player-specific relationship. Neutral game
memberships record which opening collections a game belongs to, independent of who played it. The player-specific
relationship records how this player and their color relate to those memberships. Both are kept, as separate
concerns: a game can neutrally be a Caro-Kann while the player's relationship to it is "plays it as Black,
struggles after the Advance variation."

### One game gets a set of memberships, not one label

A game is not reduced to a single opening label. Instead it receives a set of opening memberships, because a
single game can pass through several named regions of the taxonomy. Each membership carries provenance: the
source type that introduced it, the anchor position where it was introduced, and the point in the game where it
was introduced.

### Positions may belong to multiple opening collections

A position can belong to more than one opening collection at the same time. The standard taxonomy is understood
as having a canonical hierarchy — broad families containing nested variations — plus transposition cross-links
that connect lines that reach the same positions by different move orders. Membership is therefore not exclusive:
the same position may validly sit under more than one collection.

### Seed from a fixed standard taxonomy

The initial implementation seeds membership from a fixed, standard opening taxonomy. There is no user editing,
merging, or custom taxonomy in the initial version. The standard structure — canonical hierarchy plus
transposition cross-links — is taken as given.

### Broad families and nested variations are both retained

Both broad families and nested variations are retained as memberships. Exact standard matches introduce
membership directly. Recurring downstream positions — positions reached later in actual games — inherit
membership along the actual game paths that reached them, and only until an adaptive recurrence frontier. The
frontier therefore bounds how far membership inheritance travels beyond the standard matches.

## The adaptive opening frontier

### The frontier comes only from the player's own games

The adaptive opening frontier — the set of positions, routes, and collections the trainer actively treats as
"this player's openings" — is derived only from the player's own games. Population data never contributes to the
frontier. Other players' games can inform candidates elsewhere, but they do not define what this player is
tracked against.

### Recurrence signals the frontier

Two recurrence signals shape the frontier:

- absolute support — how often a position or route occurs in the player's games; and
- conditional branch frequency — how often a branch is taken given that its parent position was reached.

Both are used. Recency weighting applies, and the game sequence itself contributes to recency: later games in the
player's history weigh more than earlier ones, so the frontier reflects what the player does now, not only what
they once did. Rating proximity also matters: games played near the player's own rating carry more weight.

The frontier uses a lower retirement threshold with hysteresis: a position or route leaves the frontier only with
more evidence than it needed to enter, so the frontier is stable and does not churn on small sample changes.

No exact formula, threshold values, or weighting scheme are settled. The signals and their direction are settled;
the arithmetic is explicitly deferred.

### Global and opening-route recurrence are both preserved

Recurrence is measured in two scopes that are kept separately:

- global recurrence — how often a position occurs across the player's games; and
- opening-route recurrence — how often a position occurs specifically along the routes that reach it within an
  opening collection.

Opening-route recurrence governs the collection frontier: it decides which positions and routes are actively
tracked within a collection. Overall and color-specific counts are both preserved; color-specific evidence
governs relevant practice, so a position the player reaches often as Black but almost never as White is practiced
with Black-side relevance.

## Progressive line training

### Practice asks only user decision positions

Training asks only the player's own decision positions — the positions where the player must choose a move.
Opponent moves are retained as context around those decisions. Training is therefore full lines, never isolated
moves: the player sees the line as it actually proceeds and is asked at their decision points.

### Progression reinforces, then extends, and pauses rather than deletes

Progressive line training follows a settled rhythm:

- reinforce the current line endpoint — the deepest point of the line currently being trained;
- extend one decision deeper only after reliable recall of the current material;
- keep reviewing earlier moves as part of the line, so progress does not come at the cost of the foundation; and
- when earlier recall weakens, pause deeper progression — but never delete the progress already made.

Deferring depth is a pause, not a reset: the progress remains, waiting for recall to strengthen again.

## Shared positions and convergence

### Board mastery is shared; route progress is separate

When two training routes converge on the same exact position, the position itself is shared: mastery of the board
position is a single shared fact, while route progress — how far along each opening route the player has trained —
is tracked separately for each route.

### One accepted training move creates a shared continuation

A training move accepted at a shared position creates a shared continuation used by all routes through that
position. Initially there is exactly one accepted training move per position. Engine analysis and game history
may inform the player's choice, but neither ever auto-selects the training move: the player chooses it, and one
accepted move is stored for the position.

## Branch priority

### Priority combines recurrence, recency, rating, mistakes, engine loss, and amount trained

Branch priority — which branch of the player's opening practice should be tackled next — ultimately combines:

- personal recurrence,
- recency,
- rating relevance,
- mistake persistence,
- typical engine loss, and
- amount already trained.

The intent is that an isolated severe blunder does not dominate repeated moderate errors: a mistake the player
keeps making deserves priority even when no single instance was catastrophic. The exact combination and weights
are explicitly deferred; the factors and the intent are settled.

## Raw facts and replaceable calculations

Raw facts are preserved as the durable record, and priority is treated as a replaceable calculation layered on
top of them. The trainer keeps the full training-attempt history plus a current summary. Recomputing priority
with different weights or formulas must not destroy the underlying facts, because the priority can change without
the evidence changing.

## Opening assignment is permanent in the initial version

Opening assignment — which memberships a game and its positions receive — is permanent for the initial version.
Rebuilding or reclassifying assignments may be considered later, but it is not part of this initial direction and
is not designed for now.

## Explicitly deferred decisions

The following are deliberately not settled here:

- the exact recurrence/frontier formula, thresholds, retirement threshold, or hysteresis values;
- the exact branch-priority weighting and how the six factors combine;
- any concrete storage schema for memberships, provenance, recurrence counts, or training history;
- taxonomy editing, merging, or custom taxonomies;
- whether or how opening assignment rebuilding would work in a later version;
- the mechanics of extending a line "one decision deeper" beyond the settled rhythm above; and
- any implementation action, dependency, or product-surface detail.

Each of these remains open until the applicable later grilling or focused planning. Direction from this record
grants no authority to settle them by implementation.

## Boundaries

This record does not:

- create a Plan or master plan, or grant any implementation authority;
- rewrite `opening-position-pattern-discovery.md`, `static-position-to-analysis-roadmap.md`, `mp10-browser-evaluation.md`,
  or any other historical record;
- select a taxonomy source, engine, schema, dependency, or data change;
- settle any thresholds or formulas, or authorize any implementation action;
- alter the earlier settled contracts (exact-position identity, transposition-aware repertoire graph, manual
  preferred-move authority, backend Stockfish evaluation) — it builds on them;
- authorize edits to product source, commits, or pushes; or
- promise that future requirements can never change this direction.

## Completion rationale

The conversation produced one coherent conceptual direction: exact board positions are the primary training
identity; a fixed standard taxonomy supplies neutral opening memberships with provenance, multiple memberships per
game, and transposition cross-links; a player-only adaptive frontier uses recurrence signals (absolute support,
conditional branch frequency, recency including game sequence, and rating proximity) with a stable, hysteretic
retirement; recurrence is kept in global and opening-route scopes with color-specific evidence governing practice;
training asks full lines at user decision positions and progresses by reinforcing the endpoint, extending one
decision after reliable recall, and pausing without deleting when earlier recall weakens; shared positions
converge on one accepted, player-chosen training move; and branch priority combines six factors without allowing
isolated severe blunders to dominate repeated moderate errors — with raw facts preserved so priority remains a
replaceable calculation.

This record closes the current conversation as confirmed conceptual direction. It authorizes no implementation,
and every formula, threshold, schema, and implementation detail remains deferred to the appropriate later grilling
and planning.