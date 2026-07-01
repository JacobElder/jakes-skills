/**
 * game.js — a MINIMAL, heavily-commented boardgame.io game-logic template.
 *
 * This is the RULES ENGINE only: a pure (G, ctx, move) -> G' state machine with
 * NO UI. It demonstrates the patterns that matter for board game design:
 *   - pure moves that validate then mutate a draft of game state
 *   - phases & turn structure (incl. a simultaneous-action phase = anti-downtime)
 *   - hidden information via playerView (opponents can't see your hand)
 *   - injected randomness via ctx (reproducible; never Math.random())
 *   - an end condition + scoring
 *   - ai.enumerate: powers the built-in bot AND documents your legal-move space,
 *     which is the seed of your physical rulebook's "on your turn you may..."
 *
 * The toy game ("Gem Grab"): a tiny drafting + set-collection demo. Each round a
 * shared market of gems is revealed; players simultaneously draft one gem into a
 * hidden hand, then on their turn may cash a SET (3 of a kind = points). First to
 * the target score wins. It exists only to show the wiring — replace it with your
 * real rules, keeping the structure.
 *
 * Run: see README.md in this folder. Install with `npm i boardgame.io`.
 *
 * VERIFIED against boardgame.io 0.50.2: `random` (with .Shuffle) IS injected
 * into phase `onBegin` hooks and into moves; the object-destructuring API
 * (`({ G, random })` for hooks, `({ G, playerID }, ...args)` for moves) is
 * correct for this version. Note: boardgame.io is stable but only lightly
 * maintained — pin your version and re-verify hook signatures if you upgrade.
 */

import { INVALID_MOVE } from 'boardgame.io/core';

const GEM_TYPES = ['ruby', 'emerald', 'sapphire', 'topaz'];
const TARGET_SCORE = 9;        // points to win
const MARKET_SIZE = 4;         // gems revealed for drafting each round

// --- helpers (pure) ---------------------------------------------------------
function refillMarket(G, random) {
  // random.Shuffle is boardgame.io's injected, server-authoritative RNG.
  // NEVER use Math.random() in game logic — it breaks reproducibility & is
  // not server-safe for multiplayer.
  const bag = [];
  for (const g of GEM_TYPES) for (let i = 0; i < 5; i++) bag.push(g);
  G.market = random.Shuffle(bag).slice(0, MARKET_SIZE);
}

function countSets(hand) {
  // number of completable 3-of-a-kind sets in a hand (a {gem: count} object)
  return Object.values(hand).reduce((acc, n) => acc + Math.floor(n / 3), 0);
}

// --- the Game object (this IS your formal rules specification) --------------
export const GemGrab = {
  name: 'gem-grab',

  setup: (ctx) => ({
    // Public state everyone can see:
    market: [],
    scores: Object.fromEntries(ctx.playOrder.map((p) => [p, 0])),
    // Secret state: each player's hand of gems. Stripped per-player by
    // playerView below so a client never receives opponents' hands.
    hands: Object.fromEntries(
      ctx.playOrder.map((p) => [p, Object.fromEntries(GEM_TYPES.map((g) => [g, 0]))])
    ),
  }),

  phases: {
    // PHASE 1: simultaneous drafting. Everyone picks at once -> zero downtime.
    draft: {
      start: true,
      onBegin: ({ G, random }) => refillMarket(G, random),
      turn: {
        // activePlayers: everyone acts simultaneously this phase.
        activePlayers: { all: 'picking' },
      },
      moves: {
        // A simultaneous move: take one gem from the market into your hand.
        pickGem: ({ G, playerID }, marketIndex) => {
          if (marketIndex < 0 || marketIndex >= G.market.length) return INVALID_MOVE;
          const gem = G.market[marketIndex];
          if (gem == null) return INVALID_MOVE;       // already taken this round
          G.hands[playerID][gem] += 1;
          G.market[marketIndex] = null;               // mark as taken
        },
      },
      // When all players have picked, move to the action phase.
      // NOTE the `length > 0` guard: [].every() returns TRUE, so without it
      // this endIf fires on the empty initial market and skips the whole phase
      // before onBegin's refill is seen. (Verified against boardgame.io 0.50.2 —
      // this is a real, easy-to-miss bug; keep the guard.)
      endIf: ({ G }) => G.market.length > 0 && G.market.every((m) => m === null),
      next: 'action',
    },

    // PHASE 2: sequential actions. On your turn, optionally cash a set.
    action: {
      turn: { minMoves: 1, maxMoves: 1 },           // exactly one action per turn
      moves: {
        cashSet: ({ G, playerID }, gem) => {
          if (!GEM_TYPES.includes(gem)) return INVALID_MOVE;
          if (G.hands[playerID][gem] < 3) return INVALID_MOVE;   // not a legal set
          G.hands[playerID][gem] -= 3;
          G.scores[playerID] += 3;                  // 3 points per set
        },
        pass: () => {},                              // a legal no-op
      },
      // After everyone has had an action turn, loop back to drafting.
      endIf: ({ ctx }) => ctx.playOrderPos === ctx.playOrder.length - 1,
      next: 'draft',
    },
  },

  // GLOBAL end condition + winner. A correct endIf is the formal "game over"
  // rule your rulebook will state.
  endIf: ({ G }) => {
    for (const [p, s] of Object.entries(G.scores)) {
      if (s >= TARGET_SCORE) return { winner: p };
    }
  },

  // HIDDEN INFORMATION: strip every other player's hand before sending state to
  // a client. This is easier & more reliable than physical hidden info, and is
  // mandatory for competitive multiplayer (do not trust the client).
  playerView: ({ G, playerID }) => {
    const hands = {};
    for (const [p, h] of Object.entries(G.hands)) {
      hands[p] = p === playerID ? h : '<hidden>';
    }
    return { ...G, hands };
  },

  // BOT SUPPORT: enumerate the legal moves from a given state. This does double
  // duty: it powers boardgame.io's built-in random/MCTS bots (tireless
  // playtesters that flush crashes and expose dominant lines), AND it is an
  // executable statement of your legal-move space — copy it into your rulebook's
  // "on your turn you may..." section.
  ai: {
    enumerate: (G, ctx) => {
      const moves = [];
      if (ctx.phase === 'draft') {
        G.market.forEach((gem, i) => {
          if (gem != null) moves.push({ move: 'pickGem', args: [i] });
        });
      } else if (ctx.phase === 'action') {
        const hand = G.hands[ctx.currentPlayer];
        for (const g of GEM_TYPES) {
          if (hand[g] >= 3) moves.push({ move: 'cashSet', args: [g] });
        }
        moves.push({ move: 'pass', args: [] });
      }
      return moves;
    },
  },
};

export { countSets, GEM_TYPES, TARGET_SCORE };
