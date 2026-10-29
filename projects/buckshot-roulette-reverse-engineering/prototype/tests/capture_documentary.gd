extends SceneTree
## Filming harness for the independently authored prototype, not original-game evidence.
## Existing main.gd, rules.gd and stage.gd execute unchanged. No original assets load.
## Usage: Godot --path <prototype> --script res://tests/capture_documentary.gd
##   --resolution 1920x1080 --fixed-fps 60 --write-movie <local-cache>/items.avi
##   -- --scenario=items --event-log=<production/local>/items-events.json
## Scenarios: items, turns, damage, dealer, assets, all. Do not pass --demo.
## Optional --plan=<JSON> accepts {"scenarios":["items",...],"eventLog":"..."}.
## GPU render must be coordinated by the parent; this file never launches another process.

const MAIN_SCENE = preload("res://scenes/main.tscn")
const FPS: int = 60
const ALL_SCENARIOS: Array[String] = ["items", "turns", "damage", "dealer", "assets"]
const WHITE := Color("edf2ed")
const GOLD := Color("f4ce78")
const TEAL := Color("6ee1cf")
const RED := Color("ff8790")
const BLUE := Color("93bfff")
const MUTED := Color("b7c4c5")
const CAMERA_HOME := Vector3(0, 2.9, 4.1)
const LOOK_HOME := Vector3(0, 1.25, -0.4)

var game: Node
var overlay: CanvasLayer
var ui: Control
var guide: MotionGuide
var heading: Label
var step_label: Label
var detail_label: Label
var code_label: RichTextLabel
var state_labels: Array[Label] = []
var queue_tokens: Array[Label] = []
var queue_heading: Label
var scenario_label: Label
var scenarios: Array[String] = []
var active_scenario := ""
var event_path := ""
var events: Array[Dictionary] = []
var checks: Array[Dictionary] = []
var failures: Array[String] = []
var scenario_start_frame: int = 0
var capture_start_frame: int = 0
var show_fixture_queue := true
var camera_look := LOOK_HOME
var camera_move: Tween
var current_step := ""
var known_before: Array[int] = [-1, -1]


class MotionGuide extends Control:
    var camera: Camera3D
    var target: Node3D
    var tint := Color("6ee1cf")
    var offset := Vector3.ZERO
    var anchor := Vector2(250, 725)
    var phase := 0.0

    func _process(delta: float) -> void:
        phase += delta
        queue_redraw()

    func _draw() -> void:
        if not is_instance_valid(camera) or not is_instance_valid(target):
            return
        var world := target.global_position + offset
        if camera.is_position_behind(world):
            return
        var point := camera.unproject_position(world)
        if point.x < 35 or point.x > 1885 or point.y < 270 or point.y > 730:
            return
        # Editorial guide attached to our runtime object, not a detector or measured hitbox.
        var radius := 31.0 + sin(phase * 3.0) * 2.0
        draw_arc(point, radius, 0, TAU, 64, tint, 5.0, true)
        var end := point + (anchor - point).normalized() * (radius + 6.0)
        draw_line(anchor, end, tint, 4.0, true)
        draw_circle(anchor, 5.0, tint)


func _initialize() -> void:
    # 1x native motion only. Movie Maker and --fixed-fps=60 supply the capture clock.
    Engine.time_scale = 1.0
    _run.call_deferred()


