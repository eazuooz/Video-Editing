extends Node

# Independently authored presentation. Original game's files never load here.
const Rules = preload("res://scripts/rules.gd")
const Stage = preload("res://scripts/stage.gd")
const GOLD = Color("f4ce78")
const TEAL = Color("6ee1cf")
const RED = Color("ff8790")
const WHITE = Color("edf2ed")
const MUTED = Color("aab8bb")
const ITEMS = ["magnifier", "drink", "saw", "cuffs", "heal"]
const ITEM_NAMES = ["돋보기", "배출 캔", "톱", "수갑", "회복 팩"]
var rules = Rules.new()
var stage: Node3D
var ui: Control
var title_label: Label
var status_label: Label
var result_label: Label
var hp_labels: Array[Label] = []
var shell_label: Label
var turn_label: Label
var item_buttons: Array[Button] = []
var target_buttons: Array[Button] = []
var inventories = [[1,1,1,1,1],[1,1,1,1,1]]
var busy = false
var demo_mode = false
var evidence_panel: PanelContainer
var evidence_text: Label
var audio_player: AudioStreamPlayer
var event_log: Array[Dictionary] = []
var elapsed = 0.0
var pending_shot: Dictionary = {}

func _ready():
    demo_mode = "--demo" in OS.get_cmdline_user_args()
    stage = Node3D.new()
    stage.set_script(Stage)
    add_child(stage)
    stage.visual_event.connect(_on_visual_event)
    _build_ui()
    audio_player = AudioStreamPlayer.new()
    add_child(audio_player)
    _new_game()
    if demo_mode:
        await get_tree().create_timer(1.5).timeout
        _run_demo()

func _process(delta):
    elapsed += delta

func _font(size: int, color: Color = WHITE) -> Label:
    var l = Label.new()
    var f = SystemFont.new()
    f.font_names = PackedStringArray(["Malgun Gothic", "Segoe UI"])
    l.add_theme_font_override("font", f)
    l.add_theme_font_size_override("font_size", size)
    l.add_theme_color_override("font_color", color)
    l.mouse_filter = Control.MOUSE_FILTER_IGNORE
    return l

func _place(c: Control, pos: Vector2, sz: Vector2):
    c.position = pos
    c.size = sz
    ui.add_child(c)

func _box(color: Color, border: Color = Color.TRANSPARENT) -> StyleBoxFlat:
    var s = StyleBoxFlat.new()
    s.bg_color = color
    s.border_color = border
    s.set_border_width_all(1 if border.a > 0 else 0)
    s.set_corner_radius_all(7)
    s.content_margin_left = 20
    s.content_margin_right = 20
    s.content_margin_top = 12
    s.content_margin_bottom = 12
    return s

func _button(text: String, color: Color, pos: Vector2, sz: Vector2) -> Button:
    var b = Button.new()
    b.text = text
    b.add_theme_stylebox_override("normal", _box(Color(0.025,0.06,0.075,0.94), color.darkened(.35)))
    b.add_theme_stylebox_override("hover", _box(Color(0.07,0.14,0.16,1), color))
    b.add_theme_stylebox_override("pressed", _box(Color(0.12,0.2,0.22,1), color))
    b.add_theme_stylebox_override("disabled", _box(Color(0.035,0.045,0.05,0.8), Color(0.2,0.24,0.25,.5)))
    b.add_theme_color_override("font_color", color)
    b.add_theme_color_override("font_disabled_color", Color("56686b"))
    b.add_theme_font_size_override("font_size", 25)
    var f = SystemFont.new()
    f.font_names = PackedStringArray(["Malgun Gothic", "Segoe UI"])
    b.add_theme_font_override("font", f)
    _place(b,pos,sz)
    return b

