"""11.05 structural illustration from hash-bound actual graph/state snapshots.

No image decode, subprocess, renderer, resource reservation or speech clock.
Diagram geometry is a room graph, never a claim of native pixel visibility.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DATA = HERE / 'solution-path-composition-data-v1.py'
DATA_SHA = 'a3e8dc89206f0c188a9f818d9b07885b2fa50095848596baea33925e1d5a43ab'
CONFIG = HERE / 'solution-path-unity-source-v4/config.json'
CONFIG_SHA = '499f48570d6b2d94a7ecf8be9028d30b04591e3f0dd95d98494d116fa8612997'
if hashlib.sha256(DATA.read_bytes()).hexdigest() != DATA_SHA:
    raise ValueError('Reviewed composition data source changed')
spec = importlib.util.spec_from_file_location('solution_structure_native_data_v1', DATA)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)

LABEL = '생성 규칙 설명도 · 자체 모형'
MODES = ('construction', 'branches-a', 'branches-b', 'templates-a', 'templates-b', 'threats-a', 'threats-b', 'broken-link')


def center(room):
    d.need(type(room) is int and 0 <= room < 16, 'Actual room ID required')
    return [220 + (room % 4) * 200, 230 + (room // 4) * 165]


def adjacent(a, b):
    return abs(a // 4 - b // 4) + abs(a % 4 - b % 4) == 1


def reachable(edges, entrance, exit_room):
    seen, todo = {entrance}, [entrance]
    while todo:
        room = todo.pop()
        for edge in edges:
            other = edge['b'] if edge['a'] == room else edge['a'] if edge['b'] == room else None
            if other is not None and other not in seen:
                seen.add(other)
                todo.append(other)
    return exit_room in seen


def expected_visible(frame, mode, graph):
    count = len(graph['edges'])
    if mode != 'construction':
        return count
    main = len(graph['mandatoryRoute']) - 1
    if frame < 60:
        return 0
    if frame < 240:
        return math.floor(d.f32(d.f32((frame - 60) / 180.) * main))
    if frame < 360:
        return main + math.floor(d.f32(d.f32((frame - 240) / 120.) * (count - main)))
    return count


def graph_contract(graph):
    route, edges = graph['mandatoryRoute'], graph['edges']
    d.need(isinstance(route, list) and len(route) >= 4 and len(set(route)) == len(route)
           and all(type(v) is int and 0 <= v < 16 for v in route), 'Unique actual route rooms required')
    d.need(route[0] == graph['entrance'] and route[-1] == graph['exit']
           and route[0] // 4 == 0 and route[-1] // 4 == 3
           and all(adjacent(a, b) for a, b in zip(route, route[1:])), 'Actual derived route endpoints/adjacency differ')
    d.need(len(graph['roomRoles']) == len(graph['roomVariants']) == 16
           and all(v in ('mandatory', 'side', 'sealed') for v in graph['roomRoles'])
           and all(type(v) is int and v in (0, 1) for v in graph['roomVariants']), 'Actual16 room roles/templates required')
    keys = set()
    for edge in edges:
        a, b = edge['a'], edge['b']
        d.need(type(a) is type(b) is int and 0 <= a < b < 16 and adjacent(a, b)
               and edge['role'] in ('mandatory', 'side') and (a, b) not in keys, 'Unique reciprocal adjacent ports required')
        keys.add((a, b))
    intended = {tuple(sorted((a, b))) for a, b in zip(route, route[1:])}
    broken = tuple(sorted((graph['brokenA'], graph['brokenB'])))
    d.need(type(graph['brokenConnector']) is bool, 'Explicit broken connector state required')
    if graph['brokenConnector']:
        d.need(broken in intended and broken not in keys, 'Broken port must be absent from the actual graph')
        intended.remove(broken)
    else:
        d.need(graph['brokenA'] == graph['brokenB'] == -1, 'Unexpected broken port identity')
    d.need({(v['a'], v['b']) for v in edges if v['role'] == 'mandatory'} == intended,
           'Intended route and actual mandatory ports differ')
    for room, role in enumerate(graph['roomRoles']):
        d.need((room in route) == (role == 'mandatory'), 'Mandatory room identity differs')
        if role == 'sealed':
            d.need(not any(room in key for key in keys), 'Sealed room has an actual open port')


def build_packet(graph, state, anchors, config, inputs):
    """Pure graph/state conversion; caller verifies input bytes, never pixel rays."""
    graph_contract(graph)
    frame, mode = state['frame'], state['mode']
    d.need(type(frame) is int and 0 <= frame < 3120 and mode in MODES
           and state['appliedCommandFrame'] == frame - 1 and state['sourceKind'] == 'our-own-implementation',
           'Actual source mode/native command clock required')
    d.need(config['frames'] == 3120 and config['fps'] == 60 and config['cellSize'] == 6.0
           and graph['seed'] == config['seed'], 'Current physical configuration required')
    count = expected_visible(frame, mode, graph)
    d.need(type(state['visibleConnectorCount']) is int and state['visibleConnectorCount'] == count,
           'Actual visible port prefix differs from source generation clock')
    opened = graph['edges'][:count]
    d.need(state['modelExitConnected'] is reachable(graph['edges'], graph['entrance'], graph['exit'])
           and state['visiblePortExitConnected'] is reachable(opened, graph['entrance'], graph['exit']),
           'Actual full/current-port connectivity differs')
    exit_anchors = [v for v in anchors if v['id'] == 'derived-bottom-exit']
    exit_revealed = mode != 'construction' or frame >= 240
    d.need(len(exit_anchors) == 1 and exit_anchors[0]['active'] is exit_revealed,
           'Derived exit reveal must match actual anchor activity')
    d.need(graph['brokenConnector'] is (mode == 'broken-link'), 'Broken mode/graph mismatch')
    known = {graph['entrance']}
    for edge in opened:
        known.update((edge['a'], edge['b']))
    all_roles_revealed = mode != 'construction' or frame >= 360
    rooms = [dict(id=i, label=f'R{i:02}', center=center(i),
                  role=role if all_roles_revealed or i in known else 'unclassified',
                  templateVariant=graph['roomVariants'][i] if all_roles_revealed else None,
                  entrance=i == graph['entrance'], exit=exit_revealed and i == graph['exit'])
             for i, role in enumerate(graph['roomRoles'])]
    open_keys = {(v['a'], v['b']): v for v in opened}
    ports = []
    for a in range(16):
        for b in range(a + 1, 16):
            if adjacent(a, b):
                edge = open_keys.get((a, b))
                ports.append(dict(a=a, b=b, open=edge is not None, role=edge['role'] if edge else None,
                                  center=[(x + y) / 2 for x, y in zip(center(a), center(b))],
                                  broken=graph['brokenConnector'] and {a, b} == {graph['brokenA'], graph['brokenB']}))
    broken = graph['brokenConnector']
    route_pairs = list(zip(graph['mandatoryRoute'], graph['mandatoryRoute'][1:]))
    route = [dict(a=a, b=b, connected=tuple(sorted((a, b))) in open_keys)
             for a, b in route_pairs if broken or tuple(sorted((a, b))) in open_keys]
    p = state['playerPosition']
    d.need(all(type(p[k]) in (int, float) and math.isfinite(p[k]) for k in ('x', 'y', 'z')), 'Actual finite player position required')
    packet = dict(schemaVersion='11-05-structural-diagram-v1', physicalInputFingerprint=d.PHYSICAL,
                  mode=mode, nativeFrame=frame, sourceKind='structural-illustration-of-current-own-model',
                  sourceKindLabel=LABEL, phase=state['phase'], rooms=rooms, ports=ports, route=route,
                  routeMeaning='intended-input-only' if broken else 'currently-open-mandatory-ports',
                  routeLabel=(f'의도한 입력 경로 · R{min(graph["brokenA"], graph["brokenB"]):02}–R{max(graph["brokenA"], graph["brokenB"]):02} 닫힘'
                              if broken else '출구 연결 경로 · 현재 열린 통로'),
                  exitRevealed=exit_revealed, exitRoom=graph['exit'] if exit_revealed else None,
                  modelExitConnected=state['modelExitConnected'], currentPortExitConnected=state['visiblePortExitConnected'],
                  actualPlayerPoint=[220 + (p['x'] / config['cellSize'] + 1.5) * 200,
                                     230 + (1.5 - p['z'] / config['cellSize']) * 165],
                  exitReached=state['exitReached'], inputs=inputs, speechFrame=None,
                  actualSpeechTimingVerified=False, nativePixelVisibilityClaim=False,
                  actualPixelQaPassed=False, humanReviewed=False)
    packet['fingerprint'] = d.digest(packet)
    return packet


class NativeStructure:
    def __init__(self):
        d.need(d.sha(DATA) == DATA_SHA and d.sha(CONFIG) == CONFIG_SHA, 'Reviewed source/config changed')
        self.native = d.NativeData()
        self.config = d.read(CONFIG)
        self.graphs = {}

    def snapshot(self, mode, frame):
        record = self.native.frame(mode, frame)
        folder = Path(self.native.evidence['modeSources'][mode]['attempt']) / 'capture' / mode
        path = folder / 'generation-graph.json'
        proof = self.native.proofs[str(path.resolve())]
        d.checked(proof, d.MEDIA)
        if mode not in self.graphs:
            self.graphs[mode] = d.read(path)
        inputs = list(self.native.inputs) + [dict(path=str(Path(__file__).resolve()), sha256=d.sha(__file__)),
                                            dict(path=str(DATA), sha256=DATA_SHA), dict(path=str(CONFIG), sha256=CONFIG_SHA), proof]
        inputs += [self.native.proofs[str((folder / name).resolve())] for name in ('states.jsonl', 'projected-anchors.jsonl')]
        packet = build_packet(self.graphs[mode], record['state'], record['anchors'], self.config, inputs)
        return packet


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=MODES)
    parser.add_argument('--native-frame', type=int)
    args = parser.parse_args()
    d.need((args.mode is None) == (args.native_frame is None), 'Both actual mode and native frame required')
    if args.mode is None:
        print(json.dumps(dict(prepared=True, readyForFinalTimeline=False, actualSpeechTimingVerified=False,
                              imageDecoded=False, jobLaunched=False, reason='No source snapshot or speech clock requested')))
    else:
        print(json.dumps(NativeStructure().snapshot(args.mode, args.native_frame), ensure_ascii=False))


if __name__ == '__main__':
    main()
