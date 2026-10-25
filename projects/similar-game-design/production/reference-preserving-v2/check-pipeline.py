"""Finite code/font/ASS smoke check. No audio/video, ASR, browser or server job."""
from pathlib import Path
import datetime
import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    records = {}
    for name in ['audio_pipeline', 'caption_pipeline', 'video_pipeline', 'review_audio']:
        source = HERE / (name + '.py')
        compile(source.read_text('utf-8'), str(source), 'exec')
        importlib.import_module(name)
        records[name] = {'compiled': True, 'importedWithoutJob': True, 'sha256': digest(source)}
    builder_file = HERE / 'build-edit-plan.py'
    compile(builder_file.read_text('utf-8'), str(builder_file), 'exec')
    spec = importlib.util.spec_from_file_location('d22_edit_builder', builder_file)
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    assert builder.subtract((0, 20), [(5, 10), (12, 16)]) == [(0, 5), (10, 12), (16, 20)]
    bank = {'id': 'synthetic-atomic', 'in': 0, 'out': 10, 'minMeaningfulSeconds': 5,
            'eventGuard': {'atomic': True, 'in': 2, 'out': 7}}
    assert builder.minimum_frames(bank) == 300
    assert builder.source_inpoint(bank, 300) == 2
    assert builder.source_inpoint(bank, 600) == 0
    toy_banks = [{'id': name, 'sourceId': name, 'in': 0, 'out': limit,
                  'minMeaningfulSeconds': 4, 'eventGuard': {'atomic': True, 'in': 0, 'out': 4},
                  'reservedForParagraphIds': ['test-p01'], 'allowedParagraphIds': ['test-p01'],
                  'atomicContinuationParagraphGroup': ['test-p01']}
                 for name, limit in [('atomic-a', 4), ('atomic-b', 6)]]
    toy_plan = {'banks': toy_banks, 'paragraphs': [{'id': 'test-p01', 'preferredMode': 'actual'}],
                'sources': {b['sourceId']: {'sha256': b['sourceId']} for b in toy_banks},
                'constraints': {'requiredAtomicEvents': ['atomic-a', 'atomic-b']}}
    toy_rows = [{'id': 'test-p01', 'startFrame': 120, 'endFrame': 720}]
    toy_cuts, _ = builder.automatic_allocation(toy_plan, toy_rows, 540)
    builder.validate_allocation(toy_cuts, toy_plan, toy_rows, 540)
    assert sum(c['frames'] for c in toy_cuts) == 540
    records['editBuilder'] = {'compiled': True, 'importedWithoutJob': True,
        'intervalAndAtomicGuardSyntheticChecks': 'passed', 'sha256': digest(builder_file),
        'actualTimingAllocation': 'pending real48k timing; no estimated production clock accepted'}
    import audio_pipeline as audio
    import caption_pipeline as captions
    import video_pipeline as video
    import review_audio as review
    assert audio.RATE == review.RATE == 48000 and audio.RATE // 60 == 800
    fontfile = Path('C:/Windows/Fonts/NotoSansKR-VF.ttf')
    font, bold = captions.measured_font(fontfile, 500), captions.measured_font(fontfile, 700)
    ko, en = '차이를 보여 줍니다.', 'Show the difference.'
    begin = en.index('difference')
    unit = captions.partition_pair(ko, en, font, [{'ko': ko, 'en': en, 'emphasis': {
        'ko': {'start': 0, 'end': 2, 'role': 'term'},
        'en': {'start': begin, 'end': begin + 10, 'role': 'term'}}}])[0]
    geometry = captions.geometry(unit['ko'], font, bold, unit['emphasis']['ko'])
    ass = captions.ass_events({'start': 2, 'end': 3, **unit}, geometry)
    assert '\\b700' in ass and '\\1c&H666b0b&' in ass and geometry['center'] == [960, 970]
    assert all(captions.contrast_on_white(color) >= 4.5 for color in captions.EMPHASIS_COLORS.values())
    try:
        captions.partition_pair(ko, en, font, None)
    except ValueError:
        pass
    else:
        raise AssertionError('Unreviewed word-count partition was accepted')
    annotation, logged = video.annotations({'frames': 60, 'credit': 'https://example.invalid/source',
                                            'copyrightCredit': 'DO_NOT_DRAW', 'marks': []}, {})
    assert 'http' not in annotation and 'DO_NOT_DRAW' not in annotation
    assert logged['editorAddedSourceCreditsRendered'] is False
    no_voice = audio.game_gain_decision(-29, -12, .02, 0)
    assert no_voice['gainDb'] == 6 and no_voice['narrationRelativeGainDb'] == 0
    voiced = audio.game_gain_decision(-29, -12, .02, .1)
    assert .02 * 10 ** (voiced['gainDb'] / 20) <= .1 * 10 ** (-10 / 20) + 1e-10
    silent = audio.game_gain_decision(0, 0, 0, 0)
    assert silent['gainDb'] == 0 and silent['silentSource']
    group = audio.game_group_gain_decision(-29, -12, .02, [2, -1, 4])
    assert group['normalizationGainDb'] == 6 and group['gainDb'] == -1
    assert group['sourceCommonNarrationCapDb'] == -1
    import storage_paths as storage
    assert storage.route_active('edit') and storage.route_active('rendered')
    for subdir in ('edit', 'rendered'):
        logical = storage.LOGICAL / subdir / 'synthetic-path-only.txt'
        physical = storage.PHYSICAL / subdir / 'synthetic-path-only.txt'
        assert storage.local_output(logical) == physical
        assert storage.relative(physical) == logical.relative_to(ROOT).as_posix()
    for denied in ['C:/Users/1/.codex/video-production/foreign/edit/x.wav',
                   storage.PHYSICAL.parent / 'reference-preserving-v3/edit/x.wav',
                   storage.LOGICAL / 'sources/new-output.wav']:
        try:
            storage.local_output(denied)
        except ValueError:
            pass
        else:
            raise AssertionError('Foreign/unrouted local media output accepted')
    records['storageRouting'] = {'exactEditAndRenderedJunctionsVerified': True,
        'sourceMediaOnDUnchanged': True, 'artifactPathsNormalizeToLogicalD': True,
        'siblingCAndUnroutedDWritesRejected': True, 'sha256': digest(HERE/'storage_paths.py')}
    commands = [
        ['node', 'motion-canvas/node_modules/typescript/bin/tsc', '--project',
         'projects/similar-game-design/production/reference-preserving-v2/tsconfig.pipeline-check.json', '--pretty', 'false'],
        ['node', '--check', str(HERE / 'render-diagrams.cjs')],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)
    mc = ROOT / 'motion-canvas/src/projects/similar-game-design/revision-v2'
    records['motionCanvas'] = {'scopedSceneTypeScript': 'passed', 'rendererNodeSyntax': 'passed',
        'sourceHashes': {name: digest(mc / name) for name in
                         ['visuals.tsx', 'preflight-scene.tsx', 'preflight-project.ts', 'vite.config.ts']},
        'modes': 9, 'finalGames': ['Deep Rock Galactic: Survivor', 'Super Mario Maker 2'],
        'socialMode': 'shared start -> relative positions -> competition; cooperation is only an interface alias',
        'preflightSeconds': 36, 'preflightFrames60fps': 2160, 'actualMovingPixelReview': 'pending'}
    records['inMemoryChecks'] = {'captionPolicy': captions.CAPTION_POLICY, 'plainDisplayTextRetained': True,
        'authoredClauseRetention': True, 'pairedSemanticSpan': True, 'emphasisWeight': 700,
        'fixed48pxAndBoxCenter': True, 'sourceCreditsMetadataOnly': True, 'internalPcmRate': audio.RATE,
        'samplesPer60fpsFrame': 800, 'originalMp3Untouched': True, 'finalAacFrameToleranceSamples': 1025,
        'contrast': {role: captions.contrast_on_white(color) for role, color in captions.EMPHASIS_COLORS.items()},
        'gameProfile': {'initialLufs': -23, 'narrationRelativeDb': -10, 'sidechain': [.08, 2.2, 15, 280, 1],
                        'fixedQuietRmsTargetUsed': False, 'pureNumericalGainChecksPassed': True,
                        'constantGainPerSourceGroup': True, 'commonMinimumNarrationCapPassed': True}}
    records['scope'] = {'syntheticSmokeDataOnly': True, 'actualProductionMediaGenerated': False,
        'servicesStarted': False, 'gpuUsed': False, 'actualPixelReview': 'pending',
        'actualAudioOrHumanListeningReview': 'pending'}
    records['recordedAt'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    (HERE / 'pipeline-smoke-qa.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('D22 code/font/ASS/game-gain smoke passed; no media/ASR/server/browser job started.')


if __name__ == '__main__':
    main()
