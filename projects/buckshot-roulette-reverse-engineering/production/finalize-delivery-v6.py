"""Finalize the selected v6 local review, never produce missing QA.

Default/--check only validates and proposes metadata in memory. --apply requires
the current 26518-frame masters, concrete preservation proofs, hash-bound visual
inspection, and a NEW whole-mix audio review. The v5 text/paragraph semantic
review is reused only after every SRT cue is proved identical except for +30 s.
No media rendering, ASR, human approval, upload or next-video action occurs here.

Final visual receipt: production/local/final-qa-v6/visual-review.json with
status=passed-inspected-encoded-frames, current masterSha256, introClipIds,
inspectedFrameIndices/Count, blockingFindings=[], introPlanSha256,
preservationProofSha256 and optional bound evidenceFiles. Both each intro cut
and the introduction/body join require an inspected final encoded frame.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import assemble_documentary as asm

# These helpers are read-only. Never call the v5 validator, updater or apply.
_spec = importlib.util.spec_from_file_location('_v5_delivery_read_helpers',
                                             Path(__file__).with_name('finalize-delivery-v5.py'))
_v5 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v5)
need, read, sha = _v5.need, _v5.read, _v5.sha
resolve, bound = _v5.resolve, _v5.bound
check_binding, check_nested_bindings = _v5.check_binding, _v5.check_nested_bindings
json_bytes, stable_hash, frame_values = _v5.json_bytes, _v5.stable_hash, _v5.frame_values
ROOT, P, SLUG = asm.REPO, asm.PROJECT, asm.PROJECT.name
WORK = P / 'production/local/documentary-v6'
QA = P / 'production/local/final-qa-v6'
OUT = ROOT / f'output/{SLUG}-v6'
BASE_OUT = ROOT / f'output/{SLUG}-v5'
CONTROL = ROOT / 'shared/publishing/video-production-control.json'
WORKLIST = ROOT / 'shared/publishing/video-worklist.json'
DOC = ROOT / 'docs/VIDEO_WORKLIST.md'
BEGIN, END = _v5.BEGIN, _v5.END
MASTER_V5 = '237bbc43bfee67b0f8d5d74e20fac568a51b08b822e3337ec152603afd374450'
NARRATION = '6eb0f483642fc4a99b102abb54ea710fc0f8cb21d7a2b8c78f824b769d8e9835'
FRAMES, BASE_FRAMES, INTRO_FRAMES, BRAND_FRAMES = 26518, 24718, 1800, 120
BODY_FRAMES, OFFSET = 23998, 30


def checked_json(path):
    """Register the receipt itself as well as the files it names."""
    bound(path)
    return read(path)


def frame_proof(binding, expected_source, expected_frames):
    path = check_binding(binding)
    cache = checked_json(path.with_name(path.name + '.json'))
    need(cache['input']['file'] == expected_source and cache['input']['frames'] == expected_frames and
         cache['sha256'] == binding['sha256'], 'Decoded frame proof is bound to a different source')
    values = frame_values(path)
    need(len(values) == expected_frames, 'Decoded frame proof length differs')
    return values


def scope():
    control, manifest = read(CONTROL), read(P / 'project.json')
    auth = control.get('scopedSetupAuthorizations', {}).get(SLUG, {})
    need(auth.get('revision') == 'v6' and auth.get('productionAllowedNow') is True,
         'Selected v6 production authorization missing')
    need(manifest.get('revision', {}).get('id') == 'v6' and
         manifest.get('startGate', {}).get('productionAllowedNow') is True,
         'Project is not the authorized v6 revision')


def caption_alignment(at):
    baseline_path = P / 'production/caption-alignment-v5.json'
    baseline = checked_json(baseline_path)
    need(baseline.get('status') == 'approved-semantic-paragraph-alignment' and
         baseline.get('approved') is True and baseline.get('manualSemanticReview') is True and
         baseline.get('allParagraphTextsRetained') is True and baseline.get('paragraphCount') == 19 and
         len(baseline.get('paragraphs', [])) == 19 and baseline.get('sourceAudioSha256') == NARRATION,
         'Complete existing 19-paragraph semantic review is required')
    tracks = {row['language']: row for row in baseline['captions']}
    need(set(tracks) == {'ko', 'en'}, 'Both reviewed caption languages are required')
    result = copy.deepcopy(baseline)
    for lang, count in [('ko', 115), ('en', 135)]:
        old, new = BASE_OUT / f'{SLUG}.{lang}.srt', OUT / f'{SLUG}.{lang}.srt'
        need(resolve(tracks[lang]['path']) == old and sha(old) == tracks[lang]['sha256'],
             'Reviewed baseline SRT changed')
        old_cues, new_cues = asm.read_srt(old), asm.read_srt(new)
        need(len(old_cues) == len(new_cues) == count == tracks[lang]['cues'], 'SRT cue count changed')
        for a, b in zip(old_cues, new_cues):
            need(a['id'] == b['id'] and a['text'] == b['text'] and
                 all(abs(b[t] - a[t] - OFFSET) <= .0005 for t in ['start', 'end']),
                 'V6 must preserve every subtitle text and shift every boundary by exactly 30 seconds')
        covered = []
        for old_paragraph, paragraph in zip(baseline['paragraphs'], result['paragraphs']):
            need(old_paragraph.get('semanticMeaningReviewed') is True and old_paragraph.get('allTextRetained') is True,
                 'Baseline paragraph semantic review is incomplete')
            indices = old_paragraph[lang + 'Cues']
            need(indices and all(type(i) is int and 1 <= i <= count for i in indices), 'Invalid paragraph cue map')
            text = ' '.join(new_cues[i - 1]['text'] for i in indices)
            need(' '.join(text.split()) == ' '.join(old_paragraph[lang + 'Text'].split()),
                 'Paragraph text differs from its reviewed mapping')
            start, end = old_paragraph['start'] + OFFSET, old_paragraph['end'] + OFFSET
            need(abs(new_cues[indices[0] - 1]['start'] - start) <= .002 and
                 abs(new_cues[indices[-1] - 1]['end'] - end) <= .002, 'Paragraph alignment changed')
            paragraph.update(start=start, end=end)
            covered.extend(indices)
        need(covered == list(range(1, count + 1)), 'Paragraph map skips or repeats subtitles')
        next(r for r in result['captions'] if r['language'] == lang).update(
            path=new.relative_to(ROOT).as_posix(), sha256=sha(new))
    result.update(revision='v6', reusedAt=at, brandingOffsetSeconds=2,
        bodyOffsetSeconds=32, introductionSeconds=30, existingCueOffsetDeltaSeconds=30,
        reviewScope='V5 complete KO/EN text and paragraph meaning review reused after exact cue text equality and +30-second timing verification. Current v6 audio is a NEW mix with its own QA; no new manual semantic or human review is claimed.',
        newManualSemanticReviewPerformed=False, manualSemanticReviewReused=True,
        sourceAlignment=bound(baseline_path), preservationProof=bound(WORK / 'preservation-proof.json'),
        currentAudioReview=bound(QA / 'audio-review.json'),
        humanListening=False, humanViewing=False, userApproval=False)
    # A v5 pointer proving identical old audio cannot describe the v6 mix.
    result.pop('audioPreservation', None)
    return result


def audio_review(master, technical):
    audio = checked_json(QA / 'audio-review.json')
    need(audio.get('revision') == 'v6' and audio.get('masterSha256') == master and
         resolve(audio['masterPath']) == OUT / f'{SLUG}.captioned.mp4' and
         audio.get('technicalPassed') is True and audio.get('wholeMixAsrCompared') is True and
         audio.get('newAsrPerformed') is True and audio.get('pairedDecodedAudioIdentical') is True,
         'Actual current-v6 full-mix audio review is required; identical-v5-audio reuse is invalid')
    need(audio['preservation']['sourceNarrationSha256'] == NARRATION and
         audio['preservation'].get('baseConcatAllSamplesExact') is True and
         audio['preservation'].get('bodyStartSeconds') == 32 and
         audio['continuity'].get('continuityParagraphs') == 19 and
         audio['continuity'].get('technicalMeasurementPassed') is True,
         'Original 19-paragraph voice/base-mix placement proof is missing')
    loudness = audio['loudness']
    need(loudness.get('passed') is True and loudness['truePeakDbtp'] <= -1.5 and
         loudness['truePeakDbtp'] == technical['encodedTruePeakDbtp'], 'Current mix loudness proof differs')
    need(sha(resolve(loudness['log'])) == loudness['logSha256'], 'Loudness log changed')
    decoded = resolve(audio['decodedAudioFile'])
    need(sha(decoded) == audio['decodedAudioSha256'], 'Decoded final mix changed')
    receipt = checked_json(resolve(audio['decodeReceipt']))
    need(receipt.get('actualAACDecoded') is True and receipt['masterSha256'] == master and
         receipt['decodedAudioSha256'] == audio['decodedAudioSha256'], 'AAC decode receipt is stale')
    direct = checked_json(QA / 'mix-asr-direct-review.json')
    aggregate = checked_json(QA / 'mix-segment-asr.json')
    need(direct == audio['wholeTextReview'] and direct.get('wholeMixAsrCompared') is True and
         direct.get('sentenceOmissionsFound') is False and direct.get('sentenceRepetitionsFound') is False,
         'Direct whole-mix transcript comparison did not pass')
    need(direct['masterSha256'] == aggregate['masterSha256'] == master and
         direct['decodedAudioSha256'] == aggregate['audio_sha256'] == audio['decodedAudioSha256'] and
         aggregate.get('fullDecodedRangeAccountedFor') is True and aggregate.get('sourceOffsetSeconds') == 32 and
         aggregate.get('narrationParagraphCount') == 19, 'ASR belongs to another mix/range')
    measurement = checked_json(QA / 'audio-technical-measurements.json')
    need(measurement == audio['continuity'], 'Audio measurement receipt changed')
    regression = checked_json(QA / 'audio-concat-v6-regression.json')
    need(regression.get('passed') is True and regression.get('allDecodedSamplesExactlyEqual') is True and
         regression.get('noExtraFrames') is True and regression['maximumAbsoluteError'] == 0 and
         sha(resolve(regression['target'])) == regression['targetSha256'], 'Base audio concat proof invalid')
    check_nested_bindings(audio)
    return audio


def validate():
    scope()
    at = datetime.now(timezone.utc).isoformat()
    q = checked_json(WORK / 'technical-qa.json')
    preservation = checked_json(WORK / 'preservation-proof.json')
    preflight = checked_json(WORK / 'preflight.json')
    progress = checked_json(WORK / 'render-progress.json')
    snapshot = preflight['snapshot']
    fingerprint = stable_hash(snapshot)
    need(fingerprint == preflight['snapshotSha256'] == preservation['snapshotSha256'] == progress['snapshotSha256'],
         'Preparation/render/preservation snapshot hashes differ')
    need(preflight.get('editReady') is True and not preflight.get('readiness') and progress.get('complete') is True,
         'V6 rendering has not finished')
    need(all(q.get(k) is True for k in ['technicalDecodePassed', 'pairedAudioIdentical',
         'audioLoudnessPassed', 'preservationVerificationPassed']), 'V6 technical checks have not passed')
    need(preservation.get('revision') == 'v6' and preservation.get('technicalPassed') is True and
         preservation.get('totalFrames') == FRAMES and preservation.get('newTts') is False and
         preservation.get('newAudioMix') is True, 'Expected a new mix, original voice and exact v6 duration')
    need(preservation.get('audioSamples') == FRAMES * 800 and
         preservation.get('sourceVoiceSha256') == NARRATION and
         preservation.get('retainedBodyPreMusicFloatPcmIdentical') is True and
         preservation.get('pairedAudioPacketsAndPcmIdentical') is True,
         'Original voice/body PCM and current clean/captioned pair equality are unverified')
    check_nested_bindings(snapshot)
    check_nested_bindings(preservation)
    need(preservation['baselineMasters'] == snapshot['baselineMasters'] and
         snapshot['baselineMasters']['captioned']['sha256'] == MASTER_V5, 'Unexpected v5 baseline')
    need(sha(P / 'production/local/audio-v4/narration.wav') == NARRATION,
         'Approved original narration PCM changed')
    outputs = {}
    for kind in ['clean', 'captioned']:
        path = OUT / f'{SLUG}.{kind}.mp4'
        item = q['outputs'][kind]
        need(resolve(item['file']) == path and sha(path) == item['sha256'], 'Final output binding differs')
        outputs[kind] = bound(path)
        need(outputs[kind] == preservation['currentMasters'][kind] == progress['outputs'][kind],
             'Output/progress/preservation hashes differ')
        video = next(s for s in item['probe']['streams'] if s['codec_type'] == 'video')
        audios = [s for s in item['probe']['streams'] if s['codec_type'] == 'audio']
        need((video['width'], video['height'], Fraction(video['avg_frame_rate']), int(video['nb_read_frames'])) ==
             (1920, 1080, 60, FRAMES), 'Encoded dimensions/rate/decoded frame count differ')
        need(len(audios) == 1 and audios[0]['codec_name'] == 'aac' and
             str(audios[0]['sample_rate']) == '48000' and audios[0]['channels'] == 2,
             'Expected exactly one 48 kHz stereo AAC stream')
        for duration in [video['duration'], audios[0]['duration'], item['probe']['format']['duration']]:
            need(abs(float(duration) - FRAMES / 60) <= 1024 / 48000, 'Final stream duration differs')
    need(q['encodedTruePeakDbtp'] <= -1.5, 'Encoded true peak exceeds -1.5 dBTP')
    need(set(preservation['audioPackets']) == set(preservation['decodedAudioHashes']) == {'aac', 'clean', 'captioned'},
         'Current encoded pair audio inventory differs')
    for label, value in preservation['audioPackets'].items():
        packet = checked_json(check_binding(value['proof']))
        expected_path = WORK / 'approved-pair-audio.m4a' if label == 'aac' else OUT / f'{SLUG}.{label}.mp4'
        need(check_binding(packet['file']) == expected_path and len(packet['packets']) == packet['packetCount'] and
             stable_hash(packet['packets']) == packet['packetSequenceSha256'] == value['packetSequenceSha256'],
             'Current AAC packet proof is stale or does not match its output')
        pcm_path = WORK / 'proof' / f'{label}.audio-f32.sha256'
        bound(pcm_path)
        need(pcm_path.read_text(encoding='utf-8').strip() == preservation['decodedAudioHashes'][label],
             'Decoded audio hash record changed')
    need(len({v['packetSequenceSha256'] for v in preservation['audioPackets'].values()}) == 1 and
         len(set(preservation['decodedAudioHashes'].values())) == 1, 'Current clean/captioned audio differs')
    for label in ['retained-body', 'v4-body-reference']:
        path = WORK / 'proof' / f'{label}.audio-f32.sha256'
        bound(path)
        need(path.read_text(encoding='utf-8').strip() == preservation['retainedBodyPcmSha256'],
             'Retained pre-music body PCM proof differs')
    plan = checked_json(P / 'planning/intro-gameplay-v6.json')
    music = checked_json(P / 'planning/audio-v6-plan.json')
    need(plan['insertion']['introTotalFrames'] == INTRO_FRAMES and len(plan['clips']) == 6 and
         sum(c['outputFrames'] for c in plan['clips']) == INTRO_FRAMES, 'Expected six 30-second intro clips')
    wanted = [c['id'] for c in plan['clips']]
    need(len(set(wanted)) == 6, 'Intro identifiers are not unique')
    cursor = 0
    for clip in plan['clips']:
        need(clip['outputStartFrame'] == cursor and clip['speed'] == 2 and
             clip['outputFrames'] == clip['sourceDurationSeconds'] * 60 / 2 and
             sha(resolve(clip['sourcePath'])) == clip['sourceSha256'] and
             clip['sourceDecodedDimensions'] == [1920, 1080] and
             clip['sourceClassification'] == 'independent-gameplay', 'Intro source/timing changed')
        cursor += clip['outputFrames']
    need(sha(resolve(music['music']['absolutePath'])) == music['music']['sha256'], 'Selected music changed')
    # Actual body-pixel equality, not merely a "preserved" boolean.
    frames = checked_json(check_binding(preservation['cleanFramePreservation']))
    before = frame_proof(frames['baselineProof'], snapshot['baselineMasters']['clean'], BASE_FRAMES)
    actual = frame_proof(frames['currentProof'], outputs['clean'], FRAMES)
    cuts = progress['cuts']
    need(len(cuts) == 40 and len(frames['introProofs']) == 6 and
         progress.get('retainedV5VideoCuts') == 34 and progress.get('newIntroVideoCuts') == 6,
         'Actual render cut inventory differs')
    intro = []
    for record, cut, clip in zip(frames['introProofs'], cuts[1:7], plan['clips']):
        need(cut['id'] == 'intro-' + clip['id'] and cut['frames'] == clip['outputFrames'] and
             cut['finalStartFrame'] == BRAND_FRAMES + clip['outputStartFrame'], 'Rendered intro placement differs')
        source = {'path': str(resolve(cut['path'])), 'sha256': cut['sha256']}
        check_binding(source)
        intro.extend(frame_proof(record, source, clip['outputFrames']))
    need(len(before) == BASE_FRAMES and len(actual) == FRAMES and len(intro) == INTRO_FRAMES and
         actual == before[:BRAND_FRAMES] + intro + before[BRAND_FRAMES:],
         'Decoded clean frames do not equal v5 branding + intro + complete unchanged v5 remainder')
    need(frames.get('mismatchCount') == 0 and frames.get('retainedBodyCleanPixelsIdentical') is True and
         frames.get('continuousDecodedCfrPts') is True,
         'Clean preservation proof did not pass')
    current_frame_path = resolve(frames['currentProof']['path'])
    pts_rows = [[int(part.strip()) for part in line.split(',')[1:4]]
                for line in current_frame_path.read_text(encoding='utf-8').splitlines()
                if line.strip() and not line.startswith('#')]
    need(all(pts == i and duration == 1 for i, (_, pts, duration) in enumerate(pts_rows)),
         'Actual decoded v6 frame timestamps are not continuous CFR')
    visual = checked_json(QA / 'visual-review.json')
    master = outputs['captioned']['sha256']
    need(visual.get('status') == 'passed-inspected-encoded-frames' and visual.get('masterSha256') == master and
         visual.get('blockingFindings') == [] and visual.get('introPlanSha256') == sha(P / 'planning/intro-gameplay-v6.json') and
         visual.get('preservationProofSha256') == sha(WORK / 'preservation-proof.json'), 'Current encoded visual review missing/stale')
    need(set(visual.get('introClipIds', [])) == set(wanted) and len(visual['introClipIds']) == 6,
         'Visual review must account for all six introductory cuts')
    inspected = visual.get('inspectedFrameIndices', [])
    need(inspected and len(set(inspected)) == len(inspected) == visual.get('inspectedFrameCount') and
         all(type(i) is int and 0 <= i < FRAMES for i in inspected), 'Invalid inspected frame inventory')
    for clip in plan['clips']:
        start = BRAND_FRAMES + clip['outputStartFrame']
        need(any(start <= n < start + clip['outputFrames'] for n in inspected), 'An intro cut lacks encoded inspection')
    need(any(1920 <= n < 2040 for n in inspected), 'Intro/body join lacks encoded inspection')
    for evidence in visual.get('evidenceFiles', []):
        check_binding(evidence)
    audio = audio_review(master, q)
    scripts = checked_json(P / 'production/local/audio-v4/render-inputs.json')['sha256']
    for language in ['ko', 'en']:
        need(sha(P / f'script/revision-v4/narration.{language}.json') == scripts[language + 'Script'], 'Approved script changed')
    alignment = caption_alignment(at)
    timeline = checked_json(WORK / 'timeline.json')
    baseline_timeline = checked_json(P / 'production/timeline-v5.json')
    need(timeline.get('revision') == 'v6' and timeline.get('bodyFrameCount') == BODY_FRAMES + INTRO_FRAMES and
         resolve(timeline['outputDirectory']) == OUT, 'Current timeline is not the retained-body v6')
    need([(b['id'], b['frames']) for b in timeline['beats'][:6]] ==
         [('intro-' + c['id'], c['outputFrames']) for c in plan['clips']] and
         [(b['id'], b['frames']) for b in timeline['beats'][6:]] ==
         [(b['id'], b['frames']) for b in baseline_timeline['beats']], 'Body beat order/length changed')
    evidence = {key[0]: value for key, value in _v5.HASH_CACHE.items()}
    return dict(at=at, technical=q, preservation=preservation, outputs=outputs, master=master,
                visual=visual, audio=audio, alignment=alignment, timeline=timeline,
                introIds=wanted, evidenceToRecheck=evidence)


def build_updates(state):
    """Prepare all scoped mutations; no files are changed by this function."""
    scope()
    now, master = state['at'], state['master']
    targets = [P / 'project.json', P / 'production/checkpoint.json', CONTROL, WORKLIST, DOC]
    before = {path: sha(path) for path in targets}
    manifest, cp, control, work = [read(path) for path in targets[:4]]
    selected = [r for r in work['rows'] if r.get('id') == 'S-BUCKSHOT-RE' and r.get('slug') == SLUG]
    need(len(selected) == 1, 'Exactly one existing selected worklist entry is required')
    row = selected[0]
    doc = DOC.read_text(encoding='utf-8-sig')
    need(doc.count(BEGIN) == doc.count(END) == 1 and doc.index(BEGIN) < doc.index(END), 'Scoped document markers invalid')
    updates = {}
    def propose(path, value, raw=False):
        updates[path] = value if raw else json_bytes(value)
    def future(path):
        return {'path': path.relative_to(P).as_posix(), 'sha256': hashlib.sha256(updates[path]).hexdigest()}
    timeline_path, alignment_path = P / 'production/timeline-v6.json', P / 'production/caption-alignment-v6.json'
    propose(timeline_path, (WORK / 'timeline.json').read_bytes(), raw=True)
    propose(alignment_path, state['alignment'])
    evidence = {'technical': bound(WORK / 'technical-qa.json', True),
        'preservation': bound(WORK / 'preservation-proof.json', True),
        'visual': bound(QA / 'visual-review.json', True), 'audio': bound(QA / 'audio-review.json', True),
        'wholeMixComparison': bound(QA / 'mix-asr-direct-review.json', True),
        'introPlan': bound(P / 'planning/intro-gameplay-v6.json', True),
        'audioPlan': bound(P / 'planning/audio-v6-plan.json', True),
        'captions': future(alignment_path), 'timeline': future(timeline_path)}
    stem = f'output/{SLUG}-v6/{SLUG}'
    paths = {'videoBurnedCaptions': stem + '.captioned.mp4', 'videoClean': stem + '.clean.mp4',
        'captionsKo': stem + '.ko.srt', 'captionsEn': stem + '.en.srt',
        'captionAlignmentReview': f'projects/{SLUG}/production/caption-alignment-v6.json',
        'timeline': f'projects/{SLUG}/production/timeline-v6.json',
        'script': f'projects/{SLUG}/script/revision-v4/narration.ko.json',
        'scriptEn': f'projects/{SLUG}/script/revision-v4/narration.en.json'}
    need(all((ROOT / p).is_file() or ROOT / p in updates for p in paths.values()), 'A required delivery output is missing')
    pending = ['User final viewing of the 30-second actual-gameplay opening and retained body',
               'Contextual pronunciation, original effects/music balance and whole-version human listening',
               'No upload, publication, scheduling, deletion or automatic next video is implied']
    limits = ['The introduction is six edited original-gameplay intervals at explicitly requested 2x, not one continuous take.',
              'The complete v5 body and branding/membership pictures are retained at their original speed; body starts 30 seconds later.',
              'Original narration PCM and all 19 paragraphs are preserved. Final mixed audio is new and is not identical to v5.',
              'Current encoded AAC has its own whole-mix ASR comparison and technical measurements. These do not constitute human listening.',
              'KO/EN text and paragraph mapping retain the previous semantic review; every cue is shifted exactly 30 seconds.',
              'Unity is the explanation renderer; the independently authored prototype remains Godot. Optional Ghidra/Tripo routes are not claimed as executed.',
              'Actual documented encoded-frame inspection is limited to its evidence inventory; human full-version approval remains pending.']
    mode = 'new-v6-mix-current-encoded-audio-review'
    final = {'schemaVersion': 1, 'checkedAt': now, 'revision': 'v6',
        'status': 'local-review-ready-user-review-pending', 'captionedSha256': master,
        'outputs': state['outputs'], 'durationSeconds': FRAMES / 60, 'totalFrames': FRAMES,
        'width': 1920, 'height': 1080, 'fps': 60, 'introFrames': INTRO_FRAMES,
        'introSeconds': 30, 'introSpeed': 2, 'introClipIds': state['introIds'],
        'bodyFrameCount': BODY_FRAMES, 'bodyOffsetDeltaSeconds': 30, 'bodyPicturesPreserved': True,
        'originalNarrationPcmPreserved': True, 'narrationParagraphCount': 19,
        'newTts': False, 'newAudioMix': True, 'decodedAudioUnchangedFromV5': False,
        'aacPacketsAndTimestampsUnchangedFromV5': False, 'pairedAudioIdentical': True,
        'encodedTruePeakDbtp': state['technical']['encodedTruePeakDbtp'],
        'wholeFinalMixAsrCompared': True, 'newAsrPerformed': True, 'audioReviewMode': mode,
        'captionCues': {r['language']: r['cues'] for r in state['alignment']['captions']},
        'captionSemanticReviewReused': True, 'captionOffsetDeltaSeconds': 30,
        'visualReviewStatus': state['visual']['status'],
        'inspectedEncodedFrameCount': state['visual']['inspectedFrameCount'], 'evidence': evidence,
        'humanViewing': False, 'humanListening': False, 'userApproval': False,
        'platformMutationPerformed': False, 'remaining': pending, 'limits': limits,
        'baselinePreserved': f'output/{SLUG}-v5'}
    propose(P / 'production/final-review-v6.json', final)
    propose(P / 'production/final-review.json', final)
    manifest.update(status='local-final-review-ready', publishReady=False)
    manifest['paths'].update(paths)
    manifest['video'].update(width=1920, height=1080, fps=60, durationSeconds=FRAMES / 60)
    manifest['delivery'].update(status='v6-internal-review-complete-awaiting-user', directory=f'output/{SLUG}',
        masterDirectory=f'output/{SLUG}-v6', captionedSha256=master, humanReview=False,
        humanListening=False, audioReviewMode=mode)
    manifest['revision'].update(completedAt=now, baseline='v5', newTts=False,
        preservedNarrationPcm=True, preservedBodyVideo=True, newMusicMix=True,
        preservedAudio=False, preservedCaptions=False, preservedCaptionText=True,
        captionOffsetDeltaSeconds=30, introSeconds=30, introSpeed=2, retainedUnityExplanationCuts=8)
    manifest['revision'].pop('replacedExplanationCuts', None)
    cp.update(updatedAt=now, stage='local-final-review-ready', inProgress=[], pending=pending,
        localOutputs=paths, captionedSha256=master, humanFinalReview=False,
        reviewEvidence={k: v['path'] for k, v in evidence.items()},
        revisionPlan='planning/intro-gameplay-v6.json', evidenceLimits=limits)
    cp['completed'] = list(dict.fromkeys(cp.get('completed', []) + [
        'v6: six actual original-gameplay cuts, 60 seconds at 2x, inserted as 1800 moving frames after branding',
        'v6: complete 24718-frame v5 pictures retained around the insertion; total 26518 frames at 1080p60',
        'v6: original 19-paragraph narration PCM retained; Nimbus BGM added; current new encoded mix independently measured and ASR-compared',
        'v6: exact KO/EN cue texts and paragraph map retained with +30-second boundaries; four local review outputs ready']))
    control['scopedSetupAuthorizations'][SLUG].update(status='local-final-review-ready', revision='v6',
        humanReview=False, captionedSha256=master, audioReviewMode=mode)
    row.update(productionComplete=True, productionStatus='v6 실제 플레이 30초·2배속 + Nimbus 배경음악 · 1080p60 완료',
        reviewStatus='현재 파일 기술·본문 보존·자막 +30초·화면·새 믹스 ASR 검수 완료; 사용자 시청·청취 대기',
        humanApproval='제작 승인만 확인; v6 최종 사용자 시청 승인 전',
        executionStatus='로컬 검수 대기; 업로드·자동 다음 영상 없음', localMasterAvailable=True,
        localReviewPath=f'output/{SLUG}/index.html', captionedSha256=master)
    block = f'''{BEGIN}
## REA와 AI로 만드는 게임 기반 프로토타입

| 영상 | 수정본 | 내부 검수 | 사용자 검수 | 상태 |
|---|---|---|---|---|
| [기존 게임 분석 → 새 프로토타입](../output/{SLUG}/index.html) | v6 · 실제 플레이 30초/2배속 + BGM · 1080p60 · 7분 22초 · 자막/무자막·한영 SRT | 현재 파일 디코드·본문 프레임 보존·자막 +30초·화면 확인; 새 믹스 ASR·음량 검사 | 전체 시청·청취 대기 | 로컬 검수본 준비, 이 작업의 업로드 없음 |

실제 벅샷 룰렛의 장전·사격·아이템 사용 6구간을 2배속 30초로 도입부에 넣고 기존 Nimbus 배경음악을 더했다. v5 본문 화면과 19문단 내레이션 원본은 보존하고 본문 및 한영 자막의 시작만 30초 옮겼다. 최종 혼합 음향은 v5와 다른 새 믹스이므로 현재 파일을 별도로 ASR 비교·음량 검사했다. 이 검사는 사람의 전체 시청·청취를 대신하지 않는다. Unity는 설명용 렌더러이고 실제 재구현 프로토타입은 Godot이다. v5 출력과 검수 근거는 별도 보관한다.
{END}'''
    for path, value in [(P / 'project.json', manifest), (P / 'production/checkpoint.json', cp),
                        (CONTROL, control), (WORKLIST, work)]:
        propose(path, value)
    propose(DOC, (doc[:doc.index(BEGIN)] + block + doc[doc.index(END) + len(END):]).encode('utf-8'), True)
    for path in updates:
        before.setdefault(path, sha(path) if path.is_file() else None)
    return updates, before


def apply(updates, before, state):
    lock = WORK / 'finalize-delivery-v6.lock.json'
    with lock.open('x', encoding='utf-8') as stream:
        json.dump({'pid': os.getpid(), 'startedAt': datetime.now(timezone.utc).isoformat()}, stream)
    try:
        scope()
        for name, expected in state['evidenceToRecheck'].items():
            need(sha(name) == expected, 'Evidence changed before update: ' + name)
        for path, expected in before.items():
            need((sha(path) if path.is_file() else None) == expected, 'Concurrent metadata update; no changes written: ' + str(path))
        journal = {'status': 'validated-local-metadata-update', 'masterSha256': state['master'],
            'targets': [{'path': str(path), 'beforeSha256': before[path],
                         'afterSha256': hashlib.sha256(data).hexdigest()} for path, data in updates.items()],
            'platformMutationPerformed': False, 'humanReview': False}
        receipt = WORK / 'finalization-metadata-receipt.json'
        asm.save(receipt, journal)
        for path, data in updates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + f'.v6-{os.getpid()}.tmp')
            with temporary.open('xb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        journal.update(status='local-metadata-updated', completedAt=datetime.now(timezone.utc).isoformat())
        asm.save(receipt, journal)
    finally:
        if lock.is_file() and read(lock).get('pid') == os.getpid():
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='Validate only, the default')
    group.add_argument('--apply', action='store_true', help='Update only local scoped completion metadata after all actual QA exists')
    args = parser.parse_args()
    state = validate()
    updates, before = build_updates(state)
    if args.apply:
        apply(updates, before, state)
    print(json.dumps({'revision': 'v6', 'status': 'local-review-ready-user-review-pending' if args.apply else 'validated-no-state-changes',
        'captionedSha256': state['master'], 'metadataTargets': [str(p) for p in updates],
        'newAudioMix': True, 'newAsrPerformed': True, 'originalNarrationPcmPreserved': True,
        'humanViewing': False, 'humanListening': False, 'platformMutationPerformed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
