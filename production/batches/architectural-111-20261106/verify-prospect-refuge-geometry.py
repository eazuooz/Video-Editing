"""Pure analytic planning fixtures for selected06.02; never imports Unity.

These are independent geometric predictions, not captured collision/visibility
proof. Future native frame logs and actual player/mobile images must verify them.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "prospect-refuge-unity-source"
CONFIG = json.loads((SOURCE / "capture-config.json").read_text(encoding="utf-8"))


def vector(value):
    return tuple(value[axis] for axis in "xyz")


def command_at(config, frame):
    matches = [c for c in config["commands"] if c["startFrame"] <= frame < c["endFrameExclusive"]]
    if len(matches) != 1:
        raise ValueError("Every interval must have one unique command")
    return matches[0]


def predicted_player(config, frame):
    """Frame0 is before Move; advance with command f before state f+1."""
    position = list(vector(config["playerStart"]))
    for previous_frame in range(frame):
        velocity = vector(command_at(config, previous_frame)["velocity"])
        for axis in (0, 2):
            position[axis] += velocity[axis] / config["fps"]
    # Ground contact y is a prediction; actual CharacterController determines it.
    return tuple(position)


def enemy(config, time):
    start, turn_end, stop = (config[key] for key in (
        "enemyTurnStartSeconds", "enemyTurnEndSeconds", "enemyPauseStartSeconds"))
    x = config["enemyStartX"]
    speed = config["enemyWalkSpeed"]
    if time < start:
        return (x + speed * time, 0, config["enemyZ"]), 90
    turn_x = x + speed * start
    if time < turn_end:
        return (turn_x, 0, config["enemyZ"]), 90 + 180 * (time - start) / (turn_end - start)
    return (turn_x - speed * (min(time, stop) - turn_end), 0, config["enemyZ"]), 270


def aabb(center, size):
    return tuple(c - s / 2 for c, s in zip(center, size)), tuple(c + s / 2 for c, s in zip(center, size))


def intersects_segment(origin, target, bounds):
    low, high = 0.0, 1.0
    for axis in range(3):
        delta = target[axis] - origin[axis]
        if abs(delta) < 1e-12:
            if not bounds[0][axis] <= origin[axis] <= bounds[1][axis]:
                return False
            continue
        entry = (bounds[0][axis] - origin[axis]) / delta
        exit_ = (bounds[1][axis] - origin[axis]) / delta
        if entry > exit_:
            entry, exit_ = exit_, entry
        low, high = max(low, entry), min(high, exit_)
        if low > high:
            return False
    return True


def covers(config, offset):
    second = list(vector(config["secondCoverCenter"]))
    second[0] += offset
    return [aabb(vector(config["firstCoverCenter"]), vector(config["firstCoverSize"])),
            aabb(second, vector(config["secondCoverSize"]))]


def rays(config, frame, offset):
    player = predicted_player(config, frame)
    guard, yaw = enemy(config, frame / config["fps"])
    origin = (guard[0], config["enemyEyeHeight"], guard[2])
    forward = (math.sin(math.radians(yaw)), math.cos(math.radians(yaw)))
    output = []
    for key in ("headSampleHeight", "torsoSampleHeight", "hipsSampleHeight"):
        target = (player[0], config[key], player[2])
        dx, dz = target[0] - origin[0], target[2] - origin[2]
        dot = (dx * forward[0] + dz * forward[1]) / math.hypot(dx, dz)
        angle = math.degrees(math.acos(max(-1, min(1, dot))))
        blocked = any(intersects_segment(origin, target, cover) for cover in covers(config, offset))
        in_range = math.dist(origin, target) <= config["enemyRange"]
        in_fov = angle <= config["enemyHorizontalHalfFovDegrees"]
        output.append({"sample": key, "blocked": blocked, "inFov": in_fov, "inRange": in_range,
                       "seen": not blocked and in_fov and in_range, "angle": angle})
    return output


def capsule_horizontal_clearance(point, bounds, radius):
    dx = max(bounds[0][0] - point[0], 0, point[0] - bounds[1][0])
    dz = max(bounds[0][2] - point[2], 0, point[2] - bounds[1][2])
    return math.hypot(dx, dz) - radius


class GeometryFixtures(unittest.TestCase):
    def test_exact_capture_contract(self):
        self.assertEqual([CONFIG[k] for k in ("frames", "fps", "width", "height")], [600, 60, 1920, 1080])
        self.assertEqual(CONFIG["onlyChangedParameter"], "secondCoverOffsetX")

    def test_tape_is_complete_unique_and_same_for_both_modes(self):
        for frame in range(CONFIG["frames"]):
            self.assertEqual(vector(command_at(CONFIG, frame)["velocity"])[1], 0)
        def trial(offset):
            result = copy.deepcopy(CONFIG)
            for key in ("baselineSecondCoverOffsetX", "shiftedSecondCoverOffsetX"):
                result.pop(key)
            result["secondCoverOffsetX"] = offset
            return result
        a, b = trial(0), trial(3.4)
        self.assertEqual([key for key in a if a[key] != b[key]], ["secondCoverOffsetX"])

    def test_initial_state_before_any_move(self):
        self.assertEqual(predicted_player(CONFIG, 0), vector(CONFIG["playerStart"]))
        self.assertEqual(predicted_player(CONFIG, 90), vector(CONFIG["playerStart"]))
        self.assertGreater(predicted_player(CONFIG, 91)[0], 0)

    def test_exact_side_step_and_crossing_end(self):
        self.assertAlmostEqual(predicted_player(CONFIG, 165)[0], 1.6875, places=10)
        self.assertAlmostEqual(predicted_player(CONFIG, 360)[2], 1.85, places=10)
        self.assertEqual(predicted_player(CONFIG, 360), predicted_player(CONFIG, 599))
        self.assertEqual(CONFIG["frames"] - 1, 599)  #599 applied moves,600 captured states.

    def test_capsule_path_does_not_depend_on_cover_collision(self):
        for offset in (0, 3.4):
            minimum = min(capsule_horizontal_clearance(predicted_player(CONFIG, frame), box, CONFIG["capsuleRadius"])
                          for frame in range(600) for box in covers(CONFIG, offset))
            self.assertGreater(minimum, CONFIG["skinWidth"])

    def test_initial_cover_is_partial_and_facing_is_separate(self):
        samples = rays(CONFIG, 0, 0)
        self.assertEqual([row["blocked"] for row in samples], [False, True, True])
        self.assertEqual([row["inFov"] for row in samples], [False, False, False])
        self.assertFalse(any(row["seen"] for row in samples))

    def test_initial_eye_observes_outward_over_low_cover(self):
        player = predicted_player(CONFIG, 0)
        guard, _ = enemy(CONFIG, 0)
        eye = (player[0], CONFIG["cameraEyeHeight"], player[2])
        target = (guard[0], CONFIG["enemyTargetHeight"], guard[2])
        self.assertFalse(any(intersects_segment(eye, target, box) for box in covers(CONFIG, 0)))
        # Analytic camera angular bounds, not a rendered pixel/readability check.
        dx, dy, dz = (target[i] - eye[i] for i in range(3))
        vertical = math.degrees(math.atan2(dy, math.hypot(dx, dz))) + CONFIG["cameraPitchDegrees"]
        horizontal = math.degrees(math.atan2(dx, dz))
        half_vertical = CONFIG["verticalFieldOfView"] / 2
        half_horizontal = math.degrees(math.atan(math.tan(math.radians(half_vertical)) * CONFIG["width"] / CONFIG["height"]))
        self.assertLess(abs(vertical), half_vertical)
        self.assertLess(abs(horizontal), half_horizontal)
        self.assertNotEqual(CONFIG["cameraEyeHeight"], CONFIG["headSampleHeight"])

    def test_end_a_three_blocked_b_three_seen(self):
        a, b = rays(CONFIG, 599, 0), rays(CONFIG, 599, 3.4)
        self.assertTrue(all(row["blocked"] and not row["seen"] and row["inFov"] for row in a))
        self.assertTrue(all(not row["blocked"] and row["seen"] for row in b))

    def test_crossing_has_some_actual_rule_exposure_in_both_trials(self):
        for offset in (0, 3.4):
            self.assertTrue(any(any(row["seen"] for row in rays(CONFIG, frame, offset)) for frame in range(165, 360)))

    def test_patrol_continuity_at_turn_and_pause(self):
        for time in (5.0, 5.3, 6.3):
            left, _ = enemy(CONFIG, time - 1e-7)
            right, _ = enemy(CONFIG, time + 1e-7)
            self.assertLess(math.dist(left, right), 1e-5)
        self.assertEqual(enemy(CONFIG, 6.3), enemy(CONFIG, 9.9))

    def test_wrong_cover_position_is_caught(self):
        wrong = copy.deepcopy(CONFIG)
        wrong["secondCoverCenter"]["x"] += 8
        self.assertFalse(any(row["blocked"] for row in rays(wrong, 599, 0)))

    def test_implemented_physical_clock_and_layers_not_teleported_path(self):
        source = (SOURCE / "ProspectRefugeExperiment.cs").read_text(encoding="utf-8")
        builder = (SOURCE / "Editor" / "ProspectRefugeBuilder.cs").read_text(encoding="utf-8")
        self.assertIn("lastCollision=player.Move(", source)
        advance = source.split("public void AdvanceOneFrame()", 1)[1].split("void SetEnemyPose", 1)[0]
        self.assertNotIn("player.transform.position=", advance)
        self.assertLess(builder.index("camera.Render()"), builder.index("rig.AdvanceOneFrame()"))
        self.assertIn("1<<EnvironmentLayer,QueryTriggerInteraction.Ignore", source)
        self.assertIn("EnemyLayer=30", source)
        self.assertNotIn("1<<ProspectRefugeExperiment.EnemyLayer", builder.split("cullingMask=", 1)[1].split(";", 1)[0])
        self.assertIn('"command-tape.json"),tapeBytes', builder)
        self.assertIn('"states.jsonl"', builder)
        self.assertIn("hitColliderEntityId=blocked?hit.collider.GetEntityId().ToString():string.Empty", source)
        self.assertNotIn("GetInstanceID()", source)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GeometryFixtures)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({"topicId": "06.02", "testsRun": result.testsRun, "passed": result.wasSuccessful(),
                      "scope": "CPU analytic planning and source-contract fixtures only",
                      "unityCompiled": False, "nativeCaptureRun": False, "observedGameplayOrHumanDecision": False,
                      "configSHA256": hashlib.sha256((SOURCE / "capture-config.json").read_bytes()).hexdigest(),
                      "predictedFinalPlayer": predicted_player(CONFIG, 599)}, ensure_ascii=False))
    raise SystemExit(0 if result.wasSuccessful() else 1)
