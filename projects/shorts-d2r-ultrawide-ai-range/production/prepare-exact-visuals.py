"""Bind actual PCM/captions to immutable, input-addressed native-speed frames.

No work runs on import. Every failed attempt is preserved; only a fully checked
receipt can be reused. This is CPU decoding, not a TTS or visual-render command.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import subprocess
import uuid
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SLUGS = {'ultrawide': 'shorts-d2r-ultrawide-ai-range', 'grass': 'shorts-d2r-loot-grass-clearance', 'sprites': 'shorts-d2-modular-sprite-equipment'}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf8'))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def fingerprint(inputs):
    return hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf8')).hexdigest()


def write_new(path, content):
    """Never replace an existing receipt, partial or history snapshot."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(content)


def publish_preserving(path, value, history):
    """Snapshot exact old bytes before changing a small current-state pointer."""
    content = encoded(value)
    if path.exists():
        old = path.read_bytes()
        if old == content:
            return
        digest = hashlib.sha256(old).hexdigest()
        snapshot = history / (digest + '.json')
        if snapshot.exists():
            if snapshot.read_bytes() != old:
                raise RuntimeError('History snapshot mismatch; preserve all files: ' + str(snapshot))
        else:
            write_new(snapshot, old)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.partial')
    write_new(temporary, content)
    os.replace(temporary, path)


def inspect_frames(directory, count, dimensions):
    expected = [f'{index:05d}.jpg' for index in range(count)]
    actual = sorted(p.name for p in directory.iterdir()) if directory.is_dir() else []
    if actual != expected:
        raise RuntimeError('Frame set is not exact and contiguous: ' + str(directory))
    records = []
    for name in expected:
        path = directory / name
        with Image.open(path) as picture:
            if picture.format != 'JPEG' or picture.size != dimensions:
                raise RuntimeError('Invalid frame size or format: ' + str(path))
            picture.verify()
        records.append({'name': name, 'bytes': path.stat().st_size, 'sha256': sha(path)})
    return records


def verified_attempt(attempt, input_id, inputs, count, dimensions):
    receipt_path = attempt / 'receipt.json'
    if not receipt_path.is_file():
        return None
    try:
        receipt = read(receipt_path)
        if receipt.get('status') != 'complete' or receipt.get('inputFingerprint') != input_id or receipt.get('inputs') != inputs or receipt.get('frames') != count:
            return None
        if receipt.get('dimensions') != list(dimensions):
            return None
        if receipt.get('frameFiles') != inspect_frames(attempt / 'game', count, dimensions):
            return None
        return receipt
    except (OSError, ValueError, RuntimeError):
        return None


