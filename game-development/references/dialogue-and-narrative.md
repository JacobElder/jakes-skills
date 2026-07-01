# Dialogue and Narrative Systems

## Tool selection

| Situation | Use |
|---|---|
| Heavy branching, variables, conditions, complex narrative logic | **Ink** + godot-ink binding |
| Visual, cutscene-driven, moderate branching, Godot-native workflow | **Dialogic 2** |
| Simple linear or lightly-branching dialogue, full control needed | **Hand-rolled resource graph** |
| Visual novel with Ren'Py-style scene direction | **Dialogic 2** |

**Ink** (inkle): A narrative scripting language compiled to JSON. godot-ink (addon) runs compiled `.ink.json` files in Godot. Best for writers who want the story to be a first-class file, not a node tree. Supports variables, conditions, functions, knots, stitches, and tags. The story IS a script — no visual editor.

**Dialogic 2**: A Godot addon with a timeline editor. Better for cutscene-heavy games where the director controls portraits, camera, and music in the same timeline. Less mature for deeply branching narrative; stronger for scripted sequences.

**Hand-rolled**: Warranted when your dialogue is simple (10-20 conversations, minimal branching) or when you need tight integration with game systems that Dialogic/Ink can't easily reach.

## Data-driven dialogue format (hand-rolled)

Never hardcode dialogue in scripts. Every conversation is a **Resource** graph.

```gdscript
# DialogueLine.gd
class_name DialogueLine
extends Resource

@export var id: String = ""
@export var speaker: String = ""
@export var text: String = ""
@export var portrait: String = ""          # portrait key, not a Texture directly
@export var audio_cue: String = ""        # optional voice/sfx key
@export var choices: Array[DialogueChoice] = []
@export var next_id: String = ""          # empty = end of conversation
@export var condition: String = ""        # GDScript expression, e.g. "player.flags['met_innkeeper']"
```

```gdscript
# DialogueChoice.gd
class_name DialogueChoice
extends Resource

@export var text: String = ""
@export var next_id: String = ""
@export var condition: String = ""
@export var consequence: String = ""      # expression to eval when chosen, e.g. "player.flags['talked_to_elder'] = true"
```

```gdscript
# Conversation.gd — a .tres file in the project
class_name Conversation
extends Resource

@export var lines: Dictionary = {}        # id → DialogueLine
@export var start_id: String = "start"
```

Load conversations with `load("res://dialogue/village_elder.tres")`. This is version-controlled, hot-reloadable, and inspectable in the editor.

## DialogueRunner

```gdscript
# DialogueRunner.gd — autoload or scene singleton
extends Node

signal line_ready(line: DialogueLine)
signal choices_ready(choices: Array[DialogueChoice])
signal conversation_ended

var _conversation: Conversation
var _current_id: String = ""

func start(conversation: Conversation) -> void:
    _conversation = conversation
    _advance(conversation.start_id)

func _advance(id: String) -> void:
    if id == "" or not _conversation.lines.has(id):
        conversation_ended.emit()
        return

    var line: DialogueLine = _conversation.lines[id]

    # Evaluate entry condition
    if line.condition != "" and not _eval(line.condition):
        _advance(line.next_id)   # skip this line; follow next
        return

    line_ready.emit(line)

    if line.choices.is_empty():
        # Auto-advance on input (handled by DialogueBox UI)
        pass
    else:
        var available := line.choices.filter(func(c): return c.condition == "" or _eval(c.condition))
        choices_ready.emit(available)

func advance_from_line(line: DialogueLine) -> void:
    _advance(line.next_id)

func choose(choice: DialogueChoice) -> void:
    if choice.consequence != "":
        _eval(choice.consequence)
    _advance(choice.next_id)

func _eval(expression: String) -> Variant:
    var expr := Expression.new()
    expr.parse(expression)
    return expr.execute([], GameState)  # GameState = your global state autoload
```

The `Expression` class evaluates arbitrary GDScript expressions at runtime. Pass `GameState` (an autoload holding flags, variables, etc.) as the base instance so conditions like `"player_flags.has('met_elder')"` resolve against it.

## Ink integration (godot-ink)

```gdscript
# After installing the godot-ink addon:
extends Node

@onready var ink: InkStory = $InkStory

func _ready() -> void:
    ink.ink_file = load("res://story/main.ink.json")
    ink.story_ready.connect(_on_story_ready)

func _on_story_ready() -> void:
    _show_next()

func _show_next() -> void:
    while ink.can_continue:
        var text := ink.continue_story()
        dialogue_box.display(text)
        await dialogue_box.line_finished
    if ink.has_choices:
        dialogue_box.show_choices(ink.current_choices.map(func(c): return c.text))

func _on_choice_selected(idx: int) -> void:
    ink.choose_choice_index(idx)
    _show_next()
```

