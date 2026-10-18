"""Current portrait output QA. Import/--help never perform media work.

Root explicitly runs --verify after rendering. Hash-specific stage receipts
reuse successful decodes/pixel extraction; unresolved findings stay pending.
This does not approve human listening, moving semantics or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

_spec = importlib.util.spec_from_file_location('fov_renderer_for_qa', Path(__file__).with_name('render-short.py'))
renderer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(renderer)
ROOT, PROJECT, OUT = renderer.ROOT, renderer.PROJECT, renderer.OUT
QA = OUT / 'qa'
RATE, CHANNELS, FPS, FRAMES, SECONDS = 48000, 2, 60, 1800, 30.0
SOURCE_START, SOURCE_END, PLACEMENT = 81.26, 107.98, 2.8
VOICE_SECONDS, PLACED_END = 26.72, 29.52
SOURCE_SHA = '55f30a0aa45e043d61fcd262c1e3f306aa46eb4e046d2490d9659411b0c9bec4'


def ensure(condition, message):
    if not condition:
        raise AssertionError(message)


def artifact(path):
    path = Path(path)
    try:
        display = renderer.rel(path)
    except ValueError:
        display = path.as_posix()
    return dict(path=display, sha256=renderer.sha(path), bytes=path.stat().st_size)


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf8')).hexdigest()


def db_rms(values):
    return 20 * math.log10(max(float(np.sqrt(np.mean(np.asarray(values, dtype=np.float64) ** 2))), 1e-12))


def probe(path):
    result = renderer.run([renderer.FFPROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)])
    return json.loads(result.stdout)


def packet_audio_hash(path):
    result = renderer.run([renderer.FFPROBE, '-v', 'error', '-select_streams', 'a:0', '-show_packets', '-show_data_hash', 'sha256', '-show_entries', 'packet=pts,duration,size,data_hash', '-of', 'json', str(path)])
    packets = json.loads(result.stdout)['packets']
    ensure(packets and all('data_hash' in row and 'pts' in row and 'duration' in row for row in packets), 'Missing AAC packets/timing')
    ensure(all(int(b['pts']) == int(a['pts']) + int(a['duration']) for a, b in zip(packets, packets[1:])), 'AAC packet gap/overlap/reversal')
    return dict(packetCount=len(packets), payloadListSha256=signature([p['data_hash'] for p in packets]), ptsContiguous=True)


def decode_once(path, name):
    """One full AV decode, reusing retained decoded PCM in audio QA and ASR."""
    log = QA / f'{name}-whole-decode.log'
    command = [renderer.FFMPEG, '-hide_banner', '-loglevel', 'info', '-xerror', '-i', str(path),
               '-map', '0:v:0', '-vf', 'showinfo', '-an', '-fps_mode', 'passthrough', '-f', 'null', 'NUL',
               '-map', '0:a:0', '-vn', '-ar', str(RATE), '-ac', str(CHANNELS), '-f', 'f32le', 'pipe:1']
    result = renderer.run(command)
    stderr = result.stderr.decode(errors='replace')
    log.write_text(stderr, encoding='utf8')
    rows = [(int(n), int(pts), float(t)) for n, pts, t in re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:\s*([-+\d.eE]+)', stderr)]
    ensure(len(rows) == FRAMES and [r[0] for r in rows] == list(range(FRAMES)), f'{name}: wrong decoded frame count/order')
    error = float(np.max(np.abs(np.array([r[2] for r in rows]) - np.arange(FRAMES)/FPS)))
    ensure(error < .00006, f'{name}: offset/nonuniform video PTS ({error}s)')
    ticks = [b[1]-a[1] for a, b in zip(rows, rows[1:])]
    ensure(min(ticks) == max(ticks) and min(ticks) > 0, f'{name}: nonuniform integer video PTS')
    ensure(len(result.stdout) % (4*CHANNELS) == 0, f'{name}: truncated decoded PCM')
    pcm = np.frombuffer(result.stdout, dtype='<f4').reshape(-1, CHANNELS).copy()
    count = round(SECONDS*RATE)
    ensure(count <= len(pcm) <= count+1024 and np.isfinite(pcm).all(), f'{name}: decoded audio length/nonfinite failure')
    decoded = QA/f'{name}-decoded-audio-48k.wav'
    sf.write(decoded, pcm[:count], RATE, subtype='FLOAT')
    return dict(status='pass', log=artifact(log), decodedVideoFrames=len(rows), maximumPtsErrorSeconds=error,
                integerPtsStep=ticks[0], decodedAudioSamples=len(pcm), aacPaddingSamples=len(pcm)-count,
                decodedAudio=artifact(decoded)), pcm[:count]


def current_inputs():
    source_path = PROJECT/'script/raw-source-map.json'
    source = renderer.read(source_path)
    voice, music = source['narration'], source['music']
    ensure(voice['sourceStart'] == SOURCE_START and voice['sourceEnd'] == SOURCE_END and voice['placementStart'] == PLACEMENT, 'Source voice interval/placement changed')
    ensure(voice['duration'] == VOICE_SECONDS and voice['declickSeconds'] == 0, 'Unexpected retained PCM processing')
    ensure(voice['pcmBeforeAnyGainMustRemainExact'], 'Exact retained PCM contract missing')
    ensure(renderer.sha(ROOT/voice['path']) == voice['sha256'] == SOURCE_SHA, 'Approved voice source changed')
    ensure(renderer.sha(ROOT/voice['wordEvidence']) == voice['wordEvidenceSha256'], 'Existing word timing evidence changed')
    ensure(renderer.sha(ROOT/voice['timingEvidence']) == voice['timingEvidenceSha256'], 'Existing scene timing evidence changed')
    ensure(renderer.sha(ROOT/music['path']) == music['sha256'], 'Music input changed')
    audio = renderer.read(OUT/'audio-build.json')
    for key, expected in [('sourceStart', SOURCE_START), ('sourceEnd', SOURCE_END), ('placementStart', PLACEMENT), ('voiceSeconds', VOICE_SECONDS), ('seconds', SECONDS)]:
        ensure(abs(float(audio['signature'][key])-expected) < 1e-8, f'Wrong audio receipt {key}')
    ensure(audio['voiceDuckApplied'] is False and audio['originalGameAudioIncluded'] is False, 'Voice ducking/unrelated game audio present')
    for item in audio['files'].values():
        ensure(renderer.sha(ROOT/item['path']) == item['sha256'], 'Audio file differs from current build receipt')
    pair = renderer.read(OUT/'pair-build.json')
    ensure(pair['signature']['visual'] == renderer.sha(OUT/'portrait-visual.mp4'), 'Visual changed after mux')
    ensure(pair['signature']['audio'] == renderer.sha(OUT/'final-mix.m4a'), 'Mix changed after mux')
    ensure(pair['signature']['ass'] == renderer.sha(OUT/'captions.ko.ass'), 'Captions changed after mux')
    for item in pair['files']:
        ensure(renderer.sha(ROOT/item['path']) == item['sha256'], 'Final pair differs from build receipt')
    capture = source['capture']
    projection = ROOT/capture['projection']
    ensure(projection.is_file(), 'Missing actual capture projection provenance')
    visual = renderer.read(OUT/'visual-build.json')
    ensure(visual['signature']['projection'] == renderer.sha(projection), 'Rendered projection provenance changed')
    ensure(visual['signature']['code'] == renderer.sha(Path(__file__).with_name('render-short.py')), 'Renderer changed after the current visual build')
    ensure(visual['signature']['captions'] == renderer.sha(PROJECT/'script/captions.json'), 'Visual caption/timing input changed')
    ensure(visual['sha256'] == renderer.sha(OUT/'portrait-visual.mp4'), 'Current visual differs from its receipt')
    for item in visual['signature']['captureFrames']:
        ensure(renderer.sha(ROOT/item['path']) == item['sha256'], 'Native capture changed after rendering')
    frame_directory = ROOT/capture['frameDirectory']
    source_frames = sorted(frame_directory.glob('*.png'))
    ensure(len(source_frames) == capture['sourceFrames'], 'Native captured source frame count differs')
    captured = []
    for path in source_frames:
        with Image.open(path) as image:
            ensure(image.size[0] >= 1920 and image.size[1] >= 1080, 'Capture is below genuine FHD source minimum')
            size = list(image.size)
        captured.append(dict(**artifact(path), decodedResolution=size))
    provenance = dict(status='pass-current-source-and-build-hashes', sourceVoice=artifact(ROOT/voice['path']),
        existingWordEvidence=artifact(ROOT/voice['wordEvidence']), sourcePcmExcerpt=[SOURCE_START, SOURCE_END],
        nativeCapture=artifact(projection), nativeCaptureFrames=captured,
        narrationNewTtsJobs=0, rawNarrationAsr='reused-existing-complete-source-evidence-with-exact-excerpt-check',
        captureClassification='self-authored-explanation', measuredCommercialGameValues=False)
    inputs = [source_path, PROJECT/'script/captions.json', OUT/'audio-build.json', OUT/'pair-build.json',
              OUT/'visual-build.json', OUT/'visual-timeline.json', OUT/'caption-layout.json', OUT/'code-preflight.json',
              OUT/'captions.ko.ass', OUT/'captions.ko.srt', OUT/'captions.en.srt', projection,
              ROOT/voice['path'], ROOT/voice['wordEvidence'], ROOT/voice['timingEvidence'], ROOT/music['path'],
              Path(renderer.FONTFILE), Path(renderer.BOLDFONT)]
    return source, audio, provenance, [artifact(p) for p in inputs]


def caption_preflight():
    captions = renderer.read(PROJECT/'script/captions.json')
    layout = renderer.read(OUT/'caption-layout.json')
    code = renderer.read(OUT/'code-preflight.json')
    ensure(layout['inputSha256'] == renderer.sha(PROJECT/'script/captions.json'), 'Stale caption layout')
    ensure(code['status'] == 'passed-code-and-font-layout-only', 'Current font/layout preflight has not passed')
    cues = captions['cues']
    ensure(bool(cues) and len(layout['rows']) == len(cues), 'Caption/layout mismatch')
    previous = 0
    for cue in cues:
        ensure(cue['start'] >= previous-.001 and cue['end'] > cue['start'] and cue['end'] <= PLACED_END+.001, 'Overlapping/out-of-speech caption')
        ensure(cue['start'] >= PLACEMENT-.001, 'Narration caption appears in the silent opening hook')
        previous = cue['end']
    def stamp(value):
        h, m, s = value.replace(',', '.').split(':')
        return int(h)*3600+int(m)*60+float(s)
    for lang in ['ko', 'en']:
        blocks = re.split(r'\n\s*\n', (OUT/f'captions.{lang}.srt').read_text(encoding='utf-8-sig').strip())
        ensure(len(blocks) == len(cues), f'{lang}: wrong SRT cue count')
        for block, cue in zip(blocks, cues):
            lines = block.splitlines()
            ensure(3 <= len(lines) <= 4, f'{lang}: empty/>2-line caption')
            a, b = lines[1].split(' --> ')
            ensure(abs(stamp(a)-cue['start']) < .0006 and abs(stamp(b)-cue['end']) < .0006, f'{lang}: mismatched SRT timing')
            ensure(' '.join(' '.join(lines[2:]).split()) == ' '.join(cue[lang].split()), f'{lang}: SRT text differs')
    for row, cue in zip(layout['rows'], cues):
        ensure(row['start'] == cue['start'] and row['end'] == cue['end'], 'Layout timing changed')
        ensure(len(row['lines']) <= 2 and row['font'] == 60 and row['center'] == [510, 1380], 'Caption style/anchor changed')
        for line, width in zip(row['lines'], row['textWidths']):
            ensure(abs(renderer.font(60).getlength(line)-width) < .02 and width <= 796, 'Actual font metric exceeds planned safe width')
        x, y, w, h = row['box']
        ensure(x >= 80 and x+w <= 930 and y+h+14 < 1560, 'Caption box/shadow crosses safe area')
    return captions, dict(status='pass-code-and-current-font-metrics-only', cueCount=len(cues), maxLines=2,
        maximumMeasuredWidth=max(max(r['textWidths']) for r in layout['rows']), fontPixels=60, center=[510, 1380],
        actualEncodedPixelReview='pending', actualShortsUiReview='pending')


def read_stereo(path):
    values, rate = sf.read(path, dtype='float32', always_2d=True)
    ensure(rate == RATE and values.shape == (round(SECONDS*RATE), CHANNELS), f'Wrong stem format/length: {path}')
    return values


def context_ranges(rows):
    result = []
    for row in rows:
        a, b = max(0, row['start']-.5), min(SECONDS, row['end']+.5)
        if result and a <= result[-1]['end']:
            result[-1]['end'] = max(result[-1]['end'], b)
        else:
            result.append(dict(start=a, end=b))
    return result


def audio_review(source, receipt, encoded):
    prepared, stem, music = [read_stereo(OUT/name) for name in ['voice-input-stereo.wav', 'narration-stem.wav', 'music-stem.wav']]
    original = ROOT/source['narration']['path']
    with sf.SoundFile(original) as stream:
        source_rate = stream.samplerate
        stream.seek(round(SOURCE_START*source_rate))
        raw = stream.read(round(VOICE_SECONDS*source_rate), dtype='float32', always_2d=True)
    retained, retained_rate = sf.read(OUT/'retained-voice-24k.wav', dtype='float32', always_2d=True)
    ensure(source_rate == retained_rate == 24000 and np.array_equal(raw, retained), 'Retained approved PCM excerpt differs')
    lead = prepared[:round((PLACEMENT-.01)*RATE)]
    tail = prepared[round((PLACED_END+.01)*RATE):]
    ensure(np.max(np.abs(lead)) < 1e-8 and np.max(np.abs(tail)) < 1e-8, 'Narration padding includes another paragraph')
    gain = float(receipt['constantNarrationGainDb'])
    estimated_voice = encoded.astype(np.float64)-music.astype(np.float64)
    # Lossy AAC mixture subtraction is a diagnostic, not perfect separation.
    size, step = round(.4*RATE), round(.1*RATE)
    rows = []
    for i in range(0, len(stem)-size+1, step):
        a, b = i/RATE, (i+size)/RATE
        if a < PLACEMENT+.01 or b > PLACED_END-.01:
            continue
        src, ref = prepared[i:i+size].astype(np.float64), stem[i:i+size].astype(np.float64)
        src_db, ref_db = db_rms(src), db_rms(ref)
        if ref_db <= -43:
            continue
        residual = estimated_voice[i:i+size]
        energy = float(np.sum(ref*ref))
        cross = float(np.sum(ref*residual))
        coefficient = cross/max(energy, 1e-20)
        correlation = cross/max(float(np.sqrt(energy*np.sum(residual*residual))), 1e-20)
        rows.append(dict(start=a, end=b, sourceDbfs=src_db, narrationStemDbfs=ref_db, plannedGainDb=gain,
                         sourceToStemRelativeGainDb=ref_db-src_db-gain,
                         encodedVoiceProjectionDb=20*math.log10(max(coefficient, 1e-12)), encodedVoiceCorrelation=correlation))
    ensure(bool(rows), 'No speech-active windows measured')
    flags = [r for r in rows if r['sourceToStemRelativeGainDb'] < -2.5 or r['encodedVoiceProjectionDb'] < -2.5 or r['encodedVoiceCorrelation'] < .8]
    natural = [dict(start=a['start'], end=b['end'], sourceDropDb=a['sourceDbfs']-b['sourceDbfs'], inducedFlag=b in flags)
               for a, b in zip(rows, rows[1:]) if b['start']-a['start'] <= .5 and a['sourceDbfs']-b['sourceDbfs'] >= 6]
    measured = receipt['measurements']['encoded']
    target = float(receipt['signature']['targetSpeechLufs'])
    ensure(float(measured['input_tp']) <= -1.5, 'Encoded true peak exceeds -1.5dBTP')
    ensure(-20 <= target <= -14 and target-1.5 <= float(measured['input_i']) <= target+1.5, 'Integrated loudness differs from configured target')
    return dict(status='pass-no-induced-attenuation-flags' if not flags else 'fail-contextual-review-required',
        speechActiveWindows=rows, flaggedTransferWindows=flags, flaggedContextRanges=context_ranges(flags),
        naturalSourceDropCandidates=natural, naturalSourceDropReview='pending-contextual-review' if natural else 'no-candidates',
        constantNarrationGainDb=gain, voiceDuckApplied=False, approximateMusicSubtractionDiagnostic=True,
        measurementWindowSeconds=.4, hopSeconds=.1, activeThresholdDbfs=-43,
        exactRetainedPcm=True, sourcePcmInterval=[SOURCE_START, SOURCE_END], placementStart=PLACEMENT,
        paddingBeforeAndAfterVerified=True, sourceBoundaryRmsDbfs=dict(first10ms=db_rms(raw[:240]), last10ms=db_rms(raw[-240:])),
        rawAsrReuse='exact unchanged excerpt; existing whole source ASR and word timing hashes retained',
        encodedLoudness=measured, encodedLoudnessEvidence='hash-bound audio-build.json measurements.encoded',
        currentWholeEncodedMixAsr='pending-one-current-pass', humanListeningAndPronunciation='pending')


def pixel_samples(captions, captioned):
    timeline = renderer.read(OUT/'visual-timeline.json')
    ensure(timeline['frames'] == FRAMES and timeline['fps'] == FPS, 'Visual timeline dimensions changed')
    requested = {}
    def add(frame, reason):
        n = max(0, min(FRAMES-1, int(frame)))
        requested.setdefault(n, []).append(reason)
    for cue in captions['cues']:
        a, b = math.ceil(cue['start']*FPS-1e-7), math.ceil(cue['end']*FPS-1e-7)-1
        for n, label in [(a, 'start'), ((a+b)//2, 'middle'), (b, 'end')]:
            add(n, f'caption-{cue["id"]}-{label}')
    boundaries = []
    for category in ['cuts', 'beats']:
        for item in timeline[category]:
            if isinstance(item, (int, float)):
                boundaries.append((float(item), category))
            elif isinstance(item, dict):
                parsed = False
                for key in ['time', 'start', 'end']:
                    if key in item:
                        boundaries.append((float(item[key]), f'{category}-{item.get("id", "")}-{key}'))
                        parsed = True
                if 'range' in item:
                    for t in item['range']:
                        boundaries.append((float(t), f'{category}-{item.get("id", "")}-range'))
                    parsed = True
                ensure(parsed, f'Unsupported visual boundary timing record: {item}')
            else:
                raise AssertionError(f'Unsupported visual boundary: {item}')
    for t, reason in boundaries+[(PLACEMENT, 'voice-entry'), (PLACED_END, 'voice-exit'), (SECONDS, 'last-frame')]:
        ensure(0 <= t <= SECONDS, 'Visual boundary falls outside the final short')
        frame = math.ceil(t*FPS-1e-7)
        for delta, label in [(-1, 'before'), (0, 'at'), (1, 'after')]:
            add(frame+delta, f'{reason}-{label}')
    # Quarter-second samples observe changing camera/FOV and edge visibility;
    # still samples alone never approve continuous motion.
    for beat in timeline['beats']:
        if 'indexFrom' in beat:
            for frame in range(math.floor(beat['start']*FPS), math.ceil(beat['end']*FPS)+1, 15):
                add(frame, 'FOV-motion-quarter-second-sample')
    numbers = sorted(requested)
    plan_signature = signature(dict(captionedSha256=renderer.sha(captioned), frames=numbers))
    target = QA/'pixel-samples.json'
    if target.exists():
        old = renderer.read(target)
        ensure(old['samplePlanSignature'] == plan_signature, 'Pixel sample plan changed; preserve earlier samples')
        return old
    native, mobile = QA/'native', QA/'mobile'
    native.mkdir(parents=True, exist_ok=True); mobile.mkdir(parents=True, exist_ok=True)
    ensure(not list(native.glob('*.png')), 'Partial extraction exists; inspect it before resuming')
    select = '+'.join(f'eq(n\\,{n})' for n in numbers)
    renderer.run([renderer.FFMPEG, '-v', 'warning', '-n', '-i', str(captioned), '-vf', f'select={select}', '-fps_mode', 'vfr', '-an', str(native/'frame-%03d.png')])
    files = sorted(native.glob('frame-*.png'))
    ensure(len(files) == len(numbers), 'Wrong selected pixel sample count')
    samples = []
    for index, (frame, path) in enumerate(zip(numbers, files), 1):
        with Image.open(path) as image:
            ensure(image.size == (1080, 1920), 'Native pixel sample resolution changed')
            small = image.convert('RGB').resize((375, 667), Image.Resampling.LANCZOS)
            dest = mobile/f'frame-{index:03}.jpg'; small.save(dest, quality=94)
        samples.append(dict(index=index, frame=frame, seconds=frame/FPS, reasons=requested[frame], native=renderer.rel(path), mobile=renderer.rel(dest)))
    sheets = []
    label_font = ImageFont.truetype(renderer.FONTFILE, 16)
    for first in range(0, len(samples), 8):
        board = Image.new('RGB', (750, 2800), '#202020'); draw = ImageDraw.Draw(board)
        for local, row in enumerate(samples[first:first+8]):
            x, y = local%2*375, local//2*700
            draw.text((x+5, y+4), f'{row["index"]:03}  {row["seconds"]:.3f}s  f{row["frame"]}', font=label_font, fill='white')
            with Image.open(ROOT/row['mobile']) as image:
                board.paste(image, (x, y+30))
        path = QA/f'mobile-contact-{first//8+1:02}.jpg'; board.save(path, quality=94); sheets.append(artifact(path))
    report = dict(status='extracted-not-visually-approved', samplePlanSignature=plan_signature,
        captionedSha256=renderer.sha(captioned), everyCaptionStartMiddleEndSampled=True,
        everyCutAndBeatBoundarySampled=True, movingFovQuarterSecondSamples=True,
        nativeResolution=[1080, 1920], mobileResolution=[375, 667], uniqueFrameCount=len(samples),
        samples=samples, contactSheets=sheets, extractionPasses=1, encodedPixelDirectReview='pending',
        continuousMotionSemanticReview='pending', nativeAnd375MobileReview='pending')
    renderer.write(target, report)
    return report


def verify():
    global QA
    renderer.check_render_authorization()
    clean, captioned = [OUT/f'{PROJECT.name}.{name}.mp4' for name in ['clean', 'captioned']]
    final_files = [artifact(clean), artifact(captioned)]
    QA = OUT/'qa'/final_files[1]['sha256'][:16]
    QA.mkdir(parents=True, exist_ok=True)
    source, receipt, provenance, inputs = current_inputs()
    captions, fonts = caption_preflight()
    current_signature = signature(dict(inputs=inputs, finalFiles=final_files, verifier=renderer.sha(__file__)))
    target = QA/'short-qa.json'
    if target.exists():
        old = renderer.read(target)
        if old.get('signature') == current_signature and old.get('technicalExecutionComplete'):
            return old
    pending = dict(signature=current_signature, startedAt=datetime.now(timezone.utc).isoformat(), technicalExecutionComplete=False,
        inputs=inputs, finalFiles=final_files, mediaProductionJobsStarted=0, asrJobsStarted=0,
        directPixelReview='pending', humanListening='pending')
    renderer.write(target, pending)
    try:
        integrity_path = QA/'integrity.json'
        if integrity_path.exists():
            integrity = renderer.read(integrity_path)
            ensure(integrity['finalFiles'] == final_files and integrity['status'] == 'pass', 'Integrity cache does not match current pair')
            encoded = read_stereo(ROOT/integrity['files']['captioned']['fullDecode']['decodedAudio']['path'])
        else:
            files, decoded, hashes = {}, {}, {}
            for name, path in [('clean', clean), ('captioned', captioned)]:
                file_receipt = QA/f'{name}-decode.json'
                if file_receipt.exists():
                    retained = renderer.read(file_receipt)
                    ensure(retained['file'] == artifact(path), f'{name}: cached decode belongs to another output')
                    pcm_info = retained['fullDecode']['decodedAudio']
                    ensure(renderer.sha(ROOT/pcm_info['path']) == pcm_info['sha256'], f'{name}: cached decoded audio changed')
                    decoded[name] = read_stereo(ROOT/pcm_info['path'])
                    hashes[name] = retained['audioPackets']
                    files[name] = retained
                    continue
                meta = probe(path)
                videos = [s for s in meta['streams'] if s['codec_type'] == 'video']
                audios = [s for s in meta['streams'] if s['codec_type'] == 'audio']
                ensure(len(videos) == len(audios) == 1, f'{name}: expected one AV stream pair')
                v, a = videos[0], audios[0]
                ensure((v['width'], v['height']) == (1080, 1920) and Fraction(v['avg_frame_rate']) == FPS, f'{name}: wrong portrait resolution/fps')
                ensure(v['pix_fmt'] == 'yuv420p' and v.get('color_range') == 'tv' and v.get('color_space') == 'bt709', f'{name}: wrong display pixel format/colorspace')
                ensure(int(v.get('nb_frames', -1)) == FRAMES and abs(float(meta['format']['duration'])-SECONDS) <= 1/FPS, f'{name}: wrong duration/frame count')
                ensure(a['codec_name'] == 'aac' and int(a['sample_rate']) == RATE and a['channels'] == CHANNELS, f'{name}: wrong audio format')
                result, decoded[name] = decode_once(path, name)
                hashes[name] = packet_audio_hash(path)
                files[name] = dict(file=artifact(path), video=v, audio=a, fullDecode=result, audioPackets=hashes[name])
                renderer.write(file_receipt, files[name])
            ensure(hashes['clean']['payloadListSha256'] == hashes['captioned']['payloadListSha256'] == packet_audio_hash(OUT/'final-mix.m4a')['payloadListSha256'], 'Pair/final mix AAC payloads differ')
            ensure(np.array_equal(decoded['clean'], decoded['captioned']), 'Pair decoded audio differs')
            encoded = decoded['captioned']
            integrity = dict(status='pass', finalFiles=final_files, expectedFrames=FRAMES, expectedSeconds=SECONDS,
                pairAndMixAacPayloadIdentical=True, pairedDecodedAudioIdentical=True, files=files)
            renderer.write(integrity_path, integrity)
        audio_path = QA/'audio-review.json'
        audio_signature = signature(dict(encoded=final_files[1]['sha256'], source=SOURCE_SHA, audioBuild=renderer.sha(OUT/'audio-build.json'), verifier=renderer.sha(__file__)))
        if audio_path.exists() and renderer.read(audio_path).get('signature') == audio_signature:
            audio = renderer.read(audio_path)
        else:
            audio = audio_review(source, receipt, encoded); audio['signature'] = audio_signature; renderer.write(audio_path, audio)
        pixels = pixel_samples(captions, captioned)
        report = dict(pending, technicalExecutionComplete=True, completedAt=datetime.now(timezone.utc).isoformat(),
            status='technical-complete-context-pixel-and-user-review-pending', integrity=artifact(integrity_path),
            sourceProvenance=provenance, fontPreflight=fonts, audioReview=artifact(audio_path), pixelSamples=artifact(QA/'pixel-samples.json'),
            flaggedVoiceTransferWindows=len(audio['flaggedTransferWindows']), captionCount=len(captions['cues']),
            extractedUniqueFrames=pixels['uniqueFrameCount'], wholeCurrentEncodedMixAsr='pending-one-current-pass',
            allCaptionCutDirectPixelReview='pending', continuousFovMotionReview='pending',
            nativeAnd375MobileDirectReview='pending', humanWholeListeningAndPronunciation='pending', userFinalReview='pending', youtubeUploadPerformed=False)
        renderer.write(target, report); renderer.write(OUT/'qa/short-qa.json', report)
        return report
    except BaseException as error:
        pending.update(status='failed-retain-successful-stage-evidence', error=f'{type(error).__name__}: {error}')
        renderer.write(target, pending)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', '--verifyfull', dest='verify', action='store_true', help='Explicit root-only post-render whole-output QA')
    args = parser.parse_args()
    if not args.verify:
        parser.error('--verify required; importing starts no media work')
    report = verify()
    print(json.dumps({k: report[k] for k in ['status', 'technicalExecutionComplete', 'captionCount', 'extractedUniqueFrames', 'flaggedVoiceTransferWindows']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
