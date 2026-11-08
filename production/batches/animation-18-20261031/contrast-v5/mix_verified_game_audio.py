"""Add only the nine bounded, source-matched native gameplay audio proposals.

This is a local-review mixer, not a rights or listening approval. It follows the
actual final picture EDL through fragments and speech composites, including only
their unscaled native prefix. It never adds sound to still/UE/other-game frames.
The inherited complete mix is never gained, limited, stretched or normalized.
stdout is exactly the chosen WAV path; diagnostics and receipt live separately.
"""
from pathlib import Path
import argparse, hashlib, json, math, os, re, subprocess, sys
import numpy as np
import soundfile as sf

H = Path(__file__).resolve().parent
R = H.parents[3]
RATE, FPS, SPF = 48000, 60, 800
TECH = H / 'footage/audio-technical-windows.json'
PLATES = H / 'game-plates-manifest.json'
if (H / 'game-plates-caption-safe.json').exists():
    PLATES = H / 'game-plates-caption-safe.json'
ALLOWED = {'marisa-follow', 'ringfit-warrior1', 'juri-hit-b'}


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))


def path(p):
    return R / Path(p)


def key(p):
    return os.path.normcase(os.path.abspath(path(p)))


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix('.' + str(os.getpid()) + '.pending')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(tmp, p)


def intersection(a, b, c, d):
    return max(a, c), min(b, d)


def authorization(ep):
    c = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert ep in c['episodes'] and ep != 'A03'
    assert c['fullLocalProductionAuthorized'] and c['renderAuthorized']


def checked(p, digest, cache):
    p = path(p)
    stamp = (key(p), p.stat().st_size, p.stat().st_mtime_ns)
    actual = cache.setdefault(stamp, None)
    if actual is None:
        actual = cache[stamp] = sha(p)
    assert digest and actual == digest, ('Changed media', str(p), digest, actual)
    return p


def native_leaves(edl, registry, verify):
    """Return 1:1 output-frame -> original game-plate-frame spans.

    Registry and composition references use actual paths, not an ID substring.
    Each speech composite's originalUnscaledFrames is a hard exclusion boundary.
    """
    edits = {key(q['picture']): q for q in edl['pictureEdits'] if 'mediaComposition' in q}
    leaves = []

    def visit(source, start, frames, out, expected_hash, ancestry):
        assert all(isinstance(x, int) for x in (start, frames, out)) and min(start, out) >= 0 and frames > 0
        k = key(source)
        if k in registry:
            p = registry[k]
            assert expected_hash == p['pictureSha256'], ('Plate hash disagreement', p['id'])
            verify(source, expected_hash)
            assert start + frames <= p['sourceStartFrame'] + p['newFrames']
            leaves.append({'plate': p, 'plateStartFrame': start, 'frames': frames,
                           'outputStartFrame': out, 'ancestry': ancestry})
            return
        q = edits.get(k)
        if q is None:
            return  # Preserved baseline, own explanation or unrelated clip.
        assert expected_hash == q['pictureSha256']
        verify(source, expected_hash)
        comp = q['mediaComposition']
        ceiling = comp['originalUnscaledFrames']
        assert isinstance(ceiling, int) and ceiling >= 0
        sigfile = path(source).parent / 'signature.json'
        if verify is not _test_verify:
            sig = read(sigfile)
            assert sig['nativeFrames'] == ceiling
            assert len(sig['clips']) == len(comp['clips'])
            for c, s in zip(comp['clips'], sig['clips']):
                assert all(c.get(t) == s.get(t) for t in c), ('Composition signature mismatch', q['id'])
        else:
            sig = {'clips': [dict(c, sha256=c['testSha256']) for c in comp['clips']]}
        cursor = 0
        for c, s in zip(comp['clips'], sig['clips']):
            lo, hi = intersection(start, start + frames, cursor, min(cursor + c['frames'], ceiling))
            if lo < hi:
                visit(c['source'], c['sourceStartFrame'] + lo - cursor, hi - lo,
                      out + lo - start, s['sha256'], ancestry + [q['id'], c['id']])
            cursor += c['frames']

    for row in edl['pictureEdl']:
        assert row['frames'] == row['outputEndFrame'] - row['outputStartFrame']
        visit(row['source'], row['sourceStartFrame'], row['frames'], row['outputStartFrame'],
              row['sourceSha256'], [row['id']])
    return leaves


