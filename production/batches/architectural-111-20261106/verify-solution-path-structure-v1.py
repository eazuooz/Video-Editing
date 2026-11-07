"""Pure CPU structural-diagram tests; no images, server, renderer or resource calls."""
from __future__ import annotations
import copy, importlib.util, sys, unittest
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('solution_structure_tests', HERE / 'solution-path-structure-data-v1.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def fixture(frame=0, mode='construction'):
    route = [1, 5, 6, 7, 11, 10, 9, 8, 12, 13, 14]
    edges = [dict(a=min(a, b), b=max(a, b), role='mandatory') for a, b in zip(route, route[1:])]
    edges += [dict(a=a, b=b, role='side') for a, b in [(1, 2), (11, 15), (0, 1), (0, 4)]]
    roles = ['mandatory' if i in route else 'side' for i in range(16)]
    roles[3] = 'sealed'
    broken = mode == 'broken-link'
    if broken:
        edges = [edge for edge in edges if (edge['a'], edge['b']) != (10, 11)]
    graph = dict(seed=173, sideVariant=0, templateVariant=0, entrance=1, exit=14,
                 mandatoryRoute=route, roomRoles=roles, roomVariants=[0] * 16,
                 edges=edges, brokenConnector=broken, brokenA=11 if broken else -1, brokenB=10 if broken else -1)
    count = s.expected_visible(frame, mode, graph)
    state = dict(frame=frame, mode=mode, appliedCommandFrame=frame - 1, sourceKind='our-own-implementation',
                 visibleConnectorCount=count, modelExitConnected=not broken,
                 visiblePortExitConnected=s.reachable(edges[:count], 1, 14),
                 playerPosition=dict(x=-3., y=0., z=9.), exitReached=False, phase='fixture-only')
    anchors = [dict(id='derived-bottom-exit', active=mode != 'construction' or frame >= 240)]
    config = dict(seed=173, frames=3120, fps=60, cellSize=6.)
    inputs = [dict(path='fixture/actual-state.jsonl', sha256='a' * 64)]
    return graph, state, anchors, config, inputs


class Structure(unittest.TestCase):
    def test_four_by_four_geometry_and_safe_rail(self):
        packet = s.build_packet(*fixture(360))
        self.assertEqual([v['id'] for v in packet['rooms']], list(range(16)))
        self.assertEqual(len({tuple(v['center']) for v in packet['rooms']}), 16)
        self.assertEqual(len(packet['ports']), 24)
        for room in packet['rooms']:
            x, y = room['center']
            self.assertTrue(48 < x - 75 < x + 75 < 936)
            self.assertTrue(150 < y - 58 < y + 58 < 792)

    def test_empty_generation_grid_does_not_reveal_future_roles_or_exit(self):
        packet = s.build_packet(*fixture(0))
        self.assertEqual(packet['route'], [])
        self.assertEqual(sum(v['open'] for v in packet['ports']), 0)
        self.assertIsNone(packet['exitRoom'])
        self.assertFalse(any(v['exit'] for v in packet['rooms']))
        self.assertTrue(all(v['role'] == 'unclassified' for v in packet['rooms'] if v['id'] != 1))

    def test_exit_and_last_required_port_reveal_at_actual_frame240(self):
        before, after = s.build_packet(*fixture(239)), s.build_packet(*fixture(240))
        self.assertEqual(len(before['route']), 9)
        self.assertFalse(before['exitRevealed'])
        self.assertFalse(before['currentPortExitConnected'])
        self.assertEqual(len(after['route']), 10)
        self.assertEqual(after['exitRoom'], 14)
        self.assertTrue(after['currentPortExitConnected'])

    def test_optional_ports_and_sealed_room_follow_actual_prefix(self):
        before, after = s.build_packet(*fixture(359)), s.build_packet(*fixture(360))
        self.assertEqual(sum(v['open'] for v in before['ports']), 13)
        self.assertEqual(sum(v['open'] for v in after['ports']), 14)
        self.assertEqual(before['rooms'][3]['role'], 'unclassified')
        self.assertEqual(after['rooms'][3]['role'], 'sealed')
        self.assertEqual(after['rooms'][0]['role'], 'side')

    def test_broken_port_stays_absent_and_intended_route_is_explicit(self):
        packet = s.build_packet(*fixture(1560, 'broken-link'))
        closed = [v for v in packet['ports'] if v['broken']]
        self.assertEqual([(v['a'], v['b'], v['open']) for v in closed], [(10, 11, False)])
        self.assertEqual(packet['routeMeaning'], 'intended-input-only')
        self.assertIn('의도한 입력 경로', packet['routeLabel'])
        self.assertIn('R10–R11 닫힘', packet['routeLabel'])
        self.assertFalse(packet['modelExitConnected'])
        self.assertEqual([(v['a'], v['b']) for v in packet['route'] if not v['connected']], [(11, 10)])

    def test_lying_connectivity_or_clock_is_rejected(self):
        for field, value in [('modelExitConnected', True), ('visiblePortExitConnected', True),
                             ('appliedCommandFrame', 1560), ('visibleConnectorCount', 14)]:
            with self.subTest(field=field):
                args = fixture(1560, 'broken-link')
                args[1][field] = value
                self.assertRaises(s.d.Pending, s.build_packet, *args)

    def test_hidden_exit_cannot_be_enabled_by_arbitrary_guide(self):
        args = fixture(239)
        args[2][0]['active'] = True
        self.assertRaises(s.d.Pending, s.build_packet, *args)

    def test_missing_duplicate_and_early_exit_anchors_are_rejected(self):
        for anchors in ([], [dict(id='other', active=False)], [dict(id='derived-bottom-exit', active=False)] * 2):
            args = list(fixture(0)); args[2] = anchors
            self.assertRaises(s.d.Pending, s.build_packet, *args)

    def test_duplicate_diagonal_or_sealed_room_ports_are_rejected(self):
        for edge in (dict(a=1, b=5, role='mandatory'), dict(a=0, b=5, role='side'), dict(a=2, b=3, role='side')):
            args = fixture(360)
            args[0]['edges'].append(edge)
            self.assertRaises(s.d.Pending, s.build_packet, *args)

    def test_wrong_mode_frame_and_physical_config_are_rejected(self):
        for part, key, value in [(1, 'mode', 'other-topic'), (1, 'frame', 3120), (1, 'frame', True),
                                 (3, 'cellSize', 8.), (3, 'fps', 30), (3, 'seed', 174)]:
            with self.subTest(key=key, value=value):
                args = fixture(360); args[part][key] = value
                self.assertRaises(s.d.Pending, s.build_packet, *args)

    def test_actual_player_xz_maps_to_diagram_not_camera_projection(self):
        args = fixture(1560, 'broken-link')
        args[1]['playerPosition'] = dict(x=6.340000152587891, y=.01, z=-3.)
        packet = s.build_packet(*args)
        self.assertAlmostEqual(packet['actualPlayerPoint'][0], 731.3333384195964)
        self.assertEqual(packet['actualPlayerPoint'][1], 560.)
        self.assertFalse(packet['nativePixelVisibilityClaim'])

    def test_no_fake_speech_pixel_or_human_pass(self):
        packet = s.build_packet(*fixture(3119, 'broken-link'))
        self.assertIsNone(packet['speechFrame'])
        self.assertFalse(packet['actualSpeechTimingVerified'])
        self.assertFalse(packet['actualPixelQaPassed'])
        self.assertFalse(packet['humanReviewed'])
        self.assertEqual(packet['sourceKindLabel'], '생성 규칙 설명도 · 자체 모형')
        self.assertEqual(packet['fingerprint'], s.d.digest({k: v for k, v in packet.items() if k != 'fingerprint'}))

    def test_source_clock_prefix_for_all3120_frames(self):
        args = fixture()
        count = len(args[0]['edges'])
        values = [s.expected_visible(frame, 'construction', args[0]) for frame in range(3120)]
        self.assertEqual(values[0], 0)
        self.assertEqual(values[240], 10)
        self.assertEqual(values[360], count)
        self.assertEqual(values, sorted(values))
        self.assertTrue(all(0 <= value <= count for value in values))

    def test_actual_font_labels_fit_authored_diagram_widths(self):
        from PIL import ImageFont
        spec = s.d.read(s.d.ROOT / 'projects/shorts-leveldesign-03-02/visual-layout-v1.json')
        font_path = s.d.checked(next(v for v in spec['fontMeasurement']['fontFiles'] if Path(v['path']).name == 'NotoSansKR-VF.ttf'))
        for size, weight, width, texts in (
                (48, 700, 800, ['Solution Path (출구 연결 경로)']),
                (48, 700, 130, [f'R{i:02}' for i in range(16)]),
                (32, 500, 800, [s.LABEL]),
                (30, 700, 130, ['입구', '출구', '봉인', '옆방', '경로']),
                (34, 700, 800, [s.build_packet(*fixture(360))['routeLabel'], s.build_packet(*fixture(1560, 'broken-link'))['routeLabel']]),
                (28, 500, 800, ['초록 경로 · 청록 옆방 · 빨강 닫힘'])):
            font = ImageFont.truetype(str(font_path), size)
            font.set_variation_by_axes([weight])
            for text in texts:
                with self.subTest(text=text):
                    self.assertLessEqual(font.getlength(text), width)


if __name__ == '__main__':
    unittest.main(verbosity=2)
