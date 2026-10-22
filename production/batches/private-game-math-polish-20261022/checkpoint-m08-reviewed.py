"""Reconcile the completed M08 correction and the five remaining source gaps."""
import datetime
from polish_common import *

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
e = Episode('M08')
e.authorized()
assert read(e.H / 'visual-review.json')['status'] == 'passed'
cp = read(B / 'checkpoint.json')
cp.update(updatedAt=now, stage='eleven-ready-five-fhd-source-matching', active=[], currentJobs=[])
cp['deliverySummary'] = {
    'readyCount': 11, 'blockedCount': 5, 'productionCount': 0,
    'ready': cp['ready'], 'sourceBlocked': ['M09', 'M10', 'M11', 'M12', 'M17'],
    'production': [], 'humanReview': 'pending',
    'dashboard': 'output/private-game-math-polish/index.html', 'allSixteenComplete': False,
}
cp['sourceReplacementDecision'].update(
    summaryKo='M07·M08 FHD 교체·표식 보강·최종 QA 완료, 로컬 검수 대기. M09–M12/M17은 설명 보강·검수 완료. 같은 게임·동작 FHD 소스와 원래 발화의 대응 확인 중. 대본·음성·길이 유지.',
    status='M07-M08-ready-remaining-five-source-matching',
)
cp['nextAction'] = 'M09/M11/M12: continue exact unchanged narration-to-grapple/triangle cut matching using inspected FHD Uncle recording; reject M11 start325 and review alternative342. M10 village scene unresolved. M09–M12/M17 Portal2 sources require genuine FHD with matching action; known720p candidates rejected. No TTS/rewrite, upload, platform changes, duplicate jobs or work beyondM20.'
cp['finalCorrection'] = {
    'episode': 'M08', 'captionedMasterSha256': read(e.H / 'visual-review.json')['captionedSha256'],
    'technicalQa': rel(e.H / 'technical-qa.json'), 'visualQa': rel(e.H / 'visual-review.json'),
    'newDirectSamples': 122, 'hashIdenticalReusedSamples': 934,
    'status': 'ready-for-human-review', 'humanReview': 'pending',
}
save(B / 'checkpoint.json', cp)
w = read(R / 'shared/publishing/video-worklist.json')
w['privateMathPolish']['sourceReplacementDecision'] = cp['sourceReplacementDecision']
w['privateMathPolish']['updatedAt'] = now
save(R / 'shared/publishing/video-worklist.json', w)

research = read(B / 'fhd-remaining-research.json')
research['updatedAt'] = now
research['sourceRejections']['8h0XTRFGwOQ'] = 'Official EA Nordic Portal2 Pneumatic Diversity Vent upload: metadata maximum720p; rejected under native FHD rule. Evidence portal-fhd-format-search.json.'
research['exactCutReview'] = {
    'evidence': rel(B / 'uncle-triangle-cut-samples.json'),
    'status': '111 current candidate states inspected; no production-cut approval',
    'M11': 'Reject325s: triangle target absent initially and fall/reset later. Candidate342s needs exact cue/moving review.',
    'M12': '375s candidate includes grapple/triangular glyph/landing; exact narration and motion review pending.',
}
save(B / 'fhd-remaining-research.json', research)

blockers = read(B / 'source-blockers.json')
for ident, item in blockers.items():
    item['updatedAt'] = now
    for evidence in [rel(B / 'fhd-remaining-research.json'), rel(B / 'portal-fhd-format-search.json')]:
        if evidence not in item['evidence']:
            item['evidence'].append(evidence)
    item['explanationStatus'] = 'existing explanation scenes polished and internally reviewed; full master not ready'
    item['shortStatus'] = 'FHD 게임 장면 대응 확인 중'
    if ident in ['M09', 'M11', 'M12']:
        item['candidateEvidence'] = rel(B / 'uncle-triangle-cut-samples.json')
    if ident == 'M10':
        item['specificGap'] = 'Portal2 FHD preview and Uncle wooden-column village scene unresolved.'
    elif ident == 'M17':
        item['specificGap'] = 'Portal2 fixed-pillar viewpoint and cube/laser operation FHD scenes unresolved; Townscaper FHD available.'
    else:
        item['specificGap'] = 'Exact source-cut correspondence and Portal2 FHD preview actions unresolved; candidate approval not inferred.'
save(B / 'source-blockers.json', blockers)
print('Checkpoint: eleven ready, five still require FHD source matching.')
