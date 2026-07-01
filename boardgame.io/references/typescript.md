# TypeScript with boardgame.io 0.50.x

Read this when the game is written in TypeScript. All types are exported from the package root `boardgame.io`. The patterns below type-check clean under `--strict` (verified against 0.50.2).

## Import the types you need

```ts
import type { Game, Move, Ctx, FnContext } from 'boardgame.io';
import { INVALID_MOVE } from 'boardgame.io/core';
```

Key types: `Game<G>`, `Move<G>` (a move function or long-form move), `MoveFn<G>`, `Ctx`, `FnContext<G>` (the move/hook context object), `LongFormMove<G>`, `PhaseConfig<G>`, `TurnConfig<G>`.

## Type your state, then parametrize everything with it

```ts
interface MyG {
  cells: (string | null)[];
  scores: Record<string, number>;
}

// A move is Move<MyG>. The first param is the destructured context object, NOT (G, ctx).
const claim: Move<MyG> = ({ G, ctx }, id: number) => {
  if (G.cells[id] !== null) return INVALID_MOVE;
  G.cells[id] = ctx.currentPlayer;
};

const roll: Move<MyG> = ({ G, random }) => {
  G.scores['0'] = random.D6();
};

const TicTacToe: Game<MyG> = {
  setup: ({ ctx }): MyG => ({ cells: Array(9).fill(null), scores: {} }),
  moves: { claim, roll },
  endIf: ({ G }: FnContext<MyG>) => {
    if (G.cells.every((c) => c !== null)) return { draw: true };
  },
  // enumerate uses the OLD positional signature, even in TS:
  ai: {
    enumerate: (G: MyG, ctx: Ctx) =>
      G.cells
        .map((c, i) => (c === null ? { move: 'claim', args: [i] } : null))
        .filter(Boolean) as { move: string; args: any[] }[],
  },
};
```

Notes:
- `setup` is typed `({ ctx, random, ... }) => G` — it receives the context **without** `G` and returns the initial `G`.
- The plugin APIs on the context (`random`, `events`, `log`) and `playerID` are typed members of `FnContext`; destructure only what you use.
- `Move<G>` is a union of the plain function form and `LongFormMove<G>` (`{ move, client?, redact?, undoable?, ... }`), so a long-form move with `client: false` is still assignable to `Move<G>`.

## Required tsconfig gotcha: `skipLibCheck: true`

boardgame.io depends on `ts-toolbelt`, whose declaration files trip TS 5.x with *"Type instantiation is excessively deep and possibly infinite."* These errors come from the library's own `.d.ts`, not your code, and disappear with `skipLibCheck` (which essentially every real project already sets):

```json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true,
    "moduleResolution": "node",
    "esModuleInterop": true
  }
}
```

Without `skipLibCheck`, `tsc` reports failures inside `node_modules/ts-toolbelt` even when your game code is correct — don't chase those as if they were your bugs.

## Typing the board props (React)

The `board` component receives a typed props bag including `G: MyG`, `ctx: Ctx`, `moves`, `events`, `playerID`, `isActive`, `isMultiplayer`, etc. Define a `BoardProps<MyG>`-shaped interface for your component (boardgame.io/react exports the prop types) rather than `any`.
