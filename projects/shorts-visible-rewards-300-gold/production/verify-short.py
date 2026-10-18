"""One current-output QA pass; importing performs no media work.

Run --verify only after root finishes rendering/muxing. Each final file is fully
decoded once, collecting video PTS and decoded audio together. The captioned
decode is reused for source/stem/encoded speech analysis. Pixel samples are
extracted in one separate select pass. No rendering, TTS, ASR or platform edits.
Actual visual review and human listening deliberately remain pending.
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

_spec = importlib.util.spec_from_file_location('shorts_renderer_for_qa', Path(__file__).with_name('render-short.py'))
renderer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(renderer)
ROOT, PROJECT, OUT = renderer.ROOT, renderer.PROJECT, renderer.OUT
QA = OUT / 'qa'
RATE, CHANNELS, FPS, FRAMES, SECONDS = 48000, 2, 60, 1812, 30.2
VOICE_END, ACTUAL_END = 30.1, 13.5


def ensure(condition, message):
    if not condition:
        raise AssertionError(message)


def db_rms(values):
    return 20 * math.log10(max(float(np.sqrt(np.mean(np.asarray(values, dtype=np.float64) ** 2))), 1e-12))


def read_json(path):
    return renderer.read(path)


def write_json(path, data):
    renderer.write(path, data)


def artifact(path):
    path = Path(path)
    try:
        name = renderer.rel(path)
    except ValueError:
        name = path.as_posix()
    return dict(path=name, sha256=renderer.sha(path), bytes=path.stat().st_size)


def probe(path):
    result = renderer.run([renderer.FFPROBE, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)])
    return json.loads(result.stdout)


def packet_audio_hash(path):
    """Hash AAC packet payloads without another audio decode."""
    result = renderer.run([renderer.FFPROBE, '-v', 'error', '-select_streams', 'a:0', '-show_packets', '-show_data_hash', 'sha256', '-show_entries', 'packet=pts,duration,size,data_hash', '-of', 'json', str(path)])
    packets = json.loads(result.stdout)['packets']
    ensure(packets and all('data_hash' in row for row in packets), 'Missing AAC payload hashes')
    ensure(all('pts' in row and 'duration' in row for row in packets), 'Missing audio packet timing')
    ensure(all(int(b['pts']) == int(a['pts']) + int(a['duration']) for a, b in zip(packets, packets[1:])), 'AAC packet PTS has a gap, overlap or reversal')
    h = hashlib.sha256()
    for row in packets:
        h.update((row['data_hash'] + '\n').encode('ascii'))
    return dict(packetCount=len(packets), payloadListSha256=h.hexdigest(), firstPts=packets[0].get('pts'), lastPts=packets[-1].get('pts'), ptsContiguous=True)


def decode_once(path, name):
    """Decode video and audio in one FFmpeg invocation; retain PCM for QA."""
    log = QA / f'{name}-whole-decode.log'
    command = [renderer.FFMPEG, '-hide_banner', '-loglevel', 'info', '-xerror', '-i', str(path),
               '-map', '0:v:0', '-vf', 'showinfo', '-an', '-fps_mode', 'passthrough', '-f', 'null', 'NUL',
               '-map', '0:a:0', '-vn', '-ar', str(RATE), '-ac', str(CHANNELS), '-f', 'f32le', 'pipe:1']
    result = renderer.run(command)
    stderr = result.stderr.decode(errors='replace')
    log.write_text(stderr, encoding='utf8')
    pattern = re.compile(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+)\s+pts_time:\s*([-+\d.eE]+)')
    rows = [(int(n), int(pts), float(t)) for n, pts, t in pattern.findall(stderr)]
    ensure(len(rows) == FRAMES, f'{name}: decoded {len(rows)} video frames, expected {FRAMES}')
    ensure([r[0] for r in rows] == list(range(FRAMES)), f'{name}: frame indices are not continuous')
    times = np.array([r[2] for r in rows])
    expected = np.arange(FRAMES, dtype=np.float64) / FPS
    error = float(np.max(np.abs(times - expected)))
    # showinfo prints decimal time with finite precision; integer PTS must also
    # advance by one exact constant tick throughout the file.
    ensure(error < 0.00006, f'{name}: nonuniform or offset video PTS ({error}s)')
    ticks = [rows[i + 1][1] - rows[i][1] for i in range(FRAMES - 1)]
    ensure(min(ticks) == max(ticks) and min(ticks) > 0, f'{name}: nonuniform integer video PTS')
    ensure(len(result.stdout) % (4 * CHANNELS) == 0, f'{name}: truncated decoded PCM bytes')
    pcm = np.frombuffer(result.stdout, dtype='<f4').reshape(-1, CHANNELS).copy()
    count = round(SECONDS * RATE)
    ensure(count <= len(pcm) <= count + 1024, f'{name}: decoded audio duration is wrong ({len(pcm)} samples)')
    ensure(np.isfinite(pcm).all(), f'{name}: nonfinite audio samples')
    return dict(status='pass', log=artifact(log), decodedVideoFrames=len(rows), videoPtsMaximumErrorSeconds=error,
                integerPtsStep=ticks[0], firstVideoPts=rows[0][1], lastVideoPts=rows[-1][1],
                decodedAudioSamples=len(pcm), expectedAudioSamples=count, aacPaddingSamples=len(pcm)-count), pcm[:count]


def source_and_inputs():
    source = read_json(PROJECT/'sources/source-map.json')
    proof = read_json(PROJECT/'sources/current-source-review.json')
    visual = read_json(OUT/'visual-build.json')
    pair = read_json(OUT/'pair-build.json')
    audio = read_json(OUT/'audio-build.json')
    ensure(source['videoUse']['in'] == 0 and source['videoUse']['out'] == ACTUAL_END, 'Actual source interval changed')
    ensure(source['videoUse']['speed'] == 1 and not source['videoUse']['loop'] and source['videoUse']['audio'] is False, 'Actual source must remain native speed, finite and silent')
    ensure(visual['sourceAllowedSeconds'] == [0, ACTUAL_END] and visual['sourceAudio'] is False, 'Visual receipt does not exclude the old purchase footage/audio')
    ensure(visual['frames'] == FRAMES and visual['signature']['videoEnd'] == ACTUAL_END, 'Stale visual build interval')
    master = ROOT/source['sourceMaster']
    ensure(renderer.sha(master) == proof['masterSha256'] == visual['signature']['source'], 'Parent master hash mismatch')
    ensure(proof['first13_5SecondsDirectlyViewed'] and proof['nativeFhdSourceVerified'] and proof['noLowResolutionPurchaseCutIncluded'], 'Missing actual FHD source-range proof')
    ensure(source['narration']['in'] == 0 and source['narration']['out'] == VOICE_END, 'Narration cut changed')
    ensure(source['narration']['postSilenceSeconds'] == .1 and source['narration']['nextAudibleParagraphExcluded'], 'Next paragraph exclusion is missing')
    ensure(audio['sourceCutSeconds'] == VOICE_END and audio['postSourceSilenceSeconds'] == .1, 'Wrong audio cut receipt')
    ensure(audio['voiceDuckApplied'] is False and audio['originalGameAudioIncluded'] is False and audio['foreignCommentaryIncluded'] is False, 'Unexpected speech ducking or foreign source audio')
    inputs = [Path(__file__), Path(__file__).with_name('render-short.py'), Path(__file__).with_name('build-audio.py'),
              PROJECT/'project.json', PROJECT/'planning/production-plan.json', PROJECT/'sources/source-map.json',
              PROJECT/'sources/current-source-review.json', PROJECT/'script/captions.json',
              OUT/'visual-build.json', OUT/'audio-build.json', OUT/'pair-build.json', OUT/'caption-layout.json', OUT/'code-preflight.json',
              OUT/'captions.ko.ass', OUT/'captions.ko.srt', OUT/'captions.en.srt', ROOT/source['narration']['wordEvidence'],
              ROOT/source['narration']['path'], ROOT/source['music']['path'], Path(renderer.FONTFILE), Path(renderer.BOLDFONT)]
    ensure(renderer.sha(ROOT/source['narration']['path']) == source['narration']['sha256'], 'Retained source voice changed')
    ensure(renderer.sha(ROOT/source['music']['path']) == source['music']['sha256'], 'Music changed')
    ensure(renderer.sha(ROOT/source['narration']['wordEvidence']) == source['narration']['wordEvidenceSha256'], 'Source timing changed')
    ensure(visual['signature']['code'] == renderer.sha(Path(__file__).with_name('render-short.py')), 'Visual receipt uses a different renderer')
    ensure(visual['signature']['captions'] == renderer.sha(PROJECT/'script/captions.json'), 'Visual captions input changed')
    ensure(pair['signature']['visual'] == renderer.sha(OUT/'portrait-visual.mp4'), 'Visual file changed after mux')
    ensure(pair['signature']['audio'] == renderer.sha(OUT/'final-mix.m4a'), 'Mix changed after mux')
    ensure(pair['signature']['ass'] == renderer.sha(OUT/'captions.ko.ass'), 'Caption ASS changed after mux')
    for item in pair['files']:
        ensure(renderer.sha(ROOT/item['path']) == item['sha256'], 'Encoded pair file hash differs from receipt')
    for item in audio['files'].values():
        ensure(renderer.sha(ROOT/item['path']) == item['sha256'], 'Audio build artifact hash differs from receipt')
    return source, proof, audio, inputs, dict(status='pass-recorded-range-and-current-hashes', retainedMasterSeconds=[0, ACTUAL_END],
        originalSourceSeconds=[80, 93.5], excludedOldLowResolutionMasterSeconds=[13.5, 19.5], originalGameAudio=False,
        rawOriginalCurrentlyPresent=False, decodedRawOriginalRechecked=False,
        sourceProof=artifact(PROJECT/'sources/current-source-review.json'), master=artifact(master))


def caption_and_font_preflight():
    captions = read_json(PROJECT/'script/captions.json')
    layout = read_json(OUT/'caption-layout.json')
    code = read_json(OUT/'code-preflight.json')
    ensure(13 <= len(captions['cues']) <= 17, 'Unexpected cue count; review changed short script')
    ensure(layout['inputSha256'] == renderer.sha(PROJECT/'script/captions.json'), 'Caption layout hash is stale')
    ensure(code['status'] == 'passed-code-and-font-layout-only', 'Font preflight has not passed')
    ensure(len(layout['rows']) == len(captions['cues']), 'Layout/caption cue mismatch')
    def stamp(value):
        h, m, s = value.replace(',', '.').split(':')
        return int(h)*3600 + int(m)*60 + float(s)
    srt_counts = {}
    for language in ['ko', 'en']:
        blocks = re.split(r'\n\s*\n', (OUT/f'captions.{language}.srt').read_text(encoding='utf-8-sig').strip())
        ensure(len(blocks) == len(captions['cues']), f'{language}: SRT cue count differs')
        for block, expected in zip(blocks, captions['cues']):
            lines = block.splitlines()
            ensure(3 <= len(lines) <= 4, f'{language}: SRT exceeds two lines or is empty')
            start, end = lines[1].split(' --> ')
            ensure(abs(stamp(start)-expected['start']) < .0006 and abs(stamp(end)-expected['end']) < .0006, f'{language}: SRT timing differs')
            ensure(' '.join(' '.join(lines[2:]).split()) == ' '.join(expected[language].split()), f'{language}: SRT text differs from the paired script')
        srt_counts[language] = len(blocks)
    for row, expected in zip(layout['rows'], captions['cues']):
        ensure(row['start'] == expected['start'] and row['end'] == expected['end'], 'Caption layout timing mismatch')
        ensure(len(row['lines']) <= 2 and row['font'] == 60, 'Caption max-lines/font changed')
        ensure(row['center'] == [510, 1380], 'Caption anchor moved')
        for line, measured in zip(row['lines'], row['textWidths']):
            ensure(abs(renderer.font(60).getlength(line) - measured) < .02, 'Font metric differs from saved layout')
            ensure(measured <= 796, 'Caption text exceeds portrait safe width')
        x, y, w, h = row['box']
        ensure(x >= 80 and x+w <= 930 and y+h+14 < 1560, 'Caption box/shadow crosses the planned safe area')
    result = dict(status='pass-code-and-font-metrics-only', cueCount=len(captions['cues']), maxLines=2,
                  captionFontPixels=60, captionCenter=[510, 1380], nativeResolution=[1080, 1920],
                  maximumMeasuredTextWidth=max(max(row['textWidths']) for row in layout['rows']),
                  fontFiles=[artifact(renderer.FONTFILE), artifact(renderer.BOLDFONT)],
                  pairedSrtCounts=srt_counts, pairedSrtTimingAndTextMatches=True,
                  existingPreflight=artifact(OUT/'code-preflight.json'), actualEncodedTextReview='pending', actualShortsUiReview='pending')
    return captions, result


def read_stereo(path):
    samples, rate = sf.read(path, dtype='float32', always_2d=True)
    ensure(rate == RATE and samples.shape[1] == CHANNELS, f'Unexpected stem format: {path}')
    ensure(len(samples) == round(SECONDS * RATE), f'Unexpected stem length: {path}')
    return samples


def grouped_ranges(rows, gap=.21):
    groups = []
    for row in rows:
        a, b = row['start'], row['end']
        if groups and a <= groups[-1]['end'] + gap:
            groups[-1]['end'] = max(groups[-1]['end'], b)
            groups[-1]['windowCount'] += 1
        else:
            groups.append(dict(start=max(0, a-.5), end=min(SECONDS, b+.5), windowCount=1))
    return groups


def audio_review(source, audio_receipt, encoded):
    prepared = read_stereo(OUT/'voice-input-stereo.wav')
    stem = read_stereo(OUT/'narration-stem.wav')
    music = read_stereo(OUT/'music-stem.wav')
    estimated_voice = encoded.astype(np.float64) - music.astype(np.float64)
    # This subtraction is an editorial diagnostic using our known music stem,
    # not a claim that the lossy AAC mixture can be perfectly source-separated.
    gain = float(audio_receipt['constantNarrationGainDb'])
    size, step = round(.4*RATE), round(.1*RATE)
    rows, source_drop_candidates = [], []
    for i in range(0, len(stem)-size+1, step):
        a, b = i/RATE, (i+size)/RATE
        raw = prepared[i:i+size].astype(np.float64)
        ref = stem[i:i+size].astype(np.float64)
        src_db, stem_db = db_rms(raw), db_rms(ref)
        if stem_db <= -43:
            continue
        residual = estimated_voice[i:i+size]
        denominator = float(np.sum(ref*ref))
        coefficient = float(np.sum(ref*residual)) / max(denominator, 1e-20)
        correlation = float(np.sum(ref*residual)) / max(float(np.sqrt(np.sum(ref*ref)*np.sum(residual*residual))), 1e-20)
        transfer = 20*math.log10(max(coefficient, 1e-12))
        rows.append(dict(start=a, end=b, sourceStereoDbfs=src_db, narrationStemDbfs=stem_db,
                         plannedConstantGainDb=gain, sourceToStemAttenuationRelativeToGainDb=stem_db-src_db-gain,
                         encodedEstimatedVoiceDbfs=db_rms(residual), encodedVoiceProjectionDb=transfer,
                         encodedVoiceCorrelation=correlation))
    ensure(bool(rows), 'No speech-active local windows')
    flags = [row for row in rows if row['sourceToStemAttenuationRelativeToGainDb'] < -2.5 or row['encodedVoiceProjectionDb'] < -2.5 or row['encodedVoiceCorrelation'] < .8]
    # Preserve natural source-level changes separately from induced attenuation.
    for before, after in zip(rows, rows[1:]):
        if after['start']-before['start'] <= .5 and before['sourceStereoDbfs']-after['sourceStereoDbfs'] >= 6:
            source_drop_candidates.append(dict(start=before['start'], end=after['end'], sourceDropDb=before['sourceStereoDbfs']-after['sourceStereoDbfs'],
                                               inducedAttenuationFlag=after in flags))
    original = ROOT/source['narration']['path']
    with sf.SoundFile(original) as stream:
        source_rate = stream.samplerate
        stream.seek(0)
        raw_cut = stream.read(round(VOICE_END*source_rate), dtype='float32', always_2d=True)
        next_region = stream.read(round(.1*source_rate), dtype='float32', always_2d=True)
    retained, retained_rate = sf.read(OUT/'retained-voice-24k.wav', dtype='float32', always_2d=True)
    ensure(source_rate == retained_rate and raw_cut.shape == retained.shape, 'Wrong retained voice interval')
    fade = round(.003*source_rate)
    ensure(np.array_equal(raw_cut[:-fade], retained[:-fade]), 'Approved retained PCM changed before the quiet de-click tail')
    expected_tail = raw_cut[-fade:]*np.linspace(1, 0, fade, dtype=np.float32)[:, None]
    ensure(np.array_equal(retained[-fade:], expected_tail), 'De-click tail differs from the documented final3ms fade')
    tail_input_db = db_rms(raw_cut[-fade:])
    ensure(tail_input_db < -60, 'De-click fade intrudes into audible speech')
    pad = prepared[round((VOICE_END+.01)*RATE):]
    ensure(float(np.max(np.abs(pad))) < 1e-8, 'Narration padding contains the next paragraph')
    quiet_boundary = dict(status='pass-PCM-boundary-only', sourceCutSeconds=VOICE_END, completeCaptionEndSeconds=29.98,
        sourceLast3msRmsDbfs=tail_input_db, deClickSeconds=.003, retainedPcmBeforeFadeExact=True,
        appendedSilenceStart=VOICE_END, appendedSilenceEnd=SECONDS, paddingAfterResamplerMarginPeak=float(np.max(np.abs(pad))),
        excludedOriginalNext100msRmsDbfs=db_rms(next_region), nextParagraphSamplesCopied=False,
        semanticFinalWordListening='pending', evidence='production/local/shorts-research/first30-word-boundaries.json')
    # Reuse the already completed loudnorm measurement only after exact AAC
    # build-artifact and final-pair payload hashes have been verified. Do not
    # repeat a successful measurement of unchanged encoded audio.
    measured = audio_receipt['measurements']['encoded']
    ensure(float(measured['input_tp']) <= -1.5, 'Encoded true peak exceeds-1.5dBTP')
    working_target=float(audio_receipt['signature']['targetSpeechLufs'])
    ensure(-18 <= working_target <= -14, 'Unexpected planned speech working target')
    ensure(working_target-1.5 <= float(measured['input_i']) <= working_target+1.5, 'Final integrated loudness differs from the selected speech working target')
    report = dict(status='pass-no-induced-attenuation-flags' if not flags else 'fail-flagged-ranges-need-contextual-review',
        windowSeconds=.4, hopSeconds=.1, activeThresholdDbfs=-43, plannedConstantNarrationGainDb=gain,
        speechDuckApplied=False, musicSubtractionIsApproximateDiagnostic=True, speechActiveWindows=rows,
        flaggedTransferWindows=flags, flaggedContextRanges=grouped_ranges(flags),
        naturalSourceDropCandidates=source_drop_candidates,
        naturalSourceDropReview='pending-contextual-review' if source_drop_candidates else 'no-candidates',
        actualEncodedLoudness=measured, encodedLoudnessEvidence='same-hash-audio-build.json-measurements.encoded',
        encodedTruePeakCeilingDbtp=-1.5, quietBoundary=quiet_boundary,
        wholeCurrentMixAsr='pending-separate-one-pass-by-root', humanWholeListeningAndPronunciation='pending')
    write_json(QA/'audio-review.json', report)
    return report


def pixel_samples(captions, captioned):
    requested = {}
    def add(frame, reason):
        frame = max(0, min(FRAMES-1, int(frame)))
        requested.setdefault(frame, []).append(reason)
    for cue in captions['cues']:
        a = math.ceil(cue['start']*FPS-1e-7)
        b = math.ceil(cue['end']*FPS-1e-7)-1
        for index, label in [(a+1, 'start'), ((a+b)//2, 'middle'), (b-1, 'end')]:
            add(index, f'caption-{cue["id"]}-{label}')
    cuts = [0, 1.74, 5.16, 7.6, 13.5, 16.34, 18.44, 20.06, 22.4, 25.88, 29.98, 30.1]
    for cut in cuts:
        index = math.ceil(cut*FPS-1e-7)
        for delta, label in [(-1, 'before'), (0, 'at'), (1, 'after')]:
            add(index+delta, f'cut-or-diagram-cue-{cut:g}-{label}')
    add(FRAMES-1, 'last-frame')
    numbers = sorted(requested)
    native = QA/'native'; mobile = QA/'mobile'; native.mkdir(parents=True, exist_ok=True); mobile.mkdir(parents=True, exist_ok=True)
    # One extraction for every unique selected frame; reruns reuse only a fully
    # successful same-hash QA report, never overwrite an incomplete old pass.
    ensure(not list(native.glob('*.png')), 'Pixel extraction already exists without a reusable complete receipt; inspect it rather than extracting duplicates')
    select = '+'.join(f'eq(n\\,{n})' for n in numbers)
    renderer.run([renderer.FFMPEG, '-v', 'warning', '-n', '-i', str(captioned), '-vf', f'select={select}', '-fps_mode', 'vfr', '-an', str(native/'frame-%03d.png')])
    files = sorted(native.glob('frame-*.png'))
    ensure(len(files) == len(numbers), 'Selected pixel sample count differs from the planned unique frames')
    samples = []
    for index, (number, path) in enumerate(zip(numbers, files), 1):
        with Image.open(path) as image:
            ensure(image.size == (1080, 1920), 'Native pixel sample dimensions changed')
            small = image.convert('RGB').resize((375, 667), Image.Resampling.LANCZOS)
            target = mobile/f'frame-{index:03}.jpg'; small.save(target, quality=94)
        samples.append(dict(index=index, frame=number, seconds=number/FPS, reasons=requested[number], native=renderer.rel(path), mobile=renderer.rel(target)))
    contacts = []
    label_font = ImageFont.truetype(renderer.FONTFILE, 16)
    cell_w, cell_h = 375, 700
    for first in range(0, len(samples), 8):
        group = samples[first:first+8]
        board = Image.new('RGB', (cell_w*2, cell_h*4), '#202020'); draw = ImageDraw.Draw(board)
        for local, row in enumerate(group):
            x, y = (local%2)*cell_w, (local//2)*cell_h
            draw.text((x+5, y+4), f'{row["index"]:03}  {row["seconds"]:.3f}s  f{row["frame"]}', font=label_font, fill='white')
            with Image.open(ROOT/row['mobile']) as image: board.paste(image, (x, y+30))
        path = QA/f'mobile-contact-{first//8+1:02}.jpg'; board.save(path, quality=94)
        contacts.append(artifact(path))
    report = dict(status='extracted-not-visually-approved', captionedSha256=renderer.sha(captioned),
        nativeResolution=[1080, 1920], mobileResolution=[375, 667], everyCaptionStartMiddleEndSampled=True,
        uniqueFrameCount=len(samples), captions=len(captions['cues']), sourceCutSeconds=ACTUAL_END,
        samples=samples, contactSheets=contacts, actualEncodedTextDirectReview='pending',
        movingDiagramAndSourceCutReview='pending', actualShortsUiClearance='pending', sampleExtractionPasses=1)
    write_json(QA/'pixel-samples.json', report)
    return report


def verify():
    QA.mkdir(parents=True, exist_ok=True)
    source, proof, audio_receipt, inputs, provenance = source_and_inputs()
    captions, fonts = caption_and_font_preflight()
    clean = OUT/f'{PROJECT.name}.clean.mp4'; captioned = OUT/f'{PROJECT.name}.captioned.mp4'
    current = dict(inputs=[artifact(p) for p in inputs], finalFiles=[artifact(clean), artifact(captioned)])
    signature = hashlib.sha256(json.dumps(current, sort_keys=True).encode('utf8')).hexdigest()
    target = QA/'short-qa.json'
    if target.exists():
        old = read_json(target)
        ensure(old.get('signature') == signature, 'QA inputs changed; preserve earlier QA and create a distinct revision instead of reusing it')
        ensure(old.get('technicalExecutionComplete'), 'Earlier QA was incomplete; inspect its successful stages before rerunning')
        return old
    pending = dict(signature=signature, startedAt=datetime.now(timezone.utc).isoformat(), technicalExecutionComplete=False,
        inputs=current, mediaProductionJobsStarted=0, asrJobsStarted=0, humanListening='pending', visualDirectReview='pending')
    write_json(target, pending)
    try:
        files, decoded = {}, {}
        packet_hashes = {}
        for name, path in [('clean', clean), ('captioned', captioned)]:
            meta = probe(path)
            video = [s for s in meta['streams'] if s['codec_type'] == 'video']
            audio = [s for s in meta['streams'] if s['codec_type'] == 'audio']
            ensure(len(video) == len(audio) == 1, f'{name}: expected one video and one audio stream')
            v, a = video[0], audio[0]
            ensure((v['width'], v['height']) == (1080, 1920), f'{name}: wrong portrait dimensions')
            ensure(Fraction(v['avg_frame_rate']) == FPS, f'{name}: wrong video fps')
            ensure(int(v.get('nb_frames', -1)) == FRAMES, f'{name}: wrong frame count')
            ensure(abs(float(meta['format']['duration'])-SECONDS) <= 1/FPS, f'{name}: wrong duration')
            ensure(a['codec_name'] == 'aac' and int(a['sample_rate']) == RATE and a['channels'] == CHANNELS, f'{name}: wrong AAC format')
            result, pcm = decode_once(path, name)
            packet_hashes[name] = packet_audio_hash(path)
            files[name] = dict(file=artifact(path), streams=dict(video=v, audio=a), fullDecode=result, audioPackets=packet_hashes[name])
            decoded[name] = pcm
        encoded_mix_hash = packet_audio_hash(OUT/'final-mix.m4a')
        ensure(packet_hashes['clean']['payloadListSha256'] == packet_hashes['captioned']['payloadListSha256'] == encoded_mix_hash['payloadListSha256'], 'AAC payload differs between final pair and mix')
        ensure(np.array_equal(decoded['clean'], decoded['captioned']), 'Decoded paired audio differs')
        integrity = dict(status='pass', expectedFrames=FRAMES, expectedSeconds=SECONDS, pairedAacPayloadIdentical=True,
                         mixAacPayloadIdentical=True, pairedDecodedAudioIdentical=True, files=files)
        write_json(QA/'integrity.json', integrity)
        audio_report = audio_review(source, audio_receipt, decoded['captioned'])
        pixels = pixel_samples(captions, captioned)
        result = dict(pending)
        result.update(technicalExecutionComplete=True, completedAt=datetime.now(timezone.utc).isoformat(),
            status='technical-pass-visual-audio-context-and-user-review-pending' if not audio_report['flaggedTransferWindows'] else 'audio-flags-need-targeted-review',
            integrity=integrity, sourceProvenance=provenance, fontPreflight=fonts,
            audioReview=artifact(QA/'audio-review.json'), pixelSamples=artifact(QA/'pixel-samples.json'),
            flaggedVoiceTransferWindows=len(audio_report['flaggedTransferWindows']),
            captionCount=len(captions['cues']), extractedUniqueFrames=pixels['uniqueFrameCount'],
            currentFinalMixAsr='pending-root-separate-one-current-pass', currentAllCaptionAndCutDirectPixelReview='pending',
            currentNativeAnd375MobileDirectReview='pending', movingDiagramsAndCutDirectReview='pending',
            humanWholeListeningAndPronunciation='pending', userFinalReview='pending', youtubeUploadPerformed=False)
        write_json(target, result)
        return result
    except BaseException as error:
        pending.update(status='failed-retain-partial-evidence-do-not-blindly-rerun', error=f'{type(error).__name__}: {error}')
        write_json(target, pending)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true', help='Root-only post-render QA; never render or generate speech')
    args = parser.parse_args()
    if not args.verify:
        parser.error('--verify is required; importing does not start work')
    report = verify()
    print(json.dumps({k: report[k] for k in ['status', 'technicalExecutionComplete', 'captionCount', 'extractedUniqueFrames', 'flaggedVoiceTransferWindows']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