func _arguments() -> bool:
    var requested := "all"
    var plan_path := ""
    for argument in OS.get_cmdline_user_args():
        if argument == "--demo":
            push_error("Do not pass --demo: that starts the separate built-in demo.")
            return false
        if argument.begins_with("--scenario="):
            requested = argument.trim_prefix("--scenario=")
        elif argument.begins_with("--event-log="):
            event_path = argument.trim_prefix("--event-log=")
        elif argument.begins_with("--plan="):
            plan_path = argument.trim_prefix("--plan=")
    if not plan_path.is_empty():
        var plan_value = JSON.parse_string(FileAccess.get_file_as_string(plan_path))
        if not plan_value is Dictionary:
            push_error("Capture plan must be a JSON object.")
            return false
        for entry in plan_value.get("scenarios", []):
            scenarios.append(str(entry))
        if event_path.is_empty():
            event_path = str(plan_value.get("eventLog", ""))
    if scenarios.is_empty():
        if requested == "all":
            scenarios.assign(ALL_SCENARIOS)
        else:
            scenarios.append(requested)
    for value in scenarios:
        if not value in ALL_SCENARIOS:
            push_error("Unknown scenario: " + value)
            return false
    var local_root := ProjectSettings.globalize_path("res://").path_join("../production/local").simplify_path().replace("\\", "/")
    if event_path.is_empty():
        event_path = local_root.path_join("documentary-capture/" + requested + "-events.json")
    event_path = event_path.simplify_path().replace("\\", "/")
    if not event_path.to_lower().begins_with(local_root.to_lower() + "/"):
        push_error("Event log must stay inside this project's production/local cache.")
        return false
    if FileAccess.file_exists(event_path):
        push_error("Capture log already exists; choose a fresh local filename.")
        return false
    return true


func _run() -> void:
    if not _arguments():
        quit(2)
        return
    game = MAIN_SCENE.instantiate()
    root.add_child(game)
    await process_frame
    game.demo_mode = true
    game.set_process_unhandled_key_input(false)
    game.ui.hide()
    game._refresh()
    _build_overlay()
    game.stage.visual_event.connect(_on_visual)
    capture_start_frame = Engine.get_process_frames()
    _mark("capture_start", {"scenarios": scenarios, "time_scale": Engine.time_scale})
    for scenario in scenarios:
        active_scenario = scenario
        scenario_start_frame = Engine.get_process_frames()
        _mark("scenario_start", {"id": scenario})
        match scenario:
            "items": await _items()
            "turns": await _turns()
            "damage": await _damage()
            "dealer": await _dealer()
            "assets": await _assets()
        var length := float(Engine.get_process_frames() - scenario_start_frame) / FPS
        _check(length < 50.0, scenario + " remains below the 50-second filming bound")
        _mark("scenario_end", {"id": scenario, "seconds_at_60fps": length})
    guide.target = null
    _mark("capture_end", {"state": _state()})
    _save_report()
    # Let the last actual result be rendered before Movie Maker finalizes its local file.
    await process_frame
    quit(0 if failures.is_empty() else 1)


func _label(text: String, point: Vector2, dimensions: Vector2, size: int, color: Color = WHITE) -> Label:
    var value := Label.new()
    value.text = text
    value.position = point
    value.size = dimensions
    var font := SystemFont.new()
    font.font_names = PackedStringArray(["Malgun Gothic", "Segoe UI"])
    value.add_theme_font_override("font", font)
    value.add_theme_font_size_override("font_size", size)
    value.add_theme_color_override("font_color", color)
    value.mouse_filter = Control.MOUSE_FILTER_IGNORE
    ui.add_child(value)
    return value


func _rect(point: Vector2, dimensions: Vector2, color: Color) -> void:
    var value := ColorRect.new()
    value.position = point
    value.size = dimensions
    value.color = color
    value.mouse_filter = Control.MOUSE_FILTER_IGNORE
    ui.add_child(value)