Ink variables sync bidirectionally:
```gdscript
ink.set_variable("player_gold", player.gold)
var level_req: int = ink.get_variable("required_level")
```

## Portrait system

Store portraits as a dictionary, not as direct Texture2D on the DialogueLine — this lets you share portraits across conversations and swap them at runtime (emotions, damage states).

```gdscript
# PortraitLibrary.gd — autoload
var portraits: Dictionary = {
    "elder_neutral": preload("res://portraits/elder_neutral.png"),
    "elder_angry":   preload("res://portraits/elder_angry.png"),
    "innkeeper":     preload("res://portraits/innkeeper.png"),
}
```

```gdscript
# DialogueBox.gd
func _on_line_ready(line: DialogueLine) -> void:
    portrait_texture.texture = PortraitLibrary.portraits.get(line.portrait, null)
    portrait_texture.visible = line.portrait != ""
    speaker_label.text = line.speaker
    display(line.text)
```

## Typewriter effect (see also ui-and-hud.md)

```gdscript
# In DialogueBox — complete implementation with skip
var _typing: bool = false

func display(text: String) -> void:
    _full_text = text
    _char_index = 0
    label.text = ""
    _typing = true
    timer.start()

func _on_timer_timeout() -> void:
    if _char_index >= _full_text.length():
        timer.stop()
        _typing = false
        line_finished.emit()
        return
    label.text += _full_text[_char_index]
    _char_index += 1
    # Punctuation pauses
    var pause := {"." : 0.3, "!" : 0.3, "?" : 0.3, "," : 0.12}.get(
        _full_text[_char_index - 1], 1.0 / chars_per_second)
    timer.wait_time = pause

func _unhandled_input(event: InputEvent) -> void:
    if event.is_action_just_pressed("ui_accept"):
        if _typing:
            _skip_to_end()
        else:
            DialogueRunner.advance_from_line(_current_line)

func _skip_to_end() -> void:
    timer.stop()
    _typing = false
    label.text = _full_text
    line_finished.emit()
```

## Conditions and consequences

Use GDScript's `Expression` class for dynamic evaluation — no switch statement needed.

```gdscript
# Condition: "player_gold >= 50 and player_flags.has('spoke_to_guard')"
# Consequence: "player_gold -= 30; player_flags['bribed_guard'] = true"

func _eval_condition(expr_str: String) -> bool:
    if expr_str == "":
        return true
    var expr := Expression.new()
    if expr.parse(expr_str) != OK:
        push_error("Invalid dialogue condition: " + expr_str)
        return false
    return expr.execute([], GameState) as bool

func _eval_consequence(expr_str: String) -> void:
    if expr_str == "":
        return
    var expr := Expression.new()
    expr.parse(expr_str)
    expr.execute([], GameState)
```

## Quest system integration

Quests are separate from dialogue but triggered by it:
```gdscript
# QuestGiver.gd — on the NPC
func _on_dialogue_ended() -> void:
    if GameState.flags.get("accepted_fetch_quest") and not QuestManager.has_quest("fetch_herbs"):
        QuestManager.start_quest("fetch_herbs")
```

```gdscript
# QuestManager.gd — autoload
var active_quests: Dictionary = {}  # quest_id → QuestData

func start_quest(id: String) -> void:
    var quest: QuestData = load("res://quests/" + id + ".tres")
    active_quests[id] = quest
    quest_started.emit(quest)

func complete_objective(quest_id: String, objective_id: String) -> void:
    var quest: QuestData = active_quests.get(quest_id)
    if quest:
        quest.complete_objective(objective_id)
        if quest.all_complete():
            _complete_quest(quest_id)
```

## Anti-patterns table

| Pattern | Problem | Fix |
|---|---|---|
| Dialogue strings hardcoded in scripts | Can't be translated, edited, or branched without code changes | Resource graph or Ink file |
| `if choice == 0: ... elif choice == 1: ...` | Unmaintainable after 3 choices | Data-driven `next_id` on `DialogueChoice` |
| `Texture2D` directly on `DialogueLine` resource | Preloads all portraits at load time | Portrait library dictionary |
| Checking dialogue state with boolean flags per conversation | O(n) flag proliferation | Central `GameState.flags` dictionary |
| Advancing dialogue from game logic | Couples game code to UI | Signal from DialogueRunner; UI and game listen separately |