def _test_verify(*args):
    pass


def resolve(ep, edl, tech, plates, cache):
    proposals = [q for q in tech['nativePlateProposals'] if q['episode'] == ep]
    if not proposals:
        return []
    byid = {}
    for q in proposals:
        assert q['sourceKey'] in ALLOWED and q['speed'] == 1 and q['nativeOnly']
        assert q['neverCarryIntoAnalysis'] and q['localReviewOnly']
        byid.setdefault(q['plateId'], []).append(q)
    episode = next(e for e in plates['episodes'] if e['id'] == ep)
    selected = [p for p in episode['pictureEdits'] if p['id'] in byid]
    assert set(byid) == {p['id'] for p in selected}, 'Reviewed game plate is absent from current manifest'
    registry = {}
    for p in selected:
        assert p['sourceClassification'] == 'game' and p['kind'] == 'independent-gameplay'
        receipt = read(path(p['receipt']))
        assert receipt['sha256'] == p['pictureSha256'] and receipt['mediaSegments'] == p['mediaSegments']
        assert receipt['frames'] == p['newFrames'] and receipt['silent'] is True
        registry[key(p['picture'])] = p
    leaves = native_leaves(edl, registry, lambda p, h: checked(p, h, cache))
    records = {s['sourceKey']: s for s in tech['sources']}
    placements = []
    for leaf in leaves:
        p = leaf['plate']
        for prop in byid[p['id']]:
            record = records[prop['sourceKey']]
            assert record['localReviewMixRecommended'] and not record['publicationClear']
            assert record['audioSha256'] == prop['audioSha256']
            checked(record['videoFile'], record['videoSha256'], cache)
            checked(record['audioFile'], record['audioSha256'], cache)
            checked(record['reviewBasis']['file'], record['reviewBasis']['sha256'], cache)
            for seg in p['mediaSegments']:
                if seg['kind'] != 'native-gameplay' or seg['sourceKey'] != prop['sourceKey']:
                    continue
                assert seg['sourceSha256'] == record['videoSha256'] and seg.get('sourceFrameTimes') is None
                assert abs((seg['sourceLocalOut'] - seg['sourceLocalIn']) * FPS - seg['frames']) <= 1.01, 'Not native-time media'
                # The already-reviewed proposal must still select this exact source interval.
                offset = prop['offsetInPreparedNativePlateSeconds'] * FPS
                n = prop['durationSeconds'] * FPS
                assert abs(offset - round(offset)) < .001 and abs(n - round(n)) < .001
                a, b = round(offset), round(offset + n)
                va = seg['sourceLocalIn'] + (a - seg['offsetFrame']) / FPS
                vb = va + (b - a) / FPS
                assert seg['offsetFrame'] <= a < b <= seg['offsetFrame'] + seg['frames']
                assert abs(va - prop['videoSourceLocalRange'][0]) < 1e-5
                assert abs(vb - prop['videoSourceLocalRange'][1]) < 1e-5
                assert abs(va + record['audioSeekOffsetSeconds'] - prop['audioSeekSeconds']) < 1e-5
                lo, hi = intersection(leaf['plateStartFrame'], leaf['plateStartFrame'] + leaf['frames'], a, b)
                if lo >= hi:
                    continue
                source_in = va + (lo - a) / FPS
                source_out = source_in + (hi - lo) / FPS
                assert any(w[0] - 1e-5 <= source_in < source_out <= w[1] + 1e-5
                           for w in record['reviewedLocalAudioWindows'])
                assert any(w[0] - 1e-5 <= source_in < source_out <= w[1] + 1e-5
                           for w in record['sourceContainedVideoLocalWindows'])
                out = leaf['outputStartFrame'] + lo - leaf['plateStartFrame']
                placements.append({'plateId': p['id'], 'sourceKey': prop['sourceKey'],
                    'outputStartFrame': out, 'outputEndFrame': out + hi - lo,
                    'outputStartSample': out * SPF, 'samples': (hi - lo) * SPF,
                    'plateFrameRange': [lo, hi], 'sourceVideoSeconds': [source_in, source_out],
                    'audioFile': record['audioFile'], 'audioSha256': record['audioSha256'],
                    'audioSeekSeconds': source_in + record['audioSeekOffsetSeconds'],
                    'audioSeekOffsetSeconds': record['audioSeekOffsetSeconds'],
                    'ancestry': leaf['ancestry'], 'nativeSpeed': 1,
                    'asrEvidence': record['reviewBasis'], 'sourcePublicationClear': False,
                    'humanListening': False, 'scope': 'bounded-local-review-candidate'})
    placements.sort(key=lambda q: q['outputStartSample'])
    assert all(a['outputStartSample'] + a['samples'] <= b['outputStartSample']
               for a, b in zip(placements, placements[1:])), 'Overlapping game audio overlays'
    return placements


