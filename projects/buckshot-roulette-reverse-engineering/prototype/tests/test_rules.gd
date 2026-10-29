extends SceneTree
## Original regression cases for the independent model, not recovered game code.

const Rules = preload("res://scripts/rules.gd")
var failures: Array[String] = []
var checks: int = 0


func _initialize() -> void:
	_test_shots()
	_test_items()
	_test_cuffs()
	_test_ai_information()
	_test_random_loads()
	_test_invalid_actions()
	var result := {"suite": "independent-roulette-core", "checks": checks,
		"failures": failures, "passed": failures.is_empty()}
	print(JSON.stringify(result))
	quit(0 if failures.is_empty() else 1)


func _make(shells: Array, seed_value: int = 1):
	var rules = Rules.new()
	rules.reset(seed_value)
	_check(rules.load_fixed(shells).ok, "fixture loads")
	return rules


func _check(condition: bool, name: String) -> void:
	checks += 1
	if not condition:
		failures.append(name)
		push_error(name)


func _test_shots() -> void:
	var r = _make([false, true])
	var event: Dictionary = r.shoot(0)
	_check(event.ok and event.damage == 0 and event.keep_turn, "self blank retains action")
	_check(r.turn == 0 and r.hp == [3, 3] and r.queue == [true], "self blank exact state")
	r = _make([true, false])
	event = r.shoot(0)
	_check(event.damage == 1 and not event.keep_turn, "self live costs health and turn")
	_check(r.hp == [2, 3] and r.turn == 1, "self live exact state")
	r = _make([false, true])
	event = r.shoot(1)
	_check(event.damage == 0 and r.turn == 1, "blank aimed at opponent passes action")
	r = _make([true, false])
	event = r.shoot(1)
	_check(r.hp == [3, 2] and r.turn == 1, "live aimed at opponent")
	r = _make([false])
	event = r.shoot(0)
	_check(event.round_over and not event.keep_turn and not event.game_over, "last blank requests reload")
	r = _make([true, false])
	r.hp[1] = 1
	r.use_item(0, "saw")
	event = r.shoot(1)
	_check(r.hp[1] == 0 and event.game_over, "lethal damage clamps health")
	_check(not r.shoot(0).ok and not r.use_item(0, "drink").ok, "finished match rejects actions")


func _test_items() -> void:
	var r = _make([true, false, true])
	_check(r.use_item(0, "saw").ok and r.saw_active, "saw activates")
	_check(not r.use_item(0, "saw").ok, "saw cannot stack")
	var event: Dictionary = r.shoot(1)
	_check(event.damage == 2 and r.hp[1] == 1 and not r.saw_active, "saw shot damage and reset")
	event = r.shoot(0)
	_check(event.damage == 0 and not r.saw_active, "next blank has no saw")
	event = r.shoot(1)
	_check(event.damage == 1, "later live returns to normal damage")
	r = _make([false, true])
	r.use_item(0, "saw")
	event = r.shoot(0)
	_check(event.damage == 0 and not r.saw_active and r.turn == 0, "blank consumes saw effect")
	r = _make([true, false])
	event = r.use_item(0, "magnifier")
	_check(event.revealed and r.known_shell == [1, -1], "magnifier only informs user")
	_check(r.queue == [true, false] and r.turn == 0, "magnifier consumes no shell or turn")
	event = r.use_item(0, "drink")
	_check(event.ejected and r.queue == [false] and r.hp == [3, 3], "drink ejects without damage")
	_check(r.known_shell == [-1, -1] and r.turn == 0, "ejection invalidates old knowledge")
	event = r.use_item(0, "drink")
	_check(event.round_over and r.queue.is_empty(), "last drink requests reload")
	r = _make([true, false])
	r.use_item(0, "saw")
	r.use_item(0, "drink")
	_check(r.saw_active, "drink does not pretend to resolve a shot")
	r.hp[0] = 2
	event = r.use_item(0, "heal")
	_check(event.ok and r.hp[0] == 3 and r.turn == 0, "heal adds one without ending turn")
	_check(not r.use_item(0, "heal").ok and r.hp[0] == 3, "heal cap is validated")


