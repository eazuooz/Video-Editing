extends Node3D
## Original visual stage only. Rules and interface belong to the parent game.
## Shot target: 0 = player / camera, 1 = dealer. All animations are awaitable.

signal visual_event(kind: String, detail: String)

const ASSET_DIRECTORY := "res://assets/"
const TEAL := Color("176e70")
const BRASS := Color("bd8950")
const MINT := Color("78e6c4")
const RED := Color("df543f")
const GUN_REST := Vector3(0.05, 1.12, 0.28)
const GUN_REST_ROTATION := Vector3(0.0, 0.15, 0.0)

var camera: Camera3D
var dealer: Node3D
var gun: Node3D
var head: Node3D
var hand_left: Node3D
var hand_right: Node3D
var head_rest := Vector3.ZERO
var left_rest := Vector3.ZERO
var right_rest := Vector3.ZERO
var items: Dictionary = {}
var item_rest: Dictionary = {}
var focus_lamp: OmniLight3D
var muzzle_light: OmniLight3D
var muzzle_flash: MeshInstance3D
var dealer_hit_light: OmniLight3D
var brass_mat: StandardMaterial3D
var idle_time := 0.0
var thinking := false
var animating := false
var camera_rest := Vector3(0.0, 2.9, 4.1)
var _focus_tween: Tween
var _active_tweens: Array[Tween] = []

func _ready() -> void:
    get_viewport().msaa_3d = Viewport.MSAA_4X
    _build_room()
    _build_assets()
    _build_camera_and_lighting()
    reset_stage()

func _process(delta: float) -> void:
    idle_time += delta
    if is_instance_valid(head) and not animating:
        var amount := 0.04 if thinking else 0.014
        head.rotation = head_rest + Vector3(sin(idle_time * 0.75) * 0.018, sin(idle_time * 0.92) * amount, 0.0)
    if thinking and is_instance_valid(hand_right) and not animating:
        hand_right.rotation = right_rest + Vector3(sin(idle_time * 3.0) * 0.045, 0.0, 0.0)

func _material(color: Color, metallic: float = 0.0, roughness: float = 0.5, glow: float = 0.0) -> StandardMaterial3D:
    var mat := StandardMaterial3D.new()
    mat.albedo_color = color
    mat.metallic = metallic
    mat.roughness = roughness
    if glow > 0.0:
        mat.emission_enabled = true
        mat.emission = color
        mat.emission_energy_multiplier = glow
    return mat

func _box(object_name: String, position_: Vector3, size: Vector3, mat: Material, owner_node: Node = null) -> MeshInstance3D:
    var mesh := BoxMesh.new()
    mesh.size = size
    var instance := MeshInstance3D.new()
    instance.name = object_name
    instance.mesh = mesh
    instance.material_override = mat
    instance.position = position_
    if owner_node == null: owner_node = self
    owner_node.add_child(instance)
    return instance

func _cylinder(object_name: String, position_: Vector3, radius: float, height: float, mat: Material) -> MeshInstance3D:
    var mesh := CylinderMesh.new()
    mesh.top_radius = radius
    mesh.bottom_radius = radius
    mesh.height = height
    mesh.radial_segments = 24
    var instance := MeshInstance3D.new()
    instance.name = object_name
    instance.mesh = mesh
    instance.material_override = mat
    instance.position = position_
    add_child(instance)
    return instance

