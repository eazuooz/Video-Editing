"""Pure CPU geometry/policy tests. No image composition, decoder or renderer run."""
from __future__ import annotations
import copy, importlib.util, json, sys, unittest
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('solution_composition_test_data', HERE / 'solution-path-composition-data-v1.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def point_fixture():
    matrix = [1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1.]
    ray = dict(hit=True, hitBeforeTarget=True, hitCollider='Connector R10-R11 actual closed port')
    anchor = dict(id='closed-port-10-11', active=True, world=dict(x=0., y=0., z=0.),
                  playerViewport=dict(x=.5, y=.5, z=1.), observerViewport=dict(x=.5, y=.5, z=1.),
                  playerRay=copy.deepcopy(ray), observerRay=copy.deepcopy(ray))
    state = dict(playerVP=matrix, observerVP=matrix)
    image = dict(path=str(d.MEDIA / 'native-attempts/fixture/capture/broken-link/observer/1560.jpg'), sha256='a' * 64)
    policy = dict(method='reviewed-frame-set', mode='broken-link', camera='observer', anchorId=anchor['id'],
                  visibleFrames=[1560], allowedGuideKinds=['blocked-port-label', 'blocked-port-outline'],
                  targetSurfaceCollider=ray['hitCollider'], sourceImage=copy.deepcopy(image))
    return anchor, state, image, policy


def packet_fixture():
    panel = dict(key='construction/player/0000', mode='construction', camera='player', nativeFrame=0,
                 sourceImage=dict(path=str(d.MEDIA / 'native-attempts/fixture/capture/construction/player/0000.jpg'), sha256='b' * 64),
                 transform=d.fit(*d.LAYOUTS['single-player'][0][1:]))
    packet = dict(schemaVersion='11-05-native-composition-packet-v1', physicalInputFingerprint=d.PHYSICAL,
                  nativeFrame=0, modes=['construction'], layout='single-player', panels=[panel], commands=[],
                  purpose='explanation', catPose=None, term=None, speechFrame=None, actualSpeechTimingVerified=False)
    packet['fingerprint'] = d.digest(packet)
    return packet


class Composition(unittest.TestCase):
    def test_ab_source_kind_and_broken_intended_path_stay_explicit(self):
        source = HERE / 'composite-solution-path-frame-v1.py'
        spec = importlib.util.spec_from_file_location('solution_composer_labels_test', source)
        compositor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(compositor)
        from PIL import ImageFont
        font_spec = d.read(d.ROOT / 'projects/shorts-leveldesign-03-02/visual-layout-v1.json')
        font_path = d.checked(next(v for v in font_spec['fontMeasurement']['fontFiles'] if Path(v['path']).name == 'NotoSansKR-VF.ttf'))
        font = ImageFont.truetype(str(font_path), 36)
        font.set_variation_by_axes([700])
        for mode in ('construction', 'branches-a', 'branches-b', 'templates-a', 'templates-b', 'threats-a', 'threats-b', 'broken-link'):
            for camera in ('player', 'observer'):
                for index in (0, 1):
                    label = compositor.source_kind_label('ab-' + camera, mode, camera, index)
                    self.assertIn('자체 구현', label)
                    self.assertTrue(label.startswith('A · ' if index == 0 else 'B · '))
                    self.assertLessEqual(font.getlength(label), 800)
                    if mode == 'broken-link':
                        self.assertIn('의도한 입력 경로', label)
        label = compositor.source_kind_label('observer', 'broken-link', 'observer', 0)
        self.assertIn('의도한 입력 경로', label)
        self.assertIn('자체 구현', label)
        self.assertLessEqual(font.getlength(label), 800)

    def test_all_actual_glossary_definitions_fit_without_shrinking(self):
        from PIL import ImageFont
        narration = d.PROJECT / 'narration-final-v4.json'
        self.assertEqual(d.sha(narration), d.PINS[narration.name])
        glossary = d.read(narration)['glossary']
        spec = d.read(d.ROOT / 'projects/shorts-leveldesign-03-02/visual-layout-v1.json')
        font_row = next(v for v in spec['fontMeasurement']['fontFiles'] if Path(v['path']).name == 'NotoSansKR-VF.ttf')
        font_path = d.checked(font_row)
        heading = ImageFont.truetype(str(font_path), 48)
        heading.set_variation_by_axes([700])
        meaning = ImageFont.truetype(str(font_path), 48)
        meaning.set_variation_by_axes([500])
        self.assertEqual(len(glossary), len(d.TERM_DEFINITIONS))
        for source, (en, ko, authored) in zip(glossary, d.TERM_DEFINITIONS):
            with self.subTest(english=en):
                self.assertEqual((en, ko, ' '.join(authored)),
                                 (source['english'], source['korean'], source['plainMeaning']))
                rows = d.definition_rows(dict(presentation='definition', english=en, korean=ko, meaning=source['plainMeaning']))
                self.assertEqual(rows[0], en + ' (' + ko + ')')
                self.assertEqual(rows[1:], list(authored))
                self.assertIn(len(rows), (2, 3))
                self.assertLessEqual(heading.getlength(rows[0]), 800)
                for line in rows[1:]:
                    self.assertLessEqual(meaning.getlength(line), 800)

    def test_definition_rejects_rewritten_or_split_canonical_heading(self):
        en, ko, lines = d.TERM_DEFINITIONS[1]
        term = dict(presentation='definition', english=en, korean=ko, meaning=' '.join(lines))
        for key, replacement in (('english', 'Solution\nPath'), ('korean', '경로'),
                                 ('meaning', ' '.join(lines) + '.'), ('presentation', 'chip')):
            with self.subTest(key=key):
                bad = dict(term, **{key: replacement})
                self.assertRaises(d.Pending, d.definition_rows, bad)

    def test_native_aspect_is_preserved(self):
        t = d.fit([0, 0, 1920, 1080], [48, 410, 880, 495])
        self.assertEqual(t['rect'], [48., 410., 880., 495.])
        self.assertEqual(t['scale'], 11 / 24)

    def test_square_observer_is_contained_without_stretch(self):
        t = d.fit([420, 0, 1500, 1080], [48, 992, 880, 495])
        self.assertEqual(t['rect'], [240.5, 992., 495., 495.])
        self.assertEqual(d.mapped([.5, .5, 36], t), [488., 1239.5])

    def test_crop_and_frustum_hide_targets(self):
        t = d.fit([420, 0, 1500, 1080], [48, 410, 880, 880])
        for viewport in ([0., .5, 36], [.5, .5, -.1], [.5, 1.1, 36]):
            self.assertIsNone(d.mapped(viewport, t))

    def test_actual_float32_projection_regression(self):
        fixture = d.read(d.PROJECT / 'projection-regression-fixture-v2.json')
        sample = fixture['samples'][1]
        world = [sample['anchor']['world'][k] for k in ('x', 'y', 'z')]
        actual = [sample['anchor']['playerViewport'][k] for k in ('x', 'y')]
        self.assertEqual(d.project(sample['state']['playerVP'], world), actual)

    def test_zero_w_is_rejected(self):
        self.assertRaises(d.Pending, d.project, [0.] * 16, [0., 0., 0.])

    def test_perspective_earlier_occluder_hides_point(self):
        a, s, image, policy = point_fixture()
        self.assertEqual(d.visibility(a, s, 'player', 1560, 'broken-link', image, 'point-label', [policy]), (False, 'earlier-occluder'))
        a['playerRay']['hitBeforeTarget'] = False
        self.assertTrue(d.visibility(a, s, 'player', 1560, 'broken-link', image, 'point-label', [policy])[0])

    def test_orthographic_unblocked_segment_is_not_pixel_visibility(self):
        a, s, image, _ = point_fixture()
        a['observerRay'].update(hit=False, hitBeforeTarget=False, hitCollider='')
        self.assertEqual(d.visibility(a, s, 'observer', 1560, 'broken-link', image, 'point-label', []), (False, 'orthographic-pixel-visibility-unverified'))

    def test_exact_reviewed_surface_is_allowed_without_mutating_raw_hit(self):
        a, s, image, policy = point_fixture()
        original = copy.deepcopy(a['observerRay'])
        self.assertTrue(d.visibility(a, s, 'observer', 1560, 'broken-link', image, 'blocked-port-label', [policy])[0])
        self.assertEqual(a['observerRay'], original)

    def test_observer_override_does_not_extrapolate(self):
        for mutation in ('frame', 'mode', 'hash', 'collider', 'anchor', 'kind'):
            with self.subTest(mutation=mutation):
                a, s, image, policy = point_fixture()
                frame, mode, kind = 1560, 'broken-link', 'blocked-port-label'
                if mutation == 'frame': frame = 1561
                if mutation == 'mode': mode = 'branches-a'
                if mutation == 'hash': image['sha256'] = '0' * 64
                if mutation == 'collider': a['observerRay']['hitCollider'] = 'Other wall'
                if mutation == 'anchor': a['id'] = 'player-head'
                if mutation == 'kind': kind = 'point-label'
                self.assertFalse(d.visibility(a, s, 'observer', frame, mode, image, kind, [policy])[0])

    def test_large_cat_protects_dense_views_and_definition(self):
        for layout, modes in (('dual', ['construction']), ('observer', ['construction']), ('ab-player', ['threats-a', 'threats-b'])):
            self.assertRaises(d.Pending, d.validate_selection, layout, modes, 1000, 'hero', 'realize', None)
        d.validate_selection('single-player', ['construction'], 1000, 'hero', 'realize', dict(presentation='chip'))
        self.assertRaises(d.Pending, d.validate_selection, 'single-player', ['construction'], 1000, 'hero', 'realize', dict(presentation='definition'))

    def test_late_broken_player_has_no_automatic_hold_fallback(self):
        for frame in (2880, 3119):
            self.assertRaises(d.Pending, d.validate_selection, 'dual', ['broken-link'], frame)
        d.validate_selection('dual', ['broken-link'], 1560)
        d.validate_selection('observer', ['broken-link'], 3119)

    def test_source_change_requires_new_panel_clock_and_guide_binding(self):
        packet = packet_fixture()
        d.packet_contract(packet)
        for mutation in ('frame', 'camera', 'crop', 'source-cut'):
            with self.subTest(mutation=mutation):
                bad = copy.deepcopy(packet)
                if mutation == 'frame': bad['panels'][0]['nativeFrame'] = 1
                if mutation == 'camera': bad['panels'][0]['camera'] = 'observer'
                if mutation == 'crop': bad['panels'][0]['transform']['crop'][0] = 1
                if mutation == 'source-cut': bad['commands'] = [dict(sourcePanel='old-mode/player/0000')]
                bad['fingerprint'] = d.digest({k: v for k, v in bad.items() if k != 'fingerprint'})
                self.assertRaises(d.Pending, d.packet_contract, bad)

    def test_caption_whole_text_and_one_emphasis(self):
        cue = dict(text='연결된 방', lines=['연결된 방'], emphasis=[dict(line=0, start=0, end=2, role='term')])
        d.caption_contract(cue)
        for bad in (dict(text='다른 방', lines=['연결된 방']), dict(text='a b c', lines=['a', 'b', 'c']),
                    dict(text='연결된 방', lines=['연결된 방'], emphasis=[cue['emphasis'][0]] * 2)):
            self.assertRaises(d.Pending, d.caption_contract, bad)

    def test_ab_requires_two_distinct_modes_at_one_frame(self):
        self.assertRaises(d.Pending, d.validate_selection, 'ab-player', ['threats-a', 'threats-a'], 1658)
        d.validate_selection('ab-player', ['threats-a', 'threats-b'], 1658)

    def test_cat_cannot_cover_source_attached_target_marks(self):
        packet = packet_fixture()
        packet.update(purpose='hero', catPose='realize', commands=[dict(sourcePanel=packet['panels'][0]['key'])])
        packet['fingerprint'] = d.digest({k: v for k, v in packet.items() if k != 'fingerprint'})
        self.assertRaises(d.Pending, d.packet_contract, packet)


if __name__ == '__main__':
    unittest.main(verbosity=2)