func _test_cuffs() -> void:
	var r = _make([false, false, true, false])
	_check(r.use_item(0, "cuffs").ok and r.cuff_skip[1] == 1, "cuffs reserve one skipped entry")
	r.shoot(0)
	_check(r.turn == 0 and r.cuff_skip[1] == 1, "self blank does not spend opponent skip")
	var event: Dictionary = r.shoot(1)
	_check(r.turn == 0 and event.skipped == [1] and r.cuff_skip[1] == 0, "first opponent entry skipped")
	_check(not r.use_item(0, "cuffs").ok, "cannot recuff before opponent breaks free")
	event = r.shoot(1)
	_check(r.turn == 1 and not r.cuff_locked[1], "next opponent entry releases and acts")
	r.use_item(1, "cuffs")
	r.load_fixed([true, false])
	_check(r.cuff_skip == [0, 0] and r.cuff_locked == [false, false], "new load clears cuffs")


func _test_ai_information() -> void:
	var r = _make([true, false])
	r.use_item(0, "magnifier")
	_check(r.choose_target() == 1, "known live selects opponent")
	r = _make([false, true])
	r.use_item(0, "magnifier")
	_check(r.choose_target() == 0, "known blank selects self")
	for seed_value in range(64):
		var first = _make([true, true, true, false], seed_value)
		var second = _make([false, true, true, true], seed_value)
		_check(first.choose_target() == second.choose_target(), "story choice cannot peek at unknown order")
		first.mode = "endless"
		second.mode = "endless"
		_check(first.choose_target() == 1 and second.choose_target() == 1, "endless uses public majority")
	r = _make([false, false, true])
	r.mode = "endless"
	_check(r.choose_target() == 0, "endless blank majority")
	r = _make([true])
	_check(r.choose_target() == 1, "last live is deducible")
	r = _make([false])
	_check(r.choose_target() == 0, "last blank is deducible")
	var outcomes: Array[int] = []
	for seed_value in range(32):
		r = _make([true, false], seed_value)
		outcomes.append(r.choose_target())
	_check(outcomes.has(0) and outcomes.has(1), "equal unknown choices cover both targets")


func _test_random_loads() -> void:
	var first = Rules.new()
	var second = Rules.new()
	first.reset(4821)
	second.reset(4821)
	for iteration in range(12):
		first.load_shells(3, 3)
		second.load_shells(3, 3)
		_check(first.queue == second.queue, "seeded sequence reproducibility")
		_check(first.queue.size() == 6 and first.queue.count(true) == 3, "shuffle preserves composition")
	var seen: Dictionary = {}
	var live_first := 0
	for seed_value in range(256):
		first.reset(seed_value)
		first.load_shells(3, 3)
		seen[str(first.queue)] = true
		if first.queue[0]:
			live_first += 1
	_check(seen.size() >= 12, "seed range produces varied permutations")
	_check(live_first > 90 and live_first < 166, "first shell has no gross fixed-position bias")


func _test_invalid_actions() -> void:
	var r = _make([true, false])
	var before: String = JSON.stringify([r.hp, r.queue, r.turn, r.saw_active, r.cuff_skip])
	_check(not r.use_item(1, "drink").ok, "out of turn item rejected")
	_check(not r.use_item(0, "unknown").ok, "unknown item rejected")
	_check(not r.shoot(9).ok, "invalid target rejected")
	_check(not r.load_fixed([true, 1]).ok, "non boolean shell rejected")
	_check(not r.load_shells(-1, 2).ok, "negative shell count rejected")
	_check(not r.load_fixed([]).ok, "empty load rejected")
	_check(before == JSON.stringify([r.hp, r.queue, r.turn, r.saw_active, r.cuff_skip]), "invalid actions leave state intact")
	r.reset(10)
	_check(not r.shoot(0).ok and not r.use_item(0, "saw").ok and r.choose_target() == -1, "empty chamber blocks actions")
