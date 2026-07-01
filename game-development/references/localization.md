# Localization and Internationalization

Localization is not a feature you bolt on at the end — it is an architectural constraint that affects string handling, font loading, layout, and date/number formatting from the first line of UI code. Games built without i18n in mind require rework proportional to the amount of hardcoded text. This file covers the patterns that make localization tractable.

## Contents
- Godot 4 TranslationServer and CSV workflow
- Key naming conventions
- tr() and dynamic strings
- Runtime locale switching
- Japanese, Chinese, Korean fonts
- RTL languages (Arabic, Hebrew)
- Plural forms
- String overflow (German, Russian)
- Date, time, number formats
- Context for translators
- String concatenation traps
- PO/POT workflow for larger projects
- Testing checklist

## Godot 4 TranslationServer and CSV workflow

Godot's built-in localization reads CSV files where the first column is the key and subsequent columns are locale codes:

```
key,en,es,ja,de
MAIN_MENU_PLAY,Play,Jugar,プレイ,Spielen
MAIN_MENU_SETTINGS,Settings,Configuración,設定,Einstellungen
INVENTORY_SLOT_EMPTY,Empty slot,Ranura vacía,空のスロット,Leerer Platz
HUD_HEALTH_LABEL,HP,HP,HP,LP
ITEM_SWORD_NAME,Iron Sword,Espada de Hierro,鉄の剣,Eisenschwert
ITEM_SWORD_DESC,A basic sword.,Una espada básica.,基本的な剣です。,Ein einfaches Schwert.
```

Add the CSV: **Project Settings → Localization → Translations → Add**. Godot compiles it to a binary format at export time.

Access translations in code:

```gdscript
# GDScript
$Label.text = tr("MAIN_MENU_PLAY")

# In scene (auto-translate property)
# Set Label.auto_translate_mode = AUTO_TRANSLATE_MODE_ALWAYS
# Set Label.text = "MAIN_MENU_PLAY"  ← Godot auto-wraps with tr()
```

In Godot 4.1+, Control nodes have `auto_translate_mode` — when set to `AUTO_TRANSLATE_MODE_ALWAYS`, the node's `text` property is automatically passed through `tr()`. Set the raw key as the text value.

## Key naming conventions

Keys must be unambiguous and contextual. Two rules:

1. **Describe the context, not the translation.** `BUTTON_PLAY` not `STRING_001`. `INVENTORY_EQUIP_TOOLTIP` not `TOOLTIP_TEXT`.
2. **Namespace by scene or domain.** Format: `DOMAIN_ELEMENT_CONTEXT`.

```
MAIN_MENU_PLAY_BUTTON
MAIN_MENU_QUIT_BUTTON
INVENTORY_SLOT_EMPTY_TOOLTIP
INVENTORY_ITEM_EQUIP_ACTION
COMBAT_HUD_HEALTH_LABEL
COMBAT_DAMAGE_NUMBER
SETTINGS_AUDIO_VOLUME_LABEL
QUEST_MAIN_01_TITLE
QUEST_MAIN_01_DESCRIPTION
NPC_GUARD_GREETING
NPC_MERCHANT_BUY_PROMPT
```

Bad keys: `TEXT_1`, `LABEL`, `BUTTON_OK`, `MSG`. These are ambiguous across contexts and give translators no information about where the string appears.

## tr() and dynamic strings — never concatenate

The critical mistake in localization is building sentences from parts:

```gdscript
# WRONG — word order differs between languages; breaks in German, Japanese
var text = "You found " + item_name + " in the " + location_name + "!"

# CORRECT — use format strings with named placeholders
var text = tr("FOUND_ITEM_IN_LOCATION").format({"item": item_name, "location": location_name})
```

The translation file entry:
```
FOUND_ITEM_IN_LOCATION,"You found {item} in the {location}!","¡Encontraste {item} en {location}!","あなたは{location}で{item}を見つけました！","Du hast {item} in {location} gefunden!"
```

