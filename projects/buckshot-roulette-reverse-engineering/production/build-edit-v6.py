"""Add the selected 30-second 2x real-game opening and Nimbus music to v5.

--prepare binds inspected sources and writes captions/timeline, never renders.
--render preserves all 34 v5 picture cuts and original pre-limiter body audio.
--verify proves timing, encoded audio equality and every clean decoded frame.
Final motion/listening/whole-mix ASR and human review are separate, never inferred.
No TTS, old-master overwrite, upload, Unity launch or unrelated production.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import copy
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

import assemble_documentary as asm

PROJECT, REPO = asm.PROJECT, asm.REPO
STEM = PROJECT.name
BASE_WORK = PROJECT / 'production/local/documentary-v5'
AUDIO_WORK = PROJECT / 'production/local/documentary-v4'
BASE_OUT = REPO / 'output/buckshot-roulette-reverse-engineering-v5'
WORK = PROJECT / 'production/local/documentary-v6'
OUT = REPO / 'output/buckshot-roulette-reverse-engineering-v6'
INTRO_PLAN = PROJECT / 'planning/intro-gameplay-v6.json'
AUDIO_PLAN = PROJECT / 'planning/audio-v6-plan.json'
BASE_FRAMES, BODY_FRAMES, INTRO_FRAMES, TOTAL_FRAMES = 24718, 23998, 1800, 26518
TOTAL_SAMPLES = TOTAL_FRAMES * 800
VOICE_SHA = '6eb0f483642fc4a99b102abb54ea710fc0f8cb21d7a2b8c78f824b769d8e9835'
BASE_MASTER_SHA = {'clean': '4ff5235cc920b6074a95a7dfab47f74fe4d29d1525585d0f4d5efe0f2399b761',
                   'captioned': '237bbc43bfee67b0f8d5d74e20fac568a51b08b822e3337ec152603afd374450'}


def require(value, message):
    if not value:
        raise ValueError(message)


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode('utf-8')).hexdigest()


def binding(path):
    path = Path(path).resolve()
    require(path.is_file(), 'Required input missing: ' + str(path))
    return {'path': str(path), 'sha256': asm.digest(path)}


def scoped_authorization():
    control = asm.load(REPO / 'shared/publishing/video-production-control.json')
    auth = control.get('scopedSetupAuthorizations', {}).get(STEM, {})
    project = asm.load(PROJECT / 'project.json')
    require(auth.get('productionAllowedNow') is True and auth.get('revision') == 'v6',
            'Current selected-project v6 production authorization is required')
    require(project.get('startGate', {}).get('productionAllowedNow') is True and
            project.get('revision', {}).get('id') == 'v6', 'Project must remain selected at v6')


@contextmanager
def expensive_job_guard():
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
    path = WORK / 'build-edit-v6.lock.json'
    try:
        with path.open('x', encoding='utf-8') as stream:
            json.dump({'pid': os.getpid(), 'startedAt': asm.now(), 'script': str(Path(__file__))}, stream)
    except FileExistsError:
        raise RuntimeError('Existing v6 lock; inspect its process before retrying. No process will be stopped: ' + str(path))
    try:
        yield
    finally:
        if path.is_file() and asm.load(path).get('pid') == os.getpid():
            path.unlink()


def video_metadata(path, plan, expected_frames, retained=False):
    meta = asm.probe(path, plan)
    streams = [s for s in meta['streams'] if s['codec_type'] == 'video']
    require(len(streams) == 1, 'Exactly one video stream required: ' + str(path))
    v = streams[0]
    require((v['width'], v['height'], Fraction(v['avg_frame_rate'])) == (1920, 1080, 60),
            'Expected 1920x1080 at 60fps: ' + str(path))
    frames = v.get('nb_frames')
    if frames in (None, 'N/A'):
        frames = asm.video_stream(asm.probe(path, plan, count=True))['nb_read_frames']
    require(int(frames) == expected_frames, 'Exact frame count differs: ' + str(path))
    require(v['codec_name'] == 'h264' and v['pix_fmt'] in
            (('yuv420p', 'yuvj420p') if retained else ('yuv420p',)), 'Unexpected H264 pixel format')
    require(Fraction(v['time_base']) == Fraction(1, 90000), 'Concat requires 90k timebase')
    require(abs(float(v.get('start_time', 0))) <= 1 / 90000, 'Video must start at zero')
    require(abs(float(v['duration']) - expected_frames / 60) <= 1 / 90000 + 1e-6,
            'Video duration differs from exact frames')
    return v


def audio_samples(path, plan, expected=None):
    streams = [s for s in asm.probe(path, plan)['streams'] if s['codec_type'] == 'audio']
    require(len(streams) == 1, 'One audio stream required: ' + str(path))
    a = streams[0]
    require(a['sample_rate'] == '48000' and a['channels'] == 2, 'Expected 48kHz stereo')
    samples = Fraction(int(a['duration_ts'])) * Fraction(a['time_base']) * 48000
    require(samples.denominator == 1, 'Non-integral audio sample duration')
    if expected is not None:
        require(samples == expected, 'Exact audio sample count differs: ' + str(path))
    return int(samples)


def source_input(path, sha):
    value = binding(asm.resolve(path))
    require(value['sha256'] == sha, 'Source changed: ' + value['path'])
    return value


def prepare(write=True):
    scoped_authorization()
    base_plan = asm.load(BASE_WORK / 'timeline.json')
    base_progress = asm.load(BASE_WORK / 'render-progress.json')
    require(base_progress.get('complete') is True, 'V5 baseline must be complete')
    original_cuts = copy.deepcopy(base_progress['cuts'])
    require(len(original_cuts) == 34 and sum(c['frames'] for c in original_cuts) == BASE_FRAMES,
            'V5 baseline cut inventory changed')
    require(original_cuts[0]['id'] == 'bookend-brand' and original_cuts[0]['frames'] == 120 and
            original_cuts[-1]['frames'] == 600, 'Original bookends changed')
    cursor = 0
    for cut in original_cuts:
        require(cut['finalStartFrame'] == cursor, 'Non-contiguous v5 cut timeline')
        cut['input'] = source_input(cut['path'], cut['sha256'])
        video_metadata(Path(cut['path']), base_plan, cut['frames'], retained=True)
        cursor += cut['frames']
    masters = {}
    for kind in ['clean', 'captioned']:
        masters[kind] = source_input(BASE_OUT / f'{STEM}.{kind}.mp4', BASE_MASTER_SHA[kind])
        require(masters[kind] == base_progress['outputs'][kind], 'V5 master receipt differs')
    intro = asm.load(INTRO_PLAN)
    audio = asm.load(AUDIO_PLAN)
    clips = copy.deepcopy(intro['clips'])
    require(len(clips) == 6 and sum(c['outputFrames'] for c in clips) == INTRO_FRAMES,
            'Exactly six inspected clips and 1800 intro frames required')
    source_bindings = {}
    for clip in clips:
        path = asm.resolve(clip['sourcePath'])
        if str(path) not in source_bindings:
            source_bindings[str(path)] = source_input(path, clip['sourceSha256'])
        require(source_bindings[str(path)]['sha256'] == clip['sourceSha256'], 'Intro source SHA differs')
        require(clip['speed'] == 2 and clip['sourceStartSeconds'] >= 0 and
                Fraction(str(clip['sourceDurationSeconds'])) * 30 == clip['outputFrames'],
                'Intro cut must use exact 2x mapping, no loop/freeze/padding')
        require(clip.get('frameSequenceReviewed') is True or clip.get('motionReviewed') is True,
                'Actual source image inspection evidence required')
        meta = asm.probe(path, base_plan)
        v = asm.video_stream(meta)
        require(v['width'] >= 1920 and v['height'] >= 1080 and Fraction(v['avg_frame_rate']) == 60,
                'Intro actual source must be genuine FHD60')
        require(float(meta['format']['duration']) + .001 >=
                clip['sourceStartSeconds'] + clip['sourceDurationSeconds'], 'Source interval outside file')
        require(any(s['codec_type'] == 'audio' for s in meta['streams']), 'Actual intro audio missing')
        clip['sourcePath'] = str(path)
    stems = {}
    for row in audio['verifiedExistingStems']:
        stems[row['role']] = source_input(row['path'], row['sha256'])
    require(stems['approved-narration-source']['sha256'] == VOICE_SHA, 'Approved narration changed')
    music = audio['music']
    music_binding = source_input(music['absolutePath'], music['sha256'])
    license_binding = binding(music['licenseRecord'])
    require(music['recommendedInitialIntegratedLufs'] == -28 and
            abs(music['initialStaticGainDb'] - (-28 - music['reusedMeasurement']['integratedLufs'])) < .001,
            'Music static gain is not bound to the existing source loudness measurement')
    require(music['sidechain']['duckTarget'].startswith('music only'), 'Music-only narration sidechain required')
    intervals = music['extraMusicDuckIntervalsFinalSeconds']
    require(intervals and all(0 <= a < b <= TOTAL_FRAMES / 60 for a, b in intervals),
            'Game-audio attenuation intervals must use final v6 seconds')
    captions = {lang: binding(BASE_OUT / f'{STEM}.{lang}.srt') for lang in ['ko', 'en']}
    source_captions = {lang: binding(asm.resolve(base_plan['narration'][f'{lang}Srt'])) for lang in ['ko', 'en']}
    snapshot = {'baselinePlan': binding(BASE_WORK / 'timeline.json'),
        'baselineProgress': binding(BASE_WORK / 'render-progress.json'), 'baselineMasters': masters,
        'originalCuts': original_cuts, 'introPlan': binding(INTRO_PLAN), 'introSources': source_bindings,
        'audioPlan': binding(AUDIO_PLAN), 'stems': stems, 'music': music_binding, 'musicLicense': license_binding,
        'baselineCaptions': captions, 'sourceCaptions': source_captions,
        'assembler': binding(Path(asm.__file__)), 'builder': binding(Path(__file__))}
    plan = copy.deepcopy(base_plan)
    plan.update(revision='v6', editReady=True, encoder='libx264', workDirectory=str(WORK),
                outputDirectory=str(OUT), bodyFrameCount=BODY_FRAMES + INTRO_FRAMES,
                note='V5 picture/body PCM preserved; add 30s actual gameplay at2x and continuous Nimbus BGM.')
    intro_beats = []
    for clip in clips:
        source_id = 'intro-' + clip['id']
        plan['sources'][source_id] = {'file': clip['sourcePath'], 'sha256': clip['sourceSha256'],
            'kind': 'actual-gameplay', 'frameSequenceReviewed': True,
            'motionReviewed': clip.get('motionReviewed', False), 'evidence': str(INTRO_PLAN)}
        intro_beats.append({'id': source_id, 'source': source_id, 'sourceInSeconds': clip['sourceStartSeconds'],
            'frames': clip['outputFrames'], 'speed': 2, 'loop': False, 'freeze': False,
            'sourceAudio': True, 'viewportHeight': 1080, 'pictureLabel': '실제 플레이 · 2배속',
            'protectedRects': [], 'overlays': [], 'observedAction': clip.get('teachingRole', ''),
            'narrationConnection': 'User-requested actual gameplay opening; original voice starts at32s.'})
    plan['beats'] = intro_beats + plan['beats']
    require(sum(b['frames'] for b in plan['beats']) == BODY_FRAMES + INTRO_FRAMES, 'Body timeline differs')
    plan['narration'].update(voiceOffsetSeconds=32, timeOrigin='WAV source starts at final32s; body-relative SRT includes30s intro.')
    for lang in ['ko', 'en']:
        plan['narration'][f'{lang}Srt'] = str(WORK / f'narration-body-offset.{lang}.srt')
    receipt = {'createdAt': asm.now(), 'editReady': True, 'revision': 'v6', 'bodyFrames': BODY_FRAMES + INTRO_FRAMES,
        'totalFrames': TOTAL_FRAMES, 'audioSamples': TOTAL_SAMPLES, 'narrationSha256': VOICE_SHA,
        'snapshot': snapshot, 'snapshotSha256': stable_hash(snapshot), 'clips': clips,
        'newTts': False, 'newAudioMix': True, 'humanViewing': False, 'humanListening': False,
        'remaining': ['Current 2x opening and body-entry moving visual/audio review',
                      'Current full mixed-output ASR and localized narration continuity review',
                      '1080p/mobile caption and transition review', 'User local final review']}
    if write:
        WORK.mkdir(parents=True, exist_ok=True)
        for lang in ['ko', 'en']:
            cues = asm.read_srt(captions[lang]['path'])
            asm.write_srt(WORK / f'captions.{lang}.srt', cues, 30)
            body_cues = asm.read_srt(source_captions[lang]['path'])
            asm.write_srt(WORK / f'narration-body-offset.{lang}.srt', body_cues, 30)
        layout = asm.caption_ass(WORK / 'captions.ko.ass', asm.read_srt(source_captions['ko']['path']),
                                 32, plan.get('captionEmphasis', {}))
        asm.save(WORK / 'caption-layout.json', layout)
        asm.save(WORK / 'timeline.json', plan)
        asm.save(WORK / 'preflight.json', receipt)
    return plan, receipt, audio


def speed_label():
    lines = asm.ass_header(size=40)
    # A truthful editorial speed/source label, away from central gun/action and fixed captions.
    asm.event(lines, 0, 30, r'{\an7\pos(48,42)\p1\bord0\shad0\1c&H101714&}m 0 0 l 510 0 510 72 0 72', 0)
    asm.event(lines, 0, 30, r'{\an7\pos(66,54)\bord0\shad0\1c&HFFFFFF&}실제 플레이 · {\1c&H83CFE8&}2배속', 1)
    target = WORK / 'intro-speed.ass'
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return target


def render_intro(plan, receipt):
    overlay = speed_label()
    video_paths, audio_paths, rows = [], [], []
    cursor = 120
    for clip in receipt['clips']:
        ident = 'intro-' + clip['id']
        video, wav = WORK / (ident + '.mp4'), WORK / (ident + '.raw.wav')
        cache = WORK / (ident + '.receipt.json')
        fp = {'clip': clip, 'overlaySha256': asm.digest(overlay),
              'builderSha256': receipt['snapshot']['builder']['sha256'], 'encoder': asm.encoder(plan)}
        if cache.exists() and video.exists() and wav.exists():
            previous = asm.load(cache)
            require(previous['input'] == fp and previous['videoSha256'] == asm.digest(video) and
                    previous['audioSha256'] == asm.digest(wav), 'Existing intro cache changed: ' + ident)
        else:
            require(not video.exists() and not wav.exists(), 'Partial intro output exists; inspect before retry: ' + ident)
            start, duration, frames = clip['sourceStartSeconds'], clip['sourceDurationSeconds'], clip['outputFrames']
            vf = (f'trim=duration={duration:.9f},setpts=(PTS-STARTPTS)/2,'
                  'scale=1920:1080:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,'
                  'pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps=60,'
                  'format=yuv420p,setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709,'
                  'ass=intro-speed.ass')
            asm.ff(plan, ['-ss', f'{start:.9f}', '-i', clip['sourcePath'], '-an', '-vf', vf,
                '-frames:v', str(frames), *asm.encoder(plan), '-video_track_timescale', '90000',
                '-map_metadata', '-1', '-write_tmcd', '0', '-movflags', '+faststart', video],
                WORK / 'logs' / (ident + '.video.log'), WORK)
            af = (f'atrim=duration={duration:.9f},asetpts=PTS-STARTPTS,aresample=48000,atempo=2,'
                  f'afade=t=in:d=0.12,afade=t=out:st={frames/60-.3:.9f}:d=0.3,'
                  f'apad,atrim=end_sample={frames*800}')
            asm.ff(plan, ['-ss', f'{start:.9f}', '-i', clip['sourcePath'], '-vn', '-af', af,
                '-ar', '48000', '-ac', '2', '-c:a', 'pcm_f32le', wav], WORK / 'logs' / (ident + '.audio.log'))
            video_metadata(video, plan, frames)
            audio_samples(wav, plan, frames * 800)
            asm.save(cache, {'input': fp, 'videoSha256': asm.digest(video),
                'audioSha256': asm.digest(wav), 'completedAt': asm.now(), 'humanViewing': False})
        video_metadata(video, plan, clip['outputFrames'])
        audio_samples(wav, plan, clip['outputFrames'] * 800)
        video_paths.append(video)
        audio_paths.append(wav)
        rows.append({'id': ident, 'finalStartFrame': cursor, 'frames': clip['outputFrames'],
                     **binding(video), 'kind': 'actual-gameplay', 'speed': 2, 'source': clip})
        cursor += clip['outputFrames']
    return video_paths, audio_paths, rows


def measure_loudness(plan, path, label):
    log = WORK / 'logs' / (label + '.ebur128.log')
    asm.ff(plan, ['-v', 'info', '-i', path, '-map', '0:a:0', '-af', 'ebur128=peak=true', '-f', 'null', '-'], log)
    data = log.read_text(encoding='utf-8', errors='replace')
    values = {}
    for key, pattern in [('integratedLufs', r'Integrated loudness:\s+I:\s+(-?\d+(?:\.\d+)?)'),
                         ('truePeakDbtp', r'True peak:\s+Peak:\s+(-?\d+(?:\.\d+)?)'),
                         ('lraLu', r'Loudness range:\s+LRA:\s+(\d+(?:\.\d+)?)')]:
        match = re.findall(pattern, data)
        require(match, 'No real ' + key + ' measurement: ' + str(log))
        values[key] = float(match[-1])
    return {**values, 'file': binding(path), 'log': binding(log)}


def music_presence_expression(intervals, ramp=.45, gain_db=-3):
    """Smooth gain on music only; union prevents double attenuation at joins."""
    terms = [f'max(0,min(1,min((t-({start-ramp:.9f}))/{ramp:.9f},'
             f'(({end+ramp:.9f})-t)/{ramp:.9f})))' for start, end in intervals]
    presence = terms[0]
    for term in terms[1:]:
        presence = f'max({presence},{term})'
    return f'pow(10,({gain_db}*({presence}))/20)'


def render_audio(plan, receipt, audio, intro_audio_paths):
    target = WORK / 'approved-pair-audio.m4a'
    audio_receipt = WORK / 'audio-assembly.json'
    if target.exists() and audio_receipt.exists():
        old = asm.load(audio_receipt)
        require(old['snapshotSha256'] == receipt['snapshotSha256'], 'Cached audio inputs changed')
        for item in old['generatedFiles'].values():
            require(binding(item['path']) == item, 'Cached audio file changed')
        audio_samples(target, plan, TOTAL_SAMPLES)
        return target
    require(not target.exists(), 'Unreceipted final AAC exists')
    stems = receipt['snapshot']['stems']
    asm.concat(plan, intro_audio_paths, WORK / 'intro-raw.wav', WORK, 'intro-raw-concat', audio=True)
    audio_samples(WORK / 'intro-raw.wav', plan, INTRO_FRAMES * 800)
    measured = measure_loudness(plan, WORK / 'intro-raw.wav', 'intro-raw')
    requested_gain = -23 - measured['integratedLufs']
    gain = min(requested_gain, -6 - measured['truePeakDbtp'])
    asm.ff(plan, ['-i', WORK / 'intro-raw.wav', '-af', f'volume={gain:.6f}dB',
                 '-ar', '48000', '-ac', '2', '-c:a', 'pcm_f32le', WORK / 'intro-audio.wav'],
                 WORK / 'logs/intro-normalization.log')
    asm.concat(plan, [Path(stems['branding']['path']), WORK / 'intro-audio.wav',
        Path(stems['preferred-unchanged-body-base']['path']), Path(stems['membership']['path'])],
        WORK / 'base-mix.wav', WORK, 'base-mix-concat', audio=True)
    audio_samples(WORK / 'base-mix.wav', plan, TOTAL_SAMPLES)
    music = audio['music']
    duration = TOTAL_FRAMES / 60
    repeats = math.ceil((duration - music['loopCrossfadeSeconds']) /
                        (music['durationSeconds'] - music['loopCrossfadeSeconds']))
    require(repeats >= 1, 'Invalid music repeat count')
    inputs, filters = [], []
    for i in range(repeats):
        inputs += ['-i', music['absolutePath']]
        filters.append(f'[{i}:a]aresample=48000,aformat=sample_fmts=flt:channel_layouts=stereo,'
                       f'asetpts=PTS-STARTPTS[m{i}]')
    previous = 'm0'
    for i in range(1, repeats):
        current = f'loop{i}'
        filters.append(f'[{previous}][m{i}]acrossfade=d={music["loopCrossfadeSeconds"]}:c1=tri:c2=tri[{current}]')
        previous = current
    presence = music_presence_expression(music['extraMusicDuckIntervalsFinalSeconds'],
        music['gameAudioPresenceTransitionSeconds'], music['additionalGainWhileOriginalGameAudioActiveDb'])
    filters.append(f'[{previous}]atrim=end_sample={TOTAL_SAMPLES},asetpts=PTS-STARTPTS,'
        f'volume={music["initialStaticGainDb"]}dB,volume=\'{presence}\':eval=frame,'
        f'afade=t=in:d={music["fadeInSeconds"]},'
        f'afade=t=out:st={duration-music["fadeOutSeconds"]:.9f}:d={music["fadeOutSeconds"]}[music]')
    music_filter = ';'.join(filters)
    (WORK / 'music-bed.fffilter').write_text(music_filter + '\n', encoding='utf-8')
    asm.ff(plan, [*inputs, '-filter_complex', music_filter, '-map', '[music]',
        '-ar', '48000', '-ac', '2', '-c:a', 'pcm_f32le', WORK / 'music-bed.wav'], WORK / 'logs/music-bed.log')
    # Duplicate the original mono control channel without FFmpeg's -3dB
    # mono-to-stereo remix, matching the old mono sidechain detector amplitude.
    voice_filter = (f'aresample=48000,pan=stereo|c0=c0|c1=c0,aformat=sample_fmts=flt,'
        f'apad,atrim=end_sample={BODY_FRAMES*800},volume=3.5dB,adelay=1536000S:all=1,'
        f'apad,atrim=end_sample={TOTAL_SAMPLES},asetpts=PTS-STARTPTS')
    asm.ff(plan, ['-i', stems['approved-narration-source']['path'], '-af', voice_filter,
        '-ar', '48000', '-ac', '2', '-c:a', 'pcm_f32le', WORK / 'voice-sidechain.wav'], WORK / 'logs/voice-sidechain.log')
    sc = music['sidechain']
    mixing_filter = (f'[1:a][2:a]sidechaincompress=threshold={sc["threshold"]}:ratio={sc["ratio"]}:'
        f'attack={sc["attackMs"]}:release={sc["releaseMs"]}:makeup={sc["makeup"]}[ducked];'
        f'[0:a][ducked]amix=inputs=2:duration=first:normalize=0,atrim=end_sample={TOTAL_SAMPLES}[mixed]')
    (WORK / 'mix.fffilter').write_text(mixing_filter + '\n', encoding='utf-8')
    asm.ff(plan, ['-i', WORK / 'base-mix.wav', '-i', WORK / 'music-bed.wav', '-i', WORK / 'voice-sidechain.wav',
        '-filter_complex', mixing_filter, '-map', '[mixed]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_f32le',
        WORK / 'complete-mix.wav'], WORK / 'logs/complete-mix.log')
    limiter = f'aresample=192000,alimiter=limit=0.794328:level=false:latency=true,aresample=48000,atrim=end_sample={TOTAL_SAMPLES}'
    asm.ff(plan, ['-i', WORK / 'complete-mix.wav', '-af', limiter,
        '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', target], WORK / 'logs/encode-single-aac.log')
    generated = ['intro-raw.wav', 'intro-audio.wav', 'base-mix.wav', 'music-bed.wav',
                 'voice-sidechain.wav', 'complete-mix.wav', 'approved-pair-audio.m4a']
    for name in generated:
        audio_samples(WORK / name, plan, INTRO_FRAMES * 800 if name.startswith('intro-') else TOTAL_SAMPLES)
    asm.save(audio_receipt, {'completedAt': asm.now(), 'snapshotSha256': receipt['snapshotSha256'],
        'sourceStems': stems, 'musicProvenance': receipt['snapshot']['music'],
        'musicLicense': receipt['snapshot']['musicLicense'], 'sourceVoiceSha256': VOICE_SHA,
        'introRawMeasurement': measured, 'introTargetIntegratedLufs': -23,
        'introRequestedGainDb': requested_gain, 'introAppliedGainDb': gain,
        'introPeakHeadroomDbtp': -6, 'introGainConstrainedForTransients': gain < requested_gain,
        'pitchPreservingAudioSpeed': 'atempo=2', 'musicSourceGainDb': music['initialStaticGainDb'],
        'musicRepeatCount': repeats, 'musicFilter': music_filter, 'voiceSidechainFilter': voice_filter,
        'mixingFilter': mixing_filter, 'finalLimiterFilter': limiter, 'totalSamples': TOTAL_SAMPLES,
        'generatedFiles': {name: binding(WORK / name) for name in generated},
        'bodyVoiceAndSourceBalanceChangedBeforeMusicAddition': False, 'newTts': False,
        'fullCurrentMixedAsrPerformed': False, 'humanListening': False})
    return target


def render(plan, receipt, audio):
    OUT.mkdir(parents=True, exist_ok=True)
    clean, captioned = [OUT / f'{STEM}.{kind}.mp4' for kind in ['clean', 'captioned']]
    require(not clean.exists() and not captioned.exists(), 'V6 masters exist; use --verify, never overwrite')
    intro_paths, intro_audio_paths, intro_rows = render_intro(plan, receipt)
    old = receipt['snapshot']['originalCuts']
    paths = [Path(old[0]['path']), *intro_paths, *[Path(c['path']) for c in old[1:]]]
    rows = [copy.deepcopy(old[0]), *intro_rows]
    for cut in old[1:]:
        row = copy.deepcopy(cut)
        row['finalStartFrame'] += INTRO_FRAMES
        rows.append(row)
    require(sum(c['frames'] for c in rows) == TOTAL_FRAMES, 'Concat inventory differs')
    asm.concat(plan, paths, WORK / 'visuals.mp4', WORK, 'visuals-concat')
    video_metadata(WORK / 'visuals.mp4', plan, TOTAL_FRAMES, retained=True)
    aac = render_audio(plan, receipt, audio, intro_audio_paths)
    asm.ff(plan, ['-i', WORK / 'visuals.mp4', '-i', aac, '-map', '0:v:0', '-map', '1:a:0',
        '-c', 'copy', '-video_track_timescale', '90000', '-map_metadata', '-1', '-movflags', '+faststart', clean],
        WORK / 'logs/clean-master.log')
    asm.ff(plan, ['-i', clean, '-vf', 'ass=captions.ko.ass', '-map', '0:v:0', '-map', '0:a:0',
        *asm.encoder(plan), '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-video_track_timescale', '90000',
        '-map_metadata', '-1', '-movflags', '+faststart', captioned], WORK / 'logs/captioned-master.log', WORK)
    for lang in ['ko', 'en']:
        shutil.copy2(WORK / f'captions.{lang}.srt', OUT / f'{STEM}.{lang}.srt')
    asm.write_index(OUT, STEM)
    asm.save(WORK / 'render-progress.json', {'completedAt': asm.now(), 'complete': True,
        'snapshotSha256': receipt['snapshotSha256'], 'cuts': rows,
        'outputs': {k: binding(OUT / f'{STEM}.{k}.mp4') for k in ['clean', 'captioned']},
        'captions': {k: binding(OUT / f'{STEM}.{k}.srt') for k in ['ko', 'en']},
        'audioAssembly': binding(WORK / 'audio-assembly.json'), 'retainedV5VideoCuts': 34,
        'newIntroVideoCuts': 6, 'totalFrames': TOTAL_FRAMES, 'newTts': False,
        'humanViewing': False, 'humanListening': False})


def read_frame_hashes(target, expected):
    rows = []
    for line in Path(target).read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split(',')]
        require(len(parts) == 6 and re.fullmatch(r'[0-9a-fA-F]{64}', parts[-1]), 'Malformed frame proof')
        rows.append({'pts': int(parts[2]), 'duration': int(parts[3]), 'sha256': parts[-1]})
    require(len(rows) == expected, 'Decoded frame proof count differs')
    return rows


def frame_hashes(path, plan, label, expected):
    folder = WORK / 'proof'
    folder.mkdir(parents=True, exist_ok=True)
    target, cache = folder / (label + '.framehash'), folder / (label + '.framehash.json')
    fp = {'file': binding(path), 'frames': expected,
          'decode': 'software H264 to original yuv420p; passthrough frame rate; SHA256 per raw frame'}
    if cache.exists() and target.exists():
        old = asm.load(cache)
        require(old['input'] == fp and old['sha256'] == asm.digest(target), 'Changed current frame proof cache')
    else:
        require(not target.exists(), 'Unreceipted current frame proof exists')
        asm.ff(plan, ['-threads', '2', '-i', path, '-map', '0:v:0', '-an', '-c:v', 'rawvideo', '-threads:v', '1',
            '-pix_fmt', 'yuv420p', '-fps_mode', 'passthrough', '-f', 'framehash', '-hash', 'sha256', target],
            WORK / 'logs' / (label + '.framehash.log'))
        asm.save(cache, {'input': fp, 'sha256': asm.digest(target), 'completedAt': asm.now()})
    return read_frame_hashes(target, expected), binding(target)


def audio_hash(path, plan, label, filtering=None):
    target = WORK / 'proof' / (label + '.audio-f32.sha256')
    target.parent.mkdir(parents=True, exist_ok=True)
    args = ['-i', path, '-map', '0:a:0']
    if filtering:
        args += ['-af', filtering]
    asm.ff(plan, [*args, '-c:a', 'pcm_f32le', '-f', 'hash', '-hash', 'sha256', target],
           WORK / 'logs' / (label + '.audio-f32.log'))
    value = target.read_text(encoding='utf-8').strip()
    require(re.fullmatch(r'SHA256=[0-9a-fA-F]{64}', value), 'Invalid actual audio hash')
    return value


def audio_packets(path, plan, label):
    scoped_authorization()
    args = [asm.tool('ffprobe', plan), '-v', 'error', '-select_streams', 'a:0', '-show_packets',
        '-show_data_hash', 'sha256', '-show_entries',
        'packet=pts,dts,duration,size,flags,data_hash,side_data_list', '-of', 'json', str(path)]
    packets = json.loads(subprocess.check_output(args, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)))['packets']
    require(packets and all(p.get('data_hash', '').startswith('SHA256:') for p in packets), 'AAC packet hashes missing')
    target = WORK / 'proof' / (label + '.aac-packets.json')
    asm.save(target, {'file': binding(path), 'packetCount': len(packets), 'packets': packets,
                     'packetSequenceSha256': stable_hash(packets), 'command': args})
    return {'proof': binding(target), 'packetSequenceSha256': stable_hash(packets)}


def verify_captions(receipt):
    report = {}
    for lang in ['ko', 'en']:
        old = asm.read_srt(receipt['snapshot']['baselineCaptions'][lang]['path'])
        current = asm.read_srt(OUT / f'{STEM}.{lang}.srt')
        require(len(old) == len(current), 'Subtitle cue count changed')
        for a, b in zip(old, current):
            require(a['text'] == b['text'] and a['id'] == b['id'] and
                    abs(b['start'] - a['start'] - 30) < .00001 and
                    abs(b['end'] - a['end'] - 30) < .00001, 'Subtitle changed beyond 30-second offset')
        require(min(c['start'] for c in current) >= 32, 'Unexpected intro speech subtitle')
        report[lang] = {'cueCount': len(current), 'allTextPreserved': True, 'offsetSeconds': 30,
                        'file': binding(OUT / f'{STEM}.{lang}.srt')}
    return report


def verify(plan, receipt):
    progress = asm.load(WORK / 'render-progress.json')
    require(progress.get('complete') is True and progress['snapshotSha256'] == receipt['snapshotSha256'],
            'Current render is missing or input snapshot changed')
    for kind in ['clean', 'captioned']:
        require(binding(OUT / f'{STEM}.{kind}.mp4') == progress['outputs'][kind], 'Current master changed')
        audio_samples(OUT / f'{STEM}.{kind}.mp4', plan, TOTAL_SAMPLES)
    technical = asm.verify(plan, receipt, WORK)
    technical.update(preservationVerificationPassed=False, revision='v6')
    asm.save(WORK / 'technical-qa.json', technical)
    captions = verify_captions(receipt)
    packets, pcm = {}, {}
    for label, path in [('aac', WORK / 'approved-pair-audio.m4a'),
                        ('clean', OUT / f'{STEM}.clean.mp4'), ('captioned', OUT / f'{STEM}.captioned.mp4')]:
        packets[label] = audio_packets(path, plan, label)
        pcm[label] = audio_hash(path, plan, label)
    require(len({p['packetSequenceSha256'] for p in packets.values()}) == 1,
            'Single encoded AAC packets/timestamps were not copied identically')
    require(len(set(pcm.values())) == 1, 'Paired decoded FLOAT audio differs')
    baseline_proof = BASE_WORK / 'proof/v5-clean.framehash'
    baseline_cache = asm.load(BASE_WORK / 'proof/v5-clean.framehash.json')
    require(baseline_cache['input']['file'] == receipt['snapshot']['baselineMasters']['clean'] and
            baseline_cache['input']['frames'] == BASE_FRAMES and
            baseline_cache['sha256'] == asm.digest(baseline_proof), 'Read-only v5 frame proof is not bound to baseline')
    baseline = read_frame_hashes(baseline_proof, BASE_FRAMES)
    actual, current_proof = frame_hashes(OUT / f'{STEM}.clean.mp4', plan, 'v6-clean', TOTAL_FRAMES)
    intro_hashes, intro_proofs = [], []
    for row in progress['cuts'][1:7]:
        frames, proof = frame_hashes(Path(row['path']), plan, row['id'], row['frames'])
        intro_hashes += [f['sha256'] for f in frames]
        intro_proofs.append(proof)
    expected = [f['sha256'] for f in baseline[:120]] + intro_hashes + [f['sha256'] for f in baseline[120:]]
    require(len(expected) == len(actual) == TOTAL_FRAMES, 'Frame mapping length differs')
    mismatches = [i for i, (a, b) in enumerate(zip(actual, expected)) if a['sha256'] != b]
    continuous = actual[0]['pts'] == 0 and all(a['duration'] == 1 and b['pts'] == a['pts'] + 1
                                               for a, b in zip(actual, actual[1:]))
    frame_report = {'checkedAt': asm.now(), 'frames': TOTAL_FRAMES, 'mismatchCount': len(mismatches),
        'mismatchFrames': mismatches[:100], 'continuousDecodedCfrPts': continuous,
        'baselineProof': binding(baseline_proof), 'currentProof': current_proof, 'introProofs': intro_proofs,
        'mapping': 'v5[0:120] + six new intro clips[1800 frames] + v5[120:24718]',
        'retainedBodyCleanPixelsIdentical': not mismatches, 'captionedPixelEqualityClaimed': False}
    asm.save(WORK / 'proof/frame-preservation.json', frame_report)
    require(not mismatches and continuous, 'V6 clean frame preservation or PTS verification failed')
    body_hash = audio_hash(WORK / 'base-mix.wav', plan, 'retained-body',
        f'atrim=start_sample={32*48000}:end_sample={32*48000+BODY_FRAMES*800},asetpts=PTS-STARTPTS')
    old_body_hash = audio_hash(AUDIO_WORK / 'body-mix.wav', plan, 'v4-body-reference')
    require(body_hash == old_body_hash, 'Retained pre-music body PCM changed')
    proof = {'checkedAt': asm.now(), 'revision': 'v6', 'technicalPassed': True,
        'snapshotSha256': receipt['snapshotSha256'], 'totalFrames': TOTAL_FRAMES, 'audioSamples': TOTAL_SAMPLES,
        'baselineMasters': receipt['snapshot']['baselineMasters'], 'currentMasters': progress['outputs'],
        'captions': captions, 'audioPackets': packets, 'decodedAudioHashes': pcm,
        'pairedAudioPacketsAndPcmIdentical': True, 'retainedBodyPreMusicFloatPcmIdentical': True,
        'retainedBodyPcmSha256': body_hash, 'sourceVoiceSha256': VOICE_SHA,
        'cleanFramePreservation': binding(WORK / 'proof/frame-preservation.json'),
        'encodedTruePeakDbtp': technical['encodedTruePeakDbtp'], 'newTts': False, 'newAudioMix': True,
        'newFullMixAsrPerformedByBuilder': False, 'remaining': receipt['remaining'],
        'humanViewing': False, 'humanListening': False, 'userApproval': False}
    asm.save(WORK / 'preservation-proof.json', proof)
    technical.update(preservationVerificationPassed=True, preservationProof=str(WORK / 'preservation-proof.json'),
                     audioContentReview='Current full-mix ASR/continuity review required separately; no old mix approval inferred.',
                     remaining=receipt['remaining'])
    asm.save(WORK / 'technical-qa.json', technical)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    require(args.prepare or args.render or args.verify, 'Choose --prepare, --render or --verify')
    with job_lock(), expensive_job_guard():
        plan, receipt, audio = prepare(write=args.prepare or args.render)
        if args.render:
            render(plan, receipt, audio)
        if args.verify:
            verify(plan, receipt)
        print(json.dumps({'status': 'verified' if args.verify else 'rendered' if args.render else 'prepared',
            'timeline': str(WORK / 'timeline.json'), 'totalFrames': TOTAL_FRAMES,
            'audioSamples': TOTAL_SAMPLES, 'introSeconds': 30, 'retainedV5Cuts': 34,
            'newTts': False, 'newAudioMix': True, 'humanViewing': False, 'humanListening': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
