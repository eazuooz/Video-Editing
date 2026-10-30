"""Prepare one selected Short from actual PCM/captions and inspected source cuts.

Default invocation extracts only the used 1x gameplay intervals. No work runs on
import. All media stays in this project's verified C: local directory.
"""
from pathlib import Path
import hashlib
import json
import math
import subprocess

from audio_revision import P, R, LOCAL, L, VOICE, REVISION, MEDIA_ROOT, read, guard, assert_no_game_apps

FPS = 60
SECTION_IDS = ('game', 'cost', 'gaps', 'ends', 'blocked', 'cache', 'close')
SEMANTIC_EVENTS = {
    'positionMove': ('p2-1',), 'positionsChanged': ('p2-2',),
    'gapsUnchanged': ('p2-3',), 'transportLine': ('p3-1',),
    'storeGaps': ('p3-2',), 'sharedSpeed': ('p4-1',),
    'leftEndGrow': ('p4-2',), 'rightEndShrink': ('p4-3',),
    'internalGapsStable': ('p4-4',), 'blockOutput': ('p5-1',),
    'endGapCloses': ('p5-2',), 'followersPack': ('p5-3',),
    'internalGapShrinks': ('p5-4',), 'cacheLastGap': ('p6-1',),
    'skipSearch': ('p6-2',), 'insertRemove': ('p6-3',),
    'sameResult': ('p7-1',), 'changeOnlyChangedData': ('p7-2',),
    'conclusion': ('p7-3',),
    # Scene aliases retain the exact spoken cue edges; legacy semantic names above stay stable.
    'costMove': ('p2-1',), 'costGapReveal': ('p2-3',),
    # Both terminal gaps change in the same movement; retain that movement
    # through the left-gap AND right-gap clauses rather than finishing it early.
    'endMove': ('p4-2', 'p4-3'), 'blockReachEnd': ('p5-2',),
    'blockPackFront': ('p5-3', 'p5-4'),
    'cachePackNext': ('p6-1', 'p6-2'), 'cacheExceptions': ('p6-3',),
    'closeMove': ('p7-2',),
}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def frame(seconds):
    return math.floor(float(seconds) * FPS + .5)


def compact(text):
    return ''.join(str(text).split())


def run(args):
    result = subprocess.run(args, cwd=R, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode('utf8', errors='replace')[-5000:])
    return result.stdout


def owned(path):
    path = Path(path)
    if not path.resolve().is_relative_to(MEDIA_ROOT.resolve()):
        raise RuntimeError('All selected source/media paths must resolve into this Short C: root: ' + str(path))
    return path


def require_ready():
    guard()
    assert_no_game_apps()


def event(cues, ids):
    # Keep any later caption split suffix (p2-1b etc.) in the same spoken event.
    selected = [c for c in cues if any(c['id'] == key or
                (c['id'].startswith(key) and c['id'][len(key):].isalpha()) for key in ids)]
    if not selected or not all(any(c['id'] == key for c in selected) for key in ids):
        raise ValueError('Missing canonical spoken event: ' + repr(ids))
    start = min(c['startFrame'] for c in selected)
    end = max(c['endFrame'] for c in selected)
    return dict(startFrame=start, endFrame=end, start=start / FPS, end=end / FPS,
                cueIds=[c['id'] for c in selected], method='actual-caption-edges')


