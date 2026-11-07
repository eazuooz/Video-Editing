"""CPU-only actual-row projection regression; never imports the native controller.

Default tests use the two portable, hash-pinned actual JSON samples. Explicit
--attempt additionally rechecks every projection/depth/ray record from that same
preserved capture. This is neither a capture/pixel pass nor a recovery command.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
import math
import struct
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / 'projects/shorts-leveldesign-11-05/projection-regression-fixture-v2.json'
OLD_SHA = '57eeddcbea57cc9e12d2cf1558f98c3771c874f097b0974e706799fce144b9d4'


class Pending(RuntimeError):
    pass


def need(value, reason):
    if not value:
        raise Pending(reason)


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf8')).hexdigest()


def fixture_and_projection():
    fixture = json.loads(FIXTURE.read_text(encoding='utf-8-sig'))
    need(fixture['schemaVersion'] == '11-05-projection-regression-fixture-v2'
         and fixture['topicId'] == '11.05', 'Wrong selected fixture')
    need(fixture['oldValidator']['sha256'] == OLD_SHA, 'Old validator identity differs')
    source = (ROOT / fixture['currentValidator']['path']).resolve()
    need(source == Path(__file__).with_name('run-solution-path-native.py').resolve()
         and sha(source) == fixture['currentValidator']['sha256'], 'Current validator source changed')
    tree = ast.parse(source.read_text(encoding='utf-8-sig'))
    names = {'f32', 'vec', 'close', 'projection'}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    need(len(nodes) == len(names) and {node.name for node in nodes} == names,
         'Exact reviewed projection helper set required')
    # Compile only these pure functions; do not execute imports, resource scans,
    # module assignments, controller main(), workers, or the GPU qualifier.
    context = {'math': math, 'struct': struct, 'need': need}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), 'exec'), context)
    need(context['close'].__defaults__ == (0.0002,), 'Original XY tolerance changed')
    need(len(fixture['samples']) == 2, 'Both actual regression rows required')
    for sample in fixture['samples']:
        need(sample['sampleSHA256'] == canonical_sha({'state': sample['state'], 'anchor': sample['anchor']}),
             'Portable actual sample changed')
        need(sample['state']['frame'] == sample['frame'] and sample['anchor']['id'] == sample['anchorId'],
             'Actual sample identity differs')
    return fixture, context['projection']


def double_xy(sample, camera='player'):
    """Reproduce only the exact old Float64 dot/divide expressions, without fallback."""
    state, anchor = sample['state'], sample['anchor']
    world = [anchor['world'][k] for k in ('x', 'y', 'z')] + [1]
    matrix = state[camera + 'VP']
    clip = [sum(matrix[r * 4 + k] * world[k] for k in range(4)) for r in range(4)]
    return [(clip[0] / clip[3] + 1) / 2, (clip[1] / clip[3] + 1) / 2]


class ProjectionRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture, cls.projection = fixture_and_projection()

    def sample(self, sample_id):
        return copy.deepcopy(next(row for row in self.fixture['samples'] if row['id'] == sample_id))

    def reject(self, sample, camera, reason):
        with self.assertRaisesRegex(Pending, reason):
            type(self).projection(sample['anchor'], sample['state'], camera)

    def test_actual_inside_and_near_offscreen_rows_both_cameras(self):
        for sample in self.fixture['samples']:
            for camera in ('player', 'observer'):
                with self.subTest(sample=sample['id'], camera=camera):
                    type(self).projection(sample['anchor'], sample['state'], camera)

    def test_old_float64_failure_is_reproduced(self):
        inside = self.sample('actual-f0000-room-00')
        near = self.sample('actual-f0633-room-12')
        for sample, should_fail in ((inside, False), (near, True)):
            uv = double_xy(sample)
            actual = sample['anchor']['playerViewport']
            error = max(abs(uv[i] - actual[k]) for i, k in enumerate(('x', 'y')))
            self.assertEqual(error > 0.0002, should_fail)
        self.assertAlmostEqual(error, self.fixture['oldFailure']['maxAbsoluteXYError'], places=12)

    def test_nine_actual_mutations_are_rejected(self):
        cases = [
            ('inside viewport shift', 'actual-f0000-room-00', 'projection',
             lambda a, s: a['playerViewport'].__setitem__('x', a['playerViewport']['x'] + .001)),
            ('inside matrix shift', 'actual-f0000-room-00', 'projection',
             lambda a, s: s['playerVP'].__setitem__(3, s['playerVP'][3] + .1)),
            ('inside world shift', 'actual-f0000-room-00', 'projection',
             lambda a, s: a['world'].__setitem__('x', a['world']['x'] + .1)),
            ('near offscreen wrong viewport', 'actual-f0633-room-12', 'projection',
             lambda a, s: a['playerViewport'].__setitem__('x', a['playerViewport']['x'] + .001)),
            ('near offscreen wrong matrix', 'actual-f0633-room-12', 'projection',
             lambda a, s: s['playerVP'].__setitem__(3, s['playerVP'][3] + .01)),
            ('depth shift', 'actual-f0000-room-00', 'depth',
             lambda a, s: a['playerViewport'].__setitem__('z', a['playerViewport']['z'] + .001)),
            ('ray origin shift', 'actual-f0000-room-00', 'ray',
             lambda a, s: a['playerRay']['origin'].__setitem__('x', a['playerRay']['origin']['x'] + .01)),
            ('ray target shift', 'actual-f0000-room-00', 'ray',
             lambda a, s: a['playerRay']['target'].__setitem__('x', a['playerRay']['target']['x'] + .01)),
            ('matrix transpose', 'actual-f0000-room-00', 'depth',
             lambda a, s: s.__setitem__('playerVP', [s['playerVP'][c * 4 + r]
                                                    for r in range(4) for c in range(4)])),
        ]
        reasons = {'projection': 'Projection does not come from actual camera matrix',
                   'depth': 'Actual camera-space depth differs',
                   'ray': 'Ray is not anchored to actual camera/object'}
        for name, sample_id, reason, mutate in cases:
            with self.subTest(case=name):
                sample = self.sample(sample_id)
                mutate(sample['anchor'], sample['state'])
                self.reject(sample, 'player', reasons[reason])

    def test_zero_w_is_rejected_without_division(self):
        for camera, reason in (('player', 'Actual camera-space depth differs'),
                               ('observer', 'Projection does not come from actual camera matrix')):
            with self.subTest(camera=camera):
                sample = self.sample('actual-f0000-room-00')
                sample['state'][camera + 'VP'][12:16] = [0., 0., 0., 0.]
                self.reject(sample, camera, reason)


def recheck_attempt(value):
    fixture, projection = fixture_and_projection()
    attempt = Path(value).resolve()
    need(attempt == Path(fixture['attempt']['path']).resolve(), 'Only the pinned preserved attempt is accepted')
    inputs = fixture['rawInputs']
    for row in inputs.values():
        path = (attempt / row['relativePath']).resolve()
        need(path.is_relative_to(attempt) and path.is_file() and path.stat().st_size == row['bytes']
             and sha(path) == row['sha256'], 'Raw input changed: ' + str(path))
    request = json.loads((attempt / inputs['inputProvenance']['relativePath']).read_text(encoding='utf-8-sig'))
    need(request['physicalInputFingerprint'] == fixture['attempt']['physicalInputFingerprint']
         and request['fingerprint'] == fixture['attempt']['requestedCaptureFingerprint']
         and request['requestedModes'] == ['construction'], 'Preserved request identity differs')
    wanted = {sample['frame']: sample for sample in fixture['samples']}
    frames = calls = 0
    with (attempt / inputs['states']['relativePath']).open('rb') as states, \
            (attempt / inputs['anchors']['relativePath']).open('rb') as anchors:
        for frame, (state_line, anchor_line) in enumerate(itertools.zip_longest(states, anchors)):
            need(state_line is not None and anchor_line is not None, 'State/anchor record count differs')
            state, anchor_frame = json.loads(state_line), json.loads(anchor_line)
            need(state['frame'] == anchor_frame['frame'] == frame
                 and len(anchor_frame['anchors']) == fixture['actualCounts']['anchorsPerFrame'], 'Actual projection clock/anchor count differs')
            if frame in wanted:
                sample = wanted[frame]
                actual_anchor = [row for row in anchor_frame['anchors'] if row['id'] == sample['anchorId']]
                need(len(actual_anchor) == 1 and actual_anchor[0] == sample['anchor'] and state == sample['state']
                     and hashlib.sha256(state_line).hexdigest() == sample['stateRecordSHA256']
                     and hashlib.sha256(anchor_line).hexdigest() == sample['anchorFrameRecordSHA256'], 'Portable sample differs from exact raw records')
            for row in anchor_frame['anchors']:
                for camera in ('player', 'observer'):
                    projection(row, state, camera)
                    calls += 1
            frames += 1
    need(frames == fixture['actualCounts']['frames'] and calls == fixture['actualCounts']['projectionCalls'],
         'Full projection count differs')
    return dict(scope='projection-depth-ray-only', frames=frames, projectionCalls=calls,
                actualPixelsReviewed=False, nativeCaptureAcceptance=False, modelLoaded=False, jobLaunched=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', help='Explicitly read/recheck the same hash-pinned actual capture')
    args = parser.parse_args()
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ProjectionRegression))
    if not result.wasSuccessful():
        return 1
    report = dict(portableTestsPassed=result.testsRun, actualAttemptRechecked=False,
                  actualPixelsReviewed=False, nativeCaptureAcceptance=False, modelLoaded=False, jobLaunched=False)
    if args.attempt:
        try:
            report['attemptRecheck'] = recheck_attempt(args.attempt)
            report['actualAttemptRechecked'] = True
        except (Pending, OSError, ValueError, KeyError, TypeError) as error:
            print(json.dumps(dict(ready=False, error=str(error)), ensure_ascii=False))
            return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
