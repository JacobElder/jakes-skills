# RPG Systems

Data-driven RPG systems—status effects, equipment, inventory, abilities, crafting—share
one core principle: **behavior lives in data, not in code branches.** A new poison type
should require authoring a Resource, not touching the combat loop. A new item should require
filling in fields, not adding an if-block. Every system here follows that principle.
Violations are listed in §7 so you can recognize and reject them fast.

Engine primary: **Godot 4 / GDScript.** Unity / C# differences are noted inline.

**Contents**
1. Status effects
2. Equipment and stat modifiers
3. Inventory
4. Ability / skill systems
5. Crafting
6. Wiring it together (signals and save-state notes)
7. Anti-patterns and how to recognize them

---

## 1. Status effects

### The wrong shape

A common first implementation adds a boolean per effect:

```gdscript
# DO NOT DO THIS
var is_poisoned: bool
var is_burning: bool
var is_frozen: bool
var poison_timer: float
var burn_timer: float
```

Every new effect forces a code change. Stacking (two poisons? three burns?) is hard
to add. Iterating over active effects requires a cascade of if/elif. Serializing save
state means serializing every field by name. This breaks immediately at scale.

### The right shape: effect as Resource

Each effect is a `StatusEffectData` Resource. The Resource carries:
- **Identity:** id string, display name, icon.
- **Behavior hooks:** `enter()`, `tick()`, `exit()` — called by the entity's effect
  manager, not by the effect itself reaching into game state.
- **Duration and stacking policy:** how long it lasts, and what happens when the same
  effect is applied again.

```gdscript
# status_effect_data.gd
class_name StatusEffectData
extends Resource

@export var id: StringName
@export var display_name: String
@export var icon: Texture2D
@export var duration: float          # -1 = permanent until dispelled
@export var tick_interval: float     # seconds between tick() calls; 0 = no tick
@export var stack_policy: StackPolicy
@export var max_stacks: int = 1

enum StackPolicy {
    REPLACE,      # new application resets timer, no stacking
    ADD,          # stacks up to max_stacks (e.g. 3 poison stacks)
    IGNORE,       # if already active, do nothing
}

# Override in derived Resources via @tool scripts, or use composition:
# attach an effect_script: Script that implements enter/tick/exit.
@export var effect_script: Script    # must implement enter(entity), tick(entity, delta), exit(entity)
```

For behavior, prefer a **script reference on the Resource** (or a small inner class)
rather than a deep inheritance chain. A `PoisonEffect` resource has `effect_script =
preload("res://scripts/effects/poison_behavior.gd")`. The behavior script is a plain
object, not a Node — it receives the entity and manipulates it.

```gdscript
# poison_behavior.gd — not a Resource or Node, just a plain script
static func enter(entity: Node) -> void:
    pass  # visual, sound, etc.

static func tick(entity: Node, _delta: float) -> void:
    entity.take_damage(5, "poison")

static func exit(entity: Node) -> void:
    pass  # remove visual
```

### Active effect instances

An entity carries a list of `ActiveEffect` objects (not Resources — these are runtime
instances that track elapsed time per entity):

```gdscript
# active_effect.gd
class_name ActiveEffect
extends RefCounted

var data: StatusEffectData
var elapsed: float = 0.0
var tick_accum: float = 0.0
var stack_count: int = 1
```

### The tick loop

The entity's `EffectManager` component runs the loop. It lives in `_physics_process`
and iterates the active list:

```gdscript
# effect_manager.gd
class_name EffectManager
extends Node

var _effects: Array[ActiveEffect] = []

func add_effect(data: StatusEffectData) -> void:
    var existing := _find(data.id)
    match data.stack_policy:
        StatusEffectData.StackPolicy.REPLACE:
            if existing:
                existing.elapsed = 0.0
            else:
                _apply_new(data)
        StatusEffectData.StackPolicy.ADD:
            if existing and existing.stack_count < data.max_stacks:
                existing.stack_count += 1
            elif not existing:
                _apply_new(data)
        StatusEffectData.StackPolicy.IGNORE:
            if not existing:
                _apply_new(data)

func _physics_process(delta: float) -> void:
    var to_remove: Array[ActiveEffect] = []
    for effect in _effects:
        if effect.data.duration >= 0.0:
            effect.elapsed += delta
            if effect.elapsed >= effect.data.duration:
                to_remove.append(effect)
                continue
        if effect.data.tick_interval > 0.0:
            effect.tick_accum += delta
            while effect.tick_accum >= effect.data.tick_interval:
                effect.tick_accum -= effect.data.tick_interval
                effect.data.effect_script.tick(owner, delta)
    for effect in to_remove:
        effect.data.effect_script.exit(owner)
        _effects.erase(effect)

func _apply_new(data: StatusEffectData) -> void:
    var ae := ActiveEffect.new()
    ae.data = data
    _effects.append(ae)
    data.effect_script.enter(owner)

func _find(id: StringName) -> ActiveEffect:
    for e in _effects:
        if e.data.id == id:
            return e
    return null
```