def build_timing(lines, clauses, spec, config, pcm, captions):
    """Pure assembly. It never invents speech timing or edits source evidence."""
    if tuple(s['id'] for s in spec) != SECTION_IDS or len(lines) != len(SECTION_IDS):
        raise ValueError('Use the selected seven-paragraph game/cost/gaps/ends/blocked/cache/close structure.')
    if captions.get('fps') != FPS or abs(captions.get('voiceOffsetSeconds', -1) - .2) > 1e-8:
        raise ValueError('Actual 60fps captions with the existing 0.20s voice offset are required.')
    frames = int(captions['frames'])
    expected = math.ceil((float(pcm['duration_seconds']) + .2 + .4) * FPS - 1e-8)
    if frames != expected or abs(captions['durationSeconds'] - frames / FPS) > 1e-7:
        raise ValueError('Use the actual PCM duration +0.20s start/+0.40s tail, not a target-length pad.')
    entries = {int(e['lineIndex']): e for e in pcm['entries'] if e.get('scene_id') == 'main'}
    if sorted(entries) != list(range(len(lines))):
        raise ValueError('Actual paragraph PCM inventory differs from the selected narration.')
    for i, line in enumerate(lines):
        if compact(entries[i]['text']) != compact(line):
            raise ValueError('PCM paragraph text changed: ' + str(i))
        if compact(' '.join(c['spoken'] for c in clauses if c['lineIndex'] == i)) != compact(line):
            raise ValueError('Spoken clauses do not reconstruct paragraph ' + str(i))
    cues = captions['cues']
    if len({c['id'] for c in clauses}) != len(clauses) or [c['id'] for c in cues] != [c['id'] for c in clauses]:
        raise ValueError('Preserve every unique canonical cue ID, including split clauses.')
    for cue, canonical in zip(cues, clauses):
        if any(cue[k] != canonical[k] for k in ('id', 'lineIndex', 'ko', 'en')):
            raise ValueError('Current caption text differs: ' + canonical['id'])
        if not 0 <= cue['startFrame'] < cue['endFrame'] <= frames:
            raise ValueError('Caption frame range is invalid.')
    by_id = {c['id']: c for c in cues}
    boundaries = [0] + [frame(entries[i]['start'] + .2) for i in range(1, len(lines))] + [frames]
    if any(b <= a for a, b in zip(boundaries, boundaries[1:])):
        raise ValueError('PCM paragraph boundaries are not strictly increasing.')
    sections = []
    for i, s in enumerate(spec):
        start, end = boundaries[i], boundaries[i + 1]
        if s['paragraph'] != i or by_id[s['firstCue']]['lineIndex'] != i:
            raise ValueError('Section first-cue mapping changed: ' + s['id'])
        base = dict(s, visualId=s['id'], firstCueFrame=by_id[s['firstCue']]['startFrame'],
                    pcmParagraphStart=float(entries[i]['start']) + .2,
                    pcmParagraphEnd=float(entries[i]['end']) + .2)
        if s['id'] in config['cuts']:
            cut = config['cuts'][s['id']]
            available = math.floor(float(cut['maxDuration']) * FPS + 1e-8)
            if available < 1:
                raise ValueError('Selected source cut contains no complete frame.')
            game_end = min(end, start + available)
            if s['id'] == 'close':
                # p7-1 confirms the visible result in the real factory. At
                # p7-2 the speech returns to the representation, so expose
                # the A/B recap before its closeMove animation starts.
                recap_start = by_id['p7-2']['startFrame']
                if not start < recap_start < end:
                    raise ValueError('Closing gameplay and recap each require at least one actual frame.')
                game_end = min(game_end, max(start + 1, recap_start))
            source_start = float(cut['in'])
            sections.append(dict(base, kind='game', startFrame=start, endFrame=game_end,
                                 source='game-master', sourceStart=source_start,
                                 sourceEnd=source_start + (game_end - start) / FPS,
                                 sourceTimeBasis='original-seconds', rate=1,
                                 nativeAudioAdopted=False, frameDirectory=s['id'],
                                 firstFrame=0, digits=6, framePattern='{frame}.jpg'))
            if game_end < end:
                fallback = 'gaps' if s['id'] == 'game' else 'close'
                sections.append(dict(base, id=s['id'] + '-explain', visualId=fallback,
                                     kind='diagram', forceDiagram=True, startFrame=game_end, endFrame=end,
                                     continuity='Same paragraph continues over its principle diagram; gameplay is not looped, frozen or slowed.'))
        else:
            sections.append(dict(base, kind='diagram', forceDiagram=True, startFrame=start, endFrame=end))
    for s in sections:
        s.update(start=s['startFrame'] / FPS, end=s['endFrame'] / FPS,
                 cueIds=[c['id'] for c in cues if c['startFrame'] < s['endFrame'] and c['endFrame'] > s['startFrame']])
    if sections[0]['startFrame'] != 0 or sections[-1]['endFrame'] != frames or any(
            a['endFrame'] != b['startFrame'] for a, b in zip(sections, sections[1:])):
        raise ValueError('The real-time visual timeline has a gap or overlap.')
    events = {key: event(cues, ids) for key, ids in SEMANTIC_EVENTS.items()}
    reveal = events['storeGaps']
    reactions = [dict(kind='realize', start=reveal['start'], end=min(reveal['end'], reveal['start'] + 1.6))]
    final_diagram = [s for s in sections if s['paragraph'] == 6 and s['kind'] == 'diagram']
    if final_diagram and final_diagram[-1]['end'] - final_diagram[-1]['start'] >= 1.2:
        s = final_diagram[-1]
        reactions.append(dict(kind='relief', start=max(s['start'], s['end'] - 2.7), end=s['end'] - .4))
    return dict(revision=REVISION, previewOnly=False, fps=FPS, frames=frames,
                durationSeconds=frames / FPS, voiceOffsetSeconds=.2, sections=sections,
                sourceTimeBasis='original-seconds', sources={}, events=events, reactions=reactions,
                cueAnchors={c['id']: dict(lineIndex=c['lineIndex'], startFrame=c['startFrame'], endFrame=c['endFrame'],
                                        start=c['startFrame']/FPS, end=c['endFrame']/FPS) for c in cues},
                actualTimingMethod='Measured paragraph PCM boundaries and actual caption edges; no estimated narration durations.',
                actualAudioListening='pending', fullMovingReview='pending')


