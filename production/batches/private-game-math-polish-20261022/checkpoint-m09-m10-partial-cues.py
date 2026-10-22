"""Record two inspected FHD replacements; neither is a completed episode."""
import datetime
from polish_common import *

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
counts = {'M09': 1, 'M10': 8, 'M11': 3, 'M12': 5, 'M17': 3}
for ident in ['M09', 'M10']:
    e = Episode(ident)
    e.authorized()
    composition = read(e.H/'composition-polish.json')
    still = read(e.H/'observed-guide-preflight.json')
    moving = read(e.H/'moving-available-guide-preflight.json')
    clearance = read(e.H/'observed-ui-clearance.json')
    assert still['status'] == 'passed-still-preflight'
    assert composition['planSha256'] == still['planSha256'] == moving['planSha256'] == sha(R/composition['plan'])
    assert composition['globalAssSha256'] == still['assSha256'] == moving['assSha256'] == sha(R/composition['globalAss'])
    evidence = composition['partialPreflightEvidence']
    for kind in ['still', 'moving']:
        assert evidence[kind+'ReviewSha256'] == sha(R/evidence[kind+'Review'])
    for sid, item in composition['inputs'].items():
        scene = next(s for s in e.T['scenes'] if s['id'] == sid)
        assert item['sha256'] == sha(R/item['path'])
        e.verify(R/item['path'], scene['frames'])
        if scene['classification'] != 'explanation':
            assert item['sha256'] == clearance[sid]['sha256']
            assert clearance[sid]['source']['sourceSha256'] == sha(e.O/f'clips/{sid}.mp4')
    assert len(read(e.H/'gameplay-restoration.json')['scenes']) == counts[ident]

portal_path = B/'portal-official-page-format-review.json'
portal = read(portal_path)
for item in portal['items']:
    item['metadataSha256'] = sha(R/item['metadata'])
portal.update(status='official-linked-formats-checked-no-native-fhd',
              adopted=False, limitation='Five linked Valve uploads expose at most720p; not proof that every possible original archive lacks FHD. Do not retry unchanged failures or upscale these sources.')
save(portal_path, portal)

catalog = read(B/'fhd-candidate-catalog.json')
for source, adopted in [
    ('5u3sUKuncSU', [('M09', '02'), ('M11', '08'), ('M12', '14')]),
    ('oU__wsOyeiY', [('M10', '19')])
]:
    candidate = catalog[source]
    reviews = []
    for ident, sid in adopted:
        e = Episode(ident)
        path = e.H/('village-source-cut-review.json' if ident == 'M10' else 'uncle-source-cut-review.json')
        review = read(path)
        assert review['status'] == 'passed-source-cut-inspection'
        assert review['rawClipSha256'] == sha(e.O/f'clips/{sid}.mp4')
        reviews.append({'episode': ident, 'scene': sid, 'path': rel(path), 'sha256': sha(path)})
    candidate.update(selectionStatus='specific-reviewed-fhd-cuts-adopted-full-episodes-pending',
                     cutApproved=True, approvedCutReviews=reviews,
                     approvalScope='Only listed source cuts; not every source frame, whole master or human review.',
                     fullMasterApproval=False)
    candidate['fineReview']['cutApproved'] = True
    candidate['fineReview']['cutApprovalEvidence'] = reviews
save(B/'fhd-candidate-catalog.json', catalog)

blockers = read(B/'source-blockers.json')
restoration = read(B/'gameplay-restoration-status.json')
for ident, count in counts.items():
    e = Episode(ident)
    item = blockers[ident]
    item.update(updatedAt=now, availableOriginalFhdRestored=count,
                partialFhdReview=rel(e.H/'available-guides-review.json'),
                compositionEvidence=rel(e.H/'composition-polish.json'))
    if rel(portal_path) not in item['evidence']:
        item['evidence'].append(rel(portal_path))
    item['decision'].update(status='partial-replacements-adopted-remaining-source-matching',
        summaryKo='같은 게임·동작의 FHD 교체 승인에 따라 일부 장면 복원·표식 점검 완료. 대본·음성·순서·길이 보존. 나머지 소스와 전체 완성본 검수는 진행 중.')
    restoration[ident].update(annotationPolish='available-scenes-partial-preflight-passed-full-master-pending',
                             availableGuideReview=rel(e.H/'available-guides-review.json'))
