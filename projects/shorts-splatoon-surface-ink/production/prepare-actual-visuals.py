"""Bind the actual SurfaceInk PCM/captions, prepare native frames and finite Unity job.

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

IDS = ['game', 'sheet', 'collision', 'uv', 'stamp', 'patch', 'orbit']
CUE_IDS = [
    'p1-1', 'p1-2', 'p2-1', 'p2-2', 'p2-3', 'p3-1', 'p3-2', 'p3-3',
    'p4-1', 'p4-2', 'p4-3', 'p4-4', 'p5-1', 'p5-2', 'p5-3', 'p5-4',
    'p6-1', 'p6-2', 'p7-1', 'p7-2', 'p7-3',
]
URL_ROOT = '/@fs/D:/Github/VideoEditing/projects/shorts-splatoon-surface-ink/production/local/'
CAPTURE_OUTPUT = MEDIA_ROOT / 'local/unity-full-v1'
JOB_PATH = LOCAL / 'unity-full-job-v1.json'


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
            or captions.get('speechSpeed') != 1 or pcm.get('speechSpeed') != 1
            or not math.isfinite(pcm['duration_seconds']) or pcm['duration_seconds'] <= 0
            or captions['frames'] != math.ceil((pcm['duration_seconds'] + .6) * 60 - 1e-8)
            or abs(captions['durationSeconds'] - captions['frames'] / 60) > 1e-8):
        raise RuntimeError('Require exact current complete PCM, natural speed and actual60fps caption timing.')
    if [cue['id'] for cue in captions['cues']] != CUE_IDS:
        raise RuntimeError('Require all21 canonical clauses in their original order.')
    entries = sorted(pcm['entries'], key=lambda entry: entry['lineIndex'])
    if len(entries) != 7 or [entry['lineIndex'] for entry in entries] != list(range(7)):
        raise RuntimeError('Actual PCM timing must contain the seven canonical paragraphs.')
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


def opening_windows(first_paragraph_frames):
    """Two useful native subsets; surplus speech goes to authored stage0, never a hold."""
    if not isinstance(first_paragraph_frames, int) or first_paragraph_frames < 4:
        raise RuntimeError('First paragraph cannot contain two meaningful native windows.')
    # Preferred useful subsets are2.0s ground paint and2.4s wall paint at1x.
    # Shorter actual speech scales their split, never changes the source speed.
    available = min(first_paragraph_frames, 264)
    floor = max(2, min(120, round(available * 120 / 264)))
    wall = max(2, min(144, available - floor))
    if first_paragraph_frames - floor - wall == 1:
        # One extra real wall frame avoids an otherwise one-frame authored clip.
        # The source remains inside its inspected180-frame window at native1x.
        wall += 1
    if floor + wall > first_paragraph_frames:
        raise RuntimeError('Native windows exceed the measured first paragraph.')
    return [dict(cut='floor', startFrame=0, endFrame=floor, sourceFrameOffset=0),
            dict(cut='wall', startFrame=floor, endFrame=floor + wall, sourceFrameOffset=0)]


def unity_clips(sections, windows, events):
    clips = []
    remaining = windows[-1]['endFrame']
    if remaining < sections[0]['endFrame']:
        length = sections[0]['endFrame'] - remaining
        if length < 2:
            raise RuntimeError('One-frame game remainder: adjust a native window by one verified frame instead of freezing.')
        clips.append(dict(id='game-overflow', stage=0, startFrame=remaining,
                          endFrame=sections[0]['endFrame'], frames=length, split=.5))
    for stage, section in enumerate(sections[1:]):
        frames = section['endFrame'] - section['startFrame']
        if frames < 2:
            raise RuntimeError('Unity capture needs at least two actual timeline frames.')
        # ApplyFrame(stage4,t,joined=t>=split). The switch is exactly p6-2.
        split = ((events['p6-2']['startFrame'] - section['startFrame']) / max(1, frames - 1)
                 if section['id'] == 'patch' else .5)
        if not 0 <= split <= 1:
            raise RuntimeError('Adjacent-patch switch is outside its actual speech paragraph.')
        clips.append(dict(id=section['id'], stage=stage, frames=frames,
                          startFrame=section['startFrame'], endFrame=section['endFrame'], split=split))
    for clip in clips:
        clip.update(cueSynchronized=True, hitAt=.65, stampEnd=1.0, floorAt=0.0,
                    expectedHitTimelineFrame=-1, stampEndTimelineFrame=-1, floorTimelineFrame=-1)
        start, last = clip['startFrame'], clip['endFrame'] - 1
        denominator = max(1, clip['frames'] - 1)
        if clip['stage'] == 1:
            # Finish the visible physical hit before the next coordinate-conversion clause.
            hit = max(start + 1, min(last, events['p3-2']['startFrame'] - 2))
            clip.update(hitAt=(hit - start) / denominator, expectedHitTimelineFrame=hit)
        elif clip['stage'] == 3:
            stamp_end = max(start + 1, min(last, events['p5-1']['endFrame'] - 1))
            floor = max(start, min(last, events['p5-3']['startFrame']))
            clip.update(stampEnd=(stamp_end - start) / denominator,
                        floorAt=(floor - start) / denominator,
                        stampEndTimelineFrame=stamp_end, floorTimelineFrame=floor)
    return clips


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
         '-q:v', '3', '-threads', '1', '-start_number', '0', str(directory / '%06d.jpg')])
    files = sorted(directory.glob('*.jpg'))
    if len(files) != cut['frameCount']:
        raise RuntimeError('Native frame count differs; do not repeat missing source frames.')
    result = dict(recipe=recipe, firstSHA256=sha(files[0]), lastSHA256=sha(files[-1]),
                  actualNativeWindowPlaybackReview='pending', audioAdopted=False)
    save_exact(receipt, result)
    return result


def prepare():
    execution_guard()
    captions, pcm, digest, bounds = actual_timing()
    config = read(P / 'production/visual-config.json')
    proof = read(P / 'production/audio-source-inputs.json')
    source_map = {entry['id']: entry for entry in proof['sources']}
    selected = {'floor': source_map['splatoon3-lobby-ink'], 'wall': source_map['splatoon3-wall-ink']}
    sections = [dict(id=id, startFrame=bounds[index], endFrame=bounds[index + 1],
                     start=bounds[index] / 60, end=bounds[index + 1] / 60,
                     kind='mixed' if id == 'game' else 'diagram') for index, id in enumerate(IDS)]
    windows = opening_windows(bounds[1])
    events = {cue['id']: {key: cue[key] for key in ('startFrame', 'endFrame')} for cue in captions['cues']}
    clips = unity_clips(sections, windows, events)
    prepared = []
    for key in ('floor', 'wall'):
        cut = config['gameplayCuts'][key]
        source = Path(selected[key]['path'])
        directory = LOCAL / 'visual' / cut['directory']
        receipt = extract_native(cut, source, directory)
        prepared.append(dict(id=key, receipt=str((directory / 'capture.json').resolve()),
                             frameCount=cut['frameCount'], firstSHA256=receipt['firstSHA256'], lastSHA256=receipt['lastSHA256']))
    sources = {key: dict(path=str(Path(entry['path'])), sourceSHA256=entry['sha256'],
                        nativeDimensions=[1920, 1080], originalOffsetSeconds=0,
                        nativeAudioAdopted=False, sourceAudioAdopted=False,
                        audioRights='Selected third-party source track explicitly excluded; not an isolatedSFX permission.')
               for key, entry in selected.items()}
    native = []
    for window in windows:
        cut = config['gameplayCuts'][window['cut']]
        source_start = cut['sourceStartSeconds'] + window['sourceFrameOffset'] / 60
        native.append(dict(id='game-' + window['cut'], kind='game', source=window['cut'],
                           start=window['startFrame'] / 60, end=window['endFrame'] / 60,
                           startFrame=window['startFrame'], endFrame=window['endFrame'],
                           sourceStart=source_start, sourceEnd=source_start + (window['endFrame'] - window['startFrame']) / 60,
                           rate=1, nativeAudioAdopted=False))
    timing = dict(revision=REVISION, previewOnly=False, fps=60, frames=captions['frames'],
                  durationSeconds=captions['durationSeconds'], voiceDurationSeconds=pcm['duration_seconds'],
                  voiceOffsetSeconds=.2, timingInputs=dict(voiceSha256=digest,
                  narrationSha256=sha(R / proof['canonicalScript']), clausesSha256=sha(P / 'script/clauses.json')),
                  sections=sections, events=events, gameplayWindows=windows, nativeSegments=native,
                  sources=sources, preparedFrames=prepared,
                  actualGameSeconds=sum((window['endFrame'] - window['startFrame']) / 60 for window in windows),
                  note='Actual speech-derived seven sections. Native floor/wall subsets play once at1x; remaining game paragraph is our stage0 capture. No invented final times, loops, holds or soundtrack adoption.')
    job = dict(output=str(CAPTURE_OUTPUT), preview=False, clips=clips, revision=REVISION,
               voiceSha256=digest, timelineFrames=captions['frames'], fps=60,
               timingInputs=timing['timingInputs'], captureClass='Yamyam.Video.SurfaceInk.Editor.SurfaceInkCapture.Run',
               sourceKind='our-Unity-implementation',
               progressPolicy='Actual paragraph0..1 clock; collision completes two frames before p3-2, wall stamp finishes inside p5-1, floor stamp begins at p5-3, patch joins at p6-2. Expected/actual phase readback and realized capture review remain required.')
    save_exact(JOB_PATH, job)
    config['frameRoot'] = URL_ROOT + 'visual/'
    if config['unityFrames'].get('captured') and config['unityFrames'].get('voiceSha256') != digest:
        raise RuntimeError('Preserve prior different-voice Unity captures.')
    config['unityFrames'].update(root=URL_ROOT + 'unity-full-v1/', voiceSha256=digest,
        sequences=[dict(directory=clip['id'], startFrame=clip['startFrame'], endFrame=clip['endFrame'],
                        indexBasis='sequence-relative', firstFrame=0, pattern='{frame}.jpg', digits=6) for clip in clips],
        captureJob=str(JOB_PATH.resolve()), captureJobSHA256=sha(JOB_PATH))
    # Do not promote source or Unity quality flags from extraction/metadata alone.
    update_versioned(P / 'production/visual-config.json', config)
    update_versioned(P / 'production/visual-timing.json', timing)
    update_versioned(LOCAL / 'visual-timing.json', timing)
    print(encoded(dict(state='actual-inputs-prepared; root must capture and review', frames=timing['frames'],
                       seconds=timing['durationSeconds'], nativeSeconds=timing['actualGameSeconds'],
                       job=str(JOB_PATH.resolve()), clips=len(clips), noUnityStarted=True)))


def capture_ready(native_reviewed, anchors_reviewed):
    execution_guard()
    if not native_reviewed or not anchors_reviewed:
        raise RuntimeError('After actual internal pixel review, pass --native-reviewed and --anchors-reviewed; file existence is not viewing.')
    captions, pcm, digest, bounds = actual_timing()
    timing = read(P / 'production/visual-timing.json')
    config = read(P / 'production/visual-config.json')
    job = read(JOB_PATH)
    if (job.get('preview') is not False or job.get('voiceSha256') != digest
            or timing.get('timingInputs', {}).get('voiceSha256') != digest
            or read(LOCAL / 'visual-timing.json') != timing or timing['frames'] != captions['frames']
            or Path(job['output']).resolve() != CAPTURE_OUTPUT.resolve()
            or config['unityFrames'].get('captureJobSHA256') != sha(JOB_PATH)):
        raise RuntimeError('Capture job/current timing/voice binding changed.')
    success = read(CAPTURE_OUTPUT / 'success.json')
    if (success.get('width'), success.get('height'), success.get('fps'), success.get('clips'), success.get('preview')) != (1080, 1920, 60, len(job['clips']), False):
        raise RuntimeError('Require a complete real nonpreview capture success receipt.')
    from PIL import Image
    rows = []
    uv = None
    for clip in job['clips']:
        directory = CAPTURE_OUTPUT / clip['id']
        receipt = read(directory / 'capture.json')
        files = sorted(directory.glob('*.jpg'))
        if (receipt.get('id') != clip['id'] or receipt.get('stage') != clip['stage']
                or receipt.get('frames') != clip['frames'] or receipt.get('preview') is not False
                or receipt.get('sourceKind') != 'our-Unity-implementation'
                or len(files) != clip['frames'] or files[0].name != '000000.jpg'
                or files[-1].name != f"{clip['frames'] - 1:06}.jpg"):
            raise RuntimeError('Unity receipt/file count differs: ' + clip['id'])
        for file in (files[0], files[-1]):
            with Image.open(file) as image:
                if image.size != (1080, 1920):
                    raise RuntimeError('Unity captured dimensions differ.')
        rows.append(dict(id=clip['id'], stage=clip['stage'], startFrame=clip['startFrame'],
                         endFrame=clip['endFrame'], frames=len(files), receiptSHA256=sha(directory / 'capture.json'),
                         firstSHA256=sha(files[0]), lastSHA256=sha(files[-1])))
        if clip['id'] == 'uv':
            uv = receipt['wallUV']
            if not all(math.isfinite(float(uv[key])) and abs(float(uv[key]) - .5) <= .001 for key in ('x', 'y')):
                raise RuntimeError('Actual wallUV differs from the narrated center example.')
        if clip['id'] == 'collision':
            observed = receipt.get('firstWallHitTimelineFrame', -1)
            if (receipt.get('cueSynchronized') is not True or observed < 0
                    or abs(observed - clip['expectedHitTimelineFrame']) > 1
                    or observed >= timing['events']['p3-2']['startFrame']):
                raise RuntimeError('Actual physical hit must precede the measured coordinate-conversion clause.')
        if clip['id'] == 'orbit':
            required = ['allCapturedTextureFramesChecked', 'paintBytesUnchangedAcrossCheckedFrames',
                        'textureObjectsUnchangedAcrossCheckedFrames', 'noTextureMutationsAfterFirstCheckedFrame',
                        'cameraMovedAcrossCheckedFrames']
            if any(receipt.get(key) is not True for key in required) or len(receipt.get('textureSamples', [])) != clip['frames']:
                raise RuntimeError('Require every orbit frame\'s actual CPU texture hash/object/upload evidence and changed camera.')
    if uv is None:
        raise RuntimeError('Actual UV-stage readback is missing.')
    config['unityFrames']['captured'] = True
    config['compositing']['anchorsReviewed'] = True
    config['compositing']['uvReadout'].update(u=float(uv['x']), v=float(uv['y']), runtimeVerified=True,
        evidencePath=str((CAPTURE_OUTPUT / 'uv/capture.json').resolve()))
    for key in ('floor', 'wall'):
        config['gameplayCuts'][key]['inspected'] = True
    config['framesPrepared'] = True
    config['readyForRender'] = True
    config['timing'] = 'Current actual PCM/21clauses and real Unity/native frame sequences bound; final moving/mobile/audio review remains pending.'
    record = dict(revision=REVISION, voiceSha256=digest, jobSHA256=sha(JOB_PATH),
                  captureSuccessSHA256=sha(CAPTURE_OUTPUT / 'success.json'), sequences=rows,
                  internalNativePixelReviewAttested=native_reviewed, internalUnityAnchorPixelReviewAttested=anchors_reviewed,
                  uvReadout=config['compositing']['uvReadout'], sourceKind='our-Unity-implementation',
                  nativeAudioAdopted=False, finalMovingMobileAudioReview='pending', humanReview='pending-local-final-version')
    save_exact(LOCAL / 'unity-capture-acceptance-v1.json', record)
    update_versioned(P / 'production/visual-config.json', config)
    print(encoded(dict(state='real-captures-bound; final QA pending', clips=len(rows), uv=uv,
                       humanFinalReview='pending', noRenderStarted=True)))


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
                           sections=7, clauses=21, noModelOrMediaJobStarted=True)))
        return
    if args.command == 'capture-ready':
        capture_ready(args.native_reviewed, args.anchors_reviewed)
    else:
        prepare()


if __name__ == '__main__':
    main()
