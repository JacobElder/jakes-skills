# Lobby, matchmaking & server persistence

Read this when the game needs networked matches that outlive a single page load: a lobby where players create/join matches, server-side state persistence, or authenticated multiplayer. Signatures below are verified against 0.50.2.

## The server process

`Server` comes from `boardgame.io/server` and runs as its own Node process (separate from the client bundle).

```js
import { Server, Origins } from 'boardgame.io/server';
import { TicTacToe } from './game';

const server = Server({
  games: [TicTacToe],
  origins: [Origins.LOCALHOST],   // dev; for prod pass your site's origin string/regex
  // db defaults to in-memory (state lost on restart) — see persistence below
});

server.run(8000);
```

`ServerOpts`: `{ games, origins, apiOrigins?, db?, transport?, uuid?, authenticateCredentials?, generateCredentials?, https? }`. `Origins` has `LOCALHOST` and `LOCALHOST_IN_DEVELOPMENT`.

## Persistence (the `db` option)

State persistence is a **server** concern — boardgame.io core does not save anything client-side beyond the live session. Choose a DB adapter:

- **In-memory (default):** no config. Fast, but all matches vanish on restart. Fine for local dev and ephemeral games.
- **FlatFile:** file-backed, exported from `boardgame.io/server`:

  ```js
  import { Server, FlatFile } from 'boardgame.io/server';
  const server = Server({ games: [TicTacToe], db: new FlatFile({ dir: './storage' }) });
  ```

- **External databases (Postgres, Mongo, etc.):** provided by separate community npm packages (e.g. `bgio-postgres`), not bundled in `boardgame.io`. Install one and pass its instance as `db`. This is the path for production-grade persistence; configuring a specific external adapter is beyond this skill.

## The lobby REST API (`LobbyClient`)

`LobbyClient` (from `boardgame.io/client`) is a thin wrapper over the server's match-management HTTP API. Use it to build a custom lobby UI.

```js
import { LobbyClient } from 'boardgame.io/client';
const lobby = new LobbyClient({ server: 'http://localhost:8000' });

await lobby.listGames();                         // => ['tic-tac-toe', ...]
await lobby.listMatches('tic-tac-toe');          // => { matches: [...] }
const { matchID } = await lobby.createMatch('tic-tac-toe', { numPlayers: 2 });
const { playerCredentials } =
  await lobby.joinMatch('tic-tac-toe', matchID, { playerID: '0', playerName: 'Alice' });
// also: getMatch, leaveMatch, updatePlayer, playAgain
```

Method shapes: `createMatch(game, { numPlayers, setupData? })`, `joinMatch(game, matchID, { playerID?, playerName })` → `{ playerID, playerCredentials }`, `leaveMatch(game, matchID, { playerID, credentials })`, `playAgain(game, matchID, { playerID, credentials })`.

## Wiring the credentials back into the game client

`joinMatch` returns `playerCredentials`. Pass them, plus `matchID` and `playerID`, into the **game** Client so the server authorizes that player's moves:

```js
import { Client } from 'boardgame.io/client';   // or boardgame.io/react
import { SocketIO } from 'boardgame.io/multiplayer';

const client = Client({
  game: TicTacToe,
  multiplayer: SocketIO({ server: 'http://localhost:8000' }),
  matchID,
  playerID: '0',
  credentials: playerCredentials,
});
```

A client without a `playerID` is a spectator; without correct `credentials` the server rejects its moves. The client also exposes `updateMatchID`, `updatePlayerID`, and `updateCredentials` for switching matches without rebuilding it.

## Turnkey React lobby

If you don't need a custom UI, `boardgame.io/react` exports a ready-made `Lobby` component that lists/creates/joins matches and launches the right board — wire it with your game definitions, board components, and the server URL.
