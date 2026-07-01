# Grid and Turn-Based Tactics Systems

## Turn order and initiative

Use a sorted array — sort by initiative (speed stat, roll, or pre-set value), then advance an index:

```gdscript
# TurnManager.gd (autoload)
var units: Array[Unit] = []
var turn_index: int = 0
var current_unit: Unit

signal turn_started(unit: Unit)
signal turn_ended(unit: Unit)

func register_unit(unit: Unit) -> void:
    units.append(unit)
    units.sort_custom(func(a, b): return a.initiative > b.initiative)

func start_combat() -> void:
    turn_index = 0
    _begin_turn()

func _begin_turn() -> void:
    current_unit = units[turn_index]
    current_unit.action_points = current_unit.max_ap
    turn_started.emit(current_unit)

func end_turn() -> void:
    turn_ended.emit(current_unit)
    # Advance — skip dead units
    var checked := 0
    while checked < units.size():
        turn_index = (turn_index + 1) % units.size()
        if units[turn_index].is_alive():
            break
        checked += 1
    _begin_turn()
```

For **simultaneous / speed-tie resolution**, assign a secondary tiebreaker (random roll on combat start, stored per unit). For **reactive interrupts** (opportunity attacks), push an interrupt unit onto a stack and pop after the interrupt resolves before continuing.

## Action points

Each unit has a pool of AP refreshed at turn start. Actions cost different amounts:

```gdscript
class_name Unit extends CharacterBody2D

@export var max_ap: int = 3
var action_points: int = 0

func try_spend_ap(cost: int) -> bool:
    if action_points < cost:
        return false
    action_points -= cost
    ap_changed.emit(action_points)
    return true

# In action handlers:
func move_to(cell: Vector2i) -> void:
    if not try_spend_ap(AP_COST_MOVE):
        return
    # execute move...

func attack(target: Unit) -> void:
    if not try_spend_ap(AP_COST_ATTACK):
        return
    # execute attack...
```

**Common AP costs**: move 1 cell = 1 AP, attack = 2 AP, ability = 1–3 AP, overwatch = all remaining AP. Expose these as `@export` constants in a GameConstants Resource.

## Square grid pathfinding with AStarGrid2D

Godot 4 has a built-in `AStarGrid2D` — no manual A* needed:

```gdscript
# GridMap.gd
var astar := AStarGrid2D.new()

func _ready() -> void:
    astar.region = Rect2i(0, 0, MAP_WIDTH, MAP_HEIGHT)
    astar.cell_size = Vector2(TILE_SIZE, TILE_SIZE)
    astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER  # 4-directional
    astar.default_compute_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
    astar.update()
    _mark_walls()

func _mark_walls() -> void:
    for cell in wall_cells:
        astar.set_point_solid(cell, true)

func get_path(from: Vector2i, to: Vector2i) -> Array[Vector2i]:
    return astar.get_id_path(from, to)

func set_unit_at(cell: Vector2i, solid: bool) -> void:
    astar.set_point_solid(cell, solid)  # block cell when unit occupies it
```

Use `DIAGONAL_MODE_NEVER` for 4-directional grids (most tactics games). Use `DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES` for 8-directional grids.

## Movement range (flood fill, not A*)

Do NOT use A* for range highlighting — it only finds one path. Use BFS to enumerate all cells within AP budget:

```gdscript
func get_reachable_cells(start: Vector2i, ap: int) -> Dictionary:
    # Returns {cell: cost} for all reachable cells
    var visited := {start: 0}
    var queue := [{cell = start, cost = 0}]
    while not queue.is_empty():
        var current = queue.pop_front()
        for neighbor in _get_neighbors(current.cell):
            var new_cost: int = current.cost + _move_cost(neighbor)
            if new_cost <= ap and (neighbor not in visited or visited[neighbor] > new_cost):
                visited[neighbor] = new_cost
                queue.append({cell = neighbor, cost = new_cost})
    visited.erase(start)
    return visited

func _get_neighbors(cell: Vector2i) -> Array[Vector2i]:
    return [
        cell + Vector2i(1, 0), cell + Vector2i(-1, 0),
        cell + Vector2i(0, 1), cell + Vector2i(0, -1),
    ]

func _move_cost(cell: Vector2i) -> int:
    return 2 if is_difficult_terrain(cell) else 1
```

## Move preview and confirmation

