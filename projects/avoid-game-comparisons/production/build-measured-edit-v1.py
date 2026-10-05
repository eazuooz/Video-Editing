"""Preserve every current PCM sample and native action in an integer-frame candidate.

This candidate deliberately retains source/caption/word-alignment review gates.
No synthesis, source acquisition, final render or publishing occurs here.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, json, math, sys
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
correct_flagged_edges = '--correct-flagged-edges' in sys.argv
correct_water_edge = '--correct-water-edge' in sys.argv or correct_flagged_edges
reallocate12 = '--reallocate12' in sys.argv or correct_water_edge
target = BASE / ('measured-edit-v4' if correct_flagged_edges else 'measured-edit-v3' if correct_water_edge else 'measured-edit-v2' if reallocate12 else 'measured-edit-v1')
assert not target.exists(), 'Preserve an existing measured candidate.'
measurement = read(BASE / 'measured-paragraphs-expanded15.json')
proposal_path = BASE / ('native-cue-proposal-v5.json' if correct_flagged_edges else 'native-cue-proposal-v4.json' if correct_water_edge else 'native-cue-proposal-v3.json')
proposal = read(proposal_path)
index = read(BASE / 'narration-expanded15-index.json')
assert index['fullCurrentHashAsrApproved'] and len(measurement['scenes']) == 15
groups = {(g['sceneId'], g['paragraph']): copy.deepcopy(g) for g in proposal['groups']}
if reallocate12:
    def native_piece(raw, a, z):
        c = copy.deepcopy(raw)
        assert raw['startFrame'] <= a < z <= raw['endFrameExclusive']
        c.update(startFrame=a, endFrameExclusive=z, inSeconds=a / c['nativeFps'],
                 outSeconds=z / c['nativeFps'], seconds=(z - a) / c['nativeFps'])
        return c
    blue = groups[('08', 2)]['sourceCuts'][0]
    assert blue['id'] == 'action-65' and blue['startFrame'] == 5400 and blue['endFrameExclusive'] == 6000
    groups[('08', 2)]['sourceCuts'] = [native_piece(blue, 5400, 5790)]
    fight, stairs, desk, rocket = groups[('12', 1)]['sourceCuts']
    assert desk['id'] == 'action-52' and desk['startFrame'] == 4380 and desk['endFrameExclusive'] == 4590
    # Move distinct, already reviewed active blue-surface combat from08's
    # post-observation surplus. Intro preview → fight → stairs → desk → rocket.
    # No source frame repeats and no added quota/idle clip is required.
    groups[('12', 1)]['sourceCuts'] = [native_piece(blue, 5790, 5856), native_piece(desk, 4380, 4494),
                                    fight, stairs, native_piece(desk, 4494, 4590), rocket,
                                    native_piece(blue, 5856, 6000)]
rate, fps, samples_per_frame = 24000, 60, 400
diagram_frames = {('06', 2): 120, ('06', 4): 187, ('10', 2): 388,
                  ('10', 4): 156, ('13', 3): 450, ('14', 0): 1021, ('15', 3): 168}
if correct_water_edge:
    # The removed wipe frame cannot truncate15p3 PCM: transfer its two output
    # frames into that paragraph's new white comparison. Rebalance only the
    # unapproved cost-diagram reading tail; all original explanations remain.
    diagram_frames[('15', 3)] += 2
all_source_cuts = [c for g in groups.values() for c in g['sourceCuts']]
actual_frames = sum(round(c['seconds'] * fps) for c in all_source_cuts)
assert actual_frames == (18833 if correct_flagged_edges else 18841 if correct_water_edge else 18843)
required_explanation = round(actual_frames * 2 / 3)
assert abs(actual_frames - .6 * (actual_frames + required_explanation)) <= 1
original_six = [s for s in measurement['scenes'] if s['classification'] == 'explanation']
assert [s['id'] for s in original_six] == ['01', '03', '05', '07', '09', '11']
original_explanation_frames = sum(s['minimumSpeechFrames'] for s in original_six)
diagram_frames[('12', 2)] = required_explanation - original_explanation_frames - sum(diagram_frames.values())
assert diagram_frames[('12', 2)] == (263 if correct_flagged_edges else 269 if correct_water_edge else 272)
quiet_reviews = []
scenes, cursor = [], 120

for s in measurement['scenes']:
    sid = s['id']
    assert sha(ROOT / s['audio']) == s['audioSha256'], f'Current audio changed: {sid}'
    x, sr = sf.read(ROOT / s['audio'], dtype='float32')
    assert sr == rate and len(x) == s['samples']
    segments, placement = [], []
    output = 0

    def pcm(a, z):
        global output
        assert 0 <= a <= z <= s['samples']
        if z > a:
            placement.append({'kind': 'preserved-current-PCM', 'fromSample': a, 'toSample': z,
                              'outputFromSample': output, 'outputToSample': output + z - a})
            output += z - a

    def silence(n, reason):
        global output
        assert n >= 0, f'{sid}: insufficient candidate slot by {-n / rate:.6f}s'
        if n:
            placement.append({'kind': 'inserted-silence', 'samples': n,
                              'outputFromSample': output, 'outputToSample': output + n, 'reason': reason})
            output += n

    def actual(p):
        for raw in groups[(sid, p)]['sourceCuts']:
            c = copy.deepcopy(raw)
            c['bankCutId'] = raw['id']
            c['id'] = f'{sid}-p{p}-{raw["id"]}-{raw["startFrame"]}-{raw["endFrameExclusive"]}'
            c['sourceStartFrame'] = raw['startFrame']
            c['sourceEndFrameExclusive'] = raw['endFrameExclusive']
            c['classification'] = 'actual-existing-game'
            c['frames'] = round(raw['seconds'] * fps)
            c['seconds'] = c['frames'] / fps
            c['nativeSeconds'] = raw['seconds']
            c['nativeToOutputQuantizationFrames'] = c['frames'] - raw['seconds'] * fps
            c['speed'] = 1
            c['sourceAudioStreams'] = 0
            c['finalApproved'] = False
            c['captionPixelsApproved'] = False
            c['mediaCompiled'] = False
            c['paragraph'] = p
            if raw['id'] == 'action-100':
                c['requiredContextLabel'] = '접근기능 시연 · 무적/한방처치 ON'
            elif raw['sourceVideoId'] == 'JdNZo7E_hXU':
                c['requiredContextLabel'] = '공식 접근기능 시연의 발췌'
            segments.append(c)

    def diagram(p, n):
        segments.append({'id': f'{sid}-{p}-white-comparison', 'classification': 'explanation',
                         'diagramId': f'{sid}-{p}', 'paragraph': p, 'frames': n, 'seconds': n / fps,
                         'layoutLookdevEvidence': 'projects/avoid-game-comparisons/production/new-diagram-lookdev-review.json',
                         'lookdevLayoutReviewed': True, 'finalApproved': False,
                         'captionPixelsApproved': False})

    def block(paragraphs, add_segments):
        before_frames = sum(c['frames'] for c in segments)
        start = output
        add_segments()
        a = s['paragraphs'][paragraphs[0] - 1]['pcmFromSample']
        z = s['paragraphs'][paragraphs[-1] - 1]['pcmToSample']
        pcm(a, z)
        desired = start + (sum(c['frames'] for c in segments) - before_frames) * samples_per_frame
        silence(desired - output, 'Read the comparison or observe the named active native action at normal speed; no source loop, slowdown or idle extension.')

    if s['classification'] == 'explanation':
        segments.append({'id': f'{sid}-original-white-explanation', 'classification': 'explanation',
                         'diagramId': sid, 'frames': s['minimumSpeechFrames'], 'seconds': s['minimumSpeechFrames'] / fps,
                         'originalPcmAndExplanationPreserved': True, 'captionPixelsApproved': False, 'finalApproved': False})
        pcm(0, s['samples'])
        silence(s['minimumSpeechFrames'] * samples_per_frame - output, 'At most one frame of scene-end PCM quantization; original explanation untouched.')
    elif sid == '02':
        block([1], lambda: actual(1))
        block([2], lambda: actual(2))
        block([3, 4], lambda: (actual(3), actual(4)))
    elif sid == '04':
        block([1, 2], lambda: (actual(1), actual(2)))
        for p in [3, 4, 5]:
            block([p], lambda p=p: actual(p))
    elif sid == '14':
        actual(1)
        diagram(0, diagram_frames[(sid, 0)])
        pcm(0, s['samples'])
        silence(sum(c['frames'] for c in segments) * samples_per_frame - output,
                'Complete the observed-result/undecided-condition diagram; continuous14 PCM is not split at the chest/card visual boundary.')
    else:
        for p in range(1, len(s['paragraphs']) + 1):
            if reallocate12 and sid == '12' and p == 1:
                a, z = s['paragraphs'][0]['pcmFromSample'], s['paragraphs'][0]['pcmToSample']
                candidates = []
                for k in range(round(3.15 * rate), round(3.28 * rate), 24):
                    q = x[k - 192:k + 192]
                    rms = float(np.sqrt(np.mean(q * q)))
                    candidates.append((rms, k, float(np.max(np.abs(q)))))
                rms, boundary, peak = min(candidates)
                assert rms < .001 and 3.1 < boundary / rate < 3.28
                quiet_reviews.append({'scene': sid, 'paragraph': p, 'sample': boundary,
                                      'seconds': boundary / rate, 'rms16ms': rms, 'peak16ms': peak,
                                      'previousAsrWordEnd': 3.1, 'nextAsrWordStart': 3.28,
                                      'insertedSeconds': .46,
                                      'purpose': 'Finish the general opening before the preserved fight/stair/desk/rocket phrase; the staircase word now begins at5.00s.',
                                      'newJoinAsrApproved': False})
                before = output
                before_frames = sum(c['frames'] for c in segments)
                actual(p)
                pcm(a, boundary)
                silence(round(.46 * rate), 'A short existing quiet sentence break aligns the next specific action verbs with their visible excerpts.')
                pcm(boundary, z)
                nframes = sum(c['frames'] for c in segments) - before_frames
                silence(before + nframes * samples_per_frame - output,
                        'Observe the named rocket ascent and the distinct blue printed-surface combat; both are active native excerpts, without a loop or slowdown.')
                continue
            if sid == '12' and p == 4:
                # Native59.94→60 quantization makes p4 alone0.007667s shorter
                # than its PCM. Preserve p4/p5 continuously across the adjacent
                # named mine movement rather than cutting a syllable.
                block([4, 5], lambda: (actual(4), actual(5)))
                continue
            if sid == '12' and p == 5:
                continue
            if sid == '12' and p == 2:
                a, z = s['paragraphs'][1]['pcmFromSample'], s['paragraphs'][1]['pcmToSample']
                candidates = []
                for k in range(round(15.76 * rate), round(16.00 * rate), 24):
                    q = x[k - 192:k + 192]
                    rms = float(np.sqrt(np.mean(q * q)))
                    candidates.append((rms + abs(k / rate - 15.86) * .0001, k, rms, float(np.max(np.abs(q)))))
                _, boundary, rms, peak = min(candidates)
                assert rms < .001 and 15.68 < boundary / rate < 16.12
                quiet_reviews.append({'scene': sid, 'paragraph': p, 'sample': boundary,
                                      'seconds': boundary / rate, 'rms16ms': rms, 'peak16ms': peak,
                                      'previousAsrWordEnd': 15.68, 'nextAsrWordStart': 16.12,
                                      'purpose': 'Separate observed entry/firing from the unconfirmed cost/win-condition statement.',
                                      'newJoinAsrApproved': False})
                before = output
                before_frames = sum(c['frames'] for c in segments)
                actual(p)
                pcm(a, boundary)
                source_frames = sum(c['frames'] for c in segments) - before_frames
                silence(before + source_frames * samples_per_frame - output,
                        'Observe the already named distinct firing actions before the white unconfirmed-cost comparison; native footage plays once at normal speed.')
                white_start = output
                diagram(p, diagram_frames[(sid, p)])
                pcm(boundary, z)
                silence(white_start + diagram_frames[(sid, p)] * samples_per_frame - output,
                        'Allow the cost/win-condition comparison to be read at its actual4.533333-second duration.')
            else:
                def add(p=p):
                    if (sid, p) in groups:
                        actual(p)
                    if (sid, p) in diagram_frames:
                        diagram(p, diagram_frames[(sid, p)])
                block([p], add)

    frames = sum(c['frames'] for c in segments)
    assert output == frames * samples_per_frame
    kept = [p for p in placement if p['kind'] == 'preserved-current-PCM']
    assert kept[0]['fromSample'] == 0 and kept[-1]['toSample'] == s['samples']
    assert all(a['toSample'] == b['fromSample'] for a, b in zip(kept, kept[1:]))
    assert sum(p['toSample'] - p['fromSample'] for p in kept) == s['samples']
    local = 0
    for c in segments:
        c['localFromFrame'] = local
        c['startFrame'] = cursor + local
        local += c['frames']
        c['endFrameExclusive'] = cursor + local
    scenes.append({**{k: s[k] for k in ['id', 'title', 'audio', 'audioSha256', 'samples', 'sampleRate']},
                   'startFrame': cursor, 'frames': frames, 'seconds': frames / fps,
                   'segments': segments, 'pcmPlacement': placement, 'speechEvidence': s['paragraphs'],
                   'asrEvidence': s['asrEvidence'], 'allCurrentPcmPreserved': True,
                   'wordToActionAlignmentApproved': False, 'finalFixedCaptionApproval': False})
    cursor += frames

cuts = [c for s in scenes for c in s['segments'] if c['classification'] == 'actual-existing-game']
for source in {c['sourceVideoId'] for c in cuts}:
    intervals = sorted([c for c in cuts if c['sourceVideoId'] == source], key=lambda c: c['sourceStartFrame'])
    assert all(a['sourceEndFrameExclusive'] <= b['sourceStartFrame'] for a, b in zip(intervals, intervals[1:])), f'Repeated native samples: {source}'
assert len(cuts) == (108 if reallocate12 else 105)
explanation_frames = sum(c['frames'] for s in scenes for c in s['segments'] if c['classification'] == 'explanation')
assert explanation_frames == required_explanation
result = {
    'schemaVersion': 1, 'createdAt': datetime.now(timezone.utc).isoformat(),
    'status': 'integer-frame-current15-candidate-native-compilation-and-all-word-caption-pixels-pending',
    'fps': fps, 'width': 1920, 'height': 1080, 'brandingFrames': 120, 'membershipFrames': 600,
    'scenes': scenes, 'actualFrames': actual_frames, 'explanationFrames': explanation_frames,
    'bodyFrames': actual_frames + explanation_frames, 'finalFrames': cursor + 600,
    'body60_40ErrorFrames': actual_frames - .6 * (actual_frames + explanation_frames),
    'actualSourceCuts': len(cuts), 'allSourceIntervalsUnique': True, 'all60ParagraphsRetained': True,
    'allCurrent15PcmPreserved': True, 'originalSixExplanationMinimumFrames': original_explanation_frames,
    'wholeOverviewPreservedSeconds': 23.44, 'sourceAudioStreams': 0, 'agentCreatedGames': 0,
    'sourceLoopsOrSlowdown': 0, 'quietInternalBoundaryReviews': quiet_reviews,
    'inputHashes': {'measurement': sha(BASE / 'measured-paragraphs-expanded15.json'),
                    'currentVoiceIndex': sha(BASE / 'narration-expanded15-index.json'),
                    'nativeProposal': sha(proposal_path)},
    'nativeEdgeCorrection': ({'action': 'action-98', 'source': 'KWDk-csu460',
        'startFrame': 1530, 'endFrameExclusive': 1574, 'lastCleanFrame': 1573,
        'firstWipeFrame': 1574, 'oldEndFrameExclusive': 1575,
        'actualFramesRemoved': 2, 'explanationRoundingFramesRemoved': 1,
        'originalSixExplanationAndAllPcmUntouched': True,
        'evidence': 'projects/avoid-game-comparisons/production/native-framing-pilot-direct-review.json'} if correct_water_edge else None),
    'sourceReallocation': ({
        '08p2': 'Keep native5400–5790 (6.5s) for the6.09s blue-surface jump/attack paragraph.',
        '12p1': 'Move unused observation tail5790–6000 once:5790–5856 as a1.1s opening preview,5856–6000 as2.4s active closing combat. Split desk4380–4590 into1.9s preview and1.6s later walk. Preserve complete fight/stair/rocket excerpts.',
        'newActualSeconds': 0, 'nativeFrameRepeats': 0,
        'wordAlignment': 'With a0.46s quiet sentence pause, fight4.52–5.00 fits source3.00–5.00; stairs5.00–5.82 fits5.00–6.50; the desk bridge starts5.82 and walking6.88–7.96 fits6.50–8.10; rocket7.96–9.50 bridges into8.10–13.10.',
        'rejectedExtraSource': 'Mine2578–2788 was directly inspected and rejected as mostly stationary framing/book turn; do not count it as added active quota.'
    } if reallocate12 else None),
    'wordAlignmentReviewNotes': [
        '02p3/p4 and04p1/p2 retain continuous PCM across related adjacent visual transitions rather than truncating final syllables to rounded source boundaries.',
        '14 whole PCM crosses the actual/white transition without a splice; native chest/card and the narrated result require direct final cue inspection.',
        '12p4/p5 PCM remains continuous across adjacent native mine cuts, including the0.007667s quantization shortfall of p4 alone; no syllable is discarded.',
        ('12p1 reallocated native intervals and the0.46s quiet break align the specific verbs; final source/caption pixels and the new mix join still require direct review.' if reallocate12 else '12p1 generic opening then fight/stairs/desk/rocket verbs still need precise word/action alignment. Candidate source order is not an approved final order.'),
        'Every short cue diagram must be inspected at final duration with its actual fixed-caption pixels, beyond the silent layout review.',
        'Native59.94fps intervals are resampled to60fps without speed changes; inspect actual compiled frame counts and boundaries before final ratio approval.'
    ],
    'finalTimingApproved': False, 'bodyRatioApproved': False, 'allCaptionPixelsReviewed': False,
    'finalMixBuilt': False, 'finalMixAsrApproved': False, 'renderComplete': False,
    'humanWholeListening': 'pending', 'humanPronunciationApproval': 'pending', 'finalPublicRights': 'pending',
}
if correct_flagged_edges:
    result['flaggedNativeCorrections'] = {
        'evidence': 'projects/avoid-game-comparisons/production/flagged-native-context-direct-review.json',
        'action83': {'endExclusive': 1270, 'removedNativeFrames': 6, 'reason': 'Exclude different-map editorial dissolve.'},
        'action73': {'endExclusive': 785, 'removedNativeFrames': 1, 'reason': 'Exclude first source dialogue frame.'},
        '15p3': 'Water/lava/enemy order matches the retained narration; every current PCM sample remains.',
        '12p1': 'Rocket ascent remains pending: the retained action71 begins with desk combat. Candidate timing is not final approval.',
        'ratioRebalance': 'Only the unapproved12p2 diagram reading tail is six frames shorter than v3. All original explanations and every PCM sample remain.'}
    result['sourceReallocation']['wordAlignment'] = 'Fight/stair/desk alignment is proposed. Raw-context review rejects the rocket-ascent alignment; fix12p1 before final approval.'
target.mkdir()
(target / 'plan.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: result[k] for k in ['actualFrames', 'explanationFrames', 'bodyFrames', 'finalFrames', 'body60_40ErrorFrames', 'actualSourceCuts', 'finalTimingApproved']}))