func _build_ui():
    var layer = CanvasLayer.new()
    add_child(layer)
    ui = Control.new()
    ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
    layer.add_child(ui)
    var top = ColorRect.new()
    top.color = Color(0.015,0.025,0.033,.91)
    top.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _place(top,Vector2.ZERO,Vector2(1920,150))
    title_label = _font(38,GOLD)
    title_label.text = "NEON CHAMBER"
    _place(title_label,Vector2(60,25),Vector2(600,50))
    var subtitle = _font(22,MUTED)
    subtitle.text = "얌얌코딩  /  규칙을 읽고, 새로운 외형으로 재구현"
    _place(subtitle,Vector2(62,83),Vector2(810,40))
    var kind = _font(19,TEAL)
    kind.text = "독립 제작 프로토타입  ·  원작 화면 아님"
    kind.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
    _place(kind,Vector2(1230,35),Vector2(630,35))
    _button("규칙 근거  [F2]",MUTED,Vector2(1610,86),Vector2(250,46)).pressed.connect(_toggle_evidence)
    for i in range(2):
        var h = _font(31,TEAL if i == 0 else RED)
        h.text = ""
        _place(h,Vector2(65 if i == 0 else 1435,180),Vector2(430,50))
        hp_labels.append(h)
    turn_label = _font(24,GOLD)
    turn_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    _place(turn_label,Vector2(650,169),Vector2(620,44))
    shell_label = _font(25,WHITE)
    shell_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    _place(shell_label,Vector2(570,222),Vector2(780,48))
    var footer = ColorRect.new()
    footer.color = Color(0.012,0.024,0.03,.94)
    footer.mouse_filter = Control.MOUSE_FILTER_IGNORE
    _place(footer,Vector2(0,805),Vector2(1920,275))
    status_label = _font(27,WHITE)
    _place(status_label,Vector2(62,821),Vector2(1780,43))
    result_label = _font(21,MUTED)
    _place(result_label,Vector2(62,867),Vector2(1780,37))
    for i in range(5):
        var b = _button(ITEM_NAMES[i],TEAL,Vector2(60+i*175,929),Vector2(161,62))
        b.pressed.connect(_player_item.bind(i))
        item_buttons.append(b)
    var bs = _button("내 쪽으로  [1]",TEAL,Vector2(1010,928),Vector2(325,65))
    bs.pressed.connect(_player_shot.bind(0))
    target_buttons.append(bs)
    var bd = _button("딜러 쪽으로  [2]",RED,Vector2(1350,928),Vector2(350,65))
    bd.pressed.connect(_player_shot.bind(1))
    target_buttons.append(bd)
    _button("다시  [R]",MUTED,Vector2(1720,928),Vector2(150,65)).pressed.connect(_restart_requested)
    var hint = _font(18,MUTED)
    hint.text = "아이템 Q · W · E · T · Y    |    실탄은 피해, 자신에게 공포탄이면 차례 유지    |    실험용 기본 규칙 · 온라인/저장 기능 없음"
    _place(hint,Vector2(62,1020),Vector2(1790,35))
    evidence_panel = PanelContainer.new()
    evidence_panel.add_theme_stylebox_override("panel",_box(Color(0.015,0.025,0.03,.98),GOLD))
    _place(evidence_panel,Vector2(260,280),Vector2(1400,490))
    evidence_text = _font(27,WHITE)
    evidence_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    evidence_text.text = "확인한 구조 → 독립 구현\n\n① 장전 시 탄환 배열을 만들고, 앞에서 하나씩 소비합니다.\n② 일반 사격에서는 자기 대상 공포탄이면 차례를 유지합니다. 실탄 피해는 기본 1입니다.\n③ 돋보기는 확인, 배출 캔은 소비, 수갑은 상대의 다음 차례를 건너뜁니다.\n④ 알려진 탄환은 그 정보로 판단합니다. 미확정 일반 모드 딜러는 무작위로 선택합니다.\n\n분석 근거: 설치본의 읽기 가능한 스크립트 · REA 패키지 목록\n검증 구분: 코드 근거/독립 테스트 완료 범위와 원작 플레이 대조는 별도로 기록합니다."
    evidence_panel.add_child(evidence_text)
    evidence_panel.hide()

func _toggle_evidence(automatic: bool = false):
    if demo_mode and not automatic:
        return
    evidence_panel.visible = not evidence_panel.visible

func _restart_requested():
    if not busy and not demo_mode:
        _new_game()

func _new_game():
    stage.reset_stage()
    pending_shot.clear()
    rules.reset(20261029 if demo_mode else int(Time.get_ticks_msec()))
    inventories = [[1,1,1,1,1],[1,1,1,1,1]]
    rules.load_shells(2,2)
    status_label.text = "실탄 2발, 공포탄 2발. 순서는 보이지 않습니다."
    result_label.text = "돋보기로 첫 탄환을 확인하거나, 대상을 골라 발사하세요."
    _refresh()