func _build_room() -> void:
    var dark := _material(Color("0c141a"), 0.65, 0.46)
    var wall := _material(Color("16272b"), 0.25, 0.72)
    var floor_mat := _material(Color("101d20"), 0.45, 0.42)
    brass_mat = _material(BRASS, 0.75, 0.3)
    var teal_mat := _material(TEAL, 0.5, 0.4)
    var light_mat := _material(MINT, 0.05, 0.3, 2.0)
    _box("Floor", Vector3(0,-0.12,0), Vector3(18,.2,18), floor_mat)
    _box("Back_wall", Vector3(0,2.8,-4.4), Vector3(14,5.6,.25), wall)
    _box("Left_wall", Vector3(-6.4,2.8,0), Vector3(.25,5.6,9), wall)
    _box("Right_wall", Vector3(6.4,2.8,0), Vector3(.25,5.6,9), wall)
    for x in [-5.6,-4.2,-2.8,2.8,4.2,5.6]:
        _box("Wall_rib", Vector3(x,2.6,-4.18), Vector3(.09,5.0,.12), dark)
        _box("Panel_inset", Vector3(x+.51,2.4,-4.21), Vector3(.86,2.8,.025), teal_mat)
    for y in [.35,1.55,4.65]:
        _box("Wall_horizontal_trim", Vector3(0,y,-4.08), Vector3(12.7,.035,.055), brass_mat)
    for x in [-2.9,2.9]:
        _box("Vertical_signal", Vector3(x,2.55,-3.97), Vector3(.035,2.25,.035), light_mat)
        _box("Signal_mount", Vector3(x,2.55,-4.03), Vector3(.14,2.4,.08), dark)
        var light := OmniLight3D.new()
        light.position = Vector3(x,2.45,-3.7)
        light.light_color = MINT
        light.light_energy = .55
        light.omni_range = 3.0
        add_child(light)
    _box("Center_wall_panel", Vector3(0,2.65,-4.03), Vector3(4.7,3.0,.18), dark)
    var nameplate := Label3D.new()
    nameplate.name = "Original_title_sign"
    nameplate.text = "NEON CHAMBER"
    nameplate.font_size = 100
    nameplate.pixel_size = .0040
    nameplate.modulate = Color("ccab76")
    nameplate.outline_size = 0
    nameplate.no_depth_test = false
    nameplate.position = Vector3(0,3.55,-3.89)
    add_child(nameplate)
    var subplate := Label3D.new()
    subplate.text = "MECHANICS RECONSTRUCTION  /  D-07"
    subplate.font_size = 40
    subplate.pixel_size = .0028
    subplate.modulate = Color("60857e")
    subplate.outline_size = 0
    subplate.position = Vector3(0,3.2,-3.88)
    add_child(subplate)
    for x in [-2.0,0.0,2.0]:
        _cylinder("Ceiling_suspension", Vector3(x,4.5,-.4), .018, 2.0, brass_mat)
        _cylinder("Pendant_lamp", Vector3(x,3.52,-.4), .35, .16, dark)
        _cylinder("Pendant_diffuser", Vector3(x,3.43,-.4), .30, .025, light_mat)
        var spot := SpotLight3D.new()
        spot.position = Vector3(x,3.4,-.4)
        spot.rotation_degrees.x = -90.0
        spot.light_color = Color("ffe0a9")
        spot.light_energy = .9
        spot.spot_range = 5.0
        spot.spot_angle = 60
        spot.spot_attenuation = .65
        spot.shadow_enabled = true
        add_child(spot)
    for x in range(-4,5):
        _box("Floor_joint", Vector3(float(x)*1.5,.001,0), Vector3(.014,.004,12), dark)
    for z in range(-3,5):
        _box("Floor_joint", Vector3(0,.001,float(z)*1.5), Vector3(12,.004,.014), dark)

func _asset(asset_name: String, position_: Vector3) -> Node3D:
    var source := load(ASSET_DIRECTORY + asset_name + ".glb") as PackedScene
    if source == null:
        push_error("Missing original stage asset: " + asset_name)
        return Node3D.new()
    var instance := source.instantiate() as Node3D
    instance.name = asset_name
    instance.position = position_
    add_child(instance)
    return instance

func _build_assets() -> void:
    _asset("table", Vector3.ZERO)
    dealer = _asset("dealer", Vector3(0,.65,-1.1))
    gun = _asset("shotgun", GUN_REST)
    head = dealer.find_child("HeadPivot", true, false) as Node3D
    hand_left = dealer.find_child("LeftHandPivot", true, false) as Node3D
    hand_right = dealer.find_child("RightHandPivot", true, false) as Node3D
    if head: head_rest = head.rotation
    if hand_left: left_rest = hand_left.rotation
    if hand_right: right_rest = hand_right.rotation
    var placements := {
        "magnifier": Vector3(1.27,1.075,.32),
        "beer": Vector3(-1.47,1.075,-.06),
        "handsaw": Vector3(.94,1.075,.84),
        "handcuffs": Vector3(1.18,1.075,-.58),
        "cigarette": Vector3(-1.18,1.075,-.57)
    }
    var files := {"magnifier":"item_magnifier", "beer":"item_drink", "handsaw":"item_saw", "handcuffs":"item_cuffs", "cigarette":"item_heal"}
    for item in placements:
        items[item] = _asset(files[item], placements[item])
        item_rest[item] = placements[item]
    _asset("shell_live", Vector3(-.75,1.075,.5))
    _asset("shell_blank", Vector3(-.57,1.075,.5))
    # Detached effect meshes remain presentation cues, not inferred hitboxes.
    var flash_mesh := SphereMesh.new()
    flash_mesh.radius = .11
    flash_mesh.height = .22
    muzzle_flash = MeshInstance3D.new()
    muzzle_flash.name = "Shot_flash"
    muzzle_flash.mesh = flash_mesh
    muzzle_flash.material_override = _material(Color("ffd29d"), 0.0, .5, 4.0)
    muzzle_flash.position = Vector3(1.12,.15,0)
    gun.add_child(muzzle_flash)
    muzzle_flash.hide()
    muzzle_light = OmniLight3D.new()
    muzzle_light.position = Vector3(1.1,.15,0)
    muzzle_light.light_color = Color("ffbd6b")
    muzzle_light.omni_range = 3.5
    muzzle_light.light_energy = 0
    gun.add_child(muzzle_light)
    dealer_hit_light = OmniLight3D.new()
    dealer_hit_light.position = Vector3(0,2.1,-.4)
    dealer_hit_light.light_color = RED
    dealer_hit_light.omni_range = 2.8
    dealer_hit_light.light_energy = 0
    add_child(dealer_hit_light)

