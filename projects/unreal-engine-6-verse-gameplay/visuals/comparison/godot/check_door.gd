extends SceneTree

func _initialize() -> void:
    call_deferred("run_checks")

func run_checks() -> void:
    var door = load("res://Door.tscn").instantiate()
    root.add_child(door)
    for has_key in [false, true]:
        door.has_key = has_key
        door.get_node("Switch").pressed.emit()
        var degrees = rad_to_deg(door.get_node("Hinge").rotation.y)
        print(JSON.stringify({"has_key": has_key, "degrees": degrees, "engine": Engine.get_version_info().string}))
        if not is_equal_approx(degrees, 90.0 if has_key else 0.0):
            quit(1)
            return
    door.queue_free()
    quit(0)