Japanese and German reorder the components entirely. Only `format()` with named placeholders makes this possible. Never split a sentence across two keys.

## Runtime locale switching

```gdscript
# Change locale (saved to settings)
func set_locale(locale_code: String) -> void:
    TranslationServer.set_locale(locale_code)
    GameSettings.locale = locale_code
    GameSettings.save()
    # Emit signal for any custom classes that need to refresh
    Events.locale_changed.emit(locale_code)

# On game start, restore saved locale
func _ready() -> void:
    var saved := GameSettings.locale
    if not saved.is_empty():
        TranslationServer.set_locale(saved)
```

`Control` nodes with `auto_translate_mode` update automatically when the locale changes. Custom non-Control classes must connect to the `locale_changed` signal and refresh their text manually.

Godot locale codes follow BCP 47: `en`, `es`, `ja`, `de`, `fr`, `zh_CN`, `zh_TW`, `ko`, `pt_BR`, `ar`, `he`, `ru`, `pl`.

## Japanese, Chinese, Korean fonts

The default Godot font (Noto Sans) does not include CJK characters. Japanese text will render as empty rectangles without a CJK font.

**Option 1: Fallback font** (recommended for mixed-language text):

In the Theme resource, set `Default Font` to your primary font and add a CJK font as a `Fallback` in the DynamicFont resource. Godot uses the fallback when the primary font doesn't contain a glyph.

**Option 2: Per-locale font override**:

```gdscript
func _on_locale_changed(locale: String) -> void:
    var theme := get_theme()
    match locale:
        "ja", "zh_CN", "zh_TW", "ko":
            theme.default_font = cjk_font  # NotoSansCJK or similar
        _:
            theme.default_font = latin_font
```

**Font size for CJK**: CJK characters are more complex at small sizes. If your English UI uses 14pt, increase to 16pt for Japanese/Chinese — or expose a per-locale font size override in settings.

Test with actual Japanese text, not lorem ipsum. `テスト文字列` is a quick check; a real Japanese sentence reveals spacing and line-breaking issues.

## RTL languages (Arabic, Hebrew)

Arabic, Hebrew, Farsi, and Urdu read right-to-left. Godot 4 has built-in RTL support:

```gdscript
# Detect RTL locale and set layout direction
func _on_locale_changed(locale: String) -> void:
    var is_rtl := locale in ["ar", "he", "fa", "ur"]
    get_tree().root.set_meta("is_rtl", is_rtl)
    # Apply to all relevant containers
    for label in get_tree().get_nodes_in_group("rtl_aware"):
        label.layout_direction = Control.LAYOUT_DIRECTION_RTL if is_rtl else Control.LAYOUT_DIRECTION_LTR
        label.text_direction = Control.TEXT_DIRECTION_AUTO
```

Set `layout_direction = LAYOUT_DIRECTION_LOCALE` on top-level containers to mirror the entire UI automatically. Test by temporarily setting the locale to `ar` and checking that the entire menu reads right-to-left including icons and button order.

Arabic requires a font with Arabic glyphs and proper ligature support (Noto Sans Arabic or Amiri). Arabic script connects letters — fonts without ligature tables produce broken-looking disconnected characters.

## Plural forms

English has two plural forms: "1 item" and "2 items". Russian has three (1, 2-4, 5+). Arabic has six. Godot's `tr_n()` handles this:

```gdscript
# Display "1 item" or "5 items" correctly
var text = tr_n("ITEM_COUNT_SINGULAR", "ITEM_COUNT_PLURAL", item_count)
```

CSV entry:
```
ITEM_COUNT_SINGULAR,"1 item","1 artículo","1個のアイテム","1 Gegenstand"
ITEM_COUNT_PLURAL,"{n} items","{n} artículos","{n}個のアイテム","{n} Gegenstände"
```

For languages with more than two plural forms, use `.po` / `.pot` format instead of CSV — PO files support the full `Plural-Forms` header specification.

## String overflow

