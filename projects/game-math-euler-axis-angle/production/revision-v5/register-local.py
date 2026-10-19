"""Register the reviewed V5 visual-only pair; no render, upload or next video.

Run only after current integrity, retained-frame evidence and root's moving
reviews exist. Audio, narration and bilingual subtitles remain V4 inputs.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys

R = Path(__file__).resolve().parents[4]
P = R / 'projects/game-math-euler-axis-angle'
H = Path(__file__).resolve().parent
H4 = P / 'production/revision-v4'
O = P / 'production/local/revision-v5'
B = P / 'production/local/revision-v4-clarity'
REVISION = 'tracked-gizmos-code-colors-v5'
TIMELINE = P / 'production/revision-v3/timeline.json'
CONTROL = R / 'shared/publishing/video-production-control.json'
WORKLIST = R / 'shared/publishing/video-worklist.json'
STAGE = 'local-visual-v5-QA-complete-awaiting-Drive'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    temporary = path.with_name(path.name + '.register-v5.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, path)


def rel(path):
    return path.relative_to(R).as_posix()


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def selected():
    value = read(CONTROL)
    require(value['selectedVideo'] == P.name, 'Selected video changed; no registration performed.')
    return value


def evidence(path):
    return {'file': rel(path), 'sha256': sha(path)}


def validate():
    """Read existing evidence only. Never generate missing QA or media."""
    selected()
    pair = read(O / 'pair-source.json')
    integrity = read(O / 'qa/integrity.json')
    proof = read(H / 'visual-reuse-proof.json')
    assembly = read(H / 'assembly-plan.json')
    timeline = read(TIMELINE)
    prior_integrity = read(B / 'qa/integrity.json')
    audio_review = read(H4 / 'audio-review.json')
    gizmo = read(H / 'gizmo-review.json')
    code = read(H / 'code-color-review.json')
    moving_report = read(H / 'moving-review.json')
    require(assembly['revision'] == REVISION, 'Wrong assembly revision.')
    require(integrity['revision'] == proof['revision'] == REVISION, 'Wrong QA revision.')
    require(pair['inputs']['assemblyPlanSha256'] == sha(H / 'assembly-plan.json'), 'Stale pair assembly binding.')
    require(pair['inputs']['timelineSha256'] == sha(TIMELINE) == assembly['timelineSha256'], 'Timeline changed.')
    require(assembly['totalFrames'] == timeline['totalFrames'] == 93100 and timeline['fps'] == 60, 'Unexpected timing.')
    require(timeline['actualFrames'] == 36952 and timeline['explanationFrames'] == 55428
            and timeline['ratioErrorFrames'] == 0, '40:60 body ratio changed.')
    for report in (integrity, proof):
        require(report['inputs']['assemblyPlanSha256'] == sha(H / 'assembly-plan.json'), 'Stale QA assembly binding.')
    require(integrity['inputs']['pairSourceSha256'] == proof['pairSourceSha256'] == sha(O / 'pair-source.json'), 'Stale QA pair binding.')
    require(proof['cleanVideoSha256'] == pair['outputs']['clean']['sha256']
            and proof['captionedVideoSha256'] == pair['outputs']['captioned']['sha256'], 'Stale visual output hashes.')
    require(proof['captionedRetainedFramesExactlyEqual'] is True, 'Retained captioned pixels not verified.')
    retained = assembly['kindPlans']['captioned']['retainedFrames']
    require(proof['captionedRetainedFramesCompared'] == retained, 'Incomplete retained-frame comparison.')
    captioned_stream = next(x for x in proof['streams'] if x['kind'] == 'captioned')
    require(captioned_stream['decodedComparisonPerformed'] is True
            and captioned_stream['retainedRangesExactDecodedEqual'] is True
            and captioned_stream['retainedFrames'] == retained, 'Retained pixel comparison failed.')
    baseline_aac = {x['aacSha256'] for x in prior_integrity['outputs']}
    require(len(baseline_aac) == 1, 'V4 pair AAC disagreement.')
    require(integrity['exactAACStreamEqual'] is True and proof['audio']['exactAACStreamEqual'] is True
            and proof['audio']['asrReused'] is True, 'V4 encoded audio was not verified reusable.')
    require({proof['audio']['aacSha256']} == baseline_aac, 'Audio proof not bound to approved V4 AAC.')
    for kind in ('clean', 'captioned'):
        row = next(x for x in integrity['outputs'] if x['kind'] == kind)
        expected = pair['outputs'][kind]
        output = R / expected['file']
        require(output.resolve() == (O / f'euler-{kind}.mp4').resolve(), 'Unexpected master path.')
        require(row['sha256'] == expected['sha256'], 'Current output SHA does not match integrity.')
        if 'file' in row:
            require((R / row['file']).resolve() == output.resolve(), 'Integrity output path mismatch.')
        require(row['fullDecodePassed'] is True and row['ptsMonotonicAndUniform'] is True,
                'Current complete decode/PTS integrity missing.')
        require((row['frames'], row['width'], row['height'], float(row['fps'])) == (93100, 1920, 1080, 60), 'Master must be native FHD60.')
        require(abs(float(row.get('duration', 93100 / 60)) - 93100 / 60) < .02, 'Unexpected master duration.')
        require(int(row['audioSampleRate']) == 48000 and int(row['audioChannels']) == 2
                and row['exactAACStreamEqual'] is True and row['aacSha256'] in baseline_aac, 'Encoded audio differs from V4.')
        require(output.is_file(), 'Current master missing.')
        if 'bytes' in row:
            require(output.stat().st_size == row['bytes'], 'Current master byte count changed.')
    require(audio_review['directWholeEncodedTextCompared'] is True
            and audio_review['unresolvedConfirmedContentErrors'] == 0
            and audio_review['narrationStemUnchanged'] is True, 'V4 complete audio review missing.')
    require(audio_review['captionedSha256'] == assembly['baseline']['captioned']['sha256'], 'V4 audio-review binding mismatch.')
    require(audio_review['wholeListening'] == 'pending' and audio_review['addedBgm'] is False, 'Unexpected audio review state.')
    require(assembly['audio']['file'] == rel(B / 'final-mix.m4a'), 'Audio moved or replaced.')
    audio_sha = sha(B / 'final-mix.m4a')
    require(pair['inputs']['audioSha256'] == assembly['audio']['sha256']
            == integrity['inputs']['audioFileSha256'] == audio_sha, 'Audio-file hash changed.')
    for item in ('sourceAsrReuse', 'wholeEncodedAsr', 'wholeTextComparison', 'continuity', 'equivalence'):
        bound = audio_review[item]
        require(sha(R / bound['file']) == bound['sha256'], f'V4 {item} evidence changed.')
    replacements = {x['id']: x for x in assembly['replacements']}
    require(set(replacements) == {'02-kart', '05-kart', '14-turn', '20-mast', 'code-15', 'code-25'}, 'Unexpected replacement scope.')
    for receipt in gizmo['receipts']:
        expected = replacements[receipt['id']]['files']['captioned']['sha256']
        require(receipt['captionedSha256'] == expected and receipt['receiptInputsVerified'] is True
                and receipt['allCleanAndCaptionedFileHashesVerified'] is True, 'Stale gizmo clip review.')
    require({x['id'] for x in gizmo['receipts']} == {'02-kart', '05-kart', '14-turn', '20-mast'}, 'Incomplete gizmo review.')
    for output in code['outputs']:
        require(output['sha256'] == replacements['code-' + output['scene']]['files']['clean']['sha256'], 'Stale code clip review.')
    require({x['scene'] for x in code['outputs']} == {'15', '25'}, 'Incomplete code-color review.')
    moving = moving_report['movingReview']
    require(moving['status'] == 'passed' and moving['captionedSha256'] == pair['outputs']['captioned']['sha256'], 'Changed-range moving review not current.')
    require(all(moving.get(key) is True for key in ('changedRangesAndJoinsReviewed', 'native1080Reviewed', 'mobile375Reviewed')), 'Changed-range moving review incomplete.')
    # These are retained inputs, not copies generated in V5.
    kept = {key: evidence(B / name) for key, name in (
        ('audioMix', 'final-mix.m4a'), ('editorAudioMix', 'final-mix.wav'),
        ('captionsKo', 'captions.ko.srt'), ('captionsEn', 'captions.en.srt'))}
    return pair, integrity, proof, kept


def main():
    pair, integrity, proof, kept = validate()
    selected()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    project = read(P / 'project.json')
    previous_revision = project['revision']['id']
    project['revision'].update(id=REVISION,
        revisionScope='Visual-only: four tracked illustrative rotation gizmos and semantic code/text colors in scenes15/25. Narration, synchronized game audio, subtitles, lesson and timing unchanged.',
        nextRevision={'id': REVISION, 'stage': STAGE})
    project.update(status=STAGE, publishReady=False)
    project['paths'].update(videoClean=pair['outputs']['clean']['file'],
        videoBurnedCaptions=pair['outputs']['captioned']['file'], productionBuilder=rel(H / 'assemble.py'))
    for key, item in kept.items():
        project['paths'][key] = item['file']
    project['publishing'].update(currentRevision=REVISION, youtubeReplacementAuthorized=False)
    # Old Drive IDs remain true historical pointers; the explicit pending marker
    # prevents presenting that old file as delivery of this new revision.
    project['publishing']['pendingDriveRevision'] = REVISION
    project['finalRender'].update(status='visual-only-revision-internal-QA-complete',
        currentRevisionComplete=True, fps=60, durationSeconds=93100 / 60,
        openItems=['현재 V5 전체 마스터 Drive 업로드 및 사용자 최종 검수 대기',
                   '전체 사람 청취·발음 확인 대기', '기존 모든 Drive와 비공개 YouTube 유지'])
    qa = dict(schemaVersion=5, slug=P.name, revision=REVISION, updatedAt=now,
        status='current-visual-and-integrity-checks-complete-exact-V4-audio-reused-human-listening-pending',
        integrity=rel(O / 'qa/integrity.json'), visualReuse=rel(H / 'visual-reuse-proof.json'),
        gizmoReview=rel(H / 'gizmo-review.json'), codeColorReview=rel(H / 'code-color-review.json'),
        movingReview=rel(H / 'moving-review.json'),
        audioReview=rel(H4 / 'audio-review.json'), audioReusedByExactAAC=True,
        retainedInputs=kept, outputs=integrity['outputs'],
        evidence={name: evidence(path) for name, path in (
            ('integrity', O / 'qa/integrity.json'), ('visualReuse', H / 'visual-reuse-proof.json'),
            ('gizmoReview', H / 'gizmo-review.json'), ('codeColorReview', H / 'code-color-review.json'),
            ('movingReview', H / 'moving-review.json'),
            ('audioReview', H4 / 'audio-review.json'))},
        humanWholeListening='pending', drive='pending V5 full-master upload', baselinePreserved=True)
    ledger = read(P / 'production/review-ledger.json')
    if ledger.get('currentOutput', {}).get('revision') != REVISION and ledger.get('currentOutput'):
        ledger.setdefault('previousOutputs', []).append(ledger['currentOutput'])
    ledger.update(updatedAt=now, currentOutput=qa, humanWholeListening='pending')
    plan = read(P / 'planning/production-plan.json')
    plan.update(revision=REVISION, updatedAt=now, status=STAGE)
    plan['selectedRevision'].update(id=REVISION, stage=STAGE,
        visualScope='Four tracked conceptual rotation guides; readable semantic code/text colors in15/25; exact V4 narration/audio/subtitle/timing retained.')
    plan['currentProduction'].update(integrity='production/local/revision-v5/qa/integrity.json',
        visualReuse='production/revision-v5/visual-reuse-proof.json',
        gizmoReview='production/revision-v5/gizmo-review.json',
        codeColorReview='production/revision-v5/code-color-review.json',
        movingReview='production/revision-v5/moving-review.json',
        finalAudioReview='production/revision-v4/audio-review.json', exactAudioReuse=True,
        retainedInputs=kept, humanWholeListening='pending complete V5 Drive review')
    checkpoint = read(P / 'production/checkpoint.json')
    checkpoint.update(updatedAt=now, revision=REVISION, revisionUnderWork=REVISION,
        stage=STAGE, runningJob=None,
        nextAction='Collect four current outputs, upload the same complete V5 captioned FHD60 master to restricted Drive, then wait for exact-version human review. No YouTube or next video.')
    checkpoint['currentMaster'].update(outputs=pair['outputs'], frames=93100,
        durationSeconds=93100 / 60, dimensions=[1920, 1080], fps=60,
        status='complete; four tracked gizmos and two code-color scenes reviewed; V4 audio reused exactly')
    checkpoint['delivery'].update(driveUploaded=False, pendingRevision=REVISION,
        pendingMasterSha256=pair['outputs']['captioned']['sha256'], humanReview='pending',
        youtubeBaselinePreserved=True)
    checkpoint['visualRevisionEvidence'] = qa['evidence']
    for path, value in ((P / 'project.json', project), (P / 'production/qa.json', qa),
                        (P / 'production/review-ledger.json', ledger),
                        (P / 'planning/production-plan.json', plan),
                        (P / 'production/checkpoint.json', checkpoint)):
        save(path, value)
    # Read each shared file immediately before its own write; mutate M04 only.
    selected()
    work = read(WORKLIST)
    row = next(x for x in work['rows'] if x['slug'] == P.name)
    require(row['id'] == 'M04', 'Wrong worklist row.')
    row.update(productionComplete=True, localMasterAvailable=True,
        productionStatus='V5 회전 기즈모·코드 색상 수정 완료 / 기존 음성·게임 원음 유지',
        reviewStatus='변경 화면·연결·FHD60 기술검수 완료 / 전체 청취·발음 검수 대기',
        humanApproval='현재 V5 전체 Drive 검수본 업로드 대기',
        platformStatus='V5 로컬 완성 · 이전 Drive와 비공개 YouTube 유지',
        executionStatus='V5 완성본 Drive 업로드 대기', latestRulesPassed=None)
    row['pendingDriveRevision'] = REVISION
    row['notes'] = 'V5는 네 회전 안내 기즈모와15·25 코드/설명 색상만 수정. 내레이션·게임 원음·한영 자막·시간 유지. 이전 Drive와 비공개 YouTube 보존; 사용자 검수와 전체 청취 대기.'
    work['updatedAt'] = now
    save(WORKLIST, work)
    control = selected()
    control['selectedDelivery'].update(revision=REVISION, stage=STAGE,
        masterSha256=pair['outputs']['captioned']['sha256'],
        userReview='pending exact V5 complete version', pendingDriveRevision=REVISION,
        youtubeUploadAuthorized=False)
    control['selectedDelivery'].pop('nextRevision', None)
    control['updatedAt'] = now
    save(CONTROL, control)
    subprocess.run([sys.executable, str(R / 'scripts/render-video-worklist.py')], cwd=R, check=True)
    print(f'{REVISION}: local registration complete; previous revision {previous_revision}; Drive upload and human review pending.')


if __name__ == '__main__':
    main()
