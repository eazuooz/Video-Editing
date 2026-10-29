"""Frame-exact v4 wrapper, preserving the 27 verified v3 body cuts and PCM.

Default/--prepare writes a local timeline and required clip frame counts only.
--preflight validates actual sources; --render/--verify delegate to the existing
compositor with a narrowly scoped, hash-verified retained-cut adapter. Never
edits old timelines, caches, narration, masters, or the compositor itself.
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct
import wave

import assemble_documentary as asm

PROJECT = asm.PROJECT
BASE = PROJECT / 'production/local/revision-v3-inputs/timeline.json'
CACHE = PROJECT / 'production/local/documentary-v1'
AUDIO = PROJECT / 'production/local/audio-v4'
WORKFLOW = PROJECT / 'production/local/workflow-v4'
WORK = PROJECT / 'production/local/documentary-v4'
OLD_NUMBERS = range(4, 31)
NEW_IDS = ['01-01', '01-02', '02-01', '02-02', '08-01']
MODES = {'01-02': 'workflow-overview', '02-01': 'rea-role',
         '02-02': 'workflow-overview', '08-01': 'actual-route'}
NEW_CAPTION_EMPHASIS = {'4': {'text':'REA','role':'term'},
                        '10': {'text':'AI 에이전트','role':'term'},
                        '23': {'text':'MCP','role':'term'},
                        '115': {'text':'프로토타입','role':'result'}}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def relative(path):
    path = Path(path).resolve()
    try:
        return path.relative_to(PROJECT).as_posix()
    except ValueError:
        return str(path)


def pid(entry):
    return f'{entry["scene_id"]}-{entry["paragraph"]:02d}'


def frame_at(sample, rate):
    return round(Fraction(int(sample) * 60, int(rate)))


def ceil_frames(samples, rate):
    n = int(samples) * 60
    return (n + int(rate) - 1) // int(rate)


def retained_beats(base):
    result = [copy.deepcopy(b) for b in base['beats']
              if int(b['id'].split('-')[0][1:]) in OLD_NUMBERS]
    require(len(result) == 27, 'Expected exactly b04 through b30')
    require([int(b['id'].split('-')[0][1:]) for b in result] == list(OLD_NUMBERS),
            'Retained cut order changed')
    require(sum(b['frames'] for b in result) == 15998, 'Baseline body frame count changed')
    return result


def timing_layout(timing, proof, old_beats):
    entries = timing['entries']; sr = timing['sample_rate']
    require(len(entries) == 19, 'Expected five new and fourteen retained paragraphs')
    require([pid(e) for e in entries[:4]] + [pid(entries[-1])] == NEW_IDS,
            'Unexpected new paragraph order')
    require(all(e['mode'] == 'synthesize' for e in entries[:4] + entries[-1:]),
            'New paragraphs are not labeled synthesize')
    require(all(e['mode'] == 'reuse' for e in entries[4:-1]), 'Body was not preserved')
    for a, b in zip(entries, entries[1:]):
        require(a['segmentEndSample'] == b['startSample'], 'PCM segments are discontinuous')
    require(entries[0]['startSample'] == 0, 'Narration must begin at body zero')
    require(entries[-1]['segmentEndSample'] == proof['finalSampleCount'], 'Final sample count differs')
    require(sr == proof['sampleRate'], 'PCM sample rates differ')
    retained = sum(b['frames'] for b in old_beats)
    body = ceil_frames(proof['finalSampleCount'], sr)
    relative_boundaries = {}; cursor = 0
    for beat in old_beats:
        key = '-'.join(beat['id'].split('-')[1:]).replace('-p', '-')
        relative_boundaries.setdefault(key, [cursor, cursor])
        cursor += beat['frames']; relative_boundaries[key][1] = cursor
    nominal = frame_at(entries[4]['startSample'], sr)
    possible = []
    for candidate in [nominal, nominal-1, nominal+1]:
        errors = []
        for e in entries[4:-1]:
            a, b = relative_boundaries[e['reuse']['baselineId']]
            errors += [abs(Fraction(e['startSample']*60, sr)-candidate-a),
                       abs(Fraction(e['segmentEndSample']*60, sr)-candidate-b)]
        if max(errors) <= 1:
            possible.append((abs(candidate-Fraction(entries[4]['startSample']*60,sr)),
                             max(errors), candidate))
    require(possible, 'No unchanged-body placement keeps all PCM boundaries within one frame')
    prefix = min(possible)[2]
    closing_start = prefix + retained
    require(abs(closing_start - Fraction(entries[-1]['startSample'] * 60, sr)) <= 1,
            'Retained body end drifts more than one frame from PCM')
    boundaries = [frame_at(e['startSample'], sr) for e in entries[:5]]
    boundaries[-1] = prefix
    requirements = []
    for i, e in enumerate(entries[:4]):
        requirements.append({'id': pid(e), 'startFrame': boundaries[i],
                             'frames': boundaries[i+1] - boundaries[i],
                             'pcmStartSample': e['startSample'], 'pcmEndSample': e['endSample']})
    requirements.append({'id': '08-01', 'startFrame': closing_start,
                         'frames': body - closing_start,
                         'pcmStartSample': entries[-1]['startSample'],
                         'pcmEndSample': entries[-1]['endSample']})
    for r in requirements:
        require(r['frames'] > 0, 'New clip has no frames')
        r.update(durationSeconds=r['frames']/60,
                 speechEndSeconds=r['pcmEndSample']/sr-r['startFrame']/60,
                 pcmToVisualStartSeconds=r['pcmStartSample']/sr-r['startFrame']/60)
    paragraph_boundaries = []
    cursor = prefix
    old_by_paragraph = {}
    for beat in old_beats:
        key = '-'.join(beat['id'].split('-')[1:]).replace('-p', '-')
        old_by_paragraph.setdefault(key, [cursor, cursor])
        cursor += beat['frames']; old_by_paragraph[key][1] = cursor
    for e in entries[4:-1]:
        old_id = e['reuse']['baselineId']; a, b = old_by_paragraph[old_id]
        delta = float(Fraction(e['startSample'] * 60, sr) - a)
        end_delta = float(Fraction(e['segmentEndSample'] * 60, sr) - b)
        require(abs(delta) <= 1 and abs(end_delta) <= 1,
                f'Retained paragraph {old_id} drift exceeds one frame')
        paragraph_boundaries.append({'newId': pid(e), 'baselineId': old_id,
                                     'visualStartFrame': a, 'visualEndFrame': b,
                                     'startErrorFrames': delta, 'endErrorFrames': end_delta})
    return {'newClips': requirements, 'prefixFrames': prefix,
            'retainedBodyFrames': retained, 'bodyFrames': body, 'totalFrames': body+720,
            'retainedParagraphBoundaries': paragraph_boundaries,
            'boundaryPolicy': 'Round prefix PCM boundaries; choose nearest body-start integer whose fourteen preserved boundaries all stay within one frame; retain all 15998 body frames; closing fills ceil(final PCM samples*60/rate). No hold, loop, resampling or tail duplication.'}


def float_wave_region(path, start, count, expected_rate, expected_total=None):
    """Read exact little-endian FLOAT samples without optional audio packages."""
    with Path(path).open('rb') as f:
        header = f.read(12)
        require(header[:4] == b'RIFF' and header[8:] == b'WAVE', 'Expected RIFF WAVE narration')
        fmt = None; data = None
        while True:
            chunk = f.read(8)
            if len(chunk) != 8: break
            name, size = struct.unpack('<4sI', chunk); position = f.tell()
            if name == b'fmt ': fmt = f.read(size)
            elif name == b'data': data = (position, size)
            f.seek(position + size + size % 2)
        require(fmt is not None and len(fmt) >= 16 and data is not None, 'Missing WAVE format/data')
        encoding, channels, rate, byte_rate, block_align, bits = struct.unpack('<HHIIHH', fmt[:16])
        require((encoding, channels, rate, byte_rate, block_align, bits) ==
                (3, 1, expected_rate, expected_rate*4, 4, 32), 'Expected mono 32-bit IEEE FLOAT narration')
        require(data[1] % 4 == 0, 'Unaligned FLOAT data')
        samples = data[1] // 4
        if expected_total is not None: require(samples == expected_total, 'Actual FLOAT sample length differs')
        require(0 <= start <= start+count <= samples, 'Truncated retained PCM region')
        f.seek(data[0]+start*4); raw = f.read(count*4)
        require(len(raw) == count*4, 'Truncated retained FLOAT payload')
        return hashlib.sha256(raw).hexdigest()


def verify_pcm(base, timing, proof):
    for key in ['reusedPcmBitExact', 'reusedBreathingSamplesPreserved', 'storedPcmVerified']:
        require(proof.get(key) is True, 'Missing actual PCM proof: '+key)
    for key in ['reusedPcmResampled', 'reusedPcmNormalized', 'reusedPcmFaded']:
        require(proof.get(key) is False, 'Retained PCM was processed: '+key)
    voice = AUDIO/'narration.wav'; old = asm.resolve(base['narration']['wav'])
    require(asm.digest(voice) == proof['voiceSha256'], 'Current narration hash differs')
    require(asm.digest(old) == proof['baselineAudioSha256'] == base['narration']['sha256'],
            'Baseline narration hash differs')
    block = proof['baselineBlock']; a = proof['newBlockStartSample']; b = proof['newBlockEndSampleExclusive']
    require(b-a == block['samples'] == block['endSampleExclusive']-block['startSample'],
            'Retained PCM block lengths differ')
    require(a == timing['entries'][4]['startSample'] and b == timing['entries'][-1]['startSample'],
            'Timing does not locate the claimed retained block')
    hashes = []
    for path, start, count in [(voice, a, b-a), (old, block['startSample'], block['samples'])]:
        hashes.append(float_wave_region(path,start,count,proof['sampleRate'],
                      proof['finalSampleCount'] if path == voice else None))
    require(hashes[0] == hashes[1] == block['sha256'], 'Actual retained decoded PCM differs')
    return {'currentWavSha256': proof['voiceSha256'], 'retainedDecodedPcmSha256': hashes[0],
            'samples': b-a, 'bitExactVerifiedFromStoredFiles': True}


def expected_fingerprint(plan, source, seconds_in, frames, overlay, audio, gain, viewport):
    return {'source': str(source), 'sourceSha256': plan['sources'][next(
        sid for sid, s in plan['sources'].items() if asm.resolve(s['file']) == source)]['sha256'],
        'inSeconds': seconds_in, 'frames': frames, 'audio': audio, 'gainDb': gain,
        'viewportHeight': viewport, 'overlaySha256': asm.digest(overlay) if overlay else None,
        'encoder': asm.encoder(plan)}


def verify_cached_cut(plan, beat, work, with_probe=False):
    stem = beat['id']; previous = asm.load(CACHE/(stem+'.receipt.json'))
    overlay = work/(stem+'.ass')
    source = asm.resolve(plan['sources'][beat['source']]['file'])
    expected = expected_fingerprint(plan, source, beat['sourceInSeconds'], beat['frames'], overlay,
                                    beat.get('sourceAudio', False), beat.get('sourceAudioGainDb', 0),
                                    beat.get('viewportHeight', 1080))
    old_input = previous['input']; other = {k:v for k,v in old_input.items() if k != 'pipelineSha256'}
    require(other == expected, 'Retained cut input differs: '+stem)
    require(len(old_input.get('pipelineSha256', '')) == 64, 'Legacy pipeline identity absent')
    require(asm.digest(CACHE/(stem+'.ass')) == expected['overlaySha256'], 'Legacy overlay changed: '+stem)
    video = CACHE/(stem+'.mp4'); audio = CACHE/(stem+'.wav')
    require(asm.digest(video) == previous['videoSha256'], 'Retained encoded video changed: '+stem)
    require(asm.digest(audio) == previous['audioSha256'], 'Retained audio changed: '+stem)
    with wave.open(str(audio), 'rb') as f:
        require((f.getframerate(), f.getnchannels(), f.getsampwidth(), f.getnframes()) ==
                (48000, 2, 2, beat['frames']*800), 'Retained PCM format/length differs: '+stem)
    if with_probe:
        v = asm.video_stream(asm.probe(video, plan))
        require((v['width'], v['height'], Fraction(v['avg_frame_rate']), int(v['nb_frames'])) ==
                (1920, 1080, 60, beat['frames']), 'Retained video metadata differs: '+stem)
    return {'cut': stem, 'video': str(video), 'audio': str(audio),
            'receiptSha256': asm.digest(CACHE/(stem+'.receipt.json')),
            'videoSha256': previous['videoSha256'], 'audioSha256': previous['audioSha256'],
            'verifiedInput': expected, 'legacyPipelineSha256': old_input['pipelineSha256'],
            'currentPipelineSha256': asm.digest(Path(asm.__file__)),
            'pipelineDifferenceReason': 'Retain previously inspected exact video and S16 clip audio. Current compositor fixes downstream mixed-PCM concatenation and AAC limiting; no old cache fingerprint is rewritten.',
            'audioFramesVerified': beat['frames']*800, 'videoMetadataVerified': with_probe}


def new_source(r, review_rows):
    sid = r['id']; intro = sid == '01-01'
    path = WORKFLOW/'intro-comparison.mp4' if intro else WORKFLOW/sid/(sid+'.mp4')
    receipt_path = WORKFLOW/'intro-comparison-receipt.json' if intro else WORKFLOW/sid/'receipt.json'
    receipt = asm.load(receipt_path) if receipt_path.is_file() else {}
    record = review_rows.get(sid, receipt)
    sha = asm.digest(path) if path.is_file() else None
    reviewed = bool(sha and record.get('sha256') == sha and record.get('motionReviewed') is True
                    and record.get('evidence'))
    if sha and receipt:
        require(receipt.get('sha256') == sha, 'New clip receipt hash differs: '+sid)
        require(receipt.get('actualFrames', receipt.get('frames')) == r['frames'], 'New clip frame count differs: '+sid)
    return {'file': relative(path), 'sha256': sha, 'kind': 'explanation' if intro else 'analysis-visualization',
            'motionReviewed': reviewed, 'evidence': record.get('evidence', ''),
            'renderReceipt': relative(receipt_path)}, ([] if reviewed else [sid+': rendered source/hash-bound internal motion review pending'])


def build(work, output, reviews):
    base = asm.load(BASE); timing = asm.load(AUDIO/'narration.timing.json'); proof = asm.load(AUDIO/'pcm-reuse-proof.json')
    old = retained_beats(base); layout = timing_layout(timing, proof, old); pcm = verify_pcm(base, timing, proof)
    work.mkdir(parents=True, exist_ok=True)
    review_rows = asm.load(reviews).get('sources', {}) if reviews.is_file() else {}
    plan = {k: copy.deepcopy(v) for k,v in base.items()
            if k not in ['sources', 'beats', 'captionEmphasis', '_file_hashes']}
    plan.update(workDirectory=relative(work), outputDirectory=str(output), revision='v4',
                note='Four new prefix paragraphs, exact inspected b04–b30 body and PCM, one new workflow conclusion.',
                captionEmphasis={}, editReady=False)
    used = {b['source'] for b in old}; plan['sources'] = {k:copy.deepcopy(v) for k,v in base['sources'].items() if k in used}
    plan['narration'].update(wav=relative(AUDIO/'narration.wav'), sha256=proof['voiceSha256'],
       koSrt=relative(AUDIO/'narration.ko.clauses.srt'), enSrt=relative(AUDIO/'narration.en.clauses.srt'), timingReviewed=False)
    blockers = []; new_beats = []
    for r in layout['newClips']:
        source, pending = new_source(r, review_rows); blockers += pending
        sid = 'v4-'+r['id']; plan['sources'][sid] = source
        new_beats.append({'id': sid, 'source': sid, 'sourceInSeconds': 0, 'frames': r['frames'],
          'sourceAudio': r['id']=='01-01', 'sourceAudioGainDb': 0, 'speed': 1, 'loop': False, 'freeze': False,
          'viewportHeight': 1080, 'pictureLabel': '', 'protectedRects': [], 'overlays': [],
          'observedAction': 'Observed original action beside independently authored prototype, then native prototype progression.' if r['id']=='01-01' else 'Progressive semantic workflow nodes and evidence connections, timed to the measured narration.',
          'narrationConnection': 'V4 paragraph '+r['id']+'; '+('full-workflow result introduction' if r['id']=='01-01' else MODES[r['id']])})
    plan['beats'] = new_beats[:4] + old + new_beats[-1:]
    plan['bodyFrameCount'] = layout['bodyFrames']
    for beat in old:
        asm.overlay_ass(work/(beat['id']+'.ass'), beat, plan['sources'][beat['source']]['kind'], beat['frames']/60)
    reuse = [verify_cached_cut(plan, b, work) for b in old]
    alignment_path = AUDIO/'review/caption-alignment-review.json'
    if alignment_path.is_file():
        align = asm.load(alignment_path)
        for lang in ['ko','en']:
            p = AUDIO/f'narration.{lang}.clauses.srt'
            require(p.is_file() and asm.digest(p) == align[lang+'Sha256'], 'Caption alignment hash differs')
        require(align.get('sourceWavSha256') == proof['voiceSha256'] and align.get('allTextPreserved') is True,
                'Caption alignment does not match current narration')
        require(align.get('manualSemanticReview') is True, 'Caption semantic mapping not inspected')
        cues = {str(c['id']):c for c in asm.read_srt(AUDIO/'narration.ko.clauses.srt')}
        for cid, emphasis in NEW_CAPTION_EMPHASIS.items():
            require(cid in cues and cues[cid]['text'].count(emphasis['text']) == 1,
                    'Current subtitle cue no longer matches approved v4 emphasis: '+cid)
        plan['captionEmphasis'] = copy.deepcopy(NEW_CAPTION_EMPHASIS)
        plan['narration']['timingReviewed'] = True
    else:
        blockers.append('Current actual narration/clause alignment pending')
    plan['editReady'] = not blockers
    plan['retainedBody'] = {'baselineTimeline': relative(BASE), 'baselineTimelineSha256': asm.digest(BASE),
      'cacheDirectory': relative(CACHE), 'cutIds': [b['id'] for b in old], 'pcmProof': relative(AUDIO/'pcm-reuse-proof.json'),
      'reuseEvidence': relative(work/'reuse-proof.json'), 'frames': 15998}
    asm.save(work/'timeline.json', plan)
    asm.save(work/'required-clips.json', {'createdAt': asm.now(), **layout,
      'instructions': 'Render the five new clips to these exact frame counts. Do not extend retained cuts or duplicate final frames.',
      'sourceReadiness': blockers, 'editReady': plan['editReady']})
    asm.save(work/'reuse-proof.json', {'checkedAt': asm.now(), 'status': 'hash-verified-retained-inputs',
      'wrapperSha256': asm.digest(Path(__file__)), 'baselineTimelineSha256': asm.digest(BASE),
      'pcm': pcm, 'timing': layout, 'cuts': reuse, 'humanReview': False,
      'scope': 'Stored PCM equality, exact retained clip inputs/overlays/video+audio hashes, PCM length. Final captioned audiovisual review remains separate.'})
    return plan, layout, blockers


def install_retained_adapter(plan, work):
    original = asm.render_clip
    old_beats = {b['id']:b for b in retained_beats(asm.load(BASE))}
    actual = {}; evidence = []
    def adapter(p, source, seconds_in, frames, stem, directory, overlay=None, audio=False, gain=0, viewport_height=1080):
        if stem not in old_beats:
            return original(p, source, seconds_in, frames, stem, directory, overlay, audio, gain, viewport_height)
        beat = old_beats[stem]
        current = expected_fingerprint(p, source, seconds_in, frames, overlay, audio, gain, viewport_height)
        row = verify_cached_cut(p, beat, directory, with_probe=True)
        require(current == row['verifiedInput'], 'Adapter invocation changed retained inputs: '+stem)
        require(stem not in actual, 'Retained cut requested twice')
        actual[stem] = True; evidence.append(row)
        asm.save(work/'reuse-render-receipt.json', {'checkedAt':asm.now(), 'cuts':evidence,
          'complete':len(evidence)==27, 'notReencoded':True, 'actualOldPathsReturned':True,
          'pipelineChangedOnlyDownstream':True, 'humanReview':False})
        return Path(row['video']), Path(row['audio'])
    asm.render_clip = adapter
    return original, actual


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepare', action='store_true'); ap.add_argument('--preflight', action='store_true')
    ap.add_argument('--render', action='store_true'); ap.add_argument('--verify', action='store_true')
    ap.add_argument('--work', type=Path, default=WORK)
    ap.add_argument('--output', type=Path, default=asm.REPO/'output/buckshot-roulette-reverse-engineering-v4')
    ap.add_argument('--reviews', type=Path, default=WORKFLOW/'source-review.json')
    args = ap.parse_args(); work = args.work.resolve(); output = args.output.resolve()
    require(work.is_relative_to(PROJECT/'production/local'), 'Work must remain project-local and ignored')
    require(output.is_relative_to(asm.REPO/'output'), 'Output must remain in repository output')
    require(output != asm.resolve(asm.load(BASE)['outputDirectory']), 'Preserve old delivered output')
    plan, layout, blockers = build(work, output, args.reviews.resolve())
    if args.preflight or args.render or args.verify:
        require(not blockers, 'V4 source readiness: '+'; '.join(blockers))
        if args.render:
            control = asm.load(asm.REPO/'shared/publishing/video-production-control.json')
            auth = control.get('scopedSetupAuthorizations', {}).get(PROJECT.name, {})
            require(auth.get('productionAllowedNow') is True, 'Current scoped production authorization absent')
        receipt = asm.validate(plan, work/'timeline.json', work)
        if args.render:
            original, returned = install_retained_adapter(plan, work)
            try:
                asm.render(plan, work/'timeline.json', work, receipt)
                require(len(returned) == 27, 'Not all retained cuts were reused')
            finally:
                asm.render_clip = original
        if args.verify:
            asm.verify(plan, receipt, work)
    print(json.dumps({'status':'prepared' if blockers else 'ready-for-preflight', 'timeline':str(work/'timeline.json'),
        'requiredClips':str(work/'required-clips.json'), 'reusedCuts':27,
        'bodyFrames':layout['bodyFrames'], 'totalFrames':layout['totalFrames'],
        'readiness':blockers, 'rendered':args.render, 'verified':args.verify}, ensure_ascii=False))


if __name__ == '__main__':
    main()