Adding a new effect: create a new `StatusEffectData` Resource in the editor, fill in
fields, write a behavior script, assign it. Zero changes to the loop.

**Unity note:** Same architecture; `StatusEffectData` becomes a `ScriptableObject`,
`EffectManager` is a `MonoBehaviour`, and `tick()` is called from `FixedUpdate`. The
behavior script becomes a plain C# class implementing an `IEffectBehavior` interface.

---

## 2. Equipment and stat modifiers

### ItemData Resource

Items are Resources, not scenes. An `ItemData` holds everything static about the item —
what it looks like, what it is, what stats it provides. It does **not** hold runtime
state (durability, enchantments) — that goes on an `ItemInstance` wrapper (see §3).

```gdscript
# item_data.gd
class_name ItemData
extends Resource

@export var id: StringName
@export var display_name: String
@export var icon: Texture2D
@export var description: String
@export var slot: EquipSlot
@export var stat_modifiers: Array[StatModifier]
@export var max_stack_size: int = 1    # 1 = not stackable

enum EquipSlot { NONE, HEAD, CHEST, LEGS, FEET, MAIN_HAND, OFF_HAND, RING, AMULET }
```

No scene references. No signals. No Nodes. A `Texture2D` is fine (it's data); a
`PackedScene` attached to `ItemData` is a code smell — the item doesn't know how to
spawn itself.

### Stat modifiers: additive + multiplicative

The canonical RPG formula separates flat additive bonuses from percentage multipliers:

```
final_stat = (base + sum_of_flat_bonuses) * product_of_multipliers
```

Or equivalently, using the additive-percentage form common in ARPGs:

```
final_stat = base * (1 + sum_of_additive_pct_bonuses) * product_of_multiplicative_bonuses
```

Choose one and stick to it. The flat+percent form avoids multiplicative stacking
surprises (two items each granting +50% additive → +100%; two multiplicative → +125%).

```gdscript
# stat_modifier.gd
class_name StatModifier
extends Resource

enum ModType { FLAT, ADDITIVE_PCT, MULTIPLICATIVE }

@export var stat: StringName          # e.g. &"max_hp", &"attack", &"speed"
@export var mod_type: ModType
@export var value: float
```

### StatSheet: recalculation on equip/unequip

The `StatSheet` component owns the entity's derived stats. It holds a base dict,
listens for equipment changes via signal, and recalculates:

```gdscript
# stat_sheet.gd
class_name StatSheet
extends Node

signal stat_changed(stat: StringName, new_value: float)

@export var base_stats: Dictionary  # e.g. { &"max_hp": 100.0, &"attack": 10.0 }
var _equipment: Dictionary = {}     # EquipSlot -> ItemData (or null)
var _cached: Dictionary = {}

func equip(slot: ItemData.EquipSlot, item: ItemData) -> void:
    _equipment[slot] = item
    _recalculate()

func unequip(slot: ItemData.EquipSlot) -> void:
    _equipment.erase(slot)
    _recalculate()

func get_stat(stat: StringName) -> float:
    return _cached.get(stat, base_stats.get(stat, 0.0))

func _recalculate() -> void:
    var flat: Dictionary = {}
    var add_pct: Dictionary = {}
    var mul: Dictionary = {}

    for item in _equipment.values():
        if item == null:
            continue
        for mod in item.stat_modifiers:
            match mod.mod_type:
                StatModifier.ModType.FLAT:
                    flat[mod.stat] = flat.get(mod.stat, 0.0) + mod.value
                StatModifier.ModType.ADDITIVE_PCT:
                    add_pct[mod.stat] = add_pct.get(mod.stat, 0.0) + mod.value
                StatModifier.ModType.MULTIPLICATIVE:
                    mul[mod.stat] = mul.get(mod.stat, 1.0) * mod.value

    var old_cache := _cached.duplicate()
    _cached.clear()
    for stat in base_stats:
        var b: float = base_stats[stat]
        var result: float = (b + flat.get(stat, 0.0)) * (1.0 + add_pct.get(stat, 0.0)) * mul.get(stat, 1.0)
        _cached[stat] = result

    for stat in _cached:
        if _cached[stat] != old_cache.get(stat):
            stat_changed.emit(stat, _cached[stat])
```

The HUD connects to `stat_changed` and updates health bars, attack readouts, etc.
Nothing in `StatSheet` knows about UI.

**Unity note:** `StatSheet` is a `MonoBehaviour`. `StatModifier` is a
`ScriptableObject` or a plain `[Serializable]` struct. Emit `UnityEvent<string, float>`
or use a custom event bus instead of signals.

---

## 3. Inventory

Two shapes cover most games. Choose one based on genre:

| Shape | Fits | Key features |
|---|---|---|
| **Slot-based** | RPG, action-RPG | N slots; items stack to max_stack_size |
| **Grid-based** | Roguelike, survival, Resident Evil-style | W×H grid; items occupy W×H cells |

In both cases: **the inventory is a data structure, not a scene hierarchy.** Items are
not instanced as Nodes inside a `Container`. The UI is a *view* over the data model.

### ItemInstance: wrapping runtime state

```gdscript
# item_instance.gd
class_name ItemInstance
extends RefCounted

var data: ItemData          # the static template
var quantity: int = 1
var durability: float = -1  # -1 = indestructible
var enchantments: Array[StringName] = []
```

Serialize `data.id` (not the Resource path), `quantity`, `durability`, and
`enchantments` as plain data. On load, resolve `data` by ID from a global `ItemRegistry`.

### Slot-based inventory

```gdscript
# inventory.gd
class_name Inventory
extends Node

signal inventory_changed

@export var capacity: int = 30
var _slots: Array = []   # Array[ItemInstance | null]

func _ready() -> void:
    _slots.resize(capacity)

func add_item(instance: ItemInstance) -> bool:
    # Try to stack first
    if instance.data.max_stack_size > 1:
        for slot in _slots:
            if slot != null and slot.data.id == instance.data.id \
                    and slot.quantity < instance.data.max_stack_size:
                var space := instance.data.max_stack_size - slot.quantity
                var added := mini(space, instance.quantity)
                slot.quantity += added
                instance.quantity -= added
                if instance.quantity <= 0:
                    inventory_changed.emit()
                    return true
    # Find empty slot
    for i in capacity:
        if _slots[i] == null:
            _slots[i] = instance
            inventory_changed.emit()
            return true
    return false   # full

func remove_item(slot_index: int, amount: int = 1) -> ItemInstance:
    var slot := _slots[slot_index]
    if slot == null:
        return null
    slot.quantity -= amount
    if slot.quantity <= 0:
        _slots[slot_index] = null
        inventory_changed.emit()
        return slot
    inventory_changed.emit()
    return ItemInstance.new()  # partial remove — caller gets a new instance
```

### Grid-based inventory

Each item occupies a rectangle of cells. The grid stores item IDs (or null) per cell;
actual instances live in a separate dict keyed by a UUID.

```gdscript
# inventory_grid.gd
class_name InventoryGrid
extends Node

signal grid_changed

@export var grid_width: int = 10
@export var grid_height: int = 8

var _cells: Array = []         # flat [width * height], each cell: StringName UUID or ""
var _items: Dictionary = {}    # UUID -> ItemInstance

func _ready() -> void:
    _cells.resize(grid_width * grid_height)

func can_place(item: ItemData, origin_x: int, origin_y: int) -> bool:
    for dy in item.grid_height:
        for dx in item.grid_width:
            var x := origin_x + dx
            var y := origin_y + dy
            if x >= grid_width or y >= grid_height:
                return false
            if _cells[y * grid_width + x] != "":
                return false
    return true

func place(instance: ItemInstance, origin_x: int, origin_y: int) -> bool:
    if not can_place(instance.data, origin_x, origin_y):
        return false
    var uuid := str(Time.get_ticks_usec())   # cheap unique key; use proper UUID in prod
    _items[uuid] = instance
    for dy in instance.data.grid_height:
        for dx in instance.data.grid_width:
            _cells[(origin_y + dy) * grid_width + (origin_x + dx)] = uuid
    grid_changed.emit()
    return true
```

The UI renders the grid by reading `_cells` and `_items` — it does not own the data.
Drag-and-drop: on drag start, note the source grid position; on drop, call
`remove_from(origin)` then `place(instance, dest_x, dest_y)`.

---

## 4. Ability / skill systems

### AbilityData Resource

An ability is data. The same generic `AbilityExecutor` component fires every ability;
nothing ability-specific lives in the executor.

```gdscript
# ability_data.gd
class_name AbilityData
extends Resource

@export var id: StringName
@export var display_name: String
@export var icon: Texture2D
@export var cooldown: float         # seconds
@export var resource_cost: float    # mana, stamina, etc.
@export var resource_type: StringName  # e.g. &"mana"
@export var targeting: TargetingMode
@export var aoe_radius: float = 0.0
@export var effects: Array[AbilityEffect]  # data objects describing what happens

enum TargetingMode { SELF, SINGLE_ENEMY, AOE_RADIUS, LINE, GROUND_TARGET }
```

`AbilityEffect` is another Resource subclass — `DamageEffect`, `HealEffect`,
`ApplyStatusEffect`, etc. The executor iterates `ability.effects` and dispatches each.
New effect types: new Resource subclass, no changes to the executor.

### Cooldown: per-entity, not per-data

The `AbilityData` Resource is shared across all entities that know the ability. Cooldown
is entity-local state:

```gdscript
# ability_executor.gd
class_name AbilityExecutor
extends Node

var _cooldowns: Dictionary = {}   # StringName id -> float remaining

func can_use(ability: AbilityData) -> bool:
    var cd: float = _cooldowns.get(ability.id, 0.0)
    return cd <= 0.0 and _has_resource(ability)

func use(ability: AbilityData) -> bool:
    if not can_use(ability):
        return false
    _cooldowns[ability.id] = ability.cooldown
    _spend_resource(ability)
    var targets := _resolve_targets(ability)
    for effect in ability.effects:
        effect.apply(owner, targets)
    return true

func _physics_process(delta: float) -> void:
    for id in _cooldowns:
        _cooldowns[id] = maxf(0.0, _cooldowns[id] - delta)
```

### Target resolution

Resolve targets **before** execution. This separates "who gets hit" from "what happens."

```gdscript
func _resolve_targets(ability: AbilityData) -> Array[Node]:
    match ability.targeting:
        AbilityData.TargetingMode.SELF:
            return [owner]
        AbilityData.TargetingMode.SINGLE_ENEMY:
            return [_get_locked_target()]
        AbilityData.TargetingMode.AOE_RADIUS:
            return _get_entities_in_radius(owner.global_position, ability.aoe_radius)
        AbilityData.TargetingMode.LINE:
            return _get_entities_on_line(owner.global_position, owner.global_transform.basis.z, ability.aoe_radius)
        _:
            return []
```

**Unity note:** `AbilityData` is a `ScriptableObject`. `AbilityExecutor` is a
`MonoBehaviour`. `AbilityEffect` is an abstract `ScriptableObject` with a virtual
`Apply(GameObject caster, List<GameObject> targets)` method.

---

## 5. Crafting

### RecipeData Resource

```gdscript
# recipe_data.gd
class_name RecipeData
extends Resource

@export var id: StringName
@export var display_name: String
@export var ingredients: Array[RecipeIngredient]
@export var outputs: Array[RecipeIngredient]   # usually one, but allow multiple

# recipe_ingredient.gd
class_name RecipeIngredient
extends Resource

@export var item_id: StringName
@export var quantity: int
```

### CraftingSystem: validate, consume, produce

```gdscript
# crafting_system.gd
class_name CraftingSystem
extends Node

signal crafted(recipe: RecipeData)
signal recipe_unlocked(recipe: RecipeData)

var known_recipe_ids: Array[StringName] = []

func can_craft(recipe: RecipeData, inventory: Inventory) -> bool:
    if recipe.id not in known_recipe_ids:
        return false
    for ingredient in recipe.ingredients:
        if _count_in_inventory(inventory, ingredient.item_id) < ingredient.quantity:
            return false
    return true

func craft(recipe: RecipeData, inventory: Inventory) -> bool:
    if not can_craft(recipe, inventory):
        return false
    for ingredient in recipe.ingredients:
        _consume(inventory, ingredient.item_id, ingredient.quantity)
    for output in recipe.outputs:
        var item_data := ItemRegistry.get_item(output.item_id)
        var instance := ItemInstance.new()
        instance.data = item_data
        instance.quantity = output.quantity
        inventory.add_item(instance)
    crafted.emit(recipe)
    return true

func unlock_recipe(recipe_id: StringName) -> void:
    if recipe_id not in known_recipe_ids:
        known_recipe_ids.append(recipe_id)
        recipe_unlocked.emit(RecipeRegistry.get_recipe(recipe_id))
```

No if/elif per recipe. Adding a new craft: create a `RecipeData` Resource in the
editor. The system finds it via a `RecipeRegistry` (a Resource that holds an
`Array[RecipeData]`, loaded at startup, indexed by id).

### Discovery patterns

- **Always known:** add to `known_recipe_ids` at start.
- **Found in world:** call `crafting_system.unlock_recipe(id)` when the player picks
  up a recipe book item (whose `ItemData` carries the `unlocks_recipe_id` field).
- **Learned by crafting adjacent items:** `crafted` signal triggers a check in a
  `RecipeDiscoveryManager` that watches crafting history.

---

## 6. Wiring it together

### Signal flow, not direct calls

The correct data flow:

```
EffectManager → entity.take_damage() → StatSheet.stat_changed → HUD.update()
AbilityExecutor → effect.apply() → EffectManager.add_effect()
Inventory.inventory_changed → CraftingUI.refresh()
StatSheet.stat_changed → EquipmentUI.update_tooltips()
```

Nothing in the data layer knows about the UI layer. Nothing in the UI layer mutates
game state — it calls methods on data components.

### Save state

Serialize these structures as plain data. Do not serialize engine objects:

| System | What to save |
|---|---|
| Inventory | Array of `{item_id, quantity, durability, enchantments}` dicts |
| Equipment | Dict of `{slot: item_id}` |
| Active effects | Array of `{effect_id, elapsed, stack_count}` |
| Ability cooldowns | Dict of `{ability_id: remaining_cd}` |
| Known recipes | Array of `recipe_id` strings |

On load: resolve IDs via registries, reconstruct runtime objects, re-emit signals to
sync UI. Never store a `Resource` path or a `NodePath` in save data — those break when
files move.

---

## 7. Anti-patterns and how to recognize them

These are the failure modes that appear most often in generated RPG code. Recognize
them on sight and push back.

**Hardcoded item name checks.**
```gdscript
# WRONG
if item.display_name == "Sword of Flames":
    target.apply_effect("burning")
```
The item's effects belong in its `stat_modifiers` or a dedicated `on_hit_effects` array
on `ItemData`. The weapon's name is not its contract. The fix: `ItemData` has an
`Array[AbilityEffect] on_hit_effects`; the combat system iterates it without knowing
what's in it.

**Boolean flag forests for status effects.**
```gdscript
# WRONG
var is_poisoned: bool
var is_burning: bool
var is_slowed: bool
```
Three new effects → three more booleans, three more timer variables, three more
branches in `_process`. The correct shape is §1: a list of `ActiveEffect` instances
iterated by a generic loop.

**ItemData with scene references or signals.**
```gdscript
# WRONG
@export var pickup_scene: PackedScene   # ItemData should not know how to spawn itself
signal item_used(entity)               # ItemData is a data record, not an event emitter
```
`ItemData` is a passive data record. Spawning, instancing, and event emission belong in
the systems that operate on items — `InventorySystem`, `WorldItemSpawner`, etc.

**Items stored as Node instances in a Container.**
```gdscript
# WRONG
var item_node := item_scene.instantiate()
$InventoryContainer.add_child(item_node)
```
The `Container` is not the inventory; it is a UI representation. If the player's
inventory is "what's in `$InventoryContainer`," saving the game means saving a scene
tree — fragile, slow, and couples inventory logic to the rendering layer. The inventory
is an `Array` (or `Dictionary`); the Container renders it.

**Serializing engine objects instead of IDs.**
```gdscript
# WRONG — do not save a Resource reference or path
save_data["equipped_weapon"] = equipped_weapon   # serializes the whole Resource object
save_data["equipped_weapon"] = equipped_weapon.resource_path  # breaks when files move
# CORRECT
save_data["equipped_weapon"] = equipped_weapon.id  # stable StringName from ItemData
```

**AbilityData storing cooldown state.**
```gdscript
# WRONG — AbilityData is shared; this creates a single global cooldown across all entities
class_name AbilityData
var remaining_cooldown: float   # DO NOT
```
Cooldown is per-entity. Keep it in `AbilityExecutor._cooldowns` (a dict keyed by
ability id), not in the shared Resource.

**No ItemRegistry — resolving items by display name.**
```gdscript
# WRONG
func find_item(name: String) -> ItemData:
    for item in all_items:
        if item.display_name == name:  # display_name is localized; it changes
            return item
```
Every item gets a stable `id: StringName` at authoring time. The registry resolves by
id. Display names are for humans and localization; ids are for code.
