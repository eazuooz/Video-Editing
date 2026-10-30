"""Eight Unity visual replacements; preserve v4 timing, captions and AAC.

--prepare only writes the selected revision's local plan and readiness report.
--render requires actual hash-bound Unity source reviews, rewraps their H.264
timebase, retains every other v4 concat path, and copies audio from the v4 master.
--verify runs the existing compositor's structural checks, then compares audio
packets/decoded samples and every clean frame with the intended source frame.
No TTS, mixing, ASR, old-output replacement, publishing, or Unity launch occurs.

Unity review contract: production/local/unity-v5/source-review.json contains
sources[id]={sha256,motionReviewed:true,evidence,producerReceipt,
producerReceiptSha256}. The producer receipt binds sha256 and actualFrames.
All project-relative receipt paths resolve under this project, never the cwd.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

import assemble_documentary as asm

PROJECT = asm.PROJECT
BASE_WORK = PROJECT / 'production/local/documentary-v4'
BASE_PLAN = BASE_WORK / 'timeline.json'
BASE_OUT = asm.REPO / 'output/buckshot-roulette-reverse-engineering-v4'
CUES = PROJECT / 'production/unity-workflow-v5-cues.json'
UNITY = PROJECT / 'production/local/unity-v5'
WORK = PROJECT / 'production/local/documentary-v5'
OUT = asm.REPO / 'output/buckshot-roulette-reverse-engineering-v5'
STEM = PROJECT.name
TOTAL_FRAMES, BODY_FRAMES = 24718, 23998
BASE_MASTER_SHA = {
    'clean': '920e6ecfb8e65b3ae8c9ea821707b7718f021e5460148a25ef31756cf25f0816',
    'captioned': '58891b5c9e52d50dda41db070fe12f7c7d7fec15e8d9884eed96274f76323fa3',
}


def require(value, message):
    if not value:
        raise ValueError(message)


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def binding(path):
    path = Path(path).resolve()
    require(path.is_file(), 'Required input missing: ' + str(path))
    return {'path': str(path), 'sha256': asm.digest(path)}


def project_path(value):
    path = Path(value)
    path = path.resolve() if path.is_absolute() else (PROJECT / path).resolve()
    require(path.is_relative_to(PROJECT), 'Evidence must remain inside selected project: ' + str(path))
    return path


def scoped_authorization():
    control = asm.load(asm.REPO / 'shared/publishing/video-production-control.json')
    auth = control.get('scopedSetupAuthorizations', {}).get(STEM, {})
    project = asm.load(PROJECT / 'project.json')
    require(auth.get('productionAllowedNow') is True and auth.get('revision') == 'v5',
            'Current project-scoped v5 production authorization is required')
    require(project.get('startGate', {}).get('productionAllowedNow') is True and
            project.get('revision', {}).get('id') == 'v5', 'Selected project must still be at v5')


@contextmanager
def expensive_job_guard():
    """Re-read scope before each FFmpeg/count-frames job, including asm.verify."""
    original_ff, original_probe = asm.ff, asm.probe
    def ff(*args, **kwargs):
        scoped_authorization()
        return original_ff(*args, **kwargs)
    def probe(path, plan, count=False):
        if count:
            scoped_authorization()
        return original_probe(path, plan, count=count)
    asm.ff, asm.probe = ff, probe
    try:
        yield
    finally:
        asm.ff, asm.probe = original_ff, original_probe


@contextmanager
def job_lock():
    WORK.mkdir(parents=True, exist_ok=True)
    path = WORK / 'build-edit-v5.lock.json'
    try:
        with path.open('x', encoding='utf-8') as stream:
            json.dump({'pid': os.getpid(), 'startedAt': asm.now(), 'script': str(Path(__file__))}, stream)
    except FileExistsError:
        raise RuntimeError('Existing v5 edit lock; inspect its process before retrying. No process will be stopped: ' + str(path))
    try:
        yield
    finally:
        if path.is_file() and asm.load(path).get('pid') == os.getpid():
            path.unlink()


def concat_paths(path):
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    require(lines[0].strip() == 'ffconcat version 1.0', 'Unsupported v4 concat manifest')
    paths = []
    for line in lines[1:]:
        if not line.strip():
            continue
        match = re.fullmatch(r"file '([^']+)'", line.strip())
        require(match, 'Unexpected v4 concat directive: ' + line)
        p = Path(match[1])
        paths.append(p.resolve() if p.is_absolute() else (path.parent / p).resolve())
    return paths


def video_metadata(path, plan, expected_frames, timebase=None, allow_existing_full_range=False):
    meta = asm.probe(path, plan)
    streams = [s for s in meta['streams'] if s['codec_type'] == 'video']
    require(len(streams) == 1, 'Exactly one video stream required: ' + str(path))
    v = streams[0]
    require((v['width'], v['height'], Fraction(v['avg_frame_rate'])) == (1920, 1080, 60),
            'Expected native 1920x1080 at 60fps: ' + str(path))
    frames = v.get('nb_frames')
    if frames in (None, 'N/A'):
        v = asm.video_stream(asm.probe(path, plan, count=True))
        frames = v.get('nb_read_frames')
    require(int(frames) == expected_frames, 'Exact frame count differs: ' + str(path))
    # The hash-verified v4 prototype cuts include full-range H.264 (yuvj420p).
    # Keep those original packets and SPS range flags exactly; newly generated
    # Unity sources still require limited-range yuv420p. No conversion here.
    allowed_formats = ('yuv420p', 'yuvj420p') if allow_existing_full_range else ('yuv420p',)
    require(v['codec_name'] == 'h264' and v['pix_fmt'] in allowed_formats,
            'H.264 yuv420p source required; no silent format conversion: ' + str(path))
    require(v.get('sample_aspect_ratio', '1:1') in ('1:1', 'N/A'), 'Non-square source pixels')
    require(abs(float(v.get('start_time', 0))) <= 1 / 90000, 'Source must start at zero')
    require(abs(float(v['duration']) - expected_frames / 60) <= 1 / 90000 + .000001,
            'Clip duration does not equal its complete frames: ' + str(path))
    if timebase:
        require(Fraction(v['time_base']) == Fraction(timebase), 'Concat timebase differs: ' + str(path))
    return v


def source_review(entry, reviews, plan):
    """Return pending instead of approving nonexistent or unreviewed media."""
    ident = entry['id']
    path = UNITY / ident / 'render/unity.mp4'
    row = reviews.get(ident, {})
    result = {'id': ident, 'path': str(path), 'mode': entry['mode'],
              'frames': entry['frames'], 'bodyStartFrame': entry['bodyStartFrame']}
    blockers = []
    if not path.is_file():
        return result, [ident + ': Unity capture is not present']
    result['sha256'] = asm.digest(path)
    if row.get('sha256') != result['sha256'] or row.get('motionReviewed') is not True or not row.get('evidence'):
        blockers.append(ident + ': actual hash-bound motion review is pending')
    receipt_name = row.get('producerReceipt')
    if not receipt_name:
        blockers.append(ident + ': producer receipt is pending')
    else:
        receipt_path = project_path(receipt_name)
        if not receipt_path.is_file():
            blockers.append(ident + ': producer receipt file is missing')
        else:
            rb = binding(receipt_path)
            receipt = asm.load(receipt_path)
            require(row.get('producerReceiptSha256') == rb['sha256'], 'Producer receipt changed: ' + ident)
            require(receipt.get('sha256') == result['sha256'], 'Producer video hash differs: ' + ident)
            require(receipt.get('actualFrames') == entry['frames'], 'Producer frame count differs: ' + ident)
            require(receipt.get('completed', True) is not False, 'Producer marked incomplete: ' + ident)
            result['producerReceipt'] = rb
    result['review'] = copy.deepcopy(row)
    # Header probe only in prepare; frame-decode verification runs in --verify.
    result['video'] = video_metadata(path, plan, entry['frames'])
    require(not any(s['codec_type'] == 'audio' for s in asm.probe(path, plan)['streams']),
            'Unity replacement must be visual-only; original mix is preserved: ' + ident)
    return result, blockers


def prepare(write=True):
    scoped_authorization()
    base = asm.load(BASE_PLAN)
    require(base.get('revision') == 'v4' and base.get('bodyFrameCount') == BODY_FRAMES,
            'Unexpected v4 timeline')
    require(base.get('encoder') == 'libx264', 'Review a changed baseline encoder before composing v5')
    technical = asm.load(BASE_WORK / 'technical-qa.json')
    require(technical.get('technicalDecodePassed') is True and technical.get('pairedAudioIdentical') is True,
            'Verified v4 pair is required')
    masters = {}
    for kind in ['clean', 'captioned']:
        masters[kind] = binding(BASE_OUT / f'{STEM}.{kind}.mp4')
        require(masters[kind]['sha256'] == BASE_MASTER_SHA[kind] == technical['outputs'][kind]['sha256'],
                'Baseline master changed: ' + kind)
    manifest_path = BASE_WORK / 'visuals-concat.ffconcat'
    old_paths = concat_paths(manifest_path)
    beats = base['beats']
    require(len(beats) == 32 and len(old_paths) == 34, 'Expected 32 body cuts and two bookends')
    progress = asm.load(BASE_WORK / 'render-progress.json')
    require(progress.get('complete') is True, 'V4 render did not finish')
    prior = {r['cut']: r for r in progress['completedCuts']}
    cues = asm.load(CUES)
    entries = cues['entries']
    require(len(entries) == 8, 'This revision authorizes exactly eight replacement cuts')
    require(len({r['id'] for r in entries}) == 8, 'Unity IDs must be unique')
    for row in entries:
        require(re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', row['id']), 'Unsafe Unity ID')
        require(type(row['frames']) is int and row['frames'] > 0 and
                type(row['bodyStartFrame']) is int and row['bodyStartFrame'] >= 0,
                'Unity entries need positive integer frames and bodyStartFrame')
        require(row.get('mode') and isinstance(row.get('cues'), list), 'Missing Unity mode/cues')
    by_start = {r['bodyStartFrame']: r for r in entries}
    require(len(by_start) == 8, 'Replacement starts must be unique')
    review_path = UNITY / 'source-review.json'
    reviews = asm.load(review_path).get('sources', {}) if review_path.is_file() else {}
    require(isinstance(reviews, dict), 'Unity source reviews must be keyed by entry ID')
    blockers, cuts, replacements = [], [], []
    plan = copy.deepcopy(base)
    plan.update(revision='v5', workDirectory=str(WORK), outputDirectory=str(OUT),
                note='Eight selected Unity visual replacements; v4 captions, timing and AAC copied unchanged.',
                humanReview=False, editReady=False)
    cursor = 0
    for index, beat in enumerate(beats):
        path = old_paths[index + 1]
        old = prior[beat['id']]
        require(path == Path(old['video']).resolve(), 'V4 concat path differs from its render record')
        old_bind = binding(path)
        require(old_bind['sha256'] == old['sha256'], 'Original encoded cut changed: ' + beat['id'])
        replacement = by_start.get(cursor)
        row = {'id': beat['id'], 'frames': beat['frames'], 'bodyStartFrame': cursor,
               'finalStartFrame': cursor + 120, 'original': old_bind, 'replacement': None}
        if replacement:
            require(replacement['frames'] == beat['frames'], 'Unity replacement must occupy one exact existing cut')
            source, pending = source_review(replacement, reviews, base)
            blockers.extend(pending)
            replacements.append(source)
            row['replacement'] = source
            sid = 'unity-v5-' + replacement['id']
            plan['sources'][sid] = {'file': source['path'], 'sha256': source.get('sha256'),
                                    'kind': 'explanation', 'motionReviewed': not pending,
                                    'evidence': source.get('review', {}).get('evidence', '')}
            new = plan['beats'][index]
            new.update(source=sid, sourceInSeconds=0, sourceAudio=False, sourceAudioGainDb=0,
                       viewportHeight=1080, overlays=[], pictureLabel='', protectedRects=[],
                       observedAction='Unity-authored explanation: ' + replacement['mode'],
                       narrationConnection='Unchanged v4 speech and exact original cut interval',
                       unityId=replacement['id'])
        cuts.append(row)
        cursor += beat['frames']
    require(cursor == BODY_FRAMES and len(replacements) == 8, 'Not all Unity entries match exact existing cuts')
    require(cuts[0]['replacement'] is None, 'Preserve the actual-game/prototype abstract')
    for name, path, frames in [('branding', old_paths[0], 120), ('membership', old_paths[-1], 600)]:
        label = 'bookend-brand' if name == 'branding' else 'bookend-member'
        receipt = asm.load(BASE_WORK / (label + '.receipt.json'))
        require(path == BASE_WORK / (label + '.mp4'), 'Bookend concat path changed')
        b = binding(path)
        require(b['sha256'] == receipt['videoSha256'], 'Bookend changed: ' + name)
        entry = {'id': label, 'frames': frames, 'bodyStartFrame': None,
                 'finalStartFrame': 0 if name == 'branding' else TOTAL_FRAMES - 600,
                 'original': b, 'replacement': None}
        cuts.insert(0, entry) if name == 'branding' else cuts.append(entry)
    require(sum(r['frames'] for r in cuts) == TOTAL_FRAMES, 'Final duration changed')
    caption_files = {}
    for name in ['captions.ko.srt', 'captions.en.srt', 'captions.ko.ass']:
        caption_files[name] = binding(BASE_WORK / name)
    for language in ['ko', 'en']:
        require(asm.digest(BASE_OUT / f'{STEM}.{language}.srt') == caption_files[f'captions.{language}.srt']['sha256'],
                'Delivered SRT differs from v4 edit SRT')
    voice = binding(asm.resolve(base['narration']['wav']))
    require(voice['sha256'] == base['narration']['sha256'], 'Original narration PCM changed')
    reused_audio_qa = binding(PROJECT / 'production/local/final-qa-v4/audio-review.json')
    audio_qa = asm.load(reused_audio_qa['path'])
    require(audio_qa.get('masterSha256') == BASE_MASTER_SHA['captioned'] and
            audio_qa.get('technicalPassed') is True and audio_qa.get('wholeMixAsrCompared') is True,
            'Baseline audio content/technical evidence missing')
    plan['editReady'] = not blockers
    used = {b['source'] for b in plan['beats']}
    plan['sources'] = {k: v for k, v in plan['sources'].items() if k in used}
    snapshot = {'baselineTimeline': binding(BASE_PLAN), 'baselineConcat': binding(manifest_path),
                'baselineMasters': masters, 'baselineTechnicalQa': binding(BASE_WORK / 'technical-qa.json'),
                'narration': voice, 'captions': caption_files, 'cues': binding(CUES),
                'sourceReview': binding(review_path) if review_path.is_file() else None,
                'reusedAudioQa': reused_audio_qa, 'cuts': cuts,
                'assemblyScript': binding(Path(__file__)), 'baseAssembler': binding(Path(asm.__file__))}
    receipt = {'checkedAt': asm.now(), 'bodyFrames': BODY_FRAMES, 'totalFrames': TOTAL_FRAMES,
               'narrationSha256': voice['sha256'], 'koCues': len(asm.read_srt(BASE_WORK / 'captions.ko.srt')),
               'enCues': len(asm.read_srt(BASE_WORK / 'captions.en.srt')),
               'snapshotSha256': stable_hash(snapshot), 'snapshot': snapshot,
               'readiness': blockers, 'editReady': not blockers,
               'humanViewing': False, 'humanListening': False}
    if write:
        WORK.mkdir(parents=True, exist_ok=True)
        asm.save(WORK / 'timeline.json', plan)
        asm.save(WORK / 'preflight.json', receipt)
    return plan, receipt


def preserve_copy(source, target):
    if target.exists():
        require(asm.digest(source) == asm.digest(target), 'Existing v5 copy differs; inspect before changing: ' + str(target))
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def normalized_unity(source, plan):
    target = WORK / 'normalized' / (source['id'] + '.mp4')
    receipt_path = target.with_suffix('.receipt.json')
    fingerprint = {'sourceSha256': source['sha256'], 'frames': source['frames'], 'timebase': '1/90000',
                   'producerReceiptSha256': source['producerReceipt']['sha256'], 'method': 'H264 packet copy only'}
    if target.exists() and receipt_path.exists():
        receipt = asm.load(receipt_path)
        require(receipt['input'] == fingerprint and receipt['sha256'] == asm.digest(target),
                'Existing normalized Unity clip differs; inspect before retrying')
    else:
        require(not target.exists(), 'Unreceipted normalized clip exists: ' + str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        asm.ff(plan, ['-i', source['path'], '-map', '0:v:0', '-an', '-c:v', 'copy',
                      '-video_track_timescale', '90000', '-map_metadata', '-1', '-write_tmcd', '0',
                      '-movflags', '+faststart', target], WORK / 'logs' / (source['id'] + '.rewrap.log'))
        video_metadata(target, plan, source['frames'], '1/90000')
        asm.save(receipt_path, {'input': fingerprint, 'sha256': asm.digest(target), 'completedAt': asm.now(),
                                'videoReencoded': False, 'decodedPixelEqualityPending': True})
    video_metadata(target, plan, source['frames'], '1/90000')
    return target


def render(plan, receipt):
    require(receipt['editReady'], 'Unity readiness: ' + '; '.join(receipt['readiness']))
    OUT.mkdir(parents=True, exist_ok=True)
    clean, captioned = [OUT / f'{STEM}.{kind}.mp4' for kind in ['clean', 'captioned']]
    require(not clean.exists() and not captioned.exists(), 'V5 masters already exist; use --verify, never overwrite')
    for name, value in receipt['snapshot']['captions'].items():
        preserve_copy(Path(value['path']), WORK / name)
    paths, actual_cuts = [], []
    for row in receipt['snapshot']['cuts']:
        source = row['replacement']
        path = normalized_unity(source, plan) if source else Path(row['original']['path'])
        video_metadata(path, plan, row['frames'], '1/90000', allow_existing_full_range=source is None)
        paths.append(path)
        actual_cuts.append({'id': row['id'], 'finalStartFrame': row['finalStartFrame'], 'frames': row['frames'],
                            'path': str(path), 'sha256': asm.digest(path), 'unityId': source['id'] if source else None})
    # FFmpeg's concat demuxer auto_convert=1 inserts Annex-B SPS/PPS at source
    # boundaries. Different NVENC/x264 SPS are allowed, not assumed identical.
    # Only new clips were remuxed; every retained source path is the v4 path.
    asm.concat(plan, paths, WORK / 'visuals.mp4', WORK, 'visuals-concat')
    video_metadata(WORK / 'visuals.mp4', plan, TOTAL_FRAMES, '1/90000')
    base_clean = Path(receipt['snapshot']['baselineMasters']['clean']['path'])
    asm.ff(plan, ['-i', WORK / 'visuals.mp4', '-i', base_clean, '-map', '0:v:0', '-map', '1:a:0',
                  '-c', 'copy', '-video_track_timescale', '90000', '-map_metadata', '-1',
                  '-movflags', '+faststart', clean], WORK / 'logs/clean-master.log')
    asm.ff(plan, ['-i', clean, '-vf', 'ass=captions.ko.ass', '-map', '0:v:0', '-map', '0:a:0',
                  *asm.encoder(plan), '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-video_track_timescale', '90000',
                  '-map_metadata', '-1', '-movflags', '+faststart', captioned], WORK / 'logs/captioned-master.log', WORK)
    for language in ['ko', 'en']:
        preserve_copy(WORK / f'captions.{language}.srt', OUT / f'{STEM}.{language}.srt')
    asm.write_index(OUT, STEM)
    asm.save(WORK / 'render-progress.json', {'completedAt': asm.now(), 'complete': True,
        'snapshotSha256': receipt['snapshotSha256'], 'cuts': actual_cuts,
        'outputs': {k: binding(OUT / f'{STEM}.{k}.mp4') for k in ['clean', 'captioned']},
        'audioOperation': 'Copy v4 final AAC packets; no encode, remix, normalization or ASR',
        'captionsOperation': 'Exact copied v4 SRT and ASS; captioned video re-encoded to burn unchanged ASS',
        'retainedCaptionedVideoBytesClaimedIdentical': False, 'humanViewing': False, 'humanListening': False})


def packet_report(path, plan, label):
    """Bind actual AAC bytes, timestamps, durations and skip-sample metadata."""
    scoped_authorization()
    args = [asm.tool('ffprobe', plan), '-v', 'error', '-select_streams', 'a:0', '-show_packets',
            '-show_data_hash', 'sha256', '-show_entries',
            'packet=pts,dts,duration,size,flags,data_hash,side_data_list', '-of', 'json', str(path)]
    result = json.loads(subprocess.check_output(args, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)))
    packets = result.get('packets', [])
    require(packets and all(p.get('data_hash', '').startswith('SHA256:') for p in packets), 'AAC packet hashes absent')
    target = WORK / 'proof' / (label + '.aac-packets.json')
    asm.save(target, {'file': binding(path), 'packetCount': len(packets), 'packets': packets,
                      'packetSequenceSha256': stable_hash(packets), 'command': list(map(str, args))})
    return {'path': str(target), 'sha256': asm.digest(target), 'packetCount': len(packets),
            'packetSequenceSha256': stable_hash(packets)}


def decoded_audio_hash(path, plan, label):
    target = WORK / 'proof' / (label + '.audio-f32.sha256')
    target.parent.mkdir(parents=True, exist_ok=True)
    asm.ff(plan, ['-i', path, '-map', '0:a:0', '-c:a', 'pcm_f32le', '-f', 'hash', '-hash', 'sha256', target],
           WORK / 'logs' / (label + '.audio-f32.log'))
    value = target.read_text(encoding='utf-8').strip()
    require(re.fullmatch(r'SHA256=[0-9a-fA-F]{64}', value), 'Invalid decoded audio hash')
    return value


def frame_hashes(path, plan, label, expected_frames):
    folder = WORK / 'proof'
    folder.mkdir(parents=True, exist_ok=True)
    target, cache = folder / (label + '.framehash'), folder / (label + '.framehash.json')
    fingerprint = {'file': binding(path), 'frames': expected_frames,
                   'decode': 'software H264 to original yuv420p; passthrough frame rate; SHA256 per raw frame'}
    if cache.exists() and target.exists():
        old = asm.load(cache)
        require(old['input'] == fingerprint and old['sha256'] == asm.digest(target), 'Changed frame proof cache')
    else:
        require(not target.exists(), 'Unreceipted frame proof exists; inspect before retry')
        asm.ff(plan, ['-threads', '2', '-i', path, '-map', '0:v:0', '-an', '-c:v', 'rawvideo', '-threads:v', '1',
                      '-pix_fmt', 'yuv420p', '-fps_mode', 'passthrough', '-f', 'framehash', '-hash', 'sha256', target],
               WORK / 'logs' / (label + '.framehash.log'))
        asm.save(cache, {'input': fingerprint, 'sha256': asm.digest(target), 'completedAt': asm.now()})
    rows = []
    for line in target.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split(',')]
        require(len(parts) == 6 and re.fullmatch(r'[0-9a-fA-F]{64}', parts[-1]), 'Malformed decoded frame hash')
        rows.append({'pts': int(parts[2]), 'duration': int(parts[3]), 'size': int(parts[4]), 'sha256': parts[-1]})
    require(len(rows) == expected_frames, 'Decoded frame proof count differs: ' + label)
    return rows, binding(target)


def verify(plan, receipt):
    require(receipt['editReady'], 'Unity source review is not ready')
    progress = asm.load(WORK / 'render-progress.json')
    require(progress.get('complete') is True and progress['snapshotSha256'] == receipt['snapshotSha256'],
            'Inputs changed since v5 render; do not reuse verification')
    for kind in ['clean', 'captioned']:
        require(binding(OUT / f'{STEM}.{kind}.mp4') == progress['outputs'][kind], 'V5 master changed after render')
    for name, source in receipt['snapshot']['captions'].items():
        require(asm.digest(WORK / name) == source['sha256'], 'V4 caption copy changed')
    for language in ['ko', 'en']:
        require(asm.digest(OUT / f'{STEM}.{language}.srt') == receipt['snapshot']['captions'][f'captions.{language}.srt']['sha256'],
                'Delivered subtitle changed')
    technical = asm.verify(plan, receipt, WORK)
    technical.update(visualOnlyRevision='v5', preservationVerificationPassed=False,
                     remaining=['AAC and clean-frame preservation verification is still running',
                                'Actual new Unity/caption/cut visual review', 'User full-version review'])
    asm.save(WORK / 'technical-qa.json', technical)
    packets, pcm = {}, {}
    for label, path in [('v4-clean', BASE_OUT / f'{STEM}.clean.mp4'),
                        ('v4-captioned', BASE_OUT / f'{STEM}.captioned.mp4'),
                        ('v5-clean', OUT / f'{STEM}.clean.mp4'),
                        ('v5-captioned', OUT / f'{STEM}.captioned.mp4')]:
        packets[label] = packet_report(path, plan, label)
        pcm[label] = decoded_audio_hash(path, plan, label)
    require(len({v['packetSequenceSha256'] for v in packets.values()}) == 1,
            'Actual AAC packet bytes/timestamps/skip-samples changed')
    require(len(set(pcm.values())) == 1, 'Actual decoded FLOAT audio differs from v4')
    baseline, baseline_proof = frame_hashes(BASE_OUT / f'{STEM}.clean.mp4', plan, 'v4-clean', TOTAL_FRAMES)
    actual, current_proof = frame_hashes(OUT / f'{STEM}.clean.mp4', plan, 'v5-clean', TOTAL_FRAMES)
    expected = [r['sha256'] for r in baseline]
    frame_evidence = []
    for row in receipt['snapshot']['cuts']:
        if not row['replacement']:
            continue
        replacement = row['replacement']
        frames, proof = frame_hashes(Path(replacement['path']), plan, 'unity-' + replacement['id'], row['frames'])
        start = row['finalStartFrame']
        expected[start:start + row['frames']] = [r['sha256'] for r in frames]
        frame_evidence.append({'unityId': replacement['id'], 'finalStartFrame': start,
                               'frames': row['frames'], 'decodedSourceProof': proof})
    mismatches = [i for i, (a, b) in enumerate(zip(actual, expected)) if a['sha256'] != b]
    frame_report = {'checkedAt': asm.now(), 'frames': TOTAL_FRAMES, 'mismatchCount': len(mismatches),
                    'mismatchFrames': mismatches[:100], 'baseline': baseline_proof, 'current': current_proof,
                    'replacements': frame_evidence, 'allCleanFramesMatchIntendedSources': not mismatches,
                    'captionedVideoByteEqualityClaimed': False,
                    'scope': 'Every clean decoded pixel frame: unchanged v4 outside the eight intervals, actual Unity source inside them. Captioned frames require visual QA; ASS and SRT are exact copies.'}
    asm.save(WORK / 'proof/frame-preservation.json', frame_report)
    require(not mismatches, 'Decoded pixels differ from intended old/Unity frames; possible H264 boundary failure')
    # Framehash timestamps must be a single continuous CFR output, independent
    # of the different H.264 encoder parameter sets at input boundaries.
    require(all(b['pts'] - a['pts'] == a['duration'] and a['duration'] > 0
                for a, b in zip(actual, actual[1:])), 'Final decoded frame timestamps are discontinuous')
    proof = {'checkedAt': asm.now(), 'revision': 'v5', 'technicalPassed': True,
             'snapshotSha256': receipt['snapshotSha256'], 'totalFrames': TOTAL_FRAMES,
             'baselineMasters': receipt['snapshot']['baselineMasters'],
             'currentMasters': {k: binding(OUT / f'{STEM}.{k}.mp4') for k in ['clean', 'captioned']},
             'sourceCuts': receipt['snapshot']['cuts'], 'captions': receipt['snapshot']['captions'],
             'audioPackets': packets, 'decodedFloatAudioHashes': pcm,
             'aacPacketsAndTimestampsUnchanged': True, 'decodedAudioUnchanged': True,
             'newTts': False, 'newAudioMix': False, 'newAsr': False,
             'audioContentReviewReusedFrom': receipt['snapshot']['reusedAudioQa'],
             'cleanFramePreservation': binding(WORK / 'proof/frame-preservation.json'),
             'remaining': ['Actual new Unity/caption/cut visual review', 'User full-version review'],
             'humanViewing': False, 'humanListening': False, 'userApproval': False}
    asm.save(WORK / 'preservation-proof.json', proof)
    technical.update(visualOnlyRevision='v5', preservationVerificationPassed=True,
                     audioContentReview='reused after exact packet and FLOAT equality with v4',
                     preservationProof=str(WORK / 'preservation-proof.json'),
                     remaining=proof['remaining'])
    asm.save(WORK / 'technical-qa.json', technical)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    with job_lock(), expensive_job_guard():
        plan, receipt = prepare(write=not args.verify or args.render or args.prepare)
        if args.render:
            render(plan, receipt)
        if args.verify:
            verify(plan, receipt)
        print(json.dumps({'status': 'pending-sources' if not receipt['editReady'] else 'verified' if args.verify else 'rendered' if args.render else 'prepared',
                          'timeline': str(WORK / 'timeline.json'), 'totalFrames': TOTAL_FRAMES,
                          'replacementCuts': 8, 'retainedCutsIncludingBookends': 26,
                          'readiness': receipt['readiness'], 'newTts': False, 'newMix': False, 'newAsr': False,
                          'humanViewing': False, 'humanListening': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
