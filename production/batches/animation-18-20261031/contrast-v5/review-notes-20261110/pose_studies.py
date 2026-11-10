"""Build editable Unreal studies for the Ring Fit pose and ACCAD spinning kick."""
import math
from pathlib import Path
import sys

import numpy as np

from plan_observations import BATCH, HERE, ROOT, load, save


SERIES = BATCH.parent
WORK = Path('C:/Users/1/Videos/YamyamProduction/animation-review-notes-20261110')
sys.path[:0] = [str(SERIES / 'local/real-clips-v2/python-deps'), str(SERIES / 'native')]
from scipy.spatial.transform import Rotation
from pose_tools import ease, rig


SAMPLED = ('head', 'pelvis', 'upperarm_r', 'lowerarm_r', 'hand_r', 'hand_l', 'foot_r', 'foot_l')
CAMERA = {'cameraWidth': 535, 'cameraHeight': 87, 'actorSpacing': 135}


def aim_chain(pose, names, target, pole):
    world = rig.fk(pose)
    start, joint, end = (world[name][0] for name in names)
    first, second = np.linalg.norm(joint - start), np.linalg.norm(end - joint)
    delta = np.asarray(target) - start
    direction = delta / np.linalg.norm(delta)
    distance = np.clip(np.linalg.norm(delta), abs(first - second) + .2, first + second - .2)
    pole = np.asarray(pole) - np.dot(pole, direction) * direction
    pole /= np.linalg.norm(pole)
    projection = (first ** 2 - second ** 2 + distance ** 2) / (2 * distance)
    elbow = start + projection * direction + math.sqrt(first ** 2 - projection ** 2) * pole
    rig.aim(pose, *names[:2], elbow - start)
    rig.aim(pose, *names[1:], start + direction * distance - rig.fk(pose)[names[1]][0])


def warrior(head, chest, hands, wrists, hips, feet):
    pose = rig.pose_copy()
    initial = rig.WORLD
    rig.set_world(pose, 'pelvis', p=initial['pelvis'][0] + [0, 9 * hips, -15 * feet])
    torso_rotation = Rotation.from_euler('yxz', [17 * chest, -5 * chest, -11 * chest], degrees=True)
    rig.set_world(pose, 'spine_01', q=torso_rotation * initial['spine_01'][1])
    rig.set_world(pose, 'neck_01', q=Rotation.from_euler('yz', [12 * head, -12 * head], degrees=True)
                  * initial['neck_01'][1])
    for side, sign in (('r', -1), ('l', 1)):
        if hands:
            world = rig.fk(pose)
            shoulder = world[f'upperarm_{side}'][0]
            raised = world['head'][0] + [14 * sign + 3 * chest, 19, 28 - 5 * sign * chest] - shoulder
            lowered = initial[f'hand_{side}'][0] - initial[f'upperarm_{side}'][0]
            aim_chain(pose, [f'{bone}_{side}' for bone in ('upperarm', 'lowerarm', 'hand')],
                      shoulder + (1 - hands) * lowered + hands * raised, [sign, -.15, -.2])
            orientation = Rotation.from_euler('xz', [15 * hands, 18 * wrists * sign], degrees=True)
            name = f'hand_{side}'
            rig.set_world(pose, name, q=orientation * rig.fk(pose)[name][1])
        if feet or hips:
            name = f'foot_{side}'
            forward = 40 if side == 'r' else -26
            target = initial[name][0] + [sign * 6 * feet, forward * feet, 0]
            aim_chain(pose, [f'{bone}_{side}' for bone in ('thigh', 'calf', 'foot')],
                      target, [0, 1, .08])
            rig.set_world(pose, name, q=Rotation.from_euler('z', sign * 11 * feet, degrees=True) * initial[name][1])
    return pose


def sample_states(knots, states, frame):
    index = min(len(knots) - 2, max(0, int(np.searchsorted(knots, frame, side='right') - 1)))
    weight = ease((frame - knots[index]) / (knots[index + 1] - knots[index]))
    return (1 - weight) * np.asarray(states[index]) + weight * np.asarray(states[index + 1])


