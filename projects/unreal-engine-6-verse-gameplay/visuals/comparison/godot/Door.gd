extends Node3D

var has_key := false

func _ready() -> void:
    $Switch.pressed.connect(_on_switch_pressed)

func _on_switch_pressed() -> void:
    if has_key:
        $Hinge.rotation.y = deg_to_rad(90.0)