def decode_audio(q):
    # Decode the bounded source file from its presentation origin; explicitly
    # trim resampled PCM. A post-input -ss combined with end_sample could apply
    # in the wrong order. first_pts=0 honors the stream's tiny initial timestamp
    # gap without adding discarded preroll; AAC skip-samples stays decoder-owned.
    start = round(q['audioSeekSeconds'] * RATE)
    assert start >= 0
    cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-threads', '1', '-i', str(path(q['audioFile'])),
           '-map', '0:a:0', '-vn', '-filter_threads', '1',
           '-af', f"aresample={RATE}:first_pts=0,atrim=start_sample={start}:end_sample={start + q['samples']},asetpts=PTS-STARTPTS", '-ac', '2',
           '-c:a', 'pcm_f32le', '-f', 'f32le', '-']
    raw = subprocess.check_output(cmd, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    data = np.frombuffer(raw, dtype='<f4').reshape(-1, 2).copy()
    assert len(data) == q['samples'] and np.isfinite(data).all(), 'Source audio shorter than native picture'
    return data


def rms(x):
    return float(np.sqrt(np.mean(np.asarray(x, dtype=np.float64) ** 2))) if x.size else 0.


def db(x):
    return 20 * math.log10(max(float(x), 1e-12))


def speech_ranges(ep, edlfile, cache):
    folder = H / 'local/final-audio' / ep / 'captions'
    report = read(folder / 'review.json')
    assert report['assemblySha256'] == sha(edlfile), 'Caption timing does not match this final assembly'
    srt = folder / 'captions.provisional.ko.srt'
    if not srt.exists():
        candidates = list(folder.glob('*.ko.srt'))
        assert len(candidates) == 1
        srt = candidates[0]
    def ticks(h, m, s, ms):
        return round((int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000) * RATE)
    pattern = r'(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)'
    ranges = [(ticks(*v[:4]), ticks(*v[4:])) for v in re.findall(pattern, srt.read_text('utf-8-sig'))]
    assert ranges
    return ranges, {'path': str(srt), 'sha256': sha(srt), 'reviewSha256': sha(folder / 'review.json')}


def level_overlay(raw, base, q, speech):
    effect = raw.astype(np.float64)
    fade = min(480, len(effect) // 2)
    ramp = np.linspace(0., 1., fade)
    effect[:fade] *= ramp[:, None]
    effect[-fade:] *= ramp[::-1, None]
    source_rms = rms(effect)
    gain = min(1., 10 ** (-32 / 20) / max(source_rms, 1e-12))
    active = []
    for i in range(0, len(effect), 19200):
        j = min(i + 19200, len(effect))
        a, b = q['outputStartSample'] + i, q['outputStartSample'] + j
        voiced = sum(max(0, min(b, d) - max(a, c)) for c, d in speech) >= .5 * (b - a)
        br, er = rms(base[i:j]), rms(effect[i:j])
        if voiced and br >= .008 and er > 1e-8:
            cap = br * 10 ** (-12 / 20) / er
            gain = min(gain, cap)
            active.append({'startOffsetSample': i, 'samples': j - i,
                           'existingProgramRmsDbfs': db(br), 'rawGameRmsDbfs': db(er)})
    # Reduce only the new track. Never normalize or limit the inherited program.
    base64 = base.astype(np.float64)
    if np.max(np.abs(base64)) > 1.:
        raise AssertionError('Inherited mix already exceeds full scale; do not silently repair it')
    positive, negative = effect > 1e-10, effect < -1e-10
    caps = [gain]
    if np.any(positive):
        caps.append(float(np.min((.999999 - base64[positive]) / effect[positive])))
    if np.any(negative):
        caps.append(float(np.min((-.999999 - base64[negative]) / effect[negative])))
    pre_peak_gain = gain
    gain = max(0., min(caps))
    overlay = effect * gain
    mixed = (base64 + overlay).astype('float32')
    assert float(np.max(np.abs(mixed))) <= max(1., float(np.max(np.abs(base))))
    assert np.array_equal(mixed[[0, -1]], base[[0, -1]]), 'Fade endpoints must retain exact base samples'
    for win in active:
        i, n = win['startOffsetSample'], win['samples']
        win['mixedGameRmsDbfs'] = db(rms(overlay[i:i+n]))
        win['gameBelowExistingProgramDb'] = win['existingProgramRmsDbfs'] - win['mixedGameRmsDbfs']
        assert win['gameBelowExistingProgramDb'] >= 11.999
    return mixed, {'gain': gain, 'gainDb': db(gain), 'gainBeforePeakCap': pre_peak_gain,
        'sourceRmsDbfs': db(source_rms), 'overlayRmsDbfs': db(rms(overlay)),
        'originalPeak': float(np.max(abs(base))), 'newPeak': float(np.max(abs(mixed))),
        'gameOnlyFadeSamplesEachSide': fade, 'fadeMilliseconds': fade / RATE * 1000,
        'speechActiveWindows': active, 'baseGain': 1., 'baseLimiter': False,
        'baseNormalization': False, 'sourceAmplified': gain > 1.,
        'levelReference': 'Caption-active original complete-mix RMS proxy, NOT an isolated narration stem or human listening.',
        'limitations': 'The -32 dBFS RMS ceiling is a conservative additive local-review starting level, not LUFS or a new series audio standard. Actual voice masking and music permissions remain to be reviewed.'}


def pcm_proof(basepath, newpath, placements):
    """Re-read every serialized sample; complement must be bit-exact float PCM."""
    original_hash, untouched_hash = hashlib.sha256(), hashlib.sha256()
    unchanged, changed = 0, 0
    ranges = [(q['outputStartSample'], q['outputStartSample'] + q['samples']) for q in placements]
    with sf.SoundFile(basepath) as a, sf.SoundFile(newpath) as b:
        assert a.frames == b.frames and a.samplerate == b.samplerate == RATE and a.channels == b.channels == 2
        for start in range(0, a.frames, RATE * 8):
            x = a.read(RATE * 8, dtype='float32', always_2d=True)
            y = b.read(len(x), dtype='float32', always_2d=True)
            mask = np.ones(len(x), dtype=bool)
            for lo, hi in ranges:
                aa, bb = intersection(start, start + len(x), lo, hi)
                if aa < bb:
                    mask[aa-start:bb-start] = False
            assert np.array_equal(x[mask], y[mask]), 'Original voice/BGM changed outside native overlays'
            original_hash.update(x[mask].tobytes()); untouched_hash.update(y[mask].tobytes())
            unchanged += int(mask.sum()); changed += int(np.count_nonzero(np.any(x != y, axis=1)))
    assert original_hash.hexdigest() == untouched_hash.hexdigest()
    return {'allComplementSamplesBitExact': True, 'untouchedSampleFrames': unchanged,
            'actuallyChangedSampleFrames': changed, 'complementPcmSha256': original_hash.hexdigest(),
            'basePreservationInsideOverlay': 'Original samples are the unity-gain additive summand; only the game stem is faded/gained. Float32 sum rounding applies inside overlay.',
            'noNewClippingByConstruction': True}


def main(ep, assembly):
    authorization(ep)
    assembly = Path(assembly).absolute()
    edl = read(assembly)
    assert edl['id'] == ep and edl['sampleRate'] == RATE and edl['audioSamples'] == edl['frames'] * SPF
    cache = {}
    tech, plates = read(TECH), read(PLATES)
    assert len(tech['nativePlateProposals']) == 9 and {q['sourceKey'] for q in tech['nativePlateProposals']} == ALLOWED
    placements = resolve(ep, edl, tech, plates, cache)
    base = assembly.parent / 'captionless/mix.wav'
    assembled = read(base.parent / 'receipt.json')
    assert assembled['id'] == ep and assembled['wholeVideoRendered']
    assert assembled['pictureEdl'] == edl['pictureEdl'] and assembled['audioEdl'] == edl['audioEdl']
    checked(base, assembled['audioProof']['sha256'], cache)
    info = sf.info(base)
    assert info.samplerate == RATE and info.channels == 2 and info.frames == edl['audioSamples']
    folder = H / 'local/final-game-audio' / ep
    folder.mkdir(parents=True, exist_ok=True)
    inputs = {'assembly': str(assembly), 'assemblySha256': sha(assembly), 'baseMix': str(base),
              'baseMixSha256': sha(base), 'assemblyReceiptSha256': sha(base.parent / 'receipt.json'),
              'technicalWindowsSha256': sha(TECH), 'gamePlatesManifestSha256': sha(PLATES),
              'codeSha256': sha(__file__)}
    if not placements:
        receipt = {'episode': ep, 'status': 'passthrough-no-eligible-native-game-audio', 'inputs': inputs,
            'output': str(base), 'sha256': inputs['baseMixSha256'], 'placements': [],
            'fullWavDuplicated': False, 'unchangedPcm': True, 'humanListening': False,
            'publicationClear': False, 'newAsr': False, 'gpuUsed': False}
        save(folder / 'receipt.json', receipt)
        print(str(base)); return
    speech, caption_proof = speech_ranges(ep, assembly, cache)
    inputs['captionTiming'] = caption_proof
    prior = read(folder / 'receipt.json') if (folder / 'receipt.json').exists() else {}
    output = folder / 'mix.wav'
    if (prior.get('inputs') == inputs and output.exists() and prior.get('sha256') == sha(output)
            and prior.get('qa', {}).get('allComplementSamplesBitExact')):
        print(str(output)); return
    pending = folder / f'mix.{os.getpid()}.pending.wav'
    evidence = []
    with sf.SoundFile(base) as source, sf.SoundFile(pending, 'w', samplerate=RATE, channels=2, subtype='FLOAT') as dest:
        cursor = 0
        for q in placements:
            while cursor < q['outputStartSample']:
                data = source.read(min(RATE * 8, q['outputStartSample'] - cursor), dtype='float32', always_2d=True)
                assert len(data); dest.write(data); cursor += len(data)
            original = source.read(q['samples'], dtype='float32', always_2d=True)
            assert len(original) == q['samples']
            mixed, gain_proof = level_overlay(decode_audio(q), original, q, speech)
            dest.write(mixed); cursor += len(mixed)
            evidence.append({**q, 'level': gain_proof})
        while cursor < source.frames:
            data = source.read(min(RATE * 8, source.frames - cursor), dtype='float32', always_2d=True)
            dest.write(data); cursor += len(data)
    qa = pcm_proof(base, pending, evidence)
    # Abort rather than publish a mix from inputs changed by a concurrent job.
    assert sha(assembly) == inputs['assemblySha256'] and sha(base) == inputs['baseMixSha256']
    os.replace(pending, output)
    receipt = {'episode': ep, 'status': 'bounded-source-audio-added-local-review-pending', 'inputs': inputs,
        'output': str(output), 'sha256': sha(output), 'sampleRate': RATE, 'channels': 2,
        'samples': info.frames, 'placements': evidence, 'qa': qa, 'fullWavDuplicated': True,
        'nativeOnly': True, 'stillAnalysisExcluded': True, 'ownExplanationExcluded': True,
        'otherGamesExcluded': True, 'gainOrLimiterAppliedToOriginalMix': False,
        'humanListening': False, 'publicationClear': False, 'newAsr': False, 'gpuUsed': False,
        'remainingReview': ['Actual final listening/synchronization and masking',
                            'Conditional recorder/publisher/third-party sound and music rights before publication']}
    save(folder / 'receipt.json', receipt)
    print(str(output))


def self_test():
    # A fragmented native plate and a speech composite with a still suffix and
    # incidental next-shot tail must resolve to the exact native frames only.
    p = {'id': 'test-native', 'picture': 'test-native.mp4', 'pictureSha256': 'a',
         'sourceStartFrame': 0, 'newFrames': 600}
    comp = {'id': 'speech', 'picture': 'speech.mp4', 'pictureSha256': 'b',
        'mediaComposition': {'originalUnscaledFrames': 180, 'clips': [
            {'id': 'own', 'source': 'own.mp4', 'sourceStartFrame': 0, 'frames': 60, 'testSha256': 'c'},
            {'id': 'game', 'source': p['picture'], 'sourceStartFrame': 100, 'frames': 120, 'testSha256': 'a'},
            {'id': 'incidental', 'source': p['picture'], 'sourceStartFrame': 400, 'frames': 5, 'testSha256': 'a'}]}}
    edl = {'pictureEdits': [comp], 'pictureEdl': [
        {'id': 'fragment', 'source': p['picture'], 'sourceSha256': 'a', 'sourceStartFrame': 60,
         'frames': 40, 'outputStartFrame': 0, 'outputEndFrame': 40},
        {'id': 'speech', 'source': 'speech.mp4', 'sourceSha256': 'b', 'sourceStartFrame': 90,
         'frames': 240, 'outputStartFrame': 40, 'outputEndFrame': 280}]}
    leaves = native_leaves(edl, {key(p['picture']): p}, _test_verify)
    assert [(x['plateStartFrame'], x['frames'], x['outputStartFrame']) for x in leaves] == [(60, 40, 0), (130, 90, 40)]
    n = 48000
    t = np.arange(n) / RATE
    base = np.repeat((.2 * np.sin(t * 400 * 2 * np.pi))[:, None], 2, axis=1).astype('float32')
    game = np.repeat((.8 * np.sin(t * 900 * 2 * np.pi))[:, None], 2, axis=1).astype('float32')
    out, proof = level_overlay(game, base, {'outputStartSample': 0}, [(0, n)])
    assert proof['overlayRmsDbfs'] <= -31.999 and proof['baseGain'] == 1 and proof['gain'] <= 1
    assert np.array_equal(out[[0, -1]], base[[0, -1]])
    near_peak = np.full((n, 2), .9999, dtype='float32')
    capped, capproof = level_overlay(np.ones_like(near_peak), near_peak, {'outputStartSample': 0}, [])
    assert np.max(capped) < 1 and capproof['gain'] < capproof['gainBeforePeakCap']
    # Serialize a tiny explicit fixture and verify every sample outside its
    # overlay, including a silent gap, rather than just comparing durations.
    fixture = H / 'local/final-game-audio/_qa'
    fixture.mkdir(parents=True, exist_ok=True)
    original = np.concatenate([base[:6000], base, base[:7000]])
    final = np.concatenate([base[:6000], out, base[:7000]])
    before, after = fixture / 'fixture-base.wav', fixture / 'fixture-result.wav'
    sf.write(before, original, RATE, subtype='FLOAT')
    sf.write(after, final, RATE, subtype='FLOAT')
    exact = pcm_proof(before, after, [{'outputStartSample': 6000, 'samples': n}])
    assert exact['untouchedSampleFrames'] == 13000
    return {'fragmentAndSpeechNativePrefixMapping': 'passed', 'stillAndIncidentalTailExcluded': True,
            'gameOnlyFadeAndGain': 'passed', 'noBaseGainOrLimiter': True, 'peakCapOnlyNewStem': 'passed',
            'serializedFixtureComplementProof': exact}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episode')
    parser.add_argument('--assembly')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test()))
    else:
        assert args.episode and args.assembly, '--episode and --assembly are required'
        main(args.episode, args.assembly)
