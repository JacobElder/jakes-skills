# Custom turn order

Read this when the default "pass clockwise to the next player" turn order isn't what the game needs (reverse order, fixed seating, one-turn-each drafts, conditional next player). Configure it under `turn.order`. `TurnOrder` is imported from `boardgame.io/core`. Behaviors below are verified against 0.50.2.

## Built-in orders

```js
import { TurnOrder } from 'boardgame.io/core';

turn: { order: TurnOrder.ONCE }   // each player gets exactly one turn, then the PHASE auto-ends
```

| Value | Behavior |
|---|---|
| `TurnOrder.DEFAULT` | The default. Passes through `ctx.playOrder` one player at a time. |
| `TurnOrder.RESET` | Like DEFAULT, but a new phase starts again at the first player in `playOrder`. |
| `TurnOrder.CONTINUE` | A new phase resumes from whoever was active when the previous phase ended. |
| `TurnOrder.ONCE` | Each player takes one turn, then the phase ends automatically. Ideal for a bidding/draft round. |

`ONCE` is phase-scoped: put it on a phase's `turn` and pair it with a `next` phase. Verified trace for 3 players in a `bidding` phase: `P0 → P1 → P2` then auto-advance to the next phase.

## Fixed/custom seating with the factory helpers

```js
// A fixed explicit order (player IDs), regardless of join order:
turn: { order: TurnOrder.CUSTOM(['2', '1', '0']) }   // verified: 2 → 1 → 0 → 2 → ...

// Read the order from a field on G at runtime (e.g. a seating array you set in setup):
turn: { order: TurnOrder.CUSTOM_FROM('seating') }    // with G.seating = ['1','0'] → 1 → 0 → 1
```

`CUSTOM_FROM` is the one to use when seating is decided by game logic (a randomized seating, a snake draft you precompute, etc.) — store the order array on `G` and point `CUSTOM_FROM` at the field name.

## Fully custom order object

For logic the helpers can't express (skip eliminated players, reverse on a condition), supply a `TurnOrderConfig`:

```js
turn: {
  order: {
    // INDEX into playOrder for the first player of the turn cycle (not a playerID!)
    first: ({ G, ctx }) => 0,
    // INDEX of the next player; return undefined to end the turn-order cycle
    next: ({ G, ctx }) => (ctx.playOrderPos + 1) % ctx.numPlayers,
    // optional: compute/override ctx.playOrder
    playOrder: ({ G, ctx }) => G.seating ?? ctx.playOrder,
  },
}
```

**The classic gotcha:** `first` and `next` return **indices into `ctx.playOrder`**, not player IDs. Returning `'2'` (an ID) where an index is expected silently misbehaves. Use `ctx.playOrderPos` (the current index) to compute the next index, and read the ID via `ctx.playOrder[pos]` if you need it.

## Related

- `turn.onMove: ({ G, ctx, playerID }) => ...` runs after every move in the turn — handy for shared per-move bookkeeping without repeating it in each move.
- To end a turn imperatively from inside a move, use `events.endTurn()` (top-level on the context). To skip to a specific next player, `events.endTurn({ next: playerID })`.
- For simultaneous (not sequential) action, you want `activePlayers` + stages, not turn order — see the main SKILL.