func _build_overlay() -> void:
    overlay = CanvasLayer.new()
    overlay.layer = 10
    root.add_child(overlay)
    ui = Control.new()
    ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
    overlay.add_child(ui)
    _rect(Vector2.ZERO, Vector2(1920, 146), Color(0.012, 0.022, 0.026, 0.96))
    _rect(Vector2(0, 150), Vector2(1920, 127), Color(0.012, 0.022, 0.026, 0.92))
    _rect(Vector2(0, 741), Vector2(1920, 151), Color(0.008, 0.018, 0.022, 0.97))
    _label("NEON CHAMBER", Vector2(54, 20), Vector2(620, 52), 42, GOLD)
    heading = _label("", Vector2(54, 78), Vector2(1280, 58), 46)
    scenario_label = _label("독립 제작 · 고정 조건 테스트", Vector2(1200, 28), Vector2(660, 48), 32, TEAL)
    scenario_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _label("재구현 코드의 실제 실행", Vector2(1320, 88), Vector2(540, 42), 30, MUTED).horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    state_labels.append(_label("", Vector2(54, 161), Vector2(550, 58), 46, TEAL))
    state_labels.append(_label("", Vector2(650, 161), Vector2(600, 58), 46, GOLD))
    state_labels.append(_label("", Vector2(1280, 161), Vector2(590, 58), 46, RED))
    queue_heading = _label("테스트 장전 순서", Vector2(54, 224), Vector2(510, 46), 32, MUTED)
    for index in range(8):
        var token := _label("", Vector2(460 + index * 108, 220), Vector2(103, 52), 37)
        queue_tokens.append(token)
    _label("자막 영역은 아래에 별도로 확보", Vector2(1338, 226), Vector2(530, 40), 22, MUTED).hide()
    step_label = _label("", Vector2(54, 750), Vector2(1805, 58), 47, GOLD)
    detail_label = _label("", Vector2(54, 820), Vector2(1260, 60), 43)
    code_label = RichTextLabel.new()
    code_label.position = Vector2(1280, 817)
    code_label.size = Vector2(590, 62)
    code_label.bbcode_enabled = true
    code_label.fit_content = false
    code_label.scroll_active = false
    code_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
    var mono := SystemFont.new()
    mono.font_names = PackedStringArray(["Cascadia Mono", "Consolas"])
    code_label.add_theme_font_override("normal_font", mono)
    code_label.add_theme_font_size_override("normal_font_size", 40)
    ui.add_child(code_label)
    guide = MotionGuide.new()
    guide.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    guide.mouse_filter = Control.MOUSE_FILTER_IGNORE
    guide.camera = game.stage.camera
    ui.add_child(guide)