func _build_camera_and_lighting() -> void:
    camera = Camera3D.new()
    camera.name = "StageCamera"
    camera.position = camera_rest
    camera.fov = 58
    camera.near = .05
    camera.far = 40
    camera.current = true
    add_child(camera)
    camera.look_at(Vector3(0,1.25,-.4))
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("071014")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("668f8a")
    environment.ambient_light_energy = .28
    environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
    environment.glow_enabled = true
    environment.glow_intensity = .45
    environment.fog_enabled = true
    environment.fog_light_color = Color("102d31")
    environment.fog_density = .007
    var world := WorldEnvironment.new()
    world.environment = environment
    add_child(world)
    var key := OmniLight3D.new()
    key.position = Vector3(-2.5,3.4,2.0)
    key.light_color = Color("ffe1b1")
    key.light_energy = 1.25
    key.omni_range = 8
    key.shadow_enabled = true
    add_child(key)
    var fill := OmniLight3D.new()
    fill.position = Vector3(3.5,2.7,1.2)
    fill.light_color = Color("62c4b0")
    fill.light_energy = .75
    fill.omni_range = 7
    add_child(fill)
    var rim := OmniLight3D.new()
    rim.position = Vector3(-1.2,3.5,-2.9)
    rim.light_color = MINT
    rim.light_energy = .9
    rim.omni_range = 5
    add_child(rim)
    focus_lamp = OmniLight3D.new()
    focus_lamp.position = Vector3(0,1.8,.4)
    focus_lamp.light_color = Color("ffe6b7")
    focus_lamp.light_energy = .35
    focus_lamp.omni_range = 1.6
    add_child(focus_lamp)

func _tween() -> Tween:
    var tween := create_tween()
    tween.set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
    _active_tweens.append(tween)
    return tween

func animate_shot(target: int, live: bool) -> void:
    animating = true
    thinking = false
    var aim_position := Vector3(.12,1.50,.68)
    var aim_target := Vector3(0,2.12,-1.05) if target == 1 else Vector3(0,2.0,3.4)
    var aim_basis := Basis.looking_at((aim_target-aim_position).normalized(), Vector3.UP) * Basis(Vector3.UP, PI/2.0)
    var tween := _tween()
    tween.set_parallel(true)
    tween.tween_property(gun,"position",aim_position,.48)
    tween.tween_property(gun,"quaternion",aim_basis.get_rotation_quaternion(),.48)
    if head:
        tween.tween_property(head,"rotation",head_rest+Vector3(-.04,.04,0),.42)
    visual_event.emit("gun_pickup", "dealer" if target == 1 else "player")
    await tween.finished
    await get_tree().create_timer(.18).timeout
    visual_event.emit("shot_live" if live else "shot_blank", "dealer" if target == 1 else "player")
    if live:
        muzzle_flash.show()
        muzzle_light.light_energy = 2.4
        dealer_hit_light.light_energy = 1.0 if target == 1 else .35
        var recoil := _tween()
        recoil.set_parallel(true)
        recoil.tween_property(gun,"position",aim_position-(aim_target-aim_position).normalized()*.13,.07)
        recoil.tween_property(camera,"position",camera_rest+Vector3(.018,.012,.035),.07)
        if target == 1 and head:
            recoil.tween_property(head,"rotation",head_rest+Vector3(.16,0,.07),.09)
        await recoil.finished
        muzzle_flash.hide()
        muzzle_light.light_energy = 0
        var settle := _tween()
        settle.set_parallel(true)
        settle.tween_property(camera,"position",camera_rest,.20)
        settle.tween_property(dealer_hit_light,"light_energy",0.0,.22)
        await settle.finished
    else:
        var click_tween := _tween()
        click_tween.tween_property(gun,"position",aim_position+Vector3(0,.012,0),.055)
        click_tween.tween_property(gun,"position",aim_position,.08)
        await click_tween.finished
    await get_tree().create_timer(.20).timeout
    var lower := _tween()
    lower.set_parallel(true)
    lower.tween_property(gun,"position",GUN_REST,.44)
    lower.tween_property(gun,"rotation",GUN_REST_ROTATION,.44)
    if head: lower.tween_property(head,"rotation",head_rest,.44)
    await lower.finished
    animating = false

