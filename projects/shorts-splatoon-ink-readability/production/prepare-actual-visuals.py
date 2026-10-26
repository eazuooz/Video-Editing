"""Bind the actual InkReadability PCM/captions, prepare native frames and finite Unity job.

No media/model/editor/server work runs on import or --check. `prepare` extracts
only hash-checked native FHD source cuts and writes a speech-derived job; it does
not start Unity. `capture-ready` accepts real nonpreview receipts and explicit
internal pixel-review attestations before enabling MC. It never invents timing.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import subprocess

from audio_revision import (
    P, R, LOCAL, MEDIA_ROOT, VOICE, REVISION, LEASE, read, sha,
    guard, assert_no_game_apps, assert_media_junction,
)

IDS = ['game', 'pbs', 'boundary', 'flat', 'specular', 'close']
CUE_IDS = [cue['id'] for cue in read(P / 'production/clauses.json')['clauses']]
URL_ROOT = '/@fs/D:/Github/VideoEditing/projects/shorts-splatoon-ink-readability/production/local/'
CAPTURE_OUTPUT = MEDIA_ROOT / 'local/unity-full-v2'
JOB_PATH = LOCAL / 'unity-full-job-v2.json'


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def save_exact(path, value):
    """Idempotent immutable recipe/job/receipt; preserve any differing prior file."""
    assert_media_junction()
    path = Path(path)
    data = encoded(value)
    if path.exists():
        if path.read_text(encoding='utf8') != data:
            raise RuntimeError('Preserve differing prior input/output recipe: ' + str(path))
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8') as stream:
        stream.write(data)


def update_versioned(path, value):
    """Small mutable production metadata keeps a hash-named C: snapshot first."""
    assert_media_junction()
    path = Path(path)
    data = encoded(value)
    if path.exists() and path.read_text(encoding='utf8') == data:
        return
    if path.exists():
        backup = LOCAL / 'actual-visuals/previous' / (path.stem + '-' + sha(path)[:16] + path.suffix)
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            with backup.open('xb') as stream:
                stream.write(path.read_bytes())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding='utf8')


def execution_guard():
    guard()
    assert_no_game_apps()
    if LEASE.exists():
        raise RuntimeError('Foreign costly/GPU lease preserved; defer frame preparation/acceptance.')


def run(args):
    result = subprocess.run(args, cwd=R, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors='replace')[-4000:])
    return result.stdout


def actual_timing():
    captions = read(P / 'script/captions.json')
    pcm = read(VOICE.with_suffix('.timing.json'))
    digest = sha(VOICE)
    if (captions.get('fps') != 60 or captions.get('revision') != REVISION
            or captions.get('timingInputs', {}).get('voiceSha256') != digest
            or pcm.get('voiceSha256') != digest or pcm.get('revision') != REVISION
            or captions.get('voiceOffsetSeconds') != .2 or captions.get('tailSecondsMinimum') != .4
            or captions.get('speechSpeed') != 1 or pcm.get('speechSpeed') != 1
            or not math.isfinite(pcm['duration_seconds']) or pcm['duration_seconds'] <= 0
            or captions['frames'] != math.ceil((pcm['duration_seconds'] + .6) * 60 - 1e-8)
            or abs(captions['durationSeconds'] - captions['frames'] / 60) > 1e-8):
        raise RuntimeError('Require exact current complete PCM, natural speed and actual60fps caption timing.')
    if [cue['id'] for cue in captions['cues']] != CUE_IDS:
        raise RuntimeError('Require all29 current display clauses in their original order.')
    entries = sorted(pcm['entries'], key=lambda entry: entry['lineIndex'])
    if len(entries) != 6 or [entry['lineIndex'] for entry in entries] != list(range(6)):
        raise RuntimeError('Actual PCM timing must contain the six canonical paragraphs.')
    bounds = [0]
    for index, entry in enumerate(entries[1:], 1):
        previous_end = max(cue['endFrame'] for cue in captions['cues'] if cue['lineIndex'] == index - 1)
        first = min(cue['startFrame'] for cue in captions['cues'] if cue['lineIndex'] == index)
        if previous_end > first:
            raise RuntimeError('Observed clause timing overlaps a paragraph join.')
        bounds.append(max(previous_end, min(first, math.floor((entry['start'] + .2) * 60 + .5))))
    bounds.append(captions['frames'])
    if any(end <= start for start, end in zip(bounds, bounds[1:])):
        raise RuntimeError('A speech-linked visual section is empty.')
    return captions, pcm, digest, bounds


def extract_native(cut, source, directory):
    expected = cut['sourceSha256']
    if sha(source) != expected:
        raise RuntimeError('Selected native source changed: ' + str(source))
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)]))
    video = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    if (video['width'], video['height'], video['r_frame_rate']) != (1920, 1080, '60/1'):
        raise RuntimeError('Require the actual hash-checked native1920x1080/60 source, no upscale.')
    if not 0 <= cut['sourceStartSeconds'] < cut['sourceEndSeconds'] <= float(probe['format']['duration']):
        raise RuntimeError('Selected native source interval exceeds decoded duration.')
    recipe = dict(sourceSHA256=expected, sourceStart=cut['sourceStartSeconds'], sourceEnd=cut['sourceEndSeconds'],
                  frames=cut['frameCount'], fps=60, nativeDimensions=[1920, 1080], rate=1)
    receipt = directory / 'capture.json'
    if receipt.exists():
        old = read(receipt)
        files = sorted(directory.glob('*.jpg'))
        if (old.get('recipe') != recipe or len(files) != cut['frameCount']
                or sha(files[0]) != old.get('firstSHA256') or sha(files[-1]) != old.get('lastSHA256')):
            raise RuntimeError('Existing native frame extraction differs; preserve it.')
        return old
    if list(directory.glob('*.jpg')):
        raise RuntimeError('Unreceipted native extraction exists; preserve and inspect before retrying.')
    execution_guard()
    directory.mkdir(parents=True, exist_ok=True)
    run(['ffmpeg', '-v', 'error', '-n', '-threads', '2', '-ss', str(cut['sourceStartSeconds']),
         '-i', str(source), '-an', '-vf', 'fps=60', '-frames:v', str(cut['frameCount']),
         '-q:v', '3', '-threads', '1', '-start_number', '0', str(directory / 'frame-%06d.jpg')])
    files = sorted(directory.glob('*.jpg'))
    if len(files) != cut['frameCount']:
        raise RuntimeError('Native frame count differs; do not repeat missing source frames.')
    result = dict(recipe=recipe, firstSHA256=sha(files[0]), lastSHA256=sha(files[-1]),
                  actualNativeWindowPlaybackReview='pending', audioAdopted=False)
    save_exact(receipt, result)
    return result


def opening_windows(events):
    """Two inspected native subsets, ending before historical Splatoon2 speech."""
    available = min(300, events['p1-3']['startFrame'])
    if available < 4:
        raise RuntimeError('Observed opening cannot contain two native windows; review the actual speech.')
    surface = max(2, min(132, round(available * 132 / 300)))
    submerge = min(168, available - surface)
    if submerge < 2:
        raise RuntimeError('Submerge window is too short; no repeated source frames allowed.')
    return [dict(id='surface', startFrame=0, endFrame=surface, sourceIn=66., sourceOut=66 + surface / 60),
            dict(id='submerge', startFrame=surface, endFrame=surface + submerge,
                 sourceIn=70., sourceOut=70 + submerge / 60)]


def track(a, b=None, cue=None, end_cue=None):
    value = dict(from_=a, to=a if b is None else b, ease='smoothstep', startFrame=-1, endFrame=-1)
    value['from'] = value.pop('from_')
    if cue:
        value.update(startCueId=cue, endCueId=end_cue or cue)
    return value


def label(target, text, cue=None, end_cue=None):
    item = dict(id=target + '-focus', target=target, textKo=text,
                textEn={'boundary': 'Team-color boundary', 'join': 'Wall / floor', 'splash': 'Diving splash'}[target],
                role='concept', startFrame=-1, endFrame=-1, localOffset=dict(x=0, y=0, z=0))
    if cue:
        item.update(startCueId=cue, endCueId=end_cue or cue)
    return item


def capture_sections(sections):
    result = []
    for section in sections:
        id = section['id']
        row = {key: section[key] for key in ('id', 'startFrame', 'endFrame')}
        row.update(visualId=id, stage='balanced', comparison=track(0), phase=track(.62),
                   termEn='Physically Based Shading', termKo='물리 기반 셰이딩',
                   meaningKo='빛과 재질의 반응을 물리 원리로 계산',
                   steps=['색 경계', '지형 굴곡', '잠수 흔적'], activeStep=0, labels=[])
        if id == 'game':
            row.update(stage='specular', comparison=track(0, 1, 'p1-4', 'p1-4-b'), activeStep=2,
                       labels=[label('splash', '같은 잠수 흔적', 'p1-4', 'p1-5')])
        elif id in ('pbs', 'boundary', 'flat'):
            row.update(stage='shading', comparison=track(0))
            if id == 'boundary':
                row['labels'] = [label('boundary', '두 팀의 색 경계')]
            if id == 'flat':
                row.update(comparison=track(0, 1, 'p4-1'), activeStep=1,
                           labels=[label('join', '벽과 바닥')])
        elif id == 'specular':
            row.update(stage='specular', comparison=track(0, 1, 'p5-2'), activeStep=2,
                       phase=track(.2, .8, 'p5-3', 'p5-4'),
                       termEn='Specular reflection', termKo='정반사', meaningKo='반사된 빛이 만드는 밝은 광택',
                       labels=[label('splash', '같은 잠수 흔적', 'p5-3', 'p5-4')])
        elif id == 'close':
            row.update(activeStep=2, labels=[label('boundary', '색 경계', 'p6-3'),
                       label('join', '지형 굴곡', 'p6-4'), label('splash', '잠수 흔적', 'p6-5', 'p6-7')])
        result.append(row)
    return result


def prepare():
    execution_guard()
    captions, pcm, digest, bounds = actual_timing()
    proof = read(P / 'production/audio-source-inputs.json')
    source = next(entry for entry in proof['sources'] if entry['id'] == 'charger')
    events = {cue['id']: {key: cue[key] for key in ('startFrame', 'endFrame')} for cue in captions['cues']}
    sections = [dict(id=id, startFrame=bounds[index], endFrame=bounds[index + 1],
                     start=bounds[index] / 60, end=bounds[index + 1] / 60,
                     kind='mixed' if id == 'game' else 'diagram') for index, id in enumerate(IDS)]
    windows = opening_windows(events)
    config = read(P / 'production/visual-config.json')
    if config.get('inputsReady'):
        raise RuntimeError('Preserve already accepted captures; do not reset their config.')
    cuts, prepared, native = [], [], []
    for window in windows:
        count = window['endFrame'] - window['startFrame']
        directory = LOCAL / 'visual' / window['id']
        receipt = extract_native(dict(sourceSha256=source['sha256'], sourceStartSeconds=window['sourceIn'],
            sourceEndSeconds=window['sourceOut'], frameCount=count), Path(source['path']), directory)
        previous = next(cut for cut in config['game']['cuts'] if cut['id'] == window['id'])
        source_first = round(window['sourceIn'] * 60)
        focus = [dict(frame=window['startFrame'] + key['sourceFrame'] - source_first,
                      **{name: key[name] for name in ('x', 'y', 'radiusX', 'radiusY')})
                 for key in previous.get('sourceFocus', [])
                 if source_first <= key['sourceFrame'] < source_first + count]
        focus_window = dict(startFrame=focus[0]['frame'], endFrame=focus[-1]['frame'] + 1) if len(focus) >= 2 else None
        cuts.append(dict(**window, firstFrame=0, frameDirectory=URL_ROOT + 'visual/' + window['id'],
                         pattern='frame-{frame}.jpg', digits=6,
                         sourceFocus=previous.get('sourceFocus', []),
                         sourceFocusReviewed=previous.get('sourceFocusReviewed', False),
                         sourceFocusEvidence=previous.get('sourceFocusEvidence'),
                         focusReviewed=previous.get('sourceFocusReviewed', False) and len(focus) >= 2,
                         focusWindow=focus_window, focus=focus))
        prepared.append(dict(id=window['id'], receipt=str((directory / 'capture.json').resolve()),
                             frameCount=count, firstSHA256=receipt['firstSHA256'], lastSHA256=receipt['lastSHA256']))
        native.append(dict(id='game-' + window['id'], kind='game', source='charger',
                           start=window['startFrame'] / 60, end=window['endFrame'] / 60,
                           startFrame=window['startFrame'], endFrame=window['endFrame'],
                           sourceStart=window['sourceIn'], sourceEnd=window['sourceOut'],
                           rate=1, nativeAudioAdopted=False))
    timing = dict(revision=REVISION, previewOnly=False, fps=60, frames=captions['frames'],
                  durationSeconds=captions['durationSeconds'], voiceDurationSeconds=pcm['duration_seconds'],
                  voiceOffsetSeconds=captions['voiceOffsetSeconds'], tailSecondsMinimum=captions['tailSecondsMinimum'],
                  timingInputs=dict(voiceSha256=digest, captionsSha256=sha(P / 'script/captions.json'),
                                    narrationSha256=sha(R / proof['canonicalScript']),
                                    clausesSha256=sha(P / 'production/clauses.json')),
                  sections=sections, events=events, nativeSegments=native, preparedFrames=prepared,
                  sources={'charger': dict(path=source['path'], sourceSHA256=source['sha256'],
                      nativeDimensions=[1920, 1080], originalOffsetSeconds=0,
                      nativeAudioAdopted=False, sourceAudioAdopted=False)},
                  actualGameSeconds=windows[-1]['endFrame'] / 60,
                  note='Actual PCM and29 display clauses. Splatoon3 observed example ends before p1-3; all historical conditions are our model. No loop, padding, slowed source or adopted source audio.')
    job = dict(schemaVersion=1, revision=REVISION, mode='sequence',
               expectedProjectPath=str(MEDIA_ROOT.parent / 'unity-capture'),
               outputDirectory=str(CAPTURE_OUTPUT),
               scenePath='Assets/VideoScenes/shorts-splatoon-ink-readability/Scenes/06-BalancedIllustration.unity',
               buildIfMissing=True, width=1920, height=1080, fps=60, totalFrames=captions['frames'],
               startFrame=windows[-1]['endFrame'], endFrame=captions['frames'],
               timingVerified=True, pcmPath=str(VOICE.resolve()), pcmSha256=digest,
               timingEvidence=str((LOCAL / 'visual-timing.json').resolve()),
               cues=[dict(id=id, **cue) for id, cue in events.items()], sections=capture_sections(sections),
               writeJpg=True, encodeVideo=False, jpgQuality=95, ffmpegPath='',
               cancelFile=str(MEDIA_ROOT / 'local/ink-readability-cancel.txt'))
    save_exact(JOB_PATH, job)
    config['game'].update(cuts=cuts, framesPrepared=True)
    config['unity'].update(width=1920, height=1080, frameDirectory=URL_ROOT + 'unity-full-v2/frames')
    config['status'] = 'actual timing and native cuts prepared; real Unity capture/review pending'
    update_versioned(P / 'production/visual-timing.json', timing)
    update_versioned(LOCAL / 'visual-timing.json', timing)
    update_versioned(P / 'production/visual-config.json', config)
    print(encoded(dict(state='actual-inputs-prepared; parent owns capture', frames=timing['frames'],
                       seconds=timing['durationSeconds'], gameSeconds=timing['actualGameSeconds'],
                       job=str(JOB_PATH.resolve()), noUnityStarted=True)))


def capture_ready(native_reviewed, anchors_reviewed):
    execution_guard()
    if not native_reviewed or not anchors_reviewed:
        raise RuntimeError('After actual internal playback/pixel review pass --native-reviewed and --anchors-reviewed; file presence is not viewing.')
    captions, pcm, digest, bounds = actual_timing()
    timing = read(P / 'production/visual-timing.json')
    job, success = read(JOB_PATH), read(CAPTURE_OUTPUT / 'success.json')
    config = read(P / 'production/visual-config.json')
    if (read(LOCAL / 'visual-timing.json') != timing or timing['frames'] != captions['frames']
            or timing['timingInputs']['voiceSha256'] != digest or job.get('pcmSha256') != digest
            or job.get('mode') != 'sequence' or job.get('timingVerified') is not True
            or sha(CAPTURE_OUTPUT / 'job-used.json') != sha(JOB_PATH)
            or job.get('totalFrames') != captions['frames'] or job.get('width') != 1920 or job.get('height') != 1080
            or job.get('cues') != [dict(id=id, **cue) for id, cue in timing['events'].items()]
            or Path(job['outputDirectory']).resolve() != CAPTURE_OUTPUT.resolve()
            or job['sections'] != capture_sections(timing['sections'])
            or job['startFrame'] != config['game']['cuts'][-1]['endFrame'] or job['endFrame'] != captions['frames']):
        raise RuntimeError('Current actual PCM/timing/job binding differs; preserve existing outputs.')
    expected = dict(status='render-completed-not-reviewed', revision=REVISION, mode='sequence', width=1920,
                    height=1080, fps=60, firstFrame=job['startFrame'], endFrameExclusive=job['endFrame'],
                    renderedFrames=job['endFrame'] - job['startFrame'], timingVerified=True, jpgWritten=True)
    if any(success.get(key) != value for key, value in expected.items()):
        raise RuntimeError('Require exact completed nonpreview Unity receipt.')
    from PIL import Image
    files = sorted((CAPTURE_OUTPUT / 'frames').glob('*.jpg'))
    if [path.name for path in files] != [f'frame-{frame:06}.jpg' for frame in range(job['startFrame'], job['endFrame'])]:
        raise RuntimeError('Missing or unexpected absolute-index Unity frames.')
    for path in (files[0], files[-1]):
        with Image.open(path) as image:
            if image.size != (1920, 1080):
                raise RuntimeError('Require nativeFHD Unity output.')
    trace = CAPTURE_OUTPUT / 'readback.ndjson'
    rows = [json.loads(line) for line in trace.read_text(encoding='utf-8-sig').splitlines()]
    if len(rows) != len(files):
        raise RuntimeError('Trace/frame count mismatch.')
    for index, row in enumerate(rows):
        frame = job['startFrame'] + index
        section = next(section for section in job['sections'] if section['startFrame'] <= frame < section['endFrame'])
        if (row['frame'] != frame or row['stage'] != section['stage'] or row['visualId'] != section['visualId']
                or row.get('pictureKind') != 'our-implementation'
                or any(not math.isfinite(row['appliedState'][key]) for key in ('shadingStrength', 'specularStrength', 'submergePhase'))
                or len(row['labelRequests']) > 3):
            raise RuntimeError('Actual controller readback missing or incompatible.')
        if any(not all(math.isfinite(label[key]) for key in ('u', 'v', 'depth')) for label in row['labelRequests']):
            raise RuntimeError('Nonfinite projected label.')
    for cut in config['game']['cuts']:
        directory = LOCAL / 'visual' / cut['id']
        receipt = read(directory / 'capture.json')
        native_files = sorted(directory.glob('*.jpg'))
        if (len(native_files) != cut['endFrame'] - cut['startFrame']
                or sha(native_files[0]) != receipt['firstSHA256'] or sha(native_files[-1]) != receipt['lastSHA256']):
            raise RuntimeError('Prepared native cut changed.')
        # Focus coordinates are separately entered after observing actual motion.
        # Empty focus is permitted while planning, but not for a selected final native cut.
        if not cut.get('focusReviewed') or len(cut.get('focus', [])) < 2:
            raise RuntimeError('Review native crop/motion and enter real target focus keyframes for both cuts before acceptance.')
    assets = {'timing': P / 'production/visual-timing.json', 'voice': VOICE,
              'readback': LOCAL / 'unity-full-v2/readback.ndjson', 'captureJob': JOB_PATH,
              'captureSuccess': LOCAL / 'unity-full-v2/success.json'}
    base = '/@fs/D:/Github/VideoEditing/projects/shorts-splatoon-ink-readability/production/'
    config['inputs'] = {key: dict(url=base + path.relative_to(P / 'production').as_posix(), sha256=sha(path)) for key, path in assets.items()}
    config.update(inputsReady=True, status='real PCM/captures internally accepted; final moving/mobile/audio review pending')
    config['unity']['framesPrepared'] = True
    record = dict(revision=REVISION, inputs=config['inputs'], frameCount=len(files),
                  firstFrameSHA256=sha(files[0]), lastFrameSHA256=sha(files[-1]),
                  nativePlaybackReviewed=True, unityAnchorsReviewed=True, humanReview='pending-local-final-version',
                  finalMovingMobileAudioReview='pending', sourceKind='our-Unity-implementation')
    save_exact(LOCAL / 'unity-capture-acceptance-v2.json', record)
    update_versioned(P / 'production/visual-config.json', config)
    print(encoded(dict(state='current actual captures bound; final QA pending', frames=len(files), noRenderStarted=True)))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', nargs='?', default='prepare', choices=['prepare', 'capture-ready'])
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--native-reviewed', action='store_true')
    parser.add_argument('--anchors-reviewed', action='store_true')
    args = parser.parse_args(argv)
    if args.check:
        guard(require_current_selection=False)
        print(encoded(dict(revision=REVISION, codeInputs='passed', actualVoicePresent=VOICE.is_file(),
                           sections=6, clauses=len(CUE_IDS), noModelOrMediaJobStarted=True)))
    elif args.command == 'capture-ready':
        capture_ready(args.native_reviewed, args.anchors_reviewed)
    else:
        prepare()


if __name__ == '__main__':
    main()