func _fixture(shells: Array, actor: int = 0, seed_value: int = 29) -> void:
    if camera_move and camera_move.is_valid():
        camera_move.kill()
    game.stage.camera_rest = CAMERA_HOME
    game.stage.reset_stage()
    game.stage.camera.look_at(LOOK_HOME)
    camera_look = LOOK_HOME
    game.pending_shot.clear()
    game.busy = false
    game.rules.reset(seed_value)
    game.rules.load_fixed(shells)
    game.rules.turn = actor
    game.inventories = [[1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]
    game._refresh()
    known_before.assign(game.rules.known_shell)
    guide.target = null
    _refresh_state()
    _mark("fixture", {"seed": seed_value, "shells": shells, "starting_actor": actor,
        "explicit_test_setup": true, "state": _state()})


func _refresh_state() -> void:
    state_labels[0].text = "플레이어 체력  %d" % game.rules.hp[0]
    state_labels[1].text = ("현재 차례  플레이어" if game.rules.turn == 0 else "현재 차례  딜러")
    state_labels[2].text = "딜러 체력  %d" % game.rules.hp[1]
    queue_heading.text = ("테스트 장전 순서  →" if show_fixture_queue else "딜러가 아는 첫 탄환  →")
    for index in range(queue_tokens.size()):
        var token := queue_tokens[index]
        token.text = ""
        if show_fixture_queue and index < game.rules.queue.size():
            var live: bool = game.rules.queue[index]
            token.text = "실탄" if live else "공포"
            token.add_theme_color_override("font_color", RED if live else TEAL)
        elif not show_fixture_queue and index == 0:
            var known: int = game.rules.known_shell[1]
            token.text = "?" if known == -1 else ("실탄" if known == 1 else "공포")
            token.add_theme_color_override("font_color", MUTED if known == -1 else (RED if known == 1 else TEAL))
    if not show_fixture_queue:
        queue_tokens[2].text = "남은 %d발" % game.rules.queue.size()
        queue_tokens[2].size.x = 230
        queue_tokens[2].add_theme_color_override("font_color", MUTED)
    else:
        queue_tokens[2].size.x = 103


func _step(title: String, detail: String, code: String = "") -> void:
    current_step = title
    step_label.text = title
    detail_label.text = detail
    code_label.text = code
    _mark("teaching_step", {"title": title, "detail": detail, "code": code})


func _mark(kind: String, data: Dictionary) -> void:
    var frame := Engine.get_process_frames()
    events.append({"engine_process_frame": frame,
        "capture_relative_frame": frame - capture_start_frame,
        "capture_seconds_at_60fps": float(frame - capture_start_frame) / FPS,
        "scenario_relative_frame": frame - scenario_start_frame,
        "scenario": active_scenario, "kind": kind, "data": data.duplicate(true)})


func _state() -> Dictionary:
    return {"hp": game.rules.hp.duplicate(), "queue": game.rules.queue.duplicate(),
        "turn": game.rules.turn, "known_shell": game.rules.known_shell.duplicate(),
        "saw_active": game.rules.saw_active, "cuff_skip": game.rules.cuff_skip.duplicate(),
        "finished": game.rules.finished}


func _check(condition: bool, description: String) -> void:
    checks.append({"passed": condition, "description": description,
        "scenario": active_scenario, "engine_process_frame": Engine.get_process_frames()})
    if not condition:
        failures.append(description)
        push_error(description)


func _on_visual(kind: String, detail: String) -> void:
    _mark("visual_event", {"event": kind, "detail": detail, "step": current_step})
    if kind in ["shot_live", "shot_blank", "item_use"]:
        _refresh_state()
        _mark("visible_state", {"trigger": kind, "state": _state()})


func _focus(target: Node3D, tint: Color = TEAL, offset: Vector3 = Vector3.ZERO) -> void:
    guide.target = target
    guide.tint = tint
    guide.offset = offset


func _camera_to(position_: Vector3, look_: Vector3, seconds: float) -> void:
    var initial_position: Vector3 = game.stage.camera.position
    var initial_look := camera_look
    camera_move = game.create_tween()
    camera_move.set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
    camera_move.tween_method(func(amount: float):
        game.stage.camera.position = initial_position.lerp(position_, amount)
        camera_look = initial_look.lerp(look_, amount)
        game.stage.camera.look_at(camera_look)
        # Existing recoil restores this capture's camera rather than teleporting to a prior view.
        game.stage.camera_rest = game.stage.camera.position
    , 0.0, 1.0, seconds)
    _mark("camera_move", {"from": [initial_position.x, initial_position.y, initial_position.z],
        "to": [position_.x, position_.y, position_.z], "duration": seconds})
    await camera_move.finished


func _observe(seconds: float, purpose: String) -> void:
    # Brief reading/result comprehension, never a freeze, duplicate loop or long idle filler.
    _mark("result_reading", {"seconds": seconds, "purpose": purpose})
    await create_timer(seconds).timeout


func _item(index: int) -> void:
    var before := _state()
    await game._player_item(index, true)
    _refresh_state()
    _mark("item_complete", {"item": game.ITEMS[index], "before": before, "after": _state()})


func _shot(target: int) -> void:
    var before := _state()
    await game._resolve_shot(target)
    _refresh_state()
    _mark("shot_complete", {"target": target, "before": before, "after": _state()})


func _items() -> void:
    heading.text = "확인하는 것과 소비하는 것은 다릅니다"
    scenario_label.text = "독립 제작 · 고정 조건 테스트 01"
    show_fixture_queue = true
    _fixture([false, true, false, true])
    _step("조건: 공포탄이 맨 앞, 총 4발", "돋보기와 배출 캔을 차례로 사용합니다.")
    _focus(game.stage.gun)
    await _camera_to(Vector3(0.8, 2.6, 3.6), Vector3(0, 1.3, 0), 3.0)
    _step("① 돋보기로 첫 탄환 확인", "확인한 정보만 생깁니다.", "[color=#93bfff]peek[/color]([color=#f4ce78]0[/color])")
    _focus(game.stage.items["magnifier"])
    await _item(0)
    _check(game.rules.queue.size() == 4 and game.rules.known_shell[0] == 0, "magnifier reveals blank without consuming a shell")
    _step("4발 → 4발 · 공포탄임을 알게 됨", "같은 탄환이 아직 맨 앞에 있습니다.", "[color=#6ee1cf]known[/color] = [color=#f4ce78]blank[/color]")
    await _camera_to(Vector3(-0.4, 2.35, 3.15), Vector3(0.05, 1.18, 0.25), 3.0)
    _step("② 배출 캔으로 첫 탄환 제거", "발사하지 않고 탄환 하나를 소비합니다.", "[color=#93bfff]pop_front[/color]()")
    _focus(game.stage.items["beer"])
    await _item(1)
    _check(game.rules.queue.size() == 3 and game.rules.known_shell == [-1, -1], "drink consumes one and invalidates the earlier shell knowledge")
    _check(game.rules.hp == [3, 3] and game.rules.turn == 0, "drink preserves health and player turn")
    _step("4발 → 3발 · 체력은 그대로", "첫 탄환이 바뀌어, 확인 정보도 지워집니다.", "[color=#6ee1cf]known[/color] = [color=#b7c4c5]unknown[/color]")
    await _camera_to(Vector3(0.7, 2.7, 3.7), Vector3(0, 1.3, -0.1), 3.0)
    _step("③ 지금 맨 앞인 실탄을 발사", "고정 테스트에서 다음 탄환은 실탄입니다.", "[color=#93bfff]shoot[/color]([color=#6ee1cf]dealer[/color])")
    _focus(game.stage.gun, RED)
    await _shot(1)
    _check(game.rules.queue.size() == 2 and game.rules.hp[1] == 2, "shot after ejection uses the new front live shell")
    _step("3발 → 2발 · 딜러 체력 3 → 2", "확인과 소비를 분리해야 결과가 맞습니다.")
    await _camera_to(CAMERA_HOME, LOOK_HOME, 3.0)
    await _observe(1.0, "read the three different consequences")


func _turns() -> void:
    heading.text = "공포탄도 대상에 따라 다음 차례가 달라집니다"
    scenario_label.text = "독립 제작 · 고정 조건 테스트 02"
    show_fixture_queue = true
    _fixture([false, true, false, true])
    _step("A · 같은 공포탄을 자신에게", "탄환 종류는 같고, 대상만 바꿉니다.")
    await _camera_to(Vector3(-0.7, 2.65, 3.7), Vector3(0, 1.5, -0.15), 2.7)
    _focus(game.stage.gun)
    await _shot(0)
    _check(game.rules.turn == 0 and game.rules.hp == [3, 3], "self blank keeps the player's turn without damage")
    _step("공포탄 · 피해 0 · 플레이어 차례 유지", "다음 행동을 같은 사람이 선택합니다.", "[color=#6ee1cf]turn[/color] = [color=#f4ce78]player[/color]")
    await _camera_to(Vector3(0.7, 2.7, 3.5), Vector3(0, 1.5, -0.2), 3.0)
    _step("유지된 차례로 다음 실탄 발사", "행동 권한이 실제로 남아 있는지 확인합니다.")
    await _shot(1)
    _check(game.rules.hp[1] == 2 and game.rules.turn == 1, "retained turn permits the next live shot and then transfers")
    _step("실탄 사격 후에는 딜러 차례", "자기 대상 공포탄이라는 조건이 핵심입니다.")
    await _observe(1.5, "read the completed follow-up action")
    _fixture([false, true, false, true])
    _step("B · 처음 조건으로 되돌려, 상대에게", "같은 공포탄 · 같은 체력 · 대상만 변경")
    await _camera_to(Vector3(0.7, 2.65, 3.7), Vector3(0, 1.5, -0.15), 2.7)
    _focus(game.stage.dealer, RED, Vector3(0, 1.45, 0))
    await _shot(1)
    _check(game.rules.turn == 1 and game.rules.hp == [3, 3], "opponent blank transfers turn without damage")
    _step("공포탄 · 피해 0 · 이번에는 딜러 차례", "피해 계산과 차례 처리는 별개입니다.", "[color=#6ee1cf]turn[/color] = [color=#f4ce78]dealer[/color]")
    game.stage.dealer_think()
    await _camera_to(Vector3(0.3, 2.6, 3.05), Vector3(0, 1.9, -0.7), 3.0)
    game.stage.thinking = false
    await _observe(1.0, "compare the changed owner of the next action")


func _damage() -> void:
    heading.text = "수갑은 차례를, 톱은 다음 사격을 바꿉니다"
    scenario_label.text = "독립 제작 · 고정 조건 테스트 03"
    show_fixture_queue = true
    _fixture([true, false, true, false])
    _step("① 수갑으로 다음 딜러 차례를 묶기", "지금 피해를 주는 아이템은 아닙니다.", "[color=#6ee1cf]skip[/color] = [color=#f4ce78]1[/color]")
    _focus(game.stage.items["handcuffs"])
    await _camera_to(Vector3(-0.6, 2.5, 3.5), Vector3(0, 1.4, -0.3), 2.4)
    await _item(3)
    _step("② 톱으로 다음 사격 강화", "실탄이면 피해 2, 공포탄이면 피해 0")
    _focus(game.stage.items["handsaw"], RED)
    await _item(2)
    await _camera_to(Vector3(0.3, 2.5, 3.5), Vector3(0, 1.4, -0.2), 2.0)
    _step("③ 강화된 실탄을 딜러에게", "체력과 차례의 두 변화를 함께 확인합니다.")
    _focus(game.stage.gun, RED)
    await _shot(1)
    _check(game.rules.hp[1] == 1, "saw plus live shell produces exactly two damage")
    _check(game.rules.turn == 0 and game.rules.cuff_skip[1] == 0, "cuffs skip exactly one opponent admission")
    _check(not game.rules.saw_active, "live shot consumes saw effect")
    _step("딜러 체력 3 → 1 · 차례는 플레이어", "수갑 1회와 톱 효과가 둘 다 사용됐습니다.")
    await _camera_to(CAMERA_HOME, LOOK_HOME, 2.7)
    _step("④ 다음 공포탄은 상대에게", "이번에는 수갑 효과가 남아 있지 않습니다.")
    await _shot(1)
    _check(game.rules.turn == 1 and game.rules.hp[1] == 1, "next opponent blank transfers normally after cuffs were used")
    _step("딜러 차례로 정상 이동", "한 번 건너뛰기와 영구 차례 고정은 다릅니다.")
    await _observe(1.5, "observe that cuff state was consumed once")
    _fixture([false, true, false, true])
    _step("B · 첫 탄환만 공포탄으로 바꿔 비교", "같은 톱을 사용해도 실탄 피해는 생기지 않습니다.")
    await _camera_to(Vector3(0.6, 2.6, 3.6), Vector3(0, 1.4, -0.25), 2.5)
    _focus(game.stage.items["handsaw"], RED)
    await _item(2)
    _focus(game.stage.gun)
    await _shot(0)
    _check(game.rules.hp == [3, 3] and not game.rules.saw_active, "blank deals zero and still clears the saw effect")
    _step("공포탄 피해 0 · 톱 효과는 종료", "강화 효과는 다음 사격 한 번에 적용됩니다.", "[color=#6ee1cf]damage[/color] = [color=#f4ce78]0[/color]")
    await _camera_to(CAMERA_HOME, LOOK_HOME, 3.0)


func _dealer_reveal() -> void:
    game.busy = true
    var result: Dictionary = game.rules.use_item(1, "magnifier")
    _mark("dealer_item", result)
    if result.get("consumed_item", false):
        game.inventories[1][0] -= 1
    await game.stage.animate_item("magnifier")
    game.busy = false
    _refresh_state()


func _dealer_decide() -> int:
    game.stage.dealer_think()
    _focus(game.stage.head, GOLD)
    await _camera_to(Vector3(0.4, 2.65, 3.15), Vector3(0, 1.85, -0.65), 1.6)
    # Only this real return value determines the pictured choice. No prewritten random result.
    var known: int = game.rules.known_shell[1]
    var selected: int = game.rules.choose_target(1)
    _mark("dealer_decision", {"known_before": known, "selected": selected,
        "mode": game.rules.mode, "queue_count": game.rules.queue.size(),
        "basis": "revealed_shell" if known != -1 else "actual_seeded_random_return"})
    _step("실제 선택: " + ("딜러 자신" if selected == 1 else "상대 플레이어"),
        "확인 정보로 선택" if known != -1 else "미확인 상태의 일반 모드 선택 1회",
        "[color=#93bfff]choose_target[/color]()")
    await _shot(selected)
    return selected


func _dealer() -> void:
    heading.text = "딜러의 판단에도 알고 있는 정보가 필요합니다"
    scenario_label.text = "독립 제작 · 고정 조건 테스트 04"
    show_fixture_queue = false
    _fixture([false, true, true, false], 1, 41)
    _step("A · 돋보기로 공포탄을 확인한 딜러", "첫 탄환 정보가 ?에서 공포탄으로 바뀝니다.")
    _focus(game.stage.items["magnifier"])
    await _dealer_reveal()
    await _observe(1.2, "read the revealed information available to this actor")
    var blank_target := await _dealer_decide()
    _check(blank_target == 1 and game.rules.turn == 1, "dealer uses known blank on itself and keeps turn")
    _step("확인한 공포탄 → 자신에게 · 피해 0", "탄환을 쓰면 방금 확인한 정보도 사라집니다.")
    await _camera_to(CAMERA_HOME, LOOK_HOME, 2.2)
    _fixture([true, false, true, false], 1, 43)
    _step("B · 이번에는 실탄을 확인한 딜러", "동일한 판단 함수에 다른 정보가 들어갑니다.")
    _focus(game.stage.items["magnifier"], RED)
    await _dealer_reveal()
    await _observe(1.2, "read the new revealed input")
    var live_target := await _dealer_decide()
    _check(live_target == 0 and game.rules.hp[0] == 2, "dealer uses known live shell on opponent")
    _step("확인한 실탄 → 상대에게 · 피해 1", "보여준 정보와 실제 선택을 연결할 수 있습니다.")
    await _camera_to(CAMERA_HOME, LOOK_HOME, 2.2)
    for trial in range(3):
        _fixture([false, true, false, true], 1, 53 + trial)
        _step("C-%d · 미확인 탄환, 일반 모드" % (trial + 1), "? 상태에서 실제 함수의 반환값을 기록합니다.", "[color=#6ee1cf]known[/color] = [color=#b7c4c5]unknown[/color]")
        _check(game.rules.known_shell[1] == -1, "unknown dealer trial starts without revealed shell knowledge")
        var target := await _dealer_decide()
        _check(target in [0, 1], "unknown dealer returns a valid actual target")
        _step("이번 실행의 결과: " + ("자신" if target == 1 else "상대"), "미확인 상태의 실제 선택을 하나씩 기록합니다.")
        await _camera_to(CAMERA_HOME, LOOK_HOME, 1.6)
    guide.target = null


func _assets() -> void:
    heading.text = "같은 규칙에, 우리가 만든 새로운 외형을 연결합니다"
    scenario_label.text = "독립 제작 · 직접 만든 모델"
    show_fixture_queue = true
    _fixture([false, true, false, true])
    _step("테이블 · 조명 · 로봇 · 도구", "모든 모델은 이 실험을 위해 직접 제작했습니다.")
    await _camera_to(Vector3(2.4, 2.7, 3.0), Vector3(0, 1.4, -0.2), 4.0)
    _step("머리와 손을 별도 관절로 구성", "생각하는 동작에 머리와 손이 함께 반응합니다.")
    game.stage.dealer_think()
    _focus(game.stage.head, GOLD)
    await _camera_to(Vector3(1.55, 2.7, 1.75), Vector3(0, 1.98, -0.85), 3.6)
    _focus(game.stage.hand_right, TEAL)
    await _camera_to(Vector3(-1.0, 2.5, 1.9), Vector3(0, 1.55, -0.7), 3.4)
    game.stage.thinking = false
    _step("총열 · 펌프 · 개머리판", "총을 집고, 겨누고, 내려놓는 동작을 연결합니다.")
    _focus(game.stage.gun, GOLD)
    await _camera_to(Vector3(1.7, 2.25, 2.7), Vector3(0, 1.25, 0.15), 3.5)
    await _shot(0)
    _step("도구의 모양과 기능을 함께 확인", "돋보기는 집어 들어 첫 탄환을 확인합니다.")
    _focus(game.stage.items["magnifier"])
    await _camera_to(Vector3(-1.7, 2.25, 2.6), Vector3(0, 1.25, 0.2), 3.1)
    await _item(0)
    _step("회복 팩도 같은 규칙에 연결", "테스트 체력을 2로 설정한 뒤 1을 회복합니다.")
    game.rules.hp[0] = 2
    _refresh_state()
    _mark("fixture_health_adjustment", {"actor": 0, "hp": 2, "explicit_test_setup": true})
    _focus(game.stage.items["cigarette"])
    await _item(4)
    _check(game.rules.hp[0] == 3, "original healing packet has working restore animation and rule consequence")
    _step("모델 · 애니메이션 · 규칙이 한 장면에서 동작", "새 외형 위에서도 확인한 동작을 재현합니다.")
    guide.target = null
    await _camera_to(Vector3(-2.2, 2.8, 3.2), Vector3(0, 1.5, -0.3), 3.8)
    await _camera_to(CAMERA_HOME, LOOK_HOME, 3.2)


func _save_report() -> void:
    var source_hashes := {}
    for source in ["res://scripts/main.gd", "res://scripts/rules.gd", "res://scripts/stage.gd", "res://tests/capture_documentary.gd"]:
        source_hashes[source] = FileAccess.get_sha256(source)
    var report := {"kind": "original_prototype_documentary_harness_run",
        "engine": Engine.get_version_info().string,
        "renderer": ProjectSettings.get_setting("rendering/renderer/rendering_method"),
        "viewport": [root.size.x, root.size.y], "fps_required": FPS,
        "time_scale": Engine.time_scale, "source_hashes": source_hashes,
        "scenarios": scenarios, "events": events, "checks": checks, "failures": failures,
        "passed": failures.is_empty(), "complete": true,
        "timing_basis": "engine_process_frame; use --fixed-fps 60; validate against encoded Movie Maker frames",
        "headless_only": DisplayServer.get_name() == "headless", "video_file_verified": false,
        "visual_quality_human_reviewed": false, "original_game_runtime_evidence": false,
        "classification": "independently authored implementation; selected fixed test fixtures",
        "unknown_dealer": "displayed choices are real seeded choose_target() returns, not original-game measurements",
        "no_loop_no_speed_change_no_freeze": true,
        "original_files_read_or_modified": false}
    DirAccess.make_dir_recursive_absolute(event_path.get_base_dir())
    var report_file := FileAccess.open(event_path, FileAccess.WRITE)
    if report_file:
        report_file.store_string(JSON.stringify(report, "  "))
    else:
        failures.append("Could not write event report: " + event_path)
        push_error(failures[-1])
    print("DOCUMENTARY_CAPTURE_CHECKS ", checks.size(), " FAILURES ", failures.size(), " LOG ", event_path)
