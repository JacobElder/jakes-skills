# Flow lifecycle & hooks

Read this when hooks (`onBegin`/`onEnd`/`onMove`) fire in an order you don't expect, when state set up in one hook is missing in another, or when a hook mysteriously wipes `G`. Ordering below is an empirical trace against 0.50.2.

## Execution order

For game start plus one move that ends the turn (`maxMoves: 1`), the observed order is:

```
setup                         // once, builds initial G
phase.onBegin                 // entering the starting phase
turn.onBegin                  // entering player 0's turn
  move                        // the player's move runs
  turn.onMove                 // after each move in the turn
turn.onEnd                    // turn auto-ends (maxMoves reached)
turn.onBegin                  // next player's turn begins
```

`game.endIf` (and the active phase's `endIf`) is evaluated **after essentially every step** — setup, each hook, and each move — not just after moves. So `endIf` must be cheap and side-effect-free (see the main SKILL): it runs constantly.

Practical consequences:
- State a move relies on must exist by the time the move runs — initialize it in `setup` (always-present state) or the relevant `onBegin` (per-turn/per-phase state), never lazily in the first move.
- `phase.onBegin` runs before `turn.onBegin`. Phase-level setup is in place before any turn in that phase begins.
- `turn.onMove` is the place for per-move bookkeeping shared across every move in a turn (e.g. decrementing an action budget), instead of duplicating it in each move.

## The hook-return gotcha

Hooks are typed `(context) => void | G`. Like moves, they may mutate the draft **or** return a new `G` — but if a hook *accidentally* returns a value, that value **replaces `G` entirely**. Verified: an `onBegin: () => 42` leaves `G === 42` (the whole state object is gone).

```js
// WRONG — arrow body returns the result of the expression, which becomes the new G
turn: { onBegin: ({ G }) => (G.round += 1) }   // returns a number → G is now that number

// CORRECT — block body, mutate, return nothing
turn: { onBegin: ({ G }) => { G.round += 1; } }
```

This bites hardest with one-line helpers (`onBegin: ({ G }) => doSomething(G)`) where the helper returns anything truthy. Use a block body and return nothing unless you deliberately mean to replace `G`.

## Undo / redo

boardgame.io has built-in undo. On the client: `client.undo()` / `client.redo()`. Verified: within an open turn, `undo()` reverts the last move and `redo()` reapplies it.

Constraint: undo does **not** cross turn boundaries — once a turn ends (e.g. via `maxMoves` or `endTurn`), the previous turn's moves can't be undone (`undo()` reports "No moves to undo"). Controls:
- `disableUndo: true` on the game config disables undo entirely.
- Per-move `undoable: boolean | (({ G, ctx }) => boolean)` on a long-form move gates whether that specific move can be undone (e.g. forbid undoing a move that revealed hidden information).