def build_a08():
    stages = [[0] * 6]
    for i in range(6):
        stages.append(stages[-1].copy())
        stages[-1][i] = 1
    schedules = {
        'flow': ([0, 12, 48, 88, 179], [0, 0, 1, 2, 2]),
        'edge': ([0, 12, 48, 88, 179], [2, 2, 3, 4, 4]),
        'stance': ([0, 12, 48, 88, 179], [4, 4, 5, 6, 6]),
        'overview': ([0, 12, 38, 65, 92, 119, 145, 171, 179], [0, 0, 1, 2, 3, 4, 5, 6, 6]),
    }
    for key, (times, indices) in schedules.items():
        states = [stages[i] for i in indices]
        sequences = [[warrior(*states[0])] * 181,
                     [warrior(*sample_states(times, states, i)) for i in range(181)]]
        write_study('A08', key, sequences, yaw=-43, stageTimes=times, stageIndices=indices,
                    observationFrames=[12, 88], authoring='Warrior I inspired mannequin pose, independently authored')
    finished = rig.fk(warrior(*stages[-1]))
    assert all(finished[f'hand_{side}'][0][1] > finished['head'][0][1] + 6 for side in ('r', 'l'))
    assert all(finished[f'hand_{side}'][0][2] > finished['head'][0][2] + 10 for side in ('r', 'l'))
    assert finished['foot_r'][0][1] > finished['foot_l'][0][1] + 8


def build_warrior_motion():
    neutral = warrior(0, 0, 1, 1, 1, 1)
    times = [0, 12, 87, 110, 179]
    strengths = [[0], [0], [1], [1], [0]]
    movement = []
    for frame in range(181):
        strength = float(sample_states(times, strengths, frame)[0])
        movement.append(warrior(strength, strength, 1, 1, 1, 1))
    write_study('A08-motion', 'warrior', [[neutral] * 181, movement], yaw=-64,
                observationFrames=[12, 100], authoring='Warrior I pose, fixed overhead hands and planted feet during the lean and return')
    local = WORK / 'A08-motion'
    save(local / 'study-job.json', {'episode': 'A08WarriorMotion20261110', 'keys': ['warrior'],
         'mesh': rig.D['mesh'], 'skeleton': rig.D['skeleton'], 'local': str(local)})


def bvh_frames(path):
    header, motion = path.read_text().split('MOTION')
    skeleton = []
    stack = []
    pending = None
    for line in header.splitlines():
        parts = line.split()
        if not parts:
            continue
        token = parts[0]
        if token in ('ROOT', 'JOINT', 'End'):
            pending = parts[1] if token != 'End' else stack[-1]['name'] + '_end'
        elif token == '{':
            joint = {'name': pending, 'parent': stack[-1]['name'] if stack else None, 'channels': []}
            skeleton.append(joint)
            stack.append(joint)
        elif token == '}':
            stack.pop()
        elif token == 'OFFSET':
            stack[-1]['offset'] = np.asarray(parts[1:], float)
        elif token == 'CHANNELS':
            stack[-1]['channels'] = parts[2:]
    fields = motion.strip().splitlines()
    assert abs(float(fields[1].split(':')[1]) - 1 / 30) < 1e-6
    values = np.loadtxt(fields[2:])
    assert len(values) == int(fields[0].split(':')[1])
    points, rotations = {}, {}
    cursor = 0
    for joint in skeleton:
        name, parent, channels = (joint[k] for k in ('name', 'parent', 'channels'))
        pos = np.repeat(joint['offset'][None, :], len(values), axis=0)
        euler = []
        for channel, data in zip(channels, values[:, cursor:cursor + len(channels)].T):
            axis = 'XYZ'.index(channel[0])
            if channel.endswith('position'):
                pos[:, axis] += data
            else:
                euler.append((channel[0], data))
        cursor += len(channels)
        rot = (Rotation.from_euler(''.join(axis for axis, _ in euler), np.stack([x for _, x in euler], axis=1), degrees=True)
               if euler else Rotation.identity(len(values)))
        points[name] = points[parent] + rotations[parent].apply(pos) if parent else pos
        rotations[name] = rotations[parent] * rot if parent else rot
    assert cursor == values.shape[1]
    return points


def kick_capture():
    raw = bvh_frames(WORK / 'Male2_G20_ReverseSpinCrescentRight.bvh')
    points = {name: x[:, [0, 2, 1]] * [1, -1, 1] for name, x in raw.items()}
    initial = (points['LeftUpLeg'] - points['RightUpLeg'])[:5, :2].mean(axis=0)
    initial_angle = math.degrees(math.atan2(initial[1], initial[0]))
    align = Rotation.from_euler('z', -initial_angle, degrees=True)
    points = {name: align.apply(x - points['Hips'][0]) for name, x in points.items()}
    across = points['LeftUpLeg'] - points['RightUpLeg']
    yaw = np.unwrap(np.arctan2(across[:, 1], across[:, 0]))
    return points, yaw


