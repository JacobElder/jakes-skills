#!/usr/bin/env node
/**
 * boardgame.io 0.50.x behavior smoke-test.
 *
 * Run this against the version actually installed in the target project to confirm
 * the API behaves as this skill documents. It encodes the load-bearing facts the
 * base model tends to get wrong. Zero extra dependencies — uses only boardgame.io.
 *
 *   node scripts/smoke-test.js
 *
 * Exits 0 if every documented behavior holds, 1 otherwise. If a check FAILS, the
 * installed version differs from what the skill assumes — trust the failure and
 * re-verify that pattern against the installed package before relying on it.
 */
const { Client } = require('boardgame.io/client');
const { Local } = require('boardgame.io/multiplayer');
const { INVALID_MOVE, Stage, TurnOrder, PlayerView } = require('boardgame.io/core');

let pass = 0, fail = 0;
const ok = (name, cond) => { (cond ? pass++ : fail++); console.log(`${cond ? 'PASS' : 'FAIL'}  ${name}`); };
// boardgame.io logs expected "invalid/disallowed move" lines to console.error; silence them.
const quiet = (fn) => { const e = console.error; console.error = () => {}; try { return fn(); } finally { console.error = e; } };

// 1. Move context is a single object; random/events are top-level, not on ctx.
quiet(() => {
  const g = { setup: () => ({ r: null, ctxR: 'unset' }),
    moves: { roll: ({ G, random, ctx }) => { G.r = random.D6(); G.ctxR = ctx.random ? 'defined' : 'undefined'; } } };
  const c = Client({ game: g, numPlayers: 1, seed: 's' }); c.moves.roll();
  ok('random.D6() (top-level) returns a number with no randomMethod config', typeof c.getState().G.r === 'number');
  ok('ctx.random is undefined (old API does not exist in 0.50.x)', c.getState().G.ctxR === 'undefined');
});

// 2. INVALID_MOVE rejects + rolls back; undefined return is a no-op (not corruption).
quiet(() => {
  const g = { setup: () => ({ cells: [null, null] }),
    moves: { claim: ({ G, ctx }, i) => { if (G.cells[i] !== null) return INVALID_MOVE; G.cells[i] = ctx.currentPlayer; } } };
  const c = Client({ game: g, numPlayers: 2 }); c.moves.claim(0); c.moves.claim(0);
  ok('INVALID_MOVE rolls back an illegal move', c.getState().G.cells[0] === '0');
});

// 3. Immer is default: mutation works; mutate + return-new throws.
quiet(() => {
  const g = { setup: () => ({ n: 0 }), moves: { inc: ({ G }) => { G.n += 1; } } };
  const c = Client({ game: g, numPlayers: 1 }); c.moves.inc();
  ok('mutation works by default (Immer on, no config)', c.getState().G.n === 1);
  let threw = false;
  const g2 = { setup: () => ({ n: 0 }), moves: { bad: ({ G }) => { G.n += 1; return { n: 99 }; } } };
  const c2 = Client({ game: g2, numPlayers: 1 });
  try { c2.moves.bad(); } catch { threw = true; }
  ok('mutate + return a new object throws the Immer producer error', threw);
});

// 4. A phase's moves replace globals; a phase with no moves key inherits them.
quiet(() => {
  const g = { setup: () => ({ x: 0 }), moves: { global: ({ G }) => { G.x += 100; } },
    phases: { A: { start: true, moves: { local: ({ G }) => { G.x += 1; } } } } };
  const c = Client({ game: g, numPlayers: 1 }); c.moves.local(); c.moves.global();
  ok('global move is disallowed inside a phase that defines its own moves', c.getState().G.x === 1);
  const g2 = { setup: () => ({ x: 0 }), moves: { global: ({ G }) => { G.x += 100; } }, phases: { B: { start: true } } };
  const c2 = Client({ game: g2, numPlayers: 1 }); c2.moves.global();
  ok('a phase with no moves key inherits the global moves', c2.getState().G.x === 100);
});

