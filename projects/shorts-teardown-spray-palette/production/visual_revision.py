"""Frozen Teardown picture/audio acceptance. Imports never start media work."""
from pathlib import Path
import json, math
from audio_revision import (P, R, LOCAL, MEDIA_ROOT, VOICE, REVISION, SLUG, LEASE,
                            CAPTION_CLAUSES, guard, read, sha, assert_no_game_apps)
IDS = ['game', 'index', 'variants', 'lookup', 'capacity', 'limits', 'close']
SOURCE_ID = 'teardown-official-spray-2019'
SOURCE_SHA256 = '99943e1f9c7bfba173aeaedc67c4702f3f957a45dea75f8390951ff88675620c'
SOURCE_START = 125.625
SOURCE_END = 129.625
MAX_NATIVE_FRAMES = 240
INPUT_PROOF_SHA256 = '9144972ba3e313acadb2afec909541de46752774bc07f9698b87b26a3dfcfcee'


def static_guard(require_current_selection=True):
    control = guard(require_current_selection=require_current_selection)
    proof_path = P / 'production/video-source-inputs.json'
    if sha(proof_path) != INPUT_PROOF_SHA256:
        raise RuntimeError('Video source/input freeze changed; review before production.')
    proof = read(proof_path)
    if proof.get('slug') != SLUG or proof.get('revision') != REVISION:
        raise RuntimeError('Unexpected video preparation scope.')
    for entry in proof['frozenAssets']:
        path = Path(entry['path'])
        if not path.is_absolute(): path = R / path
        if not path.is_file() or sha(path) != entry['sha256']:
            raise RuntimeError('Frozen picture/music/canonical input changed: ' + str(path))
    config = read(P / 'production/visual-config.json')
    if any(config.get(key) != value for key,value in proof['configStatic'].items()):
        raise RuntimeError('Static title/layout/model/semantic cue configuration changed.')
    if (config.get('slug') != SLUG or config.get('revision') != REVISION
            or config.get('sourceAudioAdopted') is not False
            or config.get('headerSuppliedByFinalizer') is not True
            or config.get('fixedHeaderHeight') != 440):
        raise RuntimeError('Picture configuration scope/header/source-audio contract changed.')
    return control


def execution_guard():
    control = static_guard()
    assert_no_game_apps()
    if LEASE.exists():
        raise RuntimeError('Preserve foreign GPU lease; queue picture/audio finishing serially.')
    return control


def selected_source():
    registry = read(P / 'sources/selected-footage.json')
    items = registry.get('selected', [])
    if len(items) != 1 or items[0].get('id') != SOURCE_ID:
        raise RuntimeError('Only the inspected official spray excerpt is selected.')
    item = items[0]
    path = Path(item['absoluteMediaPath'])
    if (item.get('sha256') != SOURCE_SHA256 or sha(path) != SOURCE_SHA256
            or item.get('sourceKind') != 'official-independent-gameplay-development-demo'
            or item.get('inSeconds') != SOURCE_START or item.get('outSeconds') != SOURCE_END
            or item.get('maxDurationSeconds') != 4 or item.get('sourceAudioAdopted') is not False
            or not path.resolve().is_relative_to((MEDIA_ROOT / 'local').resolve())):
        raise RuntimeError('Official four-second source path/hash/cut/rights scope changed.')
    return path, item