func animate_item(item: String) -> void:
    var aliases := {"drink":"beer","saw":"handsaw","heal":"cigarette","cuffs":"handcuffs","cigarettes":"cigarette"}
    var key: String = aliases.get(item.to_lower(),item.to_lower())
    if not items.has(key):
        visual_event.emit("item_unknown",key)
        return
    var prop := items[key] as Node3D
    var rest: Vector3 = item_rest[key]
    animating = true
    thinking = false
    prop.show()
    var lift := _tween()
    lift.set_parallel(true)
    lift.tween_property(prop,"position",Vector3(0,1.62,.55),.35)
    lift.tween_property(prop,"rotation",Vector3(-.15,.18,0),.35)
    lift.tween_property(focus_lamp,"light_energy",1.4,.25)
    visual_event.emit("item_pickup",key)
    await lift.finished
    if key == "handsaw":
        for index in range(3):
            var saw_motion := _tween()
            saw_motion.tween_property(prop,"position",Vector3(.16 if index%2==0 else -.16,1.48,.38),.12)
            await saw_motion.finished
    elif key == "magnifier":
        var inspect := _tween()
        inspect.tween_property(prop,"position",Vector3(.16,1.42,.28),.30)
        await inspect.finished
    elif key == "beer":
        var tilt := _tween()
        tilt.tween_property(prop,"rotation",Vector3(0,0,.55),.25)
        await tilt.finished
    elif key == "handcuffs":
        var bind := _tween()
        bind.tween_property(prop,"position",Vector3(.54,1.34,-.58),.30)
        await bind.finished
    else:
        var restore := _tween()
        restore.tween_property(prop,"rotation",Vector3(0,.55,0),.25)
        await restore.finished
    visual_event.emit("item_use",key)
    await get_tree().create_timer(.25).timeout
    var lower := _tween()
    lower.set_parallel(true)
    lower.tween_property(prop,"position",rest,.35)
    lower.tween_property(prop,"rotation",Vector3.ZERO,.35)
    lower.tween_property(focus_lamp,"light_energy",.35,.3)
    await lower.finished
    animating = false

func dealer_think() -> void:
    thinking = true
    visual_event.emit("dealer_think","")
    set_focus("dealer")

func set_focus(target: String) -> void:
    if _focus_tween and _focus_tween.is_valid(): _focus_tween.kill()
    var destinations := {"dealer":Vector3(0,2.0,-.7),"gun":Vector3(0,1.65,.3),"table":Vector3(0,1.8,0),"player":Vector3(0,1.8,.9)}
    var destination: Vector3 = destinations.get(target,Vector3(0,1.8,0))
    _focus_tween = create_tween()
    _focus_tween.tween_property(focus_lamp,"position",destination,.3)

func reset_stage() -> void:
    # Caller should reset between complete awaitable actions, not mid-shot.
    for tween in _active_tweens:
        if tween and tween.is_valid(): tween.kill()
    _active_tweens.clear()
    animating = false
    thinking = false
    if gun:
        gun.position = GUN_REST
        gun.rotation = GUN_REST_ROTATION
    if head: head.rotation = head_rest
    if hand_left: hand_left.rotation = left_rest
    if hand_right: hand_right.rotation = right_rest
    for item in items:
        items[item].position = item_rest[item]
        items[item].rotation = Vector3.ZERO
        items[item].show()
    if camera: camera.position = camera_rest
    if muzzle_flash: muzzle_flash.hide()
    if muzzle_light: muzzle_light.light_energy = 0
    if dealer_hit_light: dealer_hit_light.light_energy = 0
    if focus_lamp: focus_lamp.light_energy = .35