def kick_pose(points, yaw, frame):
    i = int(frame)
    amount = frame - i
    point = lambda n: (1 - amount) * points[n][i] + amount * points[n][min(i + 1, len(yaw) - 1)]
    angle = (1 - amount) * yaw[i] + amount * yaw[min(i + 1, len(yaw) - 1)]
    pose = rig.pose_copy()
    initial = rig.WORLD
    root = point('Hips') * [.65, .65, .85]
    rig.set_world(pose, 'pelvis', p=initial['pelvis'][0] + root,
                  q=Rotation.from_euler('z', angle) * initial['pelvis'][1])
    chains = [('spine_01', 'spine_02', 'ToSpine', 'Spine'),
              ('spine_03', 'spine_04', 'Spine', 'Spine1'),
              ('neck_01', 'head', 'Neck', 'Head')]
    for side, name in (('r', 'Right'), ('l', 'Left')):
        chains.extend((f'{bone}_{side}', f'{child}_{side}', name + source, name + next_source)
                      for bone, child, source, next_source in (
                          ('upperarm', 'lowerarm', 'Arm', 'ForeArm'), ('lowerarm', 'hand', 'ForeArm', 'Hand'),
                          ('thigh', 'calf', 'UpLeg', 'Leg'), ('calf', 'foot', 'Leg', 'Foot'),
                          ('foot', 'ball', 'Foot', 'ToeBase')))
    for bone, child, source, next_source in chains:
        if bone in pose and child in pose:
            rig.aim(pose, bone, child, point(next_source) - point(source))
    world = rig.fk(pose)
    support = min(world['ball_r'][0][2], world['ball_l'][0][2])
    position, rotation = pose['root']
    pose['root'] = (position + [0, 0, 3.2 - support], rotation)
    return pose


def build_a11():
    points, yaw = kick_capture()
    # Compare the same coiled and extended poses in the same eight output frames.
    # Frame choices below come from the kick's actual forward-kinematic landmarks.
    coil, strike = 20, 28
    sequences = []
    for side in (0, 1):
        timeline = []
        for i in range(181):
            if i <= 61:
                t = np.interp(i, [0, 61], [0, coil])
            elif i <= 69:
                t = np.interp(i, [61, 66, 69], [coil, coil, strike]) if side else np.interp(i, [61, 69], [coil, strike])
            else:
                t = np.interp(i, [69, 179], [strike, len(yaw) - 1])
            timeline.append(kick_pose(points, yaw, t))
        sequences.append(timeline)
    for frame in (0, 61, 69, 179):
        assert all(np.allclose(sequences[0][frame][name][0], sequences[1][frame][name][0]) and
                   np.allclose(sequences[0][frame][name][1].as_quat(), sequences[1][frame][name][1].as_quat())
                   for name in rig.NAMES)
    write_study('A11', 'kick', sequences, yaw=-30, observationFrames=[61, 69],
                sourceClip='ACCAD Male2 G20 Reverse Spin Crescent Right', comparisonFrames=[61, 66, 69],
                sourceEventFrames=[coil, strike], transitionFrames=8)


def write_study(ep, key, sequences, **definition):
    output = WORK / ep
    tracks = []
    evidence = []
    for label, poses in zip(('left', 'right'), sequences):
        bones = {}
        for name in rig.NAMES:
            positions = np.stack([p[name][0] for p in poses])
            quaternions = np.stack([p[name][1].as_quat() for p in poses])
            for i in range(1, len(quaternions)):
                if np.dot(quaternions[i - 1], quaternions[i]) < 0:
                    quaternions[i] *= -1
            if np.allclose(positions, positions[0]) and np.allclose(quaternions, quaternions[0]):
                positions, quaternions = positions[:1], quaternions[:1]
            bones[name] = {'p': positions.round(6).tolist(), 'q': quaternions.round(7).tolist(),
                           's': rig.B[name]['baseLocal']['s']}
        tracks.append({'side': label, 'tracks': bones})
        trace = []
        for pose in poses:
            world = rig.fk(pose)
            trace.append({n: world[n][0].round(5).tolist() for n in SAMPLED})
        evidence.append(trace)
    save(output / 'poses' / f'{key}.json', dict(CAMERA, **definition, frames=180, fps=60,
                                              animations=tracks, motionEvidence=evidence))


if __name__ == '__main__':
    if '--warrior-motion' in sys.argv:
        build_warrior_motion()
        raise SystemExit
    build_a08()
    build_a11()
    for ep, keys in {'A08': ['flow', 'edge', 'stance', 'overview'], 'A11': ['kick']}.items():
        local = WORK / ep
        save(local / 'study-job.json', {'episode': ep + 'Review20261110', 'keys': keys,
             'mesh': rig.D['mesh'], 'skeleton': rig.D['skeleton'], 'local': str(local)})
