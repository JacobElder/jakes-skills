# Memory Management and Orphan Nodes

## GDScript memory model

Godot has two memory management tracks:

| Base class | Management | Examples |
|---|---|---|
| `RefCounted` (and subclasses) | Reference-counted, automatic | `Resource`, `Image`, `RegEx`, plain GDScript objects |
| `Object` (non-RefCounted) | Manual — must call `free()` or `queue_free()` | `Node` and all subclasses |

Reference-counted objects are freed when nothing holds a reference. Nodes are freed only when explicitly removed from the scene tree and freed, or when their parent is freed.

## queue_free() vs free()

```gdscript
# Safe — deferred to end of the current frame
node.queue_free()

# Immediate — use only when you know no code will touch this node again this frame
node.free()
```

**Always prefer `queue_free()`** for nodes. Calling `free()` in a signal callback, physics callback, or while iterating a list that contains the node causes use-after-free crashes. `queue_free()` is safe in all contexts.

`free()` is appropriate for non-Node RefCounted objects that you want to release immediately without waiting a frame, but those are reference-counted anyway so it's rarely needed.

## Orphan nodes — the most common memory leak

A node created via `Node.new()` or `PackedScene.instantiate()` that is **never added to the scene tree** is an orphan. It will never be freed automatically.

```gdscript
# LEAK — node created but never added anywhere
func spawn_enemy() -> void:
    var e = EnemyScene.instantiate()
    # forgot add_child(e) — e is now an orphan, leaks forever

# CORRECT
func spawn_enemy() -> void:
    var e = EnemyScene.instantiate()
    add_child(e)
```

**Detection**: Debugger → Monitors → Object → Orphan Nodes. If this number climbs during gameplay, you have a leak. Also check: remote scene tree view shows orphan nodes under a "(orphans)" entry.

**Other causes of orphans:**
- Storing a node in a variable, then clearing the variable without freeing the node
- Removing a node from the tree with `remove_child()` and never calling `queue_free()` on it
- Pooled nodes that get removed from the pool array without being freed

```gdscript
# LEAK — removes from tree but doesn't free
func disable_enemy(e: Enemy) -> void:
    remove_child(e)   # e is now an orphan

# CORRECT for pools — keep node in tree but hide it
func return_to_pool(e: Enemy) -> void:
    e.hide()
    e.set_physics_process(false)
    pool.append(e)    # still in tree, will be reused
```

## Circular references

RefCounted objects (Resources, plain GDScript classes extending RefCounted) can form cycles that prevent deallocation:

```gdscript
class_name NodeA extends RefCounted
var peer: NodeA  # holds reference to NodeA B

var a := NodeA.new()
var b := NodeA.new()
a.peer = b  # A references B
b.peer = a  # B references A → cycle, neither is ever freed
```

Break cycles with `WeakRef`:

```gdscript
class_name NodeA extends RefCounted
var peer: WeakRef  # weak reference, doesn't prevent GC

var a := NodeA.new()
var b := NodeA.new()
a.peer = weakref(b)
b.peer = weakref(a)

# To use:
var ref = a.peer.get_ref()  # returns null if b has been freed
if ref:
    ref.do_something()
```

## WeakRef for observer lists

Signals handle this automatically, but if you maintain manual listener lists, use WeakRef to avoid holding alive freed nodes:

```gdscript
# EventBus with WeakRef listeners
var _listeners: Array[WeakRef] = []

func subscribe(obj: Object) -> void:
    _listeners.append(weakref(obj))

func emit_event(event: String) -> void:
    var alive: Array[WeakRef] = []
    for wr in _listeners:
        var ref := wr.get_ref()
        if ref:
            ref.on_event(event)
            alive.append(wr)
    _listeners = alive  # prune dead refs
```

## is_instance_valid()

Before using any stored node reference that may have been freed:

```gdscript
func _process(_delta: float) -> void:
    if not is_instance_valid(target):
        target = null
        return
    # safe to use target
    move_toward(target.global_position, ...)
```

`is_instance_valid()` returns `false` for freed nodes (those that received `queue_free()` or `free()`). Checking `!= null` is **not sufficient** — a freed node variable is not null, it's an invalid reference that will crash on access.

## Signal connections and lambda captures

Lambdas (inline `func()`) capture variables by reference. A lambda that captures `self` keeps the capturing node alive or causes use-after-free if the node is freed before the signal fires:

```gdscript
# RISK — timer may outlive the node that created it
func start_delay() -> void:
    var timer := get_tree().create_timer(2.0)
    timer.timeout.connect(func():
        take_damage(10)  # 'self' captured — crashes if node freed during wait
    )

# SAFE — disconnect on exit, or check validity
func start_delay() -> void:
    var timer := get_tree().create_timer(2.0)
    timer.timeout.connect(_on_delay_expired)  # named method, safer

func _on_delay_expired() -> void:
    if not is_instance_valid(self):
        return
    take_damage(10)
```

Or use `CONNECT_ONE_SHOT` so the connection auto-disconnects after firing:

```gdscript
some_signal.connect(_on_fired, CONNECT_ONE_SHOT)
```

## _exit_tree() for cleanup

`_exit_tree()` is called when a node leaves the scene tree (before `_notification(NOTIFICATION_PREDELETE)`). Use it to disconnect signals, cancel async operations, and release external resources:

```gdscript
func _exit_tree() -> void:
    NavigationServer2D.agent_set_callback(nav_agent_id, null)
    EventBus.unsubscribe(self)
    _pending_request?.cancel()
```

Prefer `_exit_tree()` over `_notification(NOTIFICATION_PREDELETE)` for cleanup code — it runs while the node's children are still valid.

## Detecting leaks in the debugger

1. Debugger → Monitors → Object → Orphan Nodes: should not grow during steady gameplay
2. Debugger → Monitors → Object → Objects: total object count; compare before/after loading and unloading a level
3. Profile memory via `OS.get_static_memory_usage()` and `Performance.get_monitor(Performance.OBJECT_NODE_COUNT)` logged to console
4. After unloading a scene: call `ResourceLoader.clear_cache()` if you want to release cached resources from memory

## Common mistakes

- Calling `free()` inside a signal callback that the freed node emits (use `queue_free()`)
- Checking `node != null` instead of `is_instance_valid(node)` for freed-node safety
- Not calling `remove_child()` + `queue_free()` after removing from a pool — orphan leak
- Circular RefCounted references without WeakRef
- Lambda capturing `self` in a timer or tween that can outlive the node
- Forgetting `_exit_tree()` cleanup for external subscriptions (NavigationServer, event buses)