func _refresh():
    for i in range(2):
        hp_labels[i].text = ("플레이어   " if i == 0 else "딜러   ") + "● ".repeat(max(0,rules.hp[i])) + "○ ".repeat(max(0,rules.max_hp-rules.hp[i]))
    var lives = rules.queue.count(true)
    shell_label.text = "남은 탄환  %d    /    실탄 %d  ·  공포탄 %d" % [rules.queue.size(),lives,rules.queue.size()-lives]
    turn_label.text = "플레이어의 차례" if rules.turn == 0 else "딜러가 판단하고 있습니다"
    if rules.saw_active:
        turn_label.text += "  ·  다음 사격 피해 ×2"
    var ended = rules.hp[0] <= 0 or rules.hp[1] <= 0
    for i in range(5):
        item_buttons[i].text = ITEM_NAMES[i] + ("  ·  1" if inventories[0][i] > 0 else "  ·  0")
        item_buttons[i].disabled = demo_mode or busy or rules.turn != 0 or ended or inventories[0][i] == 0 or rules.queue.is_empty()
    for b in target_buttons:
        b.disabled = demo_mode or busy or rules.turn != 0 or ended or rules.queue.is_empty()

func _log(kind:String,data:Dictionary):
    event_log.append({"seconds":snapped(elapsed,.001),"kind":kind,"data":data.duplicate(true)})

func _tone(live:bool):
    var stream = AudioStreamWAV.new()
    stream.mix_rate = 24000
    stream.format = AudioStreamWAV.FORMAT_16_BITS
    var n = 7200 if live else 2400
    var bytes = PackedByteArray()
    bytes.resize(n*2)
    var rng = RandomNumberGenerator.new()
    rng.seed = 91
    for i in range(n):
        var t = float(i)/24000.0
        var envelope = exp(-t*(18.0 if live else 70.0))
        var signal_value = (rng.randf_range(-1,1)*.6 + sin(t*TAU*95)*.4) if live else sin(t*TAU*1050)
        bytes.encode_s16(i*2,int(clamp(signal_value*envelope*.28,-1,1)*32767))
    stream.data = bytes
    audio_player.stream = stream
    audio_player.play()

func _player_shot(target:int):
    if demo_mode:
        return
    if busy or rules.turn != 0 or rules.hp.min() <= 0:
        return
    await _resolve_shot(target)
    if not demo_mode:
        await _dealer_cycle()

func _resolve_shot(target:int):
    busy = true
    _refresh()
    var result:Dictionary = rules.shoot(target)
    if not result.get("ok",false):
        status_label.text = str(result.get("error","동작할 수 없습니다."))
        busy = false
        _refresh()
        return
    _log("shot",result)
    var actor_name = "플레이어" if result.actor == 0 else "딜러"
    status_label.text = actor_name + "가 " + ("자신" if result.actor == target else "상대") + "을 선택했습니다."
    pending_shot = result.duplicate(true)
    await stage.animate_shot(target,result.live)
    pending_shot.clear()
    await get_tree().create_timer(.35).timeout
    if rules.queue.is_empty() and rules.hp.min() > 0:
        rules.load_shells(2,2)
        status_label.text = "탄환을 모두 사용했습니다. 새 실탄 2발·공포탄 2발을 장전합니다."
        await get_tree().create_timer(.9).timeout
    busy = false
    _refresh()

func _on_visual_event(kind: String, detail: String):
    _log("visual", {"event": kind, "detail": detail})
    if kind != "shot_live" and kind != "shot_blank":
        return
    if pending_shot.is_empty():
        return
    _tone(kind == "shot_live")
    status_label.text = ("실탄!  피해 %d" % pending_shot.damage) if pending_shot.live else "공포탄. 피해는 없습니다."
    if pending_shot.game_over:
        result_label.text = "플레이어 승리 — [R]로 다시 실험하세요." if rules.hp[1] <= 0 else "딜러 승리 — [R]로 다시 실험하세요."
    elif pending_shot.round_over:
        result_label.text = "마지막 탄환을 사용했습니다. 다음 장전으로 넘어갑니다."
    elif not pending_shot.skipped.is_empty():
        result_label.text = "수갑으로 상대 차례 한 번을 건너뛰어 같은 사람이 다시 행동합니다."
    elif pending_shot.self_blank:
        result_label.text = "자신에게 공포탄 → 같은 사람이 한 번 더 선택합니다."
    else:
        result_label.text = "사격을 마치면 다음 차례로 넘어갑니다."
    _refresh()

