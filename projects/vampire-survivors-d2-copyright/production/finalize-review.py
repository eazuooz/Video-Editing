import os
"""Bind the inspected local delivery to its current masters, without publishing."""
from pathlib import Path
import datetime, hashlib, json

R = Path(__file__).resolve().parents[3]
P = R / 'projects/vampire-survivors-d2-copyright'
L = P / ('production/' + os.environ.get('YAMYAM_D2_LOCAL','local'))
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

def rd(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def wr(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()

control = rd(R / 'shared/publishing/video-production-control.json')
assert control['selectedVideo'] == P.name
assert control['newProductionAuthorization']['fullProductionAuthorized']
plan = rd(P / 'production/edit-plan.json')
integrity = rd(P / 'production/output-integrity.json')
assert integrity['status'] == 'passed'
masters = rd(P / 'production/master-files.json')
for kind in ('clean', 'captioned'):
    assert masters[kind]['sha256'] == sha(L / f'final.{kind}.mp4')
    assert next(x for x in integrity['outputs'] if f'.{kind}.' in x['path'])['sha256'] == masters[kind]['sha256']
pixels = rd(P / 'production/caption-pixel-audit.json')
assert pixels['masterSha256'] == masters['captioned']['sha256']
direct = rd(P / 'production/visual-direct-review.json')
assert direct['masterSha256'] == masters['captioned']['sha256']
assert direct['status'] == 'passed-scoped-direct-pixel-and-motion-review'
asr = rd(L / 'whole-final-mix-comparison.json')
assert asr['directReview'].startswith('complete-whole')
if L.name == 'local-ai-copyright-v2':
    assert rd(L/'whole-current-source-native-comparison.json')['directReview'].startswith('complete-whole')
audio = rd(P / 'production/final-audio.json')
assert audio['status'] == 'passed-current-encoded-audio-levels-and-continuity'

masters.update(status='local-full-version-ready-for-human-final-review', updatedAt=now,
               humanReview='pending', uploadAuthorized=False)
wr(P / 'production/master-files.json', masters)
pixels.update(status=f"passed-all{len(rd(L/'timing.json')['cues'])}-encoded-cue-pixels-and-scoped-direct-review",
              directReview='production/visual-direct-review.json', humanListening='pending')
wr(P / 'production/caption-pixel-audit.json', pixels)

ledger = rd(P / 'production/review-ledger.json')
current_checks = [
    {'id': 'full-source-and-current-mix-text', 'status': 'pass-text-and-order',
     'evidence': ['production/audio-review.json', f'production/{L.name}/whole-source-asr-aligned.json',
                  f'production/{L.name}/whole-final-mix-comparison.json'],
     'note': 'Both complete recognized texts directly read. Alias/phonetic ambiguities recorded; human pronunciation remains pending.'},
    {'id': 'local-narration-levels', 'status': 'pass-measured-continuity-and-speech-masking',
     'evidence': ['production/audio-review.json', 'production/final-audio.json'],
     'note': 'Corrected quiet static peak cap and chest-game masking; preserved source PCM. No human whole-listening claim.'},
    {'id': 'full-output-integrity', 'status': 'pass', 'evidence': 'production/output-integrity.json'},
    {'id': 'captions-scenes-and-annotations', 'status': 'pass-scoped-direct-review',
     'evidence': ['production/caption-pixel-audit.json', 'production/visual-direct-review.json']},
    {'id': 'ratio-and-source-geometry', 'status': 'pass', 'bodyFrames': plan['bodyFrames'],
     'actualFrames': plan['actualFrames'], 'explanationFrames': plan['explanationFrames'],
     'evidence': 'production/edit-plan.json', 'sourceMinimum': 'decoded1920x1080/60; native crop/aspect retained'},
    {'id': 'publishing-drafts-only', 'status': 'prepared-not-uploaded', 'evidence': 'publishing/plan.json',
     'note': 'Complete verified sources at absolute bottom of KO/EN descriptions. No platform write.'},
]
current_ids = {x['id'] for x in current_checks}
ledger['checks'] = [x for x in ledger['checks'] if x['id'] not in current_ids] + current_checks
if L.name == 'local-ai-copyright-v2':
    ledger['selectedRevision']='ai-copyright-awareness-v2'
    ledger['priorVersionPreserved']='production/revision-ai-copyright-v2/baseline/production/review-ledger.json'
    ledger['revisionVoiceEvidence']=[f'production/{L.name}/pcm-splice-map.json',f'production/{L.name}/whole-current-source-native-comparison.json']
ledger.update(updatedAt=now, humanWholeListening='pending', humanFinalReview='pending',
              localMaster=masters['captioned'], uploadAuthorized=False,
              reviewBoundary='Complete local captioned MP4 and four-file folder; wait for actual human review of this SHA256.')
wr(P / 'production/review-ledger.json', ledger)

manifest = rd(P / 'project.json')
titles = rd(P / 'publishing/plan.json')['selectedTitle']
manifest['titles'] = {k: titles[k] for k in ('ko', 'en')}
manifest['status'] = 'local-full-version-ready-for-human-final-review'
manifest['video']['durationSeconds'] = plan['totalFrames'] / 60
base = L.relative_to(R).as_posix() + '/'
manifest['paths'].update(videoClean=base+'final.clean.mp4', videoBurnedCaptions=base+'final.captioned.mp4',
                         captionsKo=base+'final.ko.srt', captionsEn=base+'final.en.srt',
                         timeline=P.relative_to(R).as_posix()+'/production/edit-plan.json')
manifest['tts']['status'] = ('11changed-paragraphs-sampleB;49unchanged-source-paragraphs-bit-identical;complete-source-and-mix-asr-reviewed' if L.name=='local-ai-copyright-v2' else 'one-continuous-own-voice-sampleB-take; complete-text-and-level-review-recorded')
manifest['delivery']['captionedMasterSha256']=masters['captioned']['sha256']
manifest['membershipOutro']['appliedToFinal'] = True
manifest['finalRender'] = {'status': 'complete-local-review-version', 'internalTechnicalChecks': 'passed',
                         'visualReview': 'production/visual-direct-review.json', 'knownIssues': [],
                         'openItems': ['최종 사람 청취·발음·음량과 전체 영상 검수는 사용자 확인 대기입니다.'],
                         'masterSha256': masters['captioned']['sha256']}
manifest['publishReady'] = False
wr(P / 'project.json', manifest)

design = rd(P / 'planning/production-plan.json')
design['realizedDelivery'] = {'status': manifest['status'], 'masterSha256': masters['captioned']['sha256'],
                            'durationSeconds': plan['totalFrames']/60,
                            'editPlan': 'production/edit-plan.json', 'reviewLedger': 'production/review-ledger.json',
                            'humanFinalReview': 'pending', 'youtubeUploaded': False, 'automaticNextVideo': False}
wr(P / 'planning/production-plan.json', design)
wr(P / 'production/checkpoint.json', {
    'schemaVersion': 1, 'slug': P.name, 'updatedAt': now, 'stage': 'local-final-review-delivery',
    'status': 'complete-awaiting-human-review', 'jobs': [], 'blockers': [],
    'nextAction': 'Deliver complete local captioned MP4 and four-file output folder; await human review. No upload or next video.',
    'captionedMasterSha256': masters['captioned']['sha256'],
    'humanWholeListening': 'pending', 'humanFinalReview': 'pending', 'automaticNextVideo': False,
})

worklist = rd(R / 'shared/publishing/video-worklist.json')
row = next(x for x in worklist['rows'] if x['id'] == 'S02')
assert row['slug'] == P.name
row.update(title=titles['ko'], productionComplete=True, productionStatus='1080p60 전체 검수본·한영 자막 완성',
           reviewStatus='전체 영상·발음·음량 사용자 최종 검수 대기', humanApproval='미검수',
           platformStatus='미업로드', latestRulesPassed=None,
           executionStatus='로컬 전체 완성본 전달 / 사용자 검수 대기', localMasterAvailable=True,
           notes=f"약{int(plan['totalFrames']/3600)}분{round(plan['totalFrames']/60)%60}초 · 실제60:설명40 · 내 목소리 ElevenLabs B. AI 개발·저작권 확인 관점 수정, 기존49문단 PCM 보존. 사용자 승인 전 업로드 없음.")
for evidence in ['projects/'+P.name+'/production/master-files.json', 'projects/'+P.name+'/production/review-ledger.json']:
    if evidence not in row['evidence']:
        row['evidence'].append(evidence)
worklist['updatedAt'] = now
wr(R / 'shared/publishing/video-worklist.json', worklist)
print('Bound current masters, reviewed evidence and S02 worklist; human review pending.')