```gdscript
# PlayerController.gd
var _reachable: Dictionary = {}
var _selected_unit: Unit = null

func select_unit(unit: Unit) -> void:
    _selected_unit = unit
    _reachable = GridMap.get_reachable_cells(unit.grid_cell, unit.action_points)
    _highlight_cells(_reachable.keys(), HIGHLIGHT_MOVE)

func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.pressed:
        var clicked_cell := world_to_grid(get_global_mouse_position())
        if clicked_cell in _reachable:
            _confirm_move(clicked_cell)

func _confirm_move(target: Vector2i) -> void:
    var path := GridMap.get_path(_selected_unit.grid_cell, target)
    var cost := _reachable[target]
    _selected_unit.try_spend_ap(cost)
    _selected_unit.walk_path(path)
    _clear_highlights()
```

## Line of sight

Bresenham's line — check every cell between attacker and target:

```gdscript
func has_line_of_sight(from: Vector2i, to: Vector2i) -> bool:
    var cells := _bresenham_line(from, to)
    for cell in cells:
        if cell == from or cell == to:
            continue
        if is_wall(cell):
            return false
    return true

func _bresenham_line(a: Vector2i, b: Vector2i) -> Array[Vector2i]:
    var cells: Array[Vector2i] = []
    var dx := abs(b.x - a.x)
    var dy := abs(b.y - a.y)
    var sx := 1 if a.x < b.x else -1
    var sy := 1 if a.y < b.y else -1
    var err := dx - dy
    var x := a.x
    var y := a.y
    while true:
        cells.append(Vector2i(x, y))
        if x == b.x and y == b.y:
            break
        var e2 := 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return cells
```

For attack range: BFS up to max_range steps + `has_line_of_sight()` filter.

## Hex grid coordinate math

Use **axial coordinates** (q, r) — simpler math than offset grids:

```gdscript
# 6 neighbor directions in axial coordinates (pointy-top)
const HEX_DIRECTIONS := [
    Vector2i(1, 0), Vector2i(1, -1), Vector2i(0, -1),
    Vector2i(-1, 0), Vector2i(-1, 1), Vector2i(0, 1),
]

func hex_neighbors(hex: Vector2i) -> Array[Vector2i]:
    var result: Array[Vector2i] = []
    for d in HEX_DIRECTIONS:
        result.append(hex + d)
    return result

func hex_distance(a: Vector2i, b: Vector2i) -> int:
    # Axial to cube: z = -q - r
    var dq := b.x - a.x
    var dr := b.y - a.y
    return (abs(dq) + abs(dq + dr) + abs(dr)) / 2

# Axial to pixel (pointy-top, hex_size = radius to corner)
func axial_to_world(hex: Vector2i, hex_size: float) -> Vector2:
    var x := hex_size * (sqrt(3) * hex.x + sqrt(3) / 2.0 * hex.y)
    var y := hex_size * (3.0 / 2.0 * hex.y)
    return Vector2(x, y)

# Pixel to axial (snap to nearest hex)
func world_to_axial(pos: Vector2, hex_size: float) -> Vector2i:
    var q := (sqrt(3.0) / 3.0 * pos.x - 1.0 / 3.0 * pos.y) / hex_size
    var r := (2.0 / 3.0 * pos.y) / hex_size
    return _axial_round(q, r)

func _axial_round(q: float, r: float) -> Vector2i:
    var s := -q - r
    var rq := roundi(q)
    var rr := roundi(r)
    var rs := roundi(s)
    var dq := abs(rq - q)
    var dr := abs(rr - r)
    var ds := abs(rs - s)
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    return Vector2i(rq, rr)
```

Hex BFS range and line-of-sight use the same patterns as square grids — substitute `hex_neighbors()` for `_get_neighbors()` and `hex_distance()` for Manhattan distance.

## TurnManager state machine

```gdscript
enum TurnState { AWAITING_INPUT, ANIMATING, ENEMY_THINKING, COMBAT_OVER }
var state := TurnState.AWAITING_INPUT

func _on_unit_action_complete() -> void:
    if current_unit.action_points <= 0:
        await _animate_end_turn()
        end_turn()
    else:
        state = TurnState.AWAITING_INPUT  # player chooses next action

func _on_end_turn_pressed() -> void:
    if state != TurnState.AWAITING_INPUT:
        return
    end_turn()
```

Enemy turns: call AI decision function (utility AI or simple priority rules), execute actions sequentially with `await` on each animation, then call `end_turn()`.