German averages 30-40% longer than English. Russian 20-35%. Finnish can be 50-60% longer. Fixed-width UI elements clip translated text.

**The fix is structural — not font-size reduction.**

1. Remove `minimum_size` from all Button and Label nodes.
2. Use `HBoxContainer`, `VBoxContainer`, or `GridContainer` with `SIZE_EXPAND_FILL` flags. Containers stretch to fit content.
3. Set `Label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART` for descriptive text (tooltips, dialogue).
4. Pair wrapping with a `ScrollContainer` for fixed-height areas (quest log, inventory description pane).

```gdscript
# Verify no fixed sizes in button rows
for button in $ButtonRow.get_children():
    button.custom_minimum_size = Vector2.ZERO
    button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
```

Font-size reduction per locale is a last resort:

```gdscript
const LOCALE_FONT_SCALE := {"de": 0.9, "ru": 0.88, "fi": 0.85}

func _apply_locale_font_scale(locale: String) -> void:
    var scale := LOCALE_FONT_SCALE.get(locale, 1.0)
    get_tree().root.content_scale_factor = scale
```

## Date, time, number formats

Do not hardcode formatting:

```gdscript
# WRONG
var date_str = "%d/%d/%d" % [month, day, year]  # American; breaks for EU locales

# CORRECT — format based on locale
func format_date(year: int, month: int, day: int) -> String:
    match TranslationServer.get_locale():
        "en_US": return "%d/%d/%d" % [month, day, year]
        "de", "fr", "es": return "%02d.%02d.%d" % [day, month, year]
        "ja", "zh_CN": return "%d年%d月%d日" % [year, month, day]
        _: return "%d-%02d-%02d" % [year, month, day]  # ISO 8601 fallback

# Number separators
func format_number(n: int) -> String:
    var locale := TranslationServer.get_locale()
    if locale in ["de", "fr", "es"]:
        # European: 1.000.000 with period thousands, comma decimal
        return _format_with_separator(n, ".")
    else:
        return _format_with_separator(n, ",")
```

## Context for translators

Translators who don't play games will misinterpret context-free keys. Add comments in the CSV (a `#comment` column is ignored by Godot) or a separate context document:

```
key,en,#context
MAIN_MENU_PLAY,Play,"Button on the main menu. Starts the game."
INVENTORY_USE,Use,"Button next to an item in the inventory. Activates the item's effect."
COMBAT_CRITICAL,Critical!,"Floating text shown when a critical hit lands. Should feel impactful."
```

Gender agreement is a common trap: "a brave knight" has different adjective forms in French, Spanish, and Russian depending on whether the knight is male or female. Either provide separate keys (`TITLE_KNIGHT_MALE`, `TITLE_KNIGHT_FEMALE`) or allow translators to use conditional syntax in their translation tooling.

## PO/POT workflow for larger projects

CSV works well for up to ~500 strings. For larger projects or dedicated translator tooling, use the PO/POT format:

1. **Generate POT file**: Project → Tools → Generate POT (Godot 4 built-in).
2. **Distribute POT to translators** via Weblate, Crowdin, or POEdit.
3. **Import translated PO files** back into Godot (Project Settings → Localization → Translations → Add .po file).

PO files support plural forms, comments, contexts, and translator notes natively.

## Testing checklist

Before submitting for translation:

- **Pseudolocalization**: replace all strings with `tr_pseudo()` output — strings padded to 140% of English length with accented characters (`Þlàÿ Gàmé XXXXXXX`). This catches overflow before real translations exist.
- **Font fallback test**: temporarily set locale to `ja` and verify all text renders (no empty boxes).
- **RTL test**: set locale to `ar` and verify UI mirrors correctly.
- **Overflow test**: set locale to `de` and walk through every screen. Anything clipped?
- **Concatenation audit**: `grep` for string `+` operator used with `tr()` calls — every match is a potential word-order bug.
- **Missing key check**: Godot prints a warning when `tr("KEY")` returns the key unchanged (the key is not in any translation file). Enable warnings in debug builds.