def ensure_frames(base, inputs, count, dimensions, extract):
    """Reuse only an exact successful set; give every retry a fresh directory."""
    input_id = fingerprint(inputs)
    family = base / input_id
    family.mkdir(parents=True, exist_ok=True)
    for attempt in sorted(family.glob('attempt-*')):
        if attempt.is_dir():
            receipt = verified_attempt(attempt, input_id, inputs, count, dimensions)
            if receipt:
                return attempt / 'game', receipt, True
    number = 1
    while True:
        attempt = family / f'attempt-{number:04d}'
        try:
            attempt.mkdir()
            break
        except FileExistsError:
            number += 1
    write_new(attempt / 'inputs.json', encoded(inputs))
    directory = attempt / 'game'
    directory.mkdir()
    extract(directory)
    records = inspect_frames(directory, count, dimensions)
    receipt = {'kind': 'exact-source-native-speed-frame-extraction', 'status': 'complete',
        'inputFingerprint': input_id, 'inputs': inputs, 'frames': count,
        'dimensions': list(dimensions), 'frameFiles': records,
        'audioPlaybackReview': 'pending',
        'fpsConversion': '60fps source unchanged; official30fps legacy frames duplicated at60 without slowing'}
    write_new(attempt / 'receipt.json', encoded(receipt))
    return directory, receipt, False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('topic', choices=SLUGS)
    args = parser.parse_args()
    project = ROOT / 'projects' / SLUGS[args.topic]
    auth = read(ROOT / 'shared/publishing/video-production-control.json')['scopedBatchAuthorizations']['explicit-ten-distinctive-shorts-20261025']
    assert auth['status'] == 'active' and auth['fullProductionAuthorized'] and project.name in auth['slugs']
    plan = read(project / 'planning/production-plan.json')
    assert plan['scriptFinalized'] and plan['independentFootageViewed']
    captions_path = project / 'script/captions.json'
    voice_path = project / 'production/local/audio-v1/voice/narration.wav'
    voice_timing_path = voice_path.with_suffix('.timing.json')
    captions, voice = read(captions_path), read(voice_timing_path)
    assert captions['revision'] == 'distinctive-ten-v1'
    assert captions['timingInputs']['narrationSha256'] == sha(project / 'script/narration.spoken.ko.json')
    voice_sha = sha(voice_path)
    assert captions['timingInputs']['voiceSha256'] == voice_sha == voice['voiceSha256'], 'Actual PCM/timing/caption hashes disagree.'
    offset, count = float(captions['voiceOffsetSeconds']), int(captions['frames'])
    duration = count / 60
    assert abs(duration - float(captions['durationSeconds'])) < 1e-8
    spec_path = project / 'production/section-plan.json'
    spec, entries = read(spec_path), voice['entries']
    assert len(entries) == len(spec)
    sections = []
    for i, row in enumerate(spec):
        start = 0 if i == 0 else round((float(entries[i]['start']) + offset) * 60)
        end = count if i + 1 == len(spec) else round((float(entries[i + 1]['start']) + offset) * 60)
        assert 0 <= start < end <= count
        sections.append(dict(**row, start=start / 60, end=end / 60, startFrame=start, endFrame=end))
    cues = {c['id']: {'start': c['start'], 'end': c['end']} for c in captions['cues']}
    source_record = project / 'sources/selected-footage.json'
    sources, needed = read(source_record)['sources'], sections[0]['endFrame']
    registry, cuts, source_inputs, cursor = {}, [], [], 0
    for index, entry in enumerate(sources):
        if cursor >= needed:
            break
        source, start = entry['source'], float(entry['sourceStart'])
        available = math.floor((float(entry['availableUntil']) - start) * 60)
        frames, key = min(available, needed - cursor), f'official-game-{index + 1}'
        assert frames > 0
        path = ROOT / source['path']
        source_sha = sha(path)
        assert source_sha == source['sha256'], 'Actual source differs from inspected source: ' + str(path)
        assert (int(source['width']), int(source['height'])) == (1920, 1080)
        audio = source.get('audio') != 'no stream'
        registry[key] = {'path': source['path'], 'sourceSHA256': source_sha, 'originalOffsetSeconds': 0, 'nativeAudioAdopted': audio}
        source_inputs.append({'path': source['path'], 'sha256': source_sha, 'bytes': path.stat().st_size})
        cuts.append(dict(id='game' if index == 0 else f'game-{index + 1}', paragraph=0, kind='game',
            start=cursor / 60, end=(cursor + frames) / 60, startFrame=cursor, endFrame=cursor + frames,
            source=key, sourceStart=start, sourceEnd=start + frames / 60, sourceTimeBasis='original-seconds', rate=1, nativeAudioAdopted=audio))
        cursor += frames
    assert cursor == needed, 'Inspected source duration exhausted; never loop or slow.'
    inputs = {'schemaVersion': 2, 'slug': project.name, 'builderSha256': sha(Path(__file__)),
        'actualVoiceSha256': voice_sha, 'voiceTimingSha256': sha(voice_timing_path),
        'captionsSha256': sha(captions_path), 'narrationSha256': captions['timingInputs']['narrationSha256'],
        'sourceRecordSha256': sha(source_record), 'sectionPlanSha256': sha(spec_path),
        'sourceFiles': source_inputs, 'cuts': cuts, 'captionFrames': count, 'gameFrames': needed,
        'decoder': subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True, text=True).stdout.splitlines()[0],
        'decodeSettings': {'fps': 60, 'jpegQuality': 3, 'dimensions': [1920, 1080]}}

    def extract(directory):
        for cut in cuts:
            subprocess.run(['ffmpeg', '-v', 'error', '-threads', '2', '-ss', str(cut['sourceStart']),
                '-i', str(ROOT / registry[cut['source']]['path']), '-vf', 'fps=60',
                '-frames:v', str(cut['endFrame'] - cut['startFrame']), '-start_number', str(cut['startFrame']),
                '-threads', '1', '-q:v', '3', '-n', str(directory / '%05d.jpg')], check=True)

    directory, receipt, reused = ensure_frames(project / 'production/local/game-frames', inputs, needed, (1920, 1080), extract)
    frame_root = directory.relative_to(ROOT).as_posix()
    timing = {'revision': 'distinctive-ten-v1', 'status': 'actual-pcm-caption-aligned', 'previewOnly': False,
        'frames': count, 'durationSeconds': duration, 'voiceOffsetSeconds': offset,
        'frameRoot': frame_root, 'frameInputFingerprint': receipt['inputFingerprint'],
        'frameReceipt': (directory.parent / 'receipt.json').relative_to(ROOT).as_posix(),
        'captionTimingInputs': captions['timingInputs'], 'sections': cuts + sections[1:], 'sources': registry, 'cues': cues}
    reveal = {'ultrawide': 'p4-3', 'grass': 'p3-2', 'sprites': 'p3-3'}[args.topic]
    at, close = cues[reveal]['start'], cues['p6-1']['start']
    timing['reactions'] = [{'start': at, 'end': min(at + 1.8, cues[reveal]['end']), 'kind': 'realize'},
        {'start': close, 'end': min(close + 2, duration - .4), 'kind': 'relief'}]
    history = project / 'production/local/visual-timing-history'
    publish_preserving(project / 'production/visual-timing.json', timing, history)
    publish_preserving(project / 'production/local/visual-timing.json', timing, history)
    config_path = project / 'production/scene-config.json'
    config = read(config_path)
    config.update(footageReady=True, footageFrames=needed)
    publish_preserving(config_path, config, project / 'production/local/scene-config-history')
    print(json.dumps({'slug': project.name, 'frames': count, 'gameFrames': needed, 'frameRoot': frame_root,
        'reusedFrames': reused, 'inputFingerprint': receipt['inputFingerprint'], 'timing': 'actual-pcm-caption-aligned'}))


if __name__ == '__main__':
    main()
