"""Finalize only the selected v5 local review after actual hash-bound QA.

Default / --check is read-only. --apply validates all inputs before updating the
project, its checkpoint, final-review/caption metadata, and only its existing
control/worklist entries. No render, ASR, upload, publication, schedule, deletion,
canonical media collection, or review-page generation is performed here.

Final visual review contract (production/local/final-qa-v5/visual-review.json):
status='passed-inspected-encoded-frames', masterSha256, inspectedFrameIndices,
inspectedFrameCount, blockingFindings=[], replacementCutIds (all eight),
sourceReviewSha256 and preservationProofSha256. All eight replacement intervals
must have an actually inspected encoded frame. Source motion review and final
encoded-frame review are separate evidence; neither implies human viewing.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re

import assemble_documentary as asm

ROOT, P = asm.REPO, asm.PROJECT
SLUG = P.name
WORK = P / 'production/local/documentary-v5'
QA = P / 'production/local/final-qa-v5'
UNITY = P / 'production/local/unity-v5'
OUT = ROOT / f'output/{SLUG}-v5'
BASE_OUT = ROOT / f'output/{SLUG}-v4'
CONTROL = ROOT / 'shared/publishing/video-production-control.json'
WORKLIST = ROOT / 'shared/publishing/video-worklist.json'
DOC = ROOT / 'docs/VIDEO_WORKLIST.md'
BEGIN = '<!-- BUCKSHOT-RE-SETUP-20261028-START -->'
END = '<!-- BUCKSHOT-RE-SETUP-20261028-END -->'
MASTER_V4 = '58891b5c9e52d50dda41db070fe12f7c7d7fec15e8d9884eed96274f76323fa3'
FRAMES = 24718
HASH_CACHE = {}


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return asm.load(path)


def sha(path):
    path = Path(path).resolve()
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    if key not in HASH_CACHE:
        HASH_CACHE[key] = asm.digest(path)
    return HASH_CACHE[key]


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def resolve(value):
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path if str(value).replace('\\', '/').startswith(('projects/', 'output/', 'shared/', 'docs/')) else P / path
    path = path.resolve()
    need(path.is_relative_to(ROOT), 'Evidence outside selected workspace: ' + str(path))
    return path


def bound(path, project_relative=False):
    path = Path(path).resolve()
    need(path.is_file(), 'Required evidence missing: ' + str(path))
    return {'path': path.relative_to(P).as_posix() if project_relative else str(path), 'sha256': sha(path)}


def check_binding(value):
    path = resolve(value['path'])
    need(path.is_file() and sha(path) == value['sha256'], 'Bound input changed: ' + str(path))
    return path


def check_nested_bindings(value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            check_binding(value)
        for child in value.values():
            check_nested_bindings(child)
    elif isinstance(value, list):
        for child in value:
            check_nested_bindings(child)


def frame_values(path):
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        parts = [x.strip() for x in line.split(',')]
        need(len(parts) == 6 and re.fullmatch(r'[a-fA-F0-9]{64}', parts[-1]), 'Invalid frame hash evidence')
        rows.append(parts[-1])
    return rows


def validate_caption_reuse(preservation, proposed_at):
    baseline_path = P / 'production/caption-alignment-v4.json'
    baseline = read(baseline_path)
    need(baseline.get('status') == 'approved-semantic-paragraph-alignment' and
         baseline.get('approved') is True and baseline.get('manualSemanticReview') is True and
         baseline.get('allParagraphTextsRetained') is True and baseline.get('paragraphCount') == 19,
         'Existing complete semantic caption review is required')
    need(len(baseline.get('paragraphs', [])) == 19, 'Incomplete baseline paragraph map')
    tracks = {row['language']: row for row in baseline['captions']}
    need(set(tracks) == {'ko', 'en'}, 'KO and EN baseline tracks required')
    result = copy.deepcopy(baseline)
    for language, count in [('ko', 115), ('en', 135)]:
        old = resolve(tracks[language]['path'])
        new = OUT / f'{SLUG}.{language}.srt'
        need(old == BASE_OUT / f'{SLUG}.{language}.srt', 'Unexpected baseline subtitle path')
        need(sha(old) == sha(new) == tracks[language]['sha256'] ==
             preservation['captions'][f'captions.{language}.srt']['sha256'], 'Subtitles are not byte-identical')
        cues = asm.read_srt(new)
        need(len(cues) == count == tracks[language]['cues'], 'Subtitle cue count changed')
        covered = []
        for paragraph in baseline['paragraphs']:
            need(paragraph.get('semanticMeaningReviewed') is True and paragraph.get('allTextRetained') is True,
                 'A baseline paragraph lacks semantic review')
            indices = paragraph[language + 'Cues']
            need(indices and all(type(i) is int and 1 <= i <= len(cues) for i in indices), 'Invalid cue map')
            need(abs(cues[indices[0] - 1]['start'] - paragraph['start']) <= .002 and
                 abs(cues[indices[-1] - 1]['end'] - paragraph['end']) <= .002, 'Paragraph timing changed')
            actual_text = ' '.join(cues[i - 1]['text'] for i in indices)
            need(' '.join(actual_text.split()) == ' '.join(paragraph[language + 'Text'].split()),
                 'Paragraph text differs from the directly reviewed baseline')
            covered.extend(indices)
        need(covered == list(range(1, len(cues) + 1)), 'Caption map skips or repeats cues')
        next(row for row in result['captions'] if row['language'] == language)['path'] = new.relative_to(ROOT).as_posix()
    result.update(revision='v5', reusedAt=proposed_at,
                  reviewScope='Exact KO/EN SRT and unchanged audio/timing reuse of the completed v4 paragraph semantic review. No new text review, ASR or human listening is claimed.',
                  newManualSemanticReviewPerformed=False, manualSemanticReviewReused=True,
                  sourceAlignment=bound(baseline_path), audioPreservation=bound(WORK / 'preservation-proof.json'),
                  humanListening=False, humanViewing=False, userApproval=False)
    return result


def validate():
    control = read(CONTROL)
    manifest = read(P / 'project.json')
    auth = control.get('scopedSetupAuthorizations', {}).get(SLUG, {})
    need(auth.get('productionAllowedNow') is True and auth.get('revision') == 'v5', 'Scoped v5 authorization missing')
    need(manifest.get('revision', {}).get('id') == 'v5' and manifest.get('startGate', {}).get('productionAllowedNow') is True,
         'Project is not the selected v5 revision')
    q = read(WORK / 'technical-qa.json')
    preservation_path = WORK / 'preservation-proof.json'
    preservation = read(preservation_path)
    preflight = read(WORK / 'preflight.json')
    progress = read(WORK / 'render-progress.json')
    snapshot = preflight['snapshot']
    need(q.get('technicalDecodePassed') is True and q.get('pairedAudioIdentical') is True and
         q.get('audioLoudnessPassed') is True and q.get('preservationVerificationPassed') is True,
         'V5 technical and preservation checks must actually pass')
    need(preservation.get('technicalPassed') is True and preservation.get('revision') == 'v5' and
         preservation.get('totalFrames') == FRAMES and preservation.get('aacPacketsAndTimestampsUnchanged') is True and
         preservation.get('decodedAudioUnchanged') is True, 'Complete v5 preservation proof required')
    need(all(preservation.get(k) is False for k in ['newTts', 'newAudioMix', 'newAsr']), 'This is strictly visual-only')
    fingerprint = stable_hash(snapshot)
    need(fingerprint == preflight['snapshotSha256'] == preservation['snapshotSha256'] == progress['snapshotSha256'],
         'Preparation/render/preservation snapshots differ')
    need(preflight.get('editReady') is True and not preflight.get('readiness') and progress.get('complete') is True,
         'V5 is not fully rendered from reviewed sources')
    check_nested_bindings(snapshot)
    check_nested_bindings(preservation)
    need(preservation['baselineMasters'] == snapshot['baselineMasters'], 'Different baseline masters')
    need(snapshot['baselineMasters']['captioned']['sha256'] == MASTER_V4, 'Unexpected baseline master')
    outputs = {}
    for kind in ['clean', 'captioned']:
        path = OUT / f'{SLUG}.{kind}.mp4'
        item = q['outputs'][kind]
        need(Path(item['file']).resolve() == path and sha(path) == item['sha256'], 'Final output hash/path mismatch')
        outputs[kind] = bound(path)
        need(outputs[kind] == progress['outputs'][kind] == preservation['currentMasters'][kind], 'Current output binding differs')
        video = next(s for s in item['probe']['streams'] if s['codec_type'] == 'video')
        audio = [s for s in item['probe']['streams'] if s['codec_type'] == 'audio']
        need((video['width'], video['height'], Fraction(video['avg_frame_rate']), int(video['nb_read_frames'])) ==
             (1920, 1080, 60, FRAMES), 'Final encoded dimensions/fps/decoded frame count differ')
        need(len(audio) == 1 and audio[0]['codec_name'] == 'aac' and audio[0]['sample_rate'] == '48000' and audio[0]['channels'] == 2,
             'Unexpected final AAC stream')
        for duration in [video['duration'], audio[0]['duration'], item['probe']['format']['duration']]:
            need(abs(float(duration) - FRAMES / 60) <= 1024 / 48000, 'Final stream length changed')
    need(q['encodedTruePeakDbtp'] <= -1.5, 'Encoded peak exceeds production limit')
    for label, value in preservation['audioPackets'].items():
        packet_path = check_binding(value)
        report = read(packet_path)
        check_binding(report['file'])
        need(len(report['packets']) == report['packetCount'] == value['packetCount'] and
             stable_hash(report['packets']) == report['packetSequenceSha256'] == value['packetSequenceSha256'],
             'Audio packet proof contents changed')
        expected = (BASE_OUT if label.startswith('v4-') else OUT) / f'{SLUG}.{label.split("-", 1)[1]}.mp4'
        need(resolve(report['file']['path']) == expected, 'Audio packet proof belongs to another output')
        raw_hash = (WORK / 'proof' / (label + '.audio-f32.sha256')).read_text(encoding='utf-8').strip()
        need(raw_hash == preservation['decodedFloatAudioHashes'][label], 'Decoded FLOAT hash record changed')
    labels = {'v4-clean', 'v4-captioned', 'v5-clean', 'v5-captioned'}
    need(set(preservation['audioPackets']) == set(preservation['decodedFloatAudioHashes']) == labels,
         'Audio equality must cover both complete baseline/current pairs')
    need(len({x['packetSequenceSha256'] for x in preservation['audioPackets'].values()}) == 1 and
         len(set(preservation['decodedFloatAudioHashes'].values())) == 1, 'V4/V5 audio is not identical')
    cues = read(P / 'production/unity-workflow-v5-cues.json')
    entries = cues['entries']
    wanted = {entry['id'] for entry in entries}
    need(len(entries) == len(wanted) == 8, 'Expected eight unique Unity cuts')
    sources = read(UNITY / 'source-review.json')['sources']
    replacements = [r for r in snapshot['cuts'] if r['replacement']]
    need({r['replacement']['id'] for r in replacements} == wanted and len(replacements) == 8, 'Actual replacement set differs')
    for row in replacements:
        source = row['replacement']; entry = next(x for x in entries if x['id'] == source['id'])
        record = sources[source['id']]
        need(record == source['review'] and record.get('motionReviewed') is True and record.get('evidence'), 'Unity motion evidence stale/missing')
        need(sha(Path(source['path'])) == record['sha256'] == source['sha256'], 'Unity source changed')
        need(row['frames'] == source['frames'] == entry['frames'] and row['bodyStartFrame'] == entry['bodyStartFrame'],
             'Unity cut timing changed')
        producer_path = check_binding(source['producerReceipt'])
        need(resolve(record['producerReceipt']) == producer_path and record['producerReceiptSha256'] == sha(producer_path),
             'Producer receipt binding differs')
        producer = read(producer_path)
        need(producer.get('sha256') == source['sha256'] and producer.get('actualFrames') == row['frames'] and
             producer.get('completed', True) is not False, 'Incomplete/different Unity production')
    frames = read(check_binding(preservation['cleanFramePreservation']))
    need(frames.get('frames') == FRAMES and frames.get('mismatchCount') == 0 and
         frames.get('allCleanFramesMatchIntendedSources') is True, 'Clean frame preservation failed')
    baseline_frames = frame_values(check_binding(frames['baseline']))
    actual_frames = frame_values(check_binding(frames['current']))
    need(len(baseline_frames) == len(actual_frames) == FRAMES, 'Frame proof length differs')
    expected_frames = list(baseline_frames)
    need({r['unityId'] for r in frames['replacements']} == wanted and len(frames['replacements']) == 8,
         'Frame proof is missing a Unity cut')
    for item in frames['replacements']:
        row = next(x for x in replacements if x['replacement']['id'] == item['unityId'])
        hashes = frame_values(check_binding(item['decodedSourceProof']))
        need(item['finalStartFrame'] == row['finalStartFrame'] and item['frames'] == len(hashes) == row['frames'],
             'Frame proof cut placement differs')
        expected_frames[item['finalStartFrame']:item['finalStartFrame'] + item['frames']] = hashes
    need(expected_frames == actual_frames, 'Stored pixel hashes do not prove the claimed preservation')
    visual_path = QA / 'visual-review.json'
    visual = read(visual_path)
    master = outputs['captioned']['sha256']
    need(visual.get('status') == 'passed-inspected-encoded-frames' and visual.get('masterSha256') == master,
         'Current encoded visual QA has not passed')
    need(visual.get('blockingFindings') == [], 'Visual blocking findings remain or are unreported')
    need(visual.get('sourceReviewSha256') == sha(UNITY / 'source-review.json') and
         visual.get('preservationProofSha256') == sha(preservation_path), 'Visual review uses stale source/preservation evidence')
    need(set(visual.get('replacementCutIds', [])) == wanted and len(visual['replacementCutIds']) == 8,
         'Final visual review must account for all eight replacements')
    inspected = visual.get('inspectedFrameIndices', [])
    need(inspected and len(set(inspected)) == len(inspected) == visual.get('inspectedFrameCount') and
         all(type(n) is int and 0 <= n < FRAMES for n in inspected), 'Invalid final inspected frame inventory')
    for row in replacements:
        need(any(row['finalStartFrame'] <= frame < row['finalStartFrame'] + row['frames'] for frame in inspected),
             'No actual encoded inspection recorded for ' + row['replacement']['id'])
    for evidence in visual.get('evidenceFiles', []):
        check_binding(evidence)
    audio_path = check_binding(preservation['audioContentReviewReusedFrom'])
    audio = read(audio_path)
    need(audio.get('masterSha256') == MASTER_V4 and audio.get('technicalPassed') is True and
         audio.get('wholeMixAsrCompared') is True, 'Actual baseline whole-audio review missing')
    need(audio['preservation']['sourceNarrationSha256'] == snapshot['narration']['sha256'], 'Narration PCM differs')
    need(audio['loudness']['truePeakDbtp'] == q['encodedTruePeakDbtp'], 'Identical AAC has inconsistent peak evidence')
    inputs = read(P / 'production/local/audio-v4/render-inputs.json')['sha256']
    for language in ['ko', 'en']:
        need(sha(P / f'script/revision-v4/narration.{language}.json') == inputs[language + 'Script'], 'Approved script changed')
    for name, record in snapshot['captions'].items():
        need(sha(WORK / name) == record['sha256'], 'Working caption/ASS differs from v4')
    proposed_at = datetime.now(timezone.utc).isoformat()
    alignment = validate_caption_reuse(preservation, proposed_at)
    need(alignment['sourceAudioSha256'] == snapshot['narration']['sha256'], 'Alignment source voice differs')
    timeline = read(WORK / 'timeline.json')
    need(timeline.get('revision') == 'v5' and timeline.get('bodyFrameCount') == FRAMES - 720 and
         Path(timeline['outputDirectory']).resolve() == OUT, 'Current timeline not v5')
    body_cuts = [row for row in snapshot['cuts'] if row['bodyStartFrame'] is not None]
    need([(b['id'], b['frames']) for b in timeline['beats']] ==
         [(b['id'], b['frames']) for b in body_cuts], 'Canonical timeline cut order/length differs from the rendered snapshot')
    evidence_to_recheck = {key[0]: value for key, value in HASH_CACHE.items()}
    return {'at': proposed_at, 'technical': q, 'preservation': preservation, 'snapshot': snapshot,
            'outputs': outputs, 'master': master, 'visual': visual, 'baselineAudio': audio,
            'alignment': alignment, 'timeline': timeline, 'replacementIds': sorted(wanted),
            'evidenceToRecheck': evidence_to_recheck}


def build_updates(state):
    """Resolve and validate every mutation target before the first write."""
    now, master = state['at'], state['master']
    target_paths = [P / 'project.json', P / 'production/checkpoint.json', CONTROL, WORKLIST, DOC]
    before = {path: sha(path) for path in target_paths}
    manifest, cp, control, work = [read(p) for p in target_paths[:4]]
    need(manifest['revision']['id'] == 'v5' and control['scopedSetupAuthorizations'][SLUG]['revision'] == 'v5' and
         control['scopedSetupAuthorizations'][SLUG]['productionAllowedNow'] is True, 'Scope changed before finalization')
    selected = [row for row in work['rows'] if row.get('id') == 'S-BUCKSHOT-RE' and row.get('slug') == SLUG]
    need(len(selected) == 1, 'Expected exactly one existing scoped worklist row')
    row = selected[0]
    doc = DOC.read_text(encoding='utf-8-sig')
    need(doc.count(BEGIN) == doc.count(END) == 1 and doc.index(BEGIN) < doc.index(END), 'Scoped worklist document markers invalid')
    updates = {}
    def propose(path, value, raw=False):
        updates[path] = value if raw else json_bytes(value)
    def future_binding(path):
        return {'path': path.relative_to(P).as_posix(), 'sha256': hashlib.sha256(updates[path]).hexdigest()}
    canonical_timeline = P / 'production/timeline-v5.json'
    canonical_alignment = P / 'production/caption-alignment-v5.json'
    propose(canonical_timeline, (WORK / 'timeline.json').read_bytes(), raw=True)
    propose(canonical_alignment, state['alignment'])
    source_audio = state['baselineAudio']
    audio = {'schemaVersion': 1, 'checkedAt': now, 'revision': 'v5', 'masterSha256': master,
             'masterPath': str(OUT / f'{SLUG}.captioned.mp4'), 'technicalPassed': True,
             'wholeMixAsrCompared': True, 'newAsrPerformed': False,
             'reviewMode': 'reused-v4-identical-aac-and-pcm',
             'scope': 'Current v5 AAC packet bytes/timestamps and decoded FLOAT samples are identical to v4. Reuse its actual whole-mix ASR/content and continuity evidence; no new transcription, synthesis, mixing or human listening occurred.',
             'baselineMasterSha256': MASTER_V4,
             'baselineAudioReview': state['preservation']['audioContentReviewReusedFrom'],
             'currentAudioPreservation': bound(WORK / 'preservation-proof.json', project_relative=True),
             'pairedDecodedAudioIdentical': True, 'loudness': copy.deepcopy(source_audio['loudness']),
             'newSpeechPronunciationCandidates': copy.deepcopy(source_audio.get('newSpeechPronunciationCandidates', [])),
             'retainedPronunciationCandidates': copy.deepcopy(source_audio.get('retainedPronunciationCandidates', [])),
             'sourceAndFinalListeningPage': source_audio.get('sourceAndFinalListeningPage'),
             'listeningPageReuseNote': 'The v4 audition clips remain timing/audio-identical references; their page is not a new v5 human review.',
             'humanViewing': False, 'humanListening': False, 'userApproval': False,
             'status': 'reused-technical-audio-checks-passed-human-listening-pending',
             'remaining': ['Contextual pronunciation and natural-pace listening', 'User full-version review before any upload']}
    audio_path = QA / 'audio-review.json'
    propose(audio_path, audio)
    evidence = {
        'technical': bound(WORK / 'technical-qa.json', True),
        'preservation': bound(WORK / 'preservation-proof.json', True),
        'visual': bound(QA / 'visual-review.json', True),
        'sourceReview': bound(UNITY / 'source-review.json', True),
        'audio': future_binding(audio_path),
        'audioBaseline': bound(P / 'production/local/final-qa-v4/audio-review.json', True),
        'captions': future_binding(canonical_alignment),
        'plan': bound(P / 'production/unity-workflow-v5-cues.json', True),
        'timeline': future_binding(canonical_timeline),
    }
    stem = f'output/{SLUG}-v5/{SLUG}'
    paths = {'videoBurnedCaptions': stem + '.captioned.mp4', 'videoClean': stem + '.clean.mp4',
             'captionsKo': stem + '.ko.srt', 'captionsEn': stem + '.en.srt',
             'captionAlignmentReview': f'projects/{SLUG}/production/caption-alignment-v5.json',
             'timeline': f'projects/{SLUG}/production/timeline-v5.json',
             'script': f'projects/{SLUG}/script/revision-v4/narration.ko.json',
             'scriptEn': f'projects/{SLUG}/script/revision-v4/narration.en.json'}
    need(all((ROOT / p).is_file() or ROOT / p in updates for p in paths.values()), 'A delivery path is absent')
    duration = FRAMES / 60
    pending = ['User final viewing of v5 Unity explanations and unchanged narration',
               'Whole human listening and retained pronunciation candidates remain pending',
               'No platform action or automatic next video is authorized by this completion']
    limits = ['Unity scenes are authored explanation animations; the actual independently built prototype remains Godot.',
              'Actual implementation used REA CLI/readable GDScript, own code, Blender Python and Godot. Ghidra/Tripo MCP are optional general routes, not executed tools.',
              'No measured speedup or complete original-game equivalence is claimed.',
              'Current clean pixels, duration, copied captions and encoded audio are verified; encoded visual inspection is limited to the actual documented frames/motion evidence.',
              'V4 whole-audio ASR/content review is reused only because AAC packets, timestamps and decoded samples match exactly. Human whole-video viewing/listening is pending.',
              'Original game source/assets and saves remain preserved; no platform action was performed.']
    final = {'schemaVersion': 1, 'checkedAt': now, 'revision': 'v5', 'status': 'local-review-ready-user-review-pending',
             'captionedSha256': master, 'outputs': state['outputs'], 'durationSeconds': duration,
             'totalFrames': FRAMES, 'width': 1920, 'height': 1080, 'fps': 60,
             'replacementCutIds': state['replacementIds'], 'replacementCutCount': 8,
             'retainedCutsIncludingBookends': 26, 'allCleanFramesMatchIntendedSources': True,
             'pairedAudioIdentical': True, 'aacPacketsAndTimestampsUnchanged': True,
             'decodedAudioUnchanged': True, 'encodedTruePeakDbtp': state['technical']['encodedTruePeakDbtp'],
             'wholeFinalMixAsrCompared': True, 'audioReviewMode': audio['reviewMode'], 'newAsrPerformed': False,
             'captionCues': {x['language']: x['cues'] for x in state['alignment']['captions']},
             'captionSemanticReviewReused': True, 'visualReviewStatus': state['visual']['status'],
             'inspectedEncodedFrameCount': state['visual']['inspectedFrameCount'], 'evidence': evidence,
             'humanViewing': False, 'humanListening': False, 'userApproval': False,
             'platformMutationPerformed': False, 'remaining': pending, 'limits': limits,
             'baselinePreserved': f'output/{SLUG}-v4'}
    propose(P / 'production/final-review-v5.json', final)
    propose(P / 'production/final-review.json', final)
    manifest.update(status='local-final-review-ready', publishReady=False)
    manifest['paths'].update(paths)
    manifest['video'].update(width=1920, height=1080, fps=60, durationSeconds=duration)
    manifest['delivery'].update(status='v5-internal-review-complete-awaiting-user', directory=f'output/{SLUG}',
                                masterDirectory=f'output/{SLUG}-v5', captionedSha256=master,
                                humanReview=False, humanListening=False, audioReviewMode=audio['reviewMode'])
    manifest['revision'].update(completedAt=now, baseline='v4', preservedAudio=True,
                                preservedCaptions=True, replacedExplanationCuts=8)
    cp.update(updatedAt=now, stage='local-final-review-ready', inProgress=[], pending=pending,
              localOutputs=paths, captionedSha256=master, humanFinalReview=False,
              reviewEvidence={key: value['path'] for key, value in evidence.items()},
              revisionPlan='production/unity-workflow-v5-cues.json', evidenceLimits=limits)
    cp['completed'] = list(dict.fromkeys(cp.get('completed', []) + [
        'v5: eight analysis-tool/development-environment explanation cuts replaced with inspected Unity animations',
        'v5: all 24718 clean frames match intended v4/Unity sources; original gameplay/prototype cuts and bookends retained',
        'v5: actual AAC packets/timestamps and decoded FLOAT samples identical to v4; existing audio review reused without new ASR',
        'v5: exact KO/EN SRT and ASS retained; current encoded technical/visual evidence bound to the delivered masters']))
    control['scopedSetupAuthorizations'][SLUG].update(status='local-final-review-ready', revision='v5',
        humanReview=False, captionedSha256=master, audioReviewMode=audio['reviewMode'])
    row.update(productionComplete=True, productionStatus='v5 Unity 설명 8컷 보강 · 1080p60 검수본 완료',
               reviewStatus='현재 파일 기술·보존·인코딩 화면 검수 완료; 동일 음성 v4 검수 재사용; 사용자 시청·청취 대기',
               humanApproval='제작 승인만 확인; v5 최종 사용자 시청 승인 전',
               executionStatus='로컬 검수 대기; 업로드·자동 다음 영상 없음', localMasterAvailable=True,
               localReviewPath=f'output/{SLUG}/index.html', captionedSha256=master)
    # Existing platformStatus/videoId/url and all other worklist/control rows remain unchanged.
    block = f'''{BEGIN}
## REA와 AI로 만드는 게임 기반 프로토타입

| 영상 | 수정본 | 내부 검수 | 사용자 검수 | 상태 |
|---|---|---|---|---|
| [기존 게임 분석 → 새 프로토타입](../output/{SLUG}/index.html) | v5 · Unity 설명 8컷 · 1080p60 · 6분 52초 · 자막/무자막·한영SRT | 현재 파일 디코드·프레임 보존·인코딩 화면 확인; v4와 AAC/PCM 동일성 확인 | 전체 시청·청취 대기 | 로컬 검수본 준비, 이 작업의 업로드 없음 |

REA·AI 에이전트·MCP와 개발환경 설명을 Unity 애니메이션으로 보강했다. 실제 게임·Godot 프로토타입 영상, 음성, 자막, 전체 24,718프레임의 길이는 보존했다. 기존 v4 음성과 같음을 검증해 전체 ASR·음량 검수 근거를 재사용했으며 새 음성 생성이나 ASR은 하지 않았다. Unity는 설명용 렌더러이고 실제 재구현 프로토타입은 Godot이다. v4 출력과 검수 근거는 별도 보관한다.
{END}'''
    propose(P / 'project.json', manifest)
    propose(P / 'production/checkpoint.json', cp)
    propose(CONTROL, control)
    propose(WORKLIST, work)
    propose(DOC, (doc[:doc.index(BEGIN)] + block + doc[doc.index(END) + len(END):]).encode('utf-8'), raw=True)
    # Capture original state for every target, including previously absent new metadata.
    for path in updates:
        if path not in before:
            before[path] = sha(path) if path.is_file() else None
    return updates, before


def apply(updates, before, state):
    lock = WORK / 'finalize-delivery-v5.lock.json'
    try:
        with lock.open('x', encoding='utf-8') as stream:
            json.dump({'pid': os.getpid(), 'startedAt': datetime.now(timezone.utc).isoformat()}, stream)
    except FileExistsError:
        raise RuntimeError('Finalization lock exists; inspect the existing operation, do not run a duplicate')
    try:
        for name, expected in state['evidenceToRecheck'].items():
            need(sha(Path(name)) == expected, 'Evidence changed before update: ' + name)
        for path, expected in before.items():
            need((sha(path) if path.is_file() else None) == expected, 'Concurrent target change; no update written: ' + str(path))
        journal = {'status': 'validated-local-metadata-update', 'masterSha256': state['master'],
                   'targets': [{'path': str(path), 'beforeSha256': before[path],
                                'afterSha256': hashlib.sha256(data).hexdigest()} for path, data in updates.items()],
                   'platformMutationPerformed': False, 'humanReview': False}
        journal_path = WORK / 'finalization-metadata-receipt.json'
        asm.save(journal_path, journal)
        for path, data in updates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_name(path.name + f'.v5-{os.getpid()}.tmp')
            need(not temporary.exists(), 'Unexpected temporary metadata file')
            with temporary.open('xb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        journal.update(status='local-metadata-updated', completedAt=datetime.now(timezone.utc).isoformat())
        asm.save(journal_path, journal)
    finally:
        if lock.is_file() and read(lock).get('pid') == os.getpid():
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='Validate only; default mode')
    modes.add_argument('--apply', action='store_true', help='Apply local scoped completion metadata after every validation passes')
    args = parser.parse_args()
    state = validate()
    updates, before = build_updates(state)
    if args.apply:
        apply(updates, before, state)
    print(json.dumps({'revision': 'v5', 'status': 'local-review-ready-user-review-pending' if args.apply else 'validated-no-state-changes',
                      'captionedSha256': state['master'], 'metadataTargets': [str(p) for p in updates],
                      'audioReviewMode': 'reused-v4-identical-aac-and-pcm', 'newAsrPerformed': False,
                      'humanViewing': False, 'humanListening': False, 'platformMutationPerformed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
