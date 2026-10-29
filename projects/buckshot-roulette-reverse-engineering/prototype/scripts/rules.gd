class_name RouletteRules
extends RefCounted
## Independently authored state model for the filmed reconstruction experiment.
## The caller owns inventory counts and animation; this class owns rule state.

var max_hp: int = 3
var hp: Array[int] = [3, 3]
var queue: Array[bool] = []
var turn: int = 0
var saw_active: bool = false
var cuff_skip: Array[int] = [0, 0]
var cuff_locked: Array[bool] = [false, false]
var round_index: int = 0
## -1 = unknown, 0 = blank, 1 = live, separately for each observer.
var known_shell: Array[int] = [-1, -1]
var mode: String = "story"
var finished: bool = false
var _rng := RandomNumberGenerator.new()


func reset(seed_value: int = 1) -> void:
	_rng.seed = seed_value
	max_hp = maxi(1, max_hp)
	hp = [max_hp, max_hp]
	queue.clear()
	turn = 0
	saw_active = false
	cuff_skip = [0, 0]
	cuff_locked = [false, false]
	known_shell = [-1, -1]
	round_index = 0
	finished = false


func load_shells(live: int, blank: int) -> Dictionary:
	if live < 0 or blank < 0 or live + blank < 1 or live + blank > 8:
		return _failure("invalid_shell_counts")
	var prepared: Array = []
	for index in range(live + blank):
		prepared.append(index < live)
	# Fisher-Yates uses this instance's seed, independent of visual RNG calls.
	for index in range(prepared.size() - 1, 0, -1):
		var other := _rng.randi_range(0, index)
		var saved: bool = prepared[index]
		prepared[index] = prepared[other]
		prepared[other] = saved
	return load_fixed(prepared)


func load_fixed(shells: Array) -> Dictionary:
	if shells.is_empty() or shells.size() > 8:
		return _failure("invalid_shell_counts")
	for shell in shells:
		if typeof(shell) != TYPE_BOOL:
			return _failure("shell_must_be_boolean")
	if finished:
		return _failure("match_finished")
	queue.clear()
	for shell in shells:
		queue.append(shell)
	known_shell = [-1, -1]
	cuff_skip = [0, 0]
	cuff_locked = [false, false]
	turn = 0
	round_index += 1
	# Loading does not itself consume a saw; a resolved shot does.
	return {"ok": true, "round": round_index, "remaining": queue.size(),
		"live_count": queue.count(true), "blank_count": queue.count(false)}


func shoot(target: int) -> Dictionary:
	var problem := _action_error(turn)
	if not problem.is_empty():
		return _failure(problem)
	if target < 0 or target > 1:
		return _failure("invalid_target")
	var actor := turn
	var live: bool = queue[0]
	var damage := (2 if saw_active else 1) if live else 0
	hp[target] = maxi(0, hp[target] - damage)
	_consume_shell()
	saw_active = false
	finished = hp[0] == 0 or hp[1] == 0
	var round_over := queue.is_empty()
	var self_blank := target == actor and not live
	var skipped: Array[int] = []
	if not finished and not round_over and not self_blank:
		skipped = _enter_turn(1 - actor)
	return {"ok": true, "actor": actor, "target": target, "live": live,
		"damage": damage, "keep_turn": turn == actor and not round_over and not finished,
		"self_blank": self_blank, "nextturn": turn, "round_over": round_over,
		"game_over": finished, "remaining": queue.size(), "skipped": skipped}


func use_item(actor: int, item: String) -> Dictionary:
	var problem := _action_error(actor)
	if not problem.is_empty():
		return _failure(problem)
	var outcome := {"ok": true, "actor": actor, "item": item,
		"consumed_item": true, "nextturn": turn, "round_over": false,
		"game_over": false, "remaining": queue.size()}
	match item:
		"magnifier":
			known_shell[actor] = 1 if queue[0] else 0
			outcome["revealed"] = queue[0]
		"drink":
			outcome["ejected"] = queue[0]
			_consume_shell()
			outcome["remaining"] = queue.size()
			outcome["round_over"] = queue.is_empty()
		"saw":
			if saw_active:
				return _failure("saw_already_active")
			saw_active = true
		"cuffs":
			var other := 1 - actor
			if cuff_locked[other]:
				return _failure("target_already_cuffed")
			cuff_skip[other] = 1
			cuff_locked[other] = true
			outcome["target"] = other
		"heal":
			if hp[actor] >= max_hp:
				return _failure("health_full")
			hp[actor] = mini(max_hp, hp[actor] + 1)
			outcome["healed"] = 1
		_:
			return _failure("unknown_item")
	return outcome


func choose_target(actor: int = -1) -> int:
	if actor == -1:
		actor = turn
	if not _action_error(actor).is_empty():
		return -1
	if known_shell[actor] != -1:
		return 1 - actor if known_shell[actor] == 1 else actor
	# Counts are the disclosed load minus observed consumed shells, not order.
	var live_count := queue.count(true)
	var blank_count := queue.size() - live_count
	if queue.size() == 1 or mode == "endless":
		if live_count > blank_count:
			return 1 - actor
		if blank_count > live_count:
			return actor
	return actor if _rng.randi_range(0, 1) == 0 else 1 - actor


func _consume_shell() -> void:
	queue.pop_front()
	known_shell = [-1, -1]


func _enter_turn(candidate: int) -> Array[int]:
	var skipped: Array[int] = []
	# At most two skips exist; the third visit must admit an actor.
	for attempt in range(3):
		if cuff_skip[candidate] > 0:
			cuff_skip[candidate] -= 1
			skipped.append(candidate)
			candidate = 1 - candidate
		else:
			cuff_locked[candidate] = false
			turn = candidate
			return skipped
	return skipped


func _action_error(actor: int) -> String:
	if finished:
		return "match_finished"
	if actor < 0 or actor > 1:
		return "invalid_actor"
	if actor != turn:
		return "not_your_turn"
	if queue.is_empty():
		return "empty_queue"
	return ""


func _failure(reason: String) -> Dictionary:
	return {"ok": false, "error": reason, "consumed_item": false}
