# Multiplayer and netcode

Read this when the user wants to add online multiplayer, co-op, or networking to a game. This file is organized by decision: scope first (should you do this at all?), then architecture, then implementation.

- [The scope trap — read this first](#the-scope-trap--read-this-first)
- [Local co-op vs online multiplayer](#local-co-op-vs-online-multiplayer)
- [Architecture: authoritative server vs peer-to-peer](#architecture-authoritative-server-vs-peer-to-peer)
- [Client-side prediction and server reconciliation](#client-side-prediction-and-server-reconciliation)
- [Rollback netcode](#rollback-netcode)
- [Delay-based netcode](#delay-based-netcode)
- [Godot MultiplayerAPI — what it gives you](#godot-multiplayerapi--what-it-gives-you)
- [Relay servers, NAT traversal, and managed services](#relay-servers-nat-traversal-and-managed-services)
- [Practical recommendations by game type](#practical-recommendations-by-game-type)
- [Anti-patterns](#anti-patterns)

---

## The scope trap — read this first

**Adding online multiplayer to a finished solo game typically adds 30–100% more development time, minimum.** For complex games (action, physics-driven, many interacting objects) the multiplier is often 2× or more. "I'll just add multiplayer at the end" is one of the most expensive mistakes in small-game development.

It is not "just syncing state." Online multiplayer requires:

- Redesigning your game loop to be **deterministic or delta-driven** — state must be reproducible from inputs, not from "whatever was in memory at that time"
- Handling **packet loss** — packets drop; your game must survive missing updates
- Handling **latency** — 20–150 ms one-way delay means the player's input is old by the time the server sees it; the visual must still feel responsive
- Implementing **client-side prediction** (or accepting lag) and **server reconciliation** (or accepting desyncs)
- Writing **disconnect and reconnect logic** — players quit, lose connection, and rejoin
- Addressing **cheating** — clients cannot be trusted to report their own position or health
- Building **NAT traversal** — two players behind home routers cannot connect directly to each other without infrastructure
- Adding **lobby and matchmaking** — direct IP connections are not a product

The **#1 recommendation: ship local co-op first.** Local multiplayer (same machine, shared screen, multiple gamepads) is trivially simple and often more fun. It costs almost nothing to add and gives you a shippable multiplayer feature. Evaluate online only after the game proves itself with local play — and only if your budget, timeline, and team size can absorb what it actually costs.

If the project has a fixed deadline (a jam, a class submission, a contract) and multiplayer is not in the original brief: do not add it. The time does not exist.

---

## Local co-op vs online multiplayer

These are fundamentally different engineering problems. Do not conflate them.

### Local co-op

- One machine, one simulation, multiple input sources
- Add a second gamepad (or split keyboard layout); map each to a player entity
- No networking. No packet loss. No latency. No sync bugs
- For **shared-screen co-op**: everything runs in one scene as-is; just spawn a second player character and wire controller 2 to it
- For **split-screen**: create two SubViewport nodes (Godot) or two Camera components with RenderTexture targets (Unity), assign one per player, tile or divide the screen
- Implementation time for local co-op: hours to a day, depending on how tightly the existing input is coupled to a single player

Split-screen is the hard part of local co-op, and even that is not hard — it's just viewport management and making sure each camera follows its own player. There are no sync issues because there is one simulation.

### Online multiplayer

- Multiple machines, each running a (partial or full) simulation
- Every object that moves must be synchronized
- Every player's input must be transmitted and received, with inherent latency
- Every desync is a bug that must be detected, corrected, or tolerated
- Every disconnection must be handled gracefully
- The simulation must be designed from the ground up to tolerate this

If your game was designed as a single-player game and you want to add online, budget for a significant rewrite of your game loop, entity management, and input handling. The more physics-driven, the more simulation-heavy, the harder this is.

---

## Architecture: authoritative server vs peer-to-peer

Before writing any networking code, choose an architecture. This decision is not easy to reverse.

### Authoritative server (host-as-server or dedicated server)

One machine owns the **true game state**. All others are clients.

- Clients send **inputs** (key presses, stick values, action intents) to the server
- The server runs the simulation, validates inputs, and **sends state updates** back to clients
- Clients render the authoritative state (possibly with local prediction on top — see below)

**Cheating is hard.** The server decides if a shot hit, if a pickup was collected, if a player is alive. A client cannot teleport by sending a false position — the server ignores position claims and only accepts inputs.

**Latency is unavoidable but manageable.** Clients must predict their own actions to feel responsive (see client-side prediction).

**Requires a server.** Either one player hosts (host-as-server / "listen server") — cheaper but host has an advantage and if the host quits, the session can end — or a dedicated server runs independently. Dedicated servers cost money to run.

**For action games, shooters, brawlers, and any game where cheating matters: authoritative server is almost always the correct choice.**

### Peer-to-peer (P2P)

All peers share state directly. No single authority.

- Each peer sends its simulation outputs (or inputs) to all others
- Each peer runs its own simulation and trusts (or disputes) what others send
- Lockstep P2P: all peers wait until all inputs for a frame are received before simulating

**Anyone can cheat.** Trivially. A modified client can send any state it wants.

**Lower server costs.** No central infrastructure required beyond a relay for connection setup.

**Works for**: small games (2–4 players), games with trusted players (LAN parties, friends), turn-based or slow-paced games where determinism is easy to ensure, fighting game rollback (which is a specific P2P architecture — see below).

**Does not work well for**: games with many players, competitive games, games with valuable in-game economies, games where cheating would ruin the experience.

For most indie games with small friend groups: P2P is acceptable. For any game going to strangers: authoritative server is safer.

---

## Client-side prediction and server reconciliation

The core problem: if a player presses "jump" and must wait for the server to confirm the jump before the character moves, the input feels dead at 50 ms latency and unplayable at 150 ms. The solution is **client-side prediction**.

### Client-side prediction

The client applies its own input **immediately**, before the server acknowledges it.

1. Player presses jump
2. Client immediately simulates the jump locally — character rises
3. Client sends the jump input to the server (tagged with a sequence number and timestamp)
4. Server receives the input, validates it, simulates the jump, and sends back the authoritative state
5. Client receives the authoritative state

If the server state matches the client's prediction: nothing to do. The prediction was correct.

If the server state differs (the server says the player was in a different position): the client must **reconcile**.

### Server reconciliation

When the authoritative state arrives and differs from the predicted state:

1. The client rolls its local state back to the server's reported state
2. Re-applies all inputs that were sent after the divergence point but not yet acknowledged
3. Arrives at a new predicted present — which should be closer to correct

This re-simulation from the divergence point is the expensive part. For a character controller with simple movement, it's cheap (re-apply N frames of velocity). For a physics simulation with many interacting objects, it can be very expensive.

**Smoothing the visual correction**: a sharp teleport to the corrected position is jarring. Interpolate or lerp the visual representation toward the authoritative state over a few frames while the logical state snaps. The player usually cannot tell the difference if corrections are small and infrequent.

### Implementation notes for Godot

In Godot's MultiplayerAPI model, client-side prediction is not built in — you implement it yourself. The flow:

```gdscript
# On the client — in _physics_process:
var input = gather_input()
apply_input_locally(input)               # predict immediately
send_input_to_server(input, current_tick)

# On the server — receive input, simulate, broadcast state:
func _on_input_received(peer_id, input, tick):
    apply_input_for_player(peer_id, input)
    var state = get_authoritative_state()
    rpc("receive_state", state, tick)

# On the client — receive authoritative state:
func receive_state(state, server_tick):
    if state differs from predicted_state_at[server_tick]:
        correct_to(state)
        re_apply_inputs_after(server_tick)
```

Input sequence numbers and a ring buffer of recent inputs are required to reconcile correctly. This is not trivial to get right — budget for iteration.

---

## Rollback netcode

Rollback is the standard architecture for **fighting games and fast-paced low-player-count games** (2–4 players max). It delivers low-latency feel by predicting opponent inputs, then correcting when the real inputs arrive.

### How it works

1. Every peer runs a **fully deterministic simulation** — identical inputs on the same state always produce identical outputs
2. When a client needs to simulate frame N but hasn't received opponent inputs for frame N yet, it **predicts the opponent's input** (usually: repeat the last known input)
3. Simulation proceeds with the prediction
4. When the real input arrives (possibly 3–5 frames later), the client checks: was the prediction correct?
   - If yes: nothing to do
   - If no: **roll back** the simulation to the divergence frame, re-simulate forward with the correct inputs
5. The visual output is the current simulation frame, not the "safe" confirmed frame

The user never sees the rollback — it happens internally, and the final rendered frame reflects the corrected simulation.

### The hard requirement: determinism

Rollback **will not work** on a non-deterministic simulation. "Deterministic" means:

- Same inputs + same starting state → same output, **always**, on every machine
- **No floating-point divergence across platforms.** IEEE 754 floating-point is deterministic on the same platform and compiler settings, but can differ across CPUs, GPU-side computations, and platforms. If you use Godot's built-in physics engine for gameplay logic, it may not be deterministic across machines. Options: use integer math for simulation, use fixed-point math (requires a library), or constrain the engine's physics to a single platform
- **Seeded, deterministic RNG** — `randf()` is not deterministic across independent runs unless you seed it identically and advance it in lockstep. Use a shared seed derived from session parameters
- **Frame-locked update order** — all entities must update in a fixed, consistent order every frame
- No `Time.get_ticks_msec()` or wall-clock time influencing simulation logic

Testing determinism: run two instances of your simulation with identical inputs from a replay file. If the outputs diverge at any frame, you have a non-determinism bug.

### In Godot: use an addon, not a from-scratch implementation

Implementing rollback from scratch is a multi-month project. Existing options:

- **Godot Rollback Netcode** (by Snopek) — mature, well-documented, Godot 4 port available. Uses ENet transport. Handles state save/load, rollback logic, input prediction, and tick management. Requires your simulation logic to implement `save_state()` / `load_state()` / `process_tick()` interfaces. Start here
- **GDRollback** — lighter alternative, same general approach

Do not implement rollback from scratch on a game with a ship date. It is a research project, not a feature sprint.

### When rollback is and isn't appropriate

**Appropriate for:**
- Fighting games (1v1 or 2v2)
- Beat-em-ups with a small number of synchronized entities
- Some RTS with a small unit count (Age of Empires used lockstep/delay, not rollback — but rollback is viable for unit counts in the dozens)
- Any game where low latency feel is non-negotiable and you have at most 4 players

**Not appropriate for:**
- MMOs or games with dozens of synchronized entities — rolling back many objects is expensive
- Games with physics-driven environments where the physics engine is the simulation (hard to determinize)
- Games where player count exceeds ~4 (the re-simulation cost scales with entity count and frame depth)
- Casual or turn-based games (delay-based or authoritative server is simpler and sufficient)

---

## Delay-based netcode

The simpler alternative to rollback. Instead of predicting and correcting, **add input delay** so both peers always have each other's inputs before simulating.

### How it works

1. All inputs are delayed by N frames (e.g. 4 frames = ~67 ms at 60 fps)
2. Frame X is only simulated when all peers' inputs for frame X are available
3. No rollback required — simulation is always deterministic and agreed-upon

### Tradeoffs

- **Simpler to implement** — no rollback logic, no state serialization for rollback, no re-simulation
- **Higher input latency** — the delay frames are always felt, regardless of actual network latency. At 60 fps, 4 frames of delay = 67 ms of added input latency on top of network latency
- **Variable-latency-unfriendly** — if the network jitters, the game may stall waiting for inputs. Rollback handles this gracefully; delay-based adds more delay to compensate
- Still requires deterministic simulation

**When to use it:**
- Turn-based or strategy games where input delay is not perceptible
- Games with 60–100 ms of input lag budget that can absorb the delay
- Prototypes and small games where simplicity matters more than feel
- LAN play where latency is reliably low and fixed

For most action games on the internet, delay-based feels noticeably worse than rollback. For strategy or puzzle games, it's usually fine.

---

## Godot MultiplayerAPI — what it gives you

Godot 4's built-in multiplayer system covers the transport and RPC layer. It does not implement prediction, reconciliation, or rollback for you.

### Core primitives

**`@rpc()` decorator** — marks a function as callable remotely:

```gdscript
@rpc("any_peer", "call_local", "reliable")
func take_damage(amount: int):
    health -= amount
    update_health_bar()
```

RPC modes:
- `"any_peer"` — any connected peer can call this (use carefully — anyone can call anything)
- `"authority"` — only the node's authority (usually the server) can call it
- First parameter sets *who can call*; second (`"call_local"`) sets whether the sender also executes it locally

Reliability:
- `"reliable"` — guaranteed delivery, ordered (TCP-like). For important state changes
- `"unreliable"` — no guarantee, no order (UDP-like). For frequently-updated values like position, where a dropped packet is acceptable
- `"unreliable_ordered"` — no guarantee of delivery, but delivered in order if delivered. For sequences where order matters but loss is tolerable

**`MultiplayerSpawner`** — automatically synchronizes the spawning and despawning of nodes across peers. Attach to a parent node; when the authority spawns a child of a registered type, it replicates across all peers.

**`MultiplayerSynchronizer`** — automatically synchronizes named properties of a node at a fixed rate. Configure which properties to sync, at what interval, and to which peers. For positions, health bars, animation states — anything that should stay continuously synced.

```gdscript
# In the inspector or via code, add MultiplayerSynchronizer to a node.
# Configure replication properties, e.g.:
# - position: unreliable, 60 Hz
# - health: reliable, on-change
```

**Transport backends:**
- **ENet** (default) — fast, UDP-based, built in. Good for most games. No NAT traversal
- **WebRTC** — browser-compatible, works for web exports, uses data channels. More complex setup. Enables P2P connections with a signaling server
- **WebSocket** — for web, but TCP-based; higher latency than ENet for realtime games

### What Godot does NOT give you

- NAT traversal — two players on home networks cannot connect to each other directly with ENet alone. You need a relay
- Matchmaking or lobby systems — players need a way to find each other before connecting
- Client-side prediction or rollback — you implement these in your game logic
- Anti-cheat — you design your authority model and validation

---

## Relay servers, NAT traversal, and managed services

Two players behind home routers cannot establish a direct connection without help. NAT (Network Address Translation) blocks unsolicited inbound connections. You need either:

1. **STUN/ICE** — protocols that attempt to establish a direct peer-to-peer connection by punching through NAT. Works maybe 60–80% of the time depending on NAT type. WebRTC uses this
2. **TURN relay** — when direct connection fails, traffic routes through a relay server. Always works. Costs bandwidth on the relay server

### Managed services (recommended over self-hosting)

Self-hosting a relay server is an ongoing ops burden. Managed services handle this, plus lobbying, matchmaking, presence, and often leaderboards and accounts:

- **Nakama** (Heroic Labs) — open-source server you can self-host, or use their cloud (Heroic Cloud). Real-time multiplayer, matchmaking, leaderboards, accounts. Godot SDK available. Good choice for indie games wanting control
- **Photon Engine** — commercial, widely used in Unity; Photon Fusion is their authoritative server product for Unity. Photon Realtime works with Godot. Free tier (CCU-limited) is viable for small games
- **Epic Online Services (EOS)** — free, includes NAT relay, voice, matchmaking, and lobbies. Cross-platform. More complex to set up but no per-unit cost
- **Steamworks** — if shipping on Steam, Steam Datagram Relay (SDR) is built in and handles NAT traversal automatically. Requires SteamNetworkingSockets, which has a Godot integration. Strong choice if Steam is your platform

### Lobby and room codes

Direct IP connections are not a product — players should never type IP addresses. Use a lobby system where:

1. One player creates a session and gets a room code (4–6 characters)
2. Other players enter the code to join
3. The service handles connection establishment

All the managed services above include this. Steamworks lobbies work identically. Do not ship without this.

---

## Practical recommendations by game type

### 2–4 player co-op action (platformer, dungeon crawler)

- Architecture: **authoritative server** with one player as host (listen server)
- Transport: ENet via Godot MultiplayerAPI
- Relay: Nakama or EOS for NAT traversal; Steam SDR if on Steam
- Sync: MultiplayerSynchronizer for player positions at 20–30 Hz unreliable; reliable RPCs for damage, deaths, pickups
- Prediction: for player-controlled characters only; defer enemies to server authority
- Effort estimate from a complete solo game: 4–8 weeks for a competent implementer, longer if the game loop is not already delta-correct

### 1v1 fighting game

- Architecture: **rollback P2P** using Godot Rollback Netcode addon
- Transport: ENet (the addon handles the rest)
- Relay: EOS or Steamworks; the addon has examples for both
- Requirement: simulation must be fully deterministic — audit this before starting
- Effort estimate: 6–12 weeks if the core game is already deterministic; longer if determinism work is needed

### Turn-based (card game, strategy)

- Architecture: **authoritative server** or even simple **P2P with validation**; delay-based or state-broadcast is fine because turns are slow
- Transport: can use WebSocket or ENet; latency barely matters
- Sync: send turn actions as reliable RPCs; wait for acknowledgment before advancing
- Prediction: not needed; player waits for server validation between turns
- Effort estimate: 1–3 weeks for a simple turn-based game; 4–8 weeks for complex state

### Massively multiplayer or many-player

- Do not use Godot's built-in MultiplayerAPI for this. It does not scale
- Use interest management: each client only receives updates for entities near them
- Consider a dedicated authoritative server written in Go, Rust, or a purpose-built game server framework (Nakama, Agones)
- This is a full product, not a feature sprint. Budget accordingly

### "I just want friends to play together" (small co-op, 2–4 trusted players)

- **Steamworks P2P** if on Steam — simplest for trusted players, free, handles NAT
- Or **Parsec** / **Steam Remote Play Together** — stream one player's screen to others, no networking code needed at all. Not real multiplayer but works for couch-style co-op games
- Remote Play Together is zero engineering cost and viable for many co-op game types

---

## Anti-patterns

These are the mistakes that produce games that appear to work in local testing and break in production, or that create security holes so obvious any player can exploit them.

**Building on raw TCP/UDP sockets.** Unless you are writing a networking library, do not manage your own socket connections. Use a library (ENet, WebRTC, Enet via Godot's MultiplayerAPI) that handles packet framing, connection management, and reconnection.

**Using HTTP polling for game state sync.** HTTP request-response is designed for documents, not continuous game state. Polling for game state at 10–60 Hz produces massive overhead, high latency, and server load. Use a persistent connection (WebSocket, ENet, WebRTC data channel).

**Trusting client-reported positions.** If a client sends `player_position = (0, 0)` and the server uses it, a modified client can teleport anywhere on the map in one message. The server accepts **inputs** (movement direction, jump intent), not positions. It computes where the player should be.

**Trusting client-reported hit results.** If a client sends `enemy_dead = true` and the server accepts it, the client can kill any enemy at any time. The server validates whether the hit was possible given the game state.

**Syncing the entire scene tree.** Multiplayer synchronization should cover only the **minimal state** needed by each client: positions of relevant entities, health values, animation state, relevant game events. Syncing every node in your scene is both too expensive and a security disclosure (clients should not receive state about what's happening off-screen or in other players' inventories).

**Forgetting disconnects.** In testing, players never disconnect. In production, players disconnect constantly — bad connection, phone call, rage quit. Every session must handle: mid-game disconnect, reconnect (possibly), and "session continues without the disconnected player" or "session ends." The reconnect case is especially tricky if state has diverged. Design this before you launch, not after your first user report.

**Assuming LAN behavior on the internet.** On a LAN, packets almost never drop and latency is sub-millisecond. The internet has 1–5% packet loss on a bad day, 50–200 ms latency across continents, and periodic latency spikes. Test with network condition simulation tools (Godot has no built-in one; use `tc netem` on Linux or Clumsy on Windows to add artificial delay and loss) before declaring the networking "done."

**Not separating simulation tick from render frame.** If your simulation runs at the render framerate (60 or 144 fps depending on the machine), two clients on different hardware will have different tick rates and will diverge. Fix the simulation tick rate (e.g. 20 Hz for state updates, 60 Hz for input polling) independent of rendering. In Godot, `_physics_process` runs at a fixed rate configured in Project Settings; networking simulation belongs there, not in `_process`.

**Implementing rollback from scratch.** Rollback netcode is correct only when the details are exactly right: state serialization, input ring buffers, frame timing, divergence detection. Missing any of these produces desyncs that appear only at specific latencies. Use an existing addon.