// 5. events is top-level inside moves; endTurn advances the player.
quiet(() => {
  const g = { setup: () => ({}), turn: { minMoves: 1 }, moves: { go: ({ events }) => { events.endTurn(); } } };
  const c = Client({ game: g, numPlayers: 2 }); const before = c.getState().ctx.currentPlayer; c.moves.go();
  ok('events.endTurn() (top-level) advances currentPlayer', c.getState().ctx.currentPlayer !== before);
});

// 6. endIf return value becomes ctx.gameover (winner shape matters).
quiet(() => {
  const g = { setup: () => ({ won: true }), endIf: ({ G, ctx }) => { if (G.won) return { winner: ctx.currentPlayer }; }, moves: { noop: () => {} } };
  const c = Client({ game: g, numPlayers: 2 });
  ok('endIf returning { winner } sets ctx.gameover to that object', JSON.stringify(c.getState().ctx.gameover) === '{"winner":"0"}');
});

// 7. Simultaneous play: stages + maxMoves; Stage.NULL === null.
quiet(() => {
  ok('Stage.NULL === null', Stage.NULL === null);
  const g = { setup: () => ({ picks: {} }),
    turn: { activePlayers: { all: 'pick', minMoves: 1, maxMoves: 1 }, stages: { pick: { moves: { choose: ({ G, playerID }, x) => { G.picks[playerID] = x; } } } } },
    moves: {} };
  const c = Client({ game: g, numPlayers: 2 });
  ok('stage move is callable during simultaneous play', typeof c.moves.choose === 'function');
});

// 8. maxMoves: 1 auto-ends the turn (do not also call endTurn).
quiet(() => {
  const g = { setup: () => ({ n: 0 }), turn: { minMoves: 1, maxMoves: 1 }, moves: { go: ({ G }) => { G.n++; } } };
  const c = Client({ game: g, numPlayers: 2 }); const p0 = c.getState().ctx.currentPlayer; c.moves.go();
  ok('maxMoves: 1 auto-ends the turn', c.getState().ctx.currentPlayer !== p0);
});

// 9. Secret state: PlayerView.STRIP_SECRETS hides G.secret + other players' data.
quiet(() => {
  const g = { setup: () => ({ secret: { deck: ['a'] }, players: { '0': { hand: ['A'] }, '1': { hand: ['B'] } }, pub: 1 }),
    playerView: PlayerView.STRIP_SECRETS, moves: { noop: () => {} } };
  const c = Client({ game: g, numPlayers: 2, playerID: '0', multiplayer: Local() }); c.start();
  const G = c.getState().G;
  ok('STRIP_SECRETS removes G.secret and other players\' private data', G.secret === undefined && !!G.players['0'] && !G.players['1']);
});

// 10. Custom turn order follows the supplied order.
quiet(() => {
  const g = { setup: () => ({}), turn: { minMoves: 1, maxMoves: 1, order: TurnOrder.CUSTOM(['2', '1', '0']) }, moves: { go: () => {} } };
  const c = Client({ game: g, numPlayers: 3 }); const seq = [];
  for (let i = 0; i < 3; i++) { seq.push(c.getState().ctx.currentPlayer); c.moves.go(); }
  ok('TurnOrder.CUSTOM([2,1,0]) yields order 2,1,0', seq.join('') === '210');
});

// 11. Gotcha: a hook that RETURNS a value replaces G with that value.
quiet(() => {
  const g = { setup: () => ({ keep: true }), turn: { onBegin: () => 42 }, moves: { noop: () => {} } }; // onBegin returns a number
  const c = Client({ game: g, numPlayers: 1 });
  ok('a hook returning a non-G value replaces G entirely (return nothing from hooks)', c.getState().G === 42);
});

// 12. undo / redo work within an open turn.
quiet(() => {
  const g = { setup: () => ({ played: [] }), moves: { play: ({ G }, x) => { G.played.push(x); } } };
  const c = Client({ game: g, numPlayers: 2 }); c.moves.play('A'); c.moves.play('B'); c.undo();
  ok('client.undo() reverts the last move within a turn', JSON.stringify(c.getState().G.played) === '["A"]');
});

console.log(`\n${pass} passed, ${fail} failed`);
if (fail > 0) { console.log('Some documented behaviors do NOT hold for the installed version — re-verify before relying on them.'); process.exit(1); }
console.log('All documented boardgame.io behaviors hold for the installed version.');