func _player_item(index:int, automatic: bool = false):
    if index < 0 or index >= ITEMS.size() or (demo_mode and not automatic):
        return
    if busy or rules.turn != 0 or inventories[0][index] <= 0 or rules.hp.min() <= 0 or rules.queue.is_empty():
        return
    busy = true
    _refresh()
    var result:Dictionary = rules.use_item(0,ITEMS[index])
    _log("item",result)
    if result.get("ok",false):
        if result.get("consumed_item", false):
            inventories[0][index] -= 1
        match ITEMS[index]:
            "magnifier":
                status_label.text = "돋보기: 첫 탄환은 " + ("실탄입니다." if rules.known_shell[0] == 1 else "공포탄입니다.")
                result_label.text = "확인했지만 탄환은 소비하지 않았습니다. 이제 이 정보로 대상을 선택하세요."
            "drink":
                status_label.text = "첫 탄환을 밖으로 배출했습니다."
                result_label.text = "피해 없이 탄환 하나만 소비합니다. 선택권은 그대로입니다."
            "saw":
                status_label.text = "톱: 다음 사격의 실탄 피해가 2가 됩니다."
                result_label.text = "이번 발이 공포탄이어도 사격 후 효과는 끝납니다."
            "cuffs":
                status_label.text = "수갑: 딜러의 다음 차례 한 번을 건너뜁니다."
                result_label.text = "탄환 종류와 별도로, 다음 차례에 들어갈 때 확인하는 상태입니다."
            "heal":
                status_label.text = "회복 팩: 생명력을 1 회복합니다."
                result_label.text = "최대 생명력을 넘지 않습니다. 외형은 우리 실험에 맞춰 바꿨습니다."
        await stage.animate_item(ITEMS[index])
    else:
        status_label.text = "이 상태에서는 아이템을 사용할 수 없습니다."
    if rules.queue.is_empty() and rules.hp.min() > 0:
        rules.load_shells(2,2)
        status_label.text = "마지막 탄환을 배출했습니다. 새 실탄 2발·공포탄 2발을 장전합니다."
        result_label.text = "새 탄환 묶음은 플레이어의 선택으로 시작합니다."
    busy = false
    _refresh()

func _dealer_cycle():
    while rules.turn == 1 and rules.hp.min() > 0:
        busy = true
        _refresh()
        status_label.text = "딜러가 대상을 선택합니다."
        if rules.known_shell[1] != -1:
            result_label.text = "이미 확인한 탄환 정보를 사용해 대상을 고릅니다."
        elif rules.queue.size() == 1:
            result_label.text = "한 발만 남아 있어 탄환 종류를 알 수 있습니다. 그 정보로 대상을 고릅니다."
        else:
            result_label.text = "이 프로토타입의 일반 모드: 모르는 탄환을 몰래 읽지 않고 무작위로 선택합니다."
        stage.dealer_think()
        await get_tree().create_timer(1.4).timeout
        await _resolve_shot(rules.choose_target(1))

func _unhandled_key_input(event:InputEvent):
    if demo_mode:
        return
    if event is InputEventKey and event.pressed and not event.echo:
        match event.physical_keycode:
            KEY_1: _player_shot(0)
            KEY_2: _player_shot(1)
            KEY_Q: _player_item(0)
            KEY_W: _player_item(1)
            KEY_E: _player_item(2)
            KEY_T: _player_item(3)
            KEY_Y: _player_item(4)
            KEY_R: _restart_requested()
            KEY_F2: _toggle_evidence()

func _run_demo():
    # Deterministic test scenario for filming; explicitly labelled, not original gameplay.
    rules.reset(29)
    rules.load_fixed([false,true,true,false])
    _refresh()
    status_label.text = "규칙 검증 시연  /  공포탄 → 실탄 순서의 고정 테스트"
    result_label.text = "실제 코드가 실행되는 재구현입니다. 무작위 원작 플레이 장면이 아닙니다."
    await get_tree().create_timer(3).timeout
    await _player_item(0, true)
    await get_tree().create_timer(2).timeout
    await _resolve_shot(0)
    await get_tree().create_timer(2).timeout
    await _player_item(2, true)
    await get_tree().create_timer(2).timeout
    await _resolve_shot(1)
    await get_tree().create_timer(2).timeout
    await _resolve_shot(0)
    await get_tree().create_timer(2).timeout
    if rules.turn == 0:
        await _player_item(1, true)
    await get_tree().create_timer(2).timeout
    _toggle_evidence(true)
    await get_tree().create_timer(7).timeout
    var log_path = ProjectSettings.globalize_path("res://").path_join("../production/local/demo-events.json").simplify_path()
    var file = FileAccess.open(log_path,FileAccess.WRITE)
    if file:
        file.store_string(JSON.stringify(event_log,"  "))
    get_tree().quit()
