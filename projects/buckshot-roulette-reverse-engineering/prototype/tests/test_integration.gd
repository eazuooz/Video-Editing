extends SceneTree

const MAIN_SCENE = preload("res://scenes/main.tscn")
var checks: Array[Dictionary] = []
var failures: Array[String] = []
var game: Node

func _initialize() -> void:
    Engine.time_scale = 12.0
    run_checks.call_deferred()

func check_value(condition: bool, description: String) -> void:
    checks.append({"description": description, "passed": condition})
    if not condition:
        failures.append(description)
        push_error(description)

func reset_with(shells: Array) -> void:
    game.demo_mode = false
    game._new_game()
    game.rules.load_fixed(shells)
    game._refresh()

func inspect_mid_item() -> void:
    await create_timer(0.45).timeout
    check_value(game.busy and game.stage.animating, "item stays busy during visible animation")
    var before: Array = game.rules.queue.duplicate()
    await game._player_shot(1)
    check_value(game.rules.queue == before, "user shot cannot interrupt item animation")
    var round_before: int = game.rules.round_index
    game._restart_requested()
    check_value(game.rules.round_index == round_before, "reset is blocked during active item")

func run_checks() -> void:
    game = MAIN_SCENE.instantiate()
    root.add_child(game)
    await process_frame
    check_value(game.stage != null and game.hp_labels.size() == 2, "main scene initializes stage and HUD")
    check_value(game.rules.hp == [3, 3] and game.rules.queue.size() == 4, "initial state has 3 HP and four shells")

    reset_with([false, true, false, true])
    var inventory_before: int = game.inventories[0][4]
    var events_before: int = game.event_log.size()
    await game._player_item(4)
    check_value(game.inventories[0][4] == inventory_before and game.rules.hp[0] == 3, "invalid full-health heal does not consume inventory or HP")
    check_value(game.event_log.size() == events_before + 1 and not game.busy, "invalid item returns without stage animation")

    game.rules.hp[0] = 2
    await game._player_item(4)
    check_value(game.rules.hp[0] == 3 and game.inventories[0][4] == 0, "valid heal consumes one item and restores one HP")
    check_value(not game.stage.animating and not game.busy, "heal resolves only after stage animation completes")

    inspect_mid_item()
    await game._player_item(0)
    check_value(game.rules.known_shell[0] == 0 and game.rules.queue.size() == 4, "magnifier reveals blank without consuming shell")
    check_value(game.inventories[0][0] == 0 and not game.stage.animating, "magnifier consumes one item and awaits visual completion")
    await game._player_item(3)
    check_value(game.rules.cuff_skip[1] == 1 and game.inventories[0][3] == 0, "cuffs arm next opponent turn and consume inventory")
    await game._resolve_shot(0)
    check_value(game.rules.turn == 0 and game.rules.cuff_skip[1] == 1, "self blank preserves turn without consuming cuff skip")
    check_value(game.result_label.text.contains("공포탄") and not game.result_label.text.contains("수갑"), "self blank explains its own cause")
    check_value(game.rules.known_shell == [-1, -1] and game.pending_shot.is_empty(), "shot clears knowledge and pending visual result")
    await game._resolve_shot(1)
    check_value(game.rules.turn == 0 and game.rules.cuff_skip[1] == 0 and game.rules.hp[1] == 2, "cuffs skip opponent after a live shot")
    check_value(game.result_label.text.contains("수갑") and not game.result_label.text.contains("공포탄"), "cuff skip explains cuffs rather than self blank")
    await game._resolve_shot(1)
    check_value(game.rules.turn == 1 and not game.rules.cuff_locked[1], "following opponent blank hands over and releases cuffs")
    await game._dealer_cycle()
    check_value(game.rules.hp[0] == 2 and game.rules.turn == 0 and game.rules.queue.size() == 4, "dealer deduces last live shell, shoots opponent, and reloads")
    check_value(not game.busy and not game.stage.animating and not game.stage.thinking, "dealer cycle leaves no active animation or busy state")

    reset_with([false, true])
    await game._player_item(2)
    check_value(game.rules.saw_active and game.inventories[0][2] == 0, "saw consumes one and arms doubled damage")
    await game._resolve_shot(0)
    check_value(not game.rules.saw_active and game.rules.hp == [3, 3], "blank shot clears saw without damage")
    await game._player_item(1)
    check_value(game.rules.queue.size() == 4 and game.rules.turn == 0 and game.inventories[0][1] == 0, "drink of last shell reloads and retains player control")
    check_value(game.status_label.text.contains("새 실탄 2발"), "drink-reload is narrated explicitly")

    reset_with([true, false])
    game.rules.hp[1] = 1
    await game._resolve_shot(1)
    check_value(game.rules.finished and game.result_label.text.contains("플레이어 승리"), "terminal shot reports victory")
    check_value(game.target_buttons[0].disabled and game.item_buttons[0].disabled, "terminal state disables actions")
    var terminal_queue: Array = game.rules.queue.duplicate()
    await game._player_item(0)
    check_value(game.rules.queue == terminal_queue, "terminal state rejects item input")

    reset_with([false, true])
    game.demo_mode = true
    game._refresh()
    check_value(game.target_buttons[0].disabled and game.item_buttons[0].disabled, "demo disables interactive action buttons")
    var panel_was_visible: bool = game.evidence_panel.visible
    game._toggle_evidence()
    check_value(game.evidence_panel.visible == panel_was_visible, "manual evidence toggle cannot disturb demo")
    await game._player_item(0)
    await game._player_shot(0)
    game._restart_requested()
    check_value(game.rules.queue == [false, true] and game.inventories[0][0] == 1, "demo ignores manual shot, item and reset")
    await game._player_item(0, true)
    check_value(game.rules.known_shell[0] == 0 and game.inventories[0][0] == 0, "explicit automatic demo action still works")
    game.demo_mode = false
    game._new_game()
    check_value(not game.stage.animating and game.pending_shot.is_empty() and game.inventories[0] == [1,1,1,1,1], "new game resets completed scene and inventory")

    var report := {"kind": "actual_headless_scene_integration", "engine": Engine.get_version_info().string,
        "checks": checks, "failures": failures, "check_count": checks.size(),
        "headless_only": true, "visual_or_audio_quality_verified": false,
        "time_scale": Engine.time_scale, "passed": failures.is_empty()}
    var path := ProjectSettings.globalize_path("res://").path_join("../production/local/test-evidence/integration-test-report.json").simplify_path()
    DirAccess.make_dir_recursive_absolute(path.get_base_dir())
    var report_file := FileAccess.open(path, FileAccess.WRITE)
    if report_file:
        report_file.store_string(JSON.stringify(report, "  "))
    else:
        failures.append("Could not write ignored integration evidence")
        push_error("Could not write integration evidence to " + path)
    print("INTEGRATION_CHECKS ", checks.size(), " FAILURES ", failures.size())
    game.queue_free()
    game = null
    await process_frame
    await process_frame
    quit(0 if failures.is_empty() else 1)