def actual_inputs():
    """Require actual PCM and complete derived clauses; never accept preview timing."""
    static_guard()
    captions = read(P / 'script/captions.json')
    timing = read(P / 'production/visual-timing.json')
    config = read(P / 'production/visual-config.json')
    if (timing != read(LOCAL / 'visual-timing.json') or timing.get('previewOnly') is not False
            or timing.get('revision') != REVISION or timing.get('fps') != 60
            or captions.get('revision') != REVISION or captions.get('fps') != 60
            or timing.get('frames') != captions.get('frames')):
        raise RuntimeError('Use matching actual 60fps timeline/captions, not provisional times.')
    voice_hash = sha(VOICE)
    derived = read(CAPTION_CLAUSES)['clauses']
    if (captions.get('timingInputs', {}).get('voiceSha256') != voice_hash
            or captions['timingInputs'].get('clausesSha256') != sha(CAPTION_CLAUSES)
            or timing.get('timingInputs', {}).get('voiceSha256') != voice_hash
            or timing['timingInputs'].get('productionClausesSha256') != sha(CAPTION_CLAUSES)
            or [c['id'] for c in captions['cues']] != [c['id'] for c in derived]
            or len(timing.get('sections', [])) != len(IDS)):
        raise RuntimeError('Current PCM or complete derived-clause binding changed.')
    previous = 0
    for expected_id, section in zip(IDS, timing['sections']):
        if (section['id'] != expected_id or section['startFrame'] != previous
                or not section['startFrame'] < section['endFrame'] <= timing['frames']
                or abs(section['start'] - section['startFrame']/60) > 1e-8
                or abs(section['end'] - section['endFrame']/60) > 1e-8):
            raise RuntimeError('Seven teaching sections must stay ordered, continuous and frame-exact.')
        previous = section['endFrame']
    if previous != timing['frames']:
        raise RuntimeError('Teaching sections do not cover the whole actual timeline.')
    native = timing.get('nativeSegments', [])
    if len(native) != 1:
        raise RuntimeError('Only one four-second official spray segment is adopted.')
    n = native[0]
    if (n.get('id') != 'game' or n.get('source') != 'game-master' or n.get('kind') != 'game'
            or n.get('startFrame') != 0 or n.get('endFrame') != MAX_NATIVE_FRAMES
            or n.get('sourceStart') != SOURCE_START or n.get('sourceEnd') != SOURCE_END
            or n.get('rate') != 1 or n.get('nativeAudioAdopted') is not False
            or n.get('start') != 0 or n.get('end') != 4
            or timing['sections'][0]['endFrame'] < MAX_NATIVE_FRAMES):
        raise RuntimeError('Official gameplay must be exactly the reviewed four-second 1x opening.')
    source, _ = selected_source()
    registered = timing.get('sources', {}).get('game-master', {})
    if (Path(registered.get('path', '')).resolve() != source.resolve()
            or registered.get('sourceSHA256') != SOURCE_SHA256
            or registered.get('sourceAudioAdopted') is not False
            or config.get('sourceSHA256') != SOURCE_SHA256
            or config.get('framesPrepared') is not True or config.get('footageReady') is not True):
        raise RuntimeError('Actual extracted frames/source registration are not ready.')
    if set(config.get('cuts', {})) != {'game'} or config['cuts']['game'].get('maxDuration') != 4:
        raise RuntimeError('Additional source cuts/loops are not authorized.')
    anchors = timing.get('cueAnchors', {})
    for cue in captions['cues']:
        anchor = anchors.get(cue['id'], {})
        if anchor.get('startFrame') != cue['startFrame'] or anchor.get('endFrame') != cue['endFrame']:
            raise RuntimeError('Missing/different actual cue anchor: ' + cue['id'])
    close_cues = [cue for cue in captions['cues'] if cue['lineIndex'] == len(IDS)-1]
    end = max(cue['endFrame'] for cue in close_cues)
    if timing.get('events', {}).get('conclusion', {}).get('endFrame') != end:
        raise RuntimeError('Conclusion event must include the derived p7-2b ending.')
    capture = read(LOCAL / 'frames/game/capture.json')
    if capture.get('recipe', {}).get('sourceSHA256') != SOURCE_SHA256 or capture['recipe'].get('frames') != 240:
        raise RuntimeError('Capture receipt does not match the exact reviewed source recipe.')
    actual = sorted((LOCAL / 'frames/game').glob('*.jpg'))
    if len(actual) != 240 or len(capture.get('artifacts', [])) != 240:
        raise RuntimeError('Complete four-second extraction required.')
    for file, artifact in zip(actual, capture['artifacts']):
        if file.name != artifact['name'] or sha(file) != artifact['sha256']:
            raise RuntimeError('Captured source frame differs from its receipt.')
    return captions, timing, config