blockers['M09'].update(shortStatus='손·바위 표식 점검 완료 · 나머지 FHD 대응 중',
    candidateEvidence=rel(Episode('M09').H/'uncle-source-cut-review.json'),
    specificGap='Scene02 V3 FHD cut and endpoint annotations adopted after rejecting the beam-absent V2 interval. Four further Uncle action slots and one Portal2 official-demo slot still need matched FHD; whole-master QA pending.')
blockers['M10'].update(shortStatus='마을 FHD·표식 점검 완료 · Portal2 소스 확보 중',
    candidateEvidence=rel(Episode('M10').H/'village-source-cut-review.json'),
    specificGap='All eight non-Portal gameplay slots restored, including3781-frame village scene19. Its visible timber contours/screen boxes and current UI-clearance passed partial preflight. LG05 Portal2 FHD official-demo action and full-master QA remain unresolved.')
save(B/'source-blockers.json', blockers)
save(B/'gameplay-restoration-status.json', restoration)

p = read(B/'checkpoint.json')
p.update(updatedAt=now, stage='eleven-ready-five-remaining-fhd-and-full-master-qa', active=[], currentJobs=[],
    nextAction='Match four remaining M09 Uncle action slots to unchanged speech using inspected native FHD; continue Portal2 original-demo FHD source search without repeating rejected720p sources. M09/M10 partial composition includes current UI-clearance and already reviewed geometry clips. Before eventual M11/M12/M17 assembly also verify their polished explanation inputs are registered. Preserve eleven ready masters; incomplete episodes still require all source replacements and complete encoded-master QA.')
p['sourceReplacementDecision']['summaryKo']='11편 검수대기 유지. 나머지5편 설명 보강·검수 완료, FHD 게임 장면20개 복원. M09 손·바위 연결과 M10 마을 목재 장면을 새로 교체하고 표식·자막 사전 점검 및 합성 입력 등록 완료. 나머지 게임 소스와 전체 합성 검수는 미완료.'
p['partialFhdRestoration'].update(restoredSlots=sum(counts.values()), episodes=counts,
    guideReviews={ident: rel(Episode(ident).H/'available-guides-review.json') for ident in counts},
    masterCountAdded=0, fullMastersReady=11, remainingEpisodes=5)
p['cueGuideRepair'].update(reviewedAt=now,
    M09='Scene02 V3:45 captioned source states,15 dense target states and7 current composited states inspected. Blue endpoint corrected after native-frame review; two selected playback windows start/end states observed. Twelve existing reviewed geometry clips and one FHD UI-clearance clip registered. Full master pending.',
    M10='Scene19:63 captioned source states and56 dense target states inspected. Seventy partial composition states:59 unchanged hashes reuse previous review,11 new states directly inspected. Two selected playback windows start/end observed. Eight FHD UI-clearance clips and16 reviewed geometry clips registered. Full master pending.',
    additionalFullMasters=0)
p['candidateAcquisition'].update(activeWorker=False,
    latestCandidate={'id':'oU__wsOyeiY','status':'scene19-reviewed-cut-adopted-partial-composition-registered',
        'review':rel(Episode('M10').H/'village-source-cut-review.json'),'activeWorker':False})
p['sourceIssues']['portalOfficialFhd'] = {'report':rel(portal_path), 'sha256':sha(portal_path),
    'result':'Five additional official-page-linked Valve uploads expose maximum720p; no FHD cut adopted. Narration-specific official-demo scenes must not be mislabeled retail footage.'}
p['latestStatusReport'] = {'at':now,'ready':11,'incomplete':5,
    'restoredFhdSlotsWithinIncompleteEpisodes':20,'activeMediaWorkerObserved':False,'pendingNewWholeMasters':True}
p['completedJobs'].append('M09scene02 and M10scene19 exact-frame FHD cut/guide partial reviews completed; current UI-clearance and reviewed geometry inputs registered.20 restored gameplay slots across five incomplete episodes.11 whole masters remain ready; no new human approval.')
save(B/'checkpoint.json', p)
w = read(R/'shared/publishing/video-worklist.json')
for key in ['sourceReplacementDecision','partialFhdRestoration','cueGuideRepair']:
    w['privateMathPolish'][key] = p[key]
w['privateMathPolish']['updatedAt'] = now
save(R/'shared/publishing/video-worklist.json', w)
print('Verified current partial inputs: M09=13, M10=24;20 restored FHD slots;11 ready,5 incomplete.')
