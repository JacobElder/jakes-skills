# Collision Layer and Mask Architecture in Godot 4

## The two-property model

Every physics body (CharacterBody2D/3D, RigidBody2D/3D, StaticBody2D/3D, Area2D/3D) has:

- **`collision_layer`**: which layer(s) this object *occupies* — "what it IS"
- **`collision_mask`**: which layer(s) this object *detects* — "what it can interact with"

A collision occurs only when body A's mask includes a layer that body B occupies (and vice versa for two-way physics; Area2D only needs a one-way match).

## Layer naming convention (Project Settings → Layer Names)

Name layers in Project Settings before assigning them. Use nouns for layers, not roles:

```
Layer 1:  world          (terrain, static platforms, walls)
Layer 2:  player         (the player CharacterBody)
Layer 3:  enemies        (enemy CharacterBodies)
Layer 4:  player_attack  (player hitbox Area2D)
Layer 5:  enemy_attack   (enemy hitbox Area2D)
Layer 6:  pickups        (coin, health, ammo Area2D)
Layer 7:  player_bullet  (projectiles fired by player)
Layer 8:  enemy_bullet   (projectiles fired by enemies)
```

## Standard layer/mask table for a 2D action game

| Node | Layer | Mask | Why |
|---|---|---|---|
| Static terrain | 1 (world) | — | Doesn't detect anything |
| Player CharacterBody | 2 (player) | 1, 5, 6 | Collides with world; detects enemy attacks and pickups |
| Enemy CharacterBody | 3 (enemies) | 1, 4 | Collides with world; detects player attacks |
| Player hitbox Area2D | 4 (player_attack) | 3 | Only detects enemies |
| Enemy hitbox Area2D | 5 (enemy_attack) | 2 | Only detects the player |
| Pickup Area2D | 6 (pickups) | 0 | Passive — player mask detects it |
| Player bullet | 7 (player_bullet) | 1, 3 | Hits world and enemies, not the player |
| Enemy bullet | 8 (enemy_bullet) | 1, 2 | Hits world and player, not enemies |

## Hitbox / Hurtbox pattern

A hitbox deals damage; a hurtbox receives damage. Keep them on separate nodes from the physics body so you can enable/disable them independently (e.g., during i-frames or attack animation windows).

```
Player (CharacterBody2D) — layer=2, mask=1|5|6
├── CollisionShape2D           ← body physics shape
├── HurtboxArea (Area2D)       ← layer=2, mask=5  — receives enemy attacks
│   └── CollisionShape2D
└── HitboxArea (Area2D)        ← layer=4, mask=3  — deals damage to enemies
    └── CollisionShape2D       ← disabled except during attack animation window
```

```
Enemy (CharacterBody2D) — layer=3, mask=1|4
├── CollisionShape2D
├── HurtboxArea (Area2D)       ← layer=3, mask=4  — receives player attacks
│   └── CollisionShape2D
└── HitboxArea (Area2D)        ← layer=5, mask=2  — deals damage to player
    └── CollisionShape2D
```

Connecting the hitbox/hurtbox signals:

```gdscript
# EnemyHurtbox.gd — on the enemy's HurtboxArea
func _ready() -> void:
    area_entered.connect(_on_hitbox_entered)

func _on_hitbox_entered(hitbox: Area2D) -> void:
    if hitbox.has_method("get_damage"):
        var damage: int = hitbox.get_damage()
        get_parent().take_damage(damage)
```

The hitbox exposes `get_damage()` — the hurtbox pulls it. This keeps the damage value on the attacker (where it belongs) without coupling to specific node types.

## Enabling hitbox only during attack window

Use AnimationPlayer call tracks to enable/disable the hitbox CollisionShape2D:

```gdscript
# Called by AnimationPlayer call track at attack start frame
func _enable_hitbox() -> void:
    $HitboxArea/CollisionShape2D.disabled = false

# Called by AnimationPlayer call track at attack end frame  
func _disable_hitbox() -> void:
    $HitboxArea/CollisionShape2D.disabled = true
```

This is safer than toggling `monitoring` — disabling the CollisionShape prevents any overlap detection, including leftover contacts from a previous frame.

## Invincibility frames (i-frames)

During i-frames, disable the player's hurtbox — don't modify physics layer/mask at runtime, which can leave stale contacts:

```gdscript
func start_iframes(duration: float) -> void:
    $HurtboxArea/CollisionShape2D.disabled = true
    await get_tree().create_timer(duration).timeout
    $HurtboxArea/CollisionShape2D.disabled = false
```

## Setting layers in code

Use bit-shift syntax for clarity:

```gdscript
# Set layer 2 and layer 4 (layers are 1-indexed, bits are 0-indexed)
body.collision_layer = (1 << 1) | (1 << 3)  # layers 2 and 4
body.collision_mask  = (1 << 0) | (1 << 4)  # layers 1 and 5

# Or use the named helper (Godot 4.1+)
body.set_collision_layer_value(2, true)
body.set_collision_mask_value(1, true)
```

## Common mistakes

**Setting mask=0 on static bodies**: StaticBody doesn't need to detect anything — its mask should be 0. Only set mask on bodies that need to react to overlaps.

**Using layer for damage value**: The collision layer is NOT a damage type. Don't try to encode damage amount in the layer number. Put damage on the hitbox node as a property.

**Forgetting to disable hitbox by default**: Child hitbox CollisionShape2D should start disabled in the Inspector. If it's enabled at scene start, the first physics frame will register hits before any animation plays.

**Same layers for player and enemy physics bodies**: Player (layer 2) and enemies (layer 3) should be on different layers so you can stop them from physically blocking each other if needed (remove 3 from player mask), while still letting hitboxes work on dedicated attack layers.