def immutable_json(path, value):
    path = owned(path)
    data = encoded(value)
    if path.exists():
        if path.read_text(encoding='utf8') != data:
            raise RuntimeError('Preserve differing prior output: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf8', newline='\n') as handle:
            handle.write(data)


def advance_json(path, value):
    data = encoded(value).encode('utf8')
    if path.exists():
        old = path.read_bytes()
        if old == data:
            return
        archive = owned(LOCAL / 'actual-visuals/previous-active-json')
        archive.mkdir(parents=True, exist_ok=True)
        backup = archive / (path.stem + '-' + hashlib.sha256(old).hexdigest()[:12] + '.json')
        if backup.exists() and backup.read_bytes() != old:
            raise RuntimeError('Archive hash collision; preserve previous timing.')
        if not backup.exists():
            with backup.open('xb') as handle:
                handle.write(old)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main():
    require_ready()
    paths = dict(script=P/'script/narration.spoken.ko.json', clauses=P/'script/clauses.json',
                 captions=P/'script/captions.json', pcmTiming=VOICE.with_suffix('.timing.json'),
                 voice=VOICE, config=P/'production/visual-config.json', sections=P/'production/section-plan.json',
                 sourceRecord=P/'sources/selected-footage.json')
    for path in paths.values():
        if not path.is_file():
            raise FileNotFoundError('Required actual input not ready: ' + str(path))
    data = {k: read(v) for k,v in paths.items() if k != 'voice'}
    hashes = {k: sha(v) for k,v in paths.items()}
    caption_inputs = data['captions'].get('timingInputs', {})
    if caption_inputs.get('voiceSha256') != hashes['voice'] or caption_inputs.get('clausesSha256') != hashes['clauses']:
        raise RuntimeError('Actual captions do not belong to these unchanged voice/clauses.')
    if caption_inputs.get('narrationSha256') and caption_inputs['narrationSha256'] != hashes['script']:
        raise RuntimeError('Narration changed after caption alignment.')
    config = data['config']
    source = owned(R / config['source'])
    source_sha = sha(source)
    if source_sha != config['sourceSHA256'] or source_sha not in encoded(data['sourceRecord']):
        raise RuntimeError('Selected original source hash/evidence changed.')
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]))
    stream = next(v for v in probe['streams'] if v['codec_type'] == 'video')
    source_duration = float(probe['format']['duration'])
    if stream['width'] < 1920 or stream['height'] < 1080:
        raise RuntimeError('The original selected recording must be genuinely FHD or higher.')
    for cut in config['cuts'].values():
        if not 0 <= float(cut['in']) < float(cut['in']) + float(cut['maxDuration']) <= source_duration + 1/FPS:
            raise RuntimeError('Inspected source cut exceeds the actual source duration.')
    voice_probe = json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-of', 'json', str(VOICE)]))
    if abs(float(voice_probe['format']['duration']) - float(data['pcmTiming']['duration_seconds'])) > .002:
        raise RuntimeError('PCM metadata and paragraph timing duration differ.')
    timing = build_timing(data['script']['scenes'][0]['lines'], data['clauses']['clauses'],
                          data['sections'], config, data['pcmTiming'], data['captions'])
    timing['sources']['game-master'] = dict(path=config['source'], sourceSHA256=source_sha,
        originalOffsetSeconds=0, nativeAudioAdopted=False, sourceAudioAdopted=False,
        audioPolicy='Official trailer music excluded; no replacement game sounds fabricated.',
        nativeDimensions=[stream['width'], stream['height']], nativeFrameRate=stream['avg_frame_rate'],
        sourceDuration=source_duration)
    fingerprint = hashlib.sha256(encoded(dict(inputs=hashes, source=source_sha, preparationCode=sha(__file__))).encode()).hexdigest()
    timing['timingInputs'] = dict(hashes, voiceSha256=hashes['voice'])
    timing['preparationFingerprint'] = fingerprint
    outputs = []
    for s in timing['sections']:
        if s['kind'] != 'game':
            continue
        require_ready()
        count = s['endFrame'] - s['startFrame']
        cut = config['cuts'][s['frameDirectory']]
        size = (int(cut.get('proxyWidth', 1920)), int(cut.get('proxyHeight', 1080)))
        if size not in ((1920,1080),(1080,608)):
            raise RuntimeError('Use the agreed FHD frames or aspect-preserving 1080x608 playback proxy.')
        folder = owned(LOCAL / 'frames' / s['frameDirectory'])
        receipt = folder / 'capture.json'
        recipe = dict(sourceSHA256=source_sha, sourceStart=s['sourceStart'], sourceEnd=s['sourceEnd'],
                      frames=count, fps=FPS, rate=1, size=list(size), nativeDimensions=[stream['width'],stream['height']])
        files = sorted(folder.glob('*.jpg')) if folder.exists() else []
        if files or receipt.exists():
            if not receipt.exists() or read(receipt).get('recipe') != recipe:
                raise RuntimeError('Preserve prior/partial frame folder; version it before a different extraction: ' + str(folder))
            previous = read(receipt)
            if len(files) != count or [v.name for v in files] != [f'{i:06}.jpg' for i in range(count)]:
                raise RuntimeError('Existing frame inventory differs.')
            if sha(files[0]) != previous['firstSha256'] or sha(files[-1]) != previous['lastSha256']:
                raise RuntimeError('Existing frame boundary hash changed.')
        else:
            folder.mkdir(parents=True, exist_ok=True)
            run(['ffmpeg', '-v', 'error', '-n', '-threads', '3', '-ss', str(s['sourceStart']), '-i', str(source), '-an',
                 '-vf', f'scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease,pad={size[0]}:{size[1]}:(ow-iw)/2:(oh-ih)/2,fps=60',
                 '-frames:v', str(count), '-q:v', '3', '-threads', '1', '-start_number', '0', str(folder/'%06d.jpg')])
            files = sorted(folder.glob('*.jpg'))
            if len(files) != count:
                raise RuntimeError('Incomplete source-frame extraction retained for inspection.')
            immutable_json(receipt, dict(recipe=recipe, firstSha256=sha(files[0]), lastSha256=sha(files[-1])))
        outputs.append(dict(id=s['id'], path=str(folder.resolve()), frames=count, sourceStart=s['sourceStart'],
                            sourceEnd=s['sourceEnd'], rate=1, dimensions=list(size),
                            firstSha256=sha(files[0]), lastSha256=sha(files[-1])))
    timing['preparedFrames'] = outputs
    require_ready()
    if any(sha(path) != hashes[key] for key,path in paths.items()):
        raise RuntimeError('Inputs changed during extraction; retain frames but do not advance timing.')
    immutable_json(LOCAL/'actual-visuals'/fingerprint/'visual-timing.json', timing)
    advance_json(P/'production/visual-timing.json', timing)
    advance_json(LOCAL/'visual-timing.json', timing)
    print(encoded(dict(slug=P.name, revision=REVISION, frames=timing['frames'], actualTimingPrepared=True,
                       sourceIntervals=[dict(id=s['id'],start=s['sourceStart'],end=s['sourceEnd']) for s in timing['sections'] if s['kind']=='game'],
                       overflowDiagrams=[s['id'] for s in timing['sections'] if s.get('continuity')],
                       frameRoot=str((LOCAL/'frames').resolve()), humanListening='pending', fullMovingReview='pending')))


if __name__ == '__main__':
    main()
