"""Verify partial inputs and report restored slots without advancing whole-master QA."""
import datetime
from polish_common import *

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
counts = {'M09':5, 'M10':8, 'M11':3, 'M12':5, 'M17':3}
e = Episode('M09'); e.authorized()
composition = read(e.H/'composition-polish.json')
still = read(e.H/'observed-guide-preflight.json')
moving = read(e.H/'moving-available-guide-preflight.json')
clearance = read(e.H/'observed-ui-clearance.json')
assert len(composition['inputs']) == 17
assert still['status'] == 'passed-still-preflight'
assert composition['planSha256'] == still['planSha256'] == moving['planSha256'] == sha(R/composition['plan'])
assert composition['globalAssSha256'] == still['assSha256'] == moving['assSha256'] == sha(R/composition['globalAss'])
for kind in ['still', 'moving']:
    evidence = composition['partialPreflightEvidence']
    assert evidence[kind+'ReviewSha256'] == sha(R/evidence[kind+'Review'])
for sid, item in composition['inputs'].items():
    scene = next(s for s in e.T['scenes'] if s['id'] == sid)
    assert sha(R/item['path']) == item['sha256']
    e.verify(R/item['path'], scene['frames'])
    if scene['classification'] != 'explanation':
        assert item['sha256'] == clearance[sid]['sha256']
        assert clearance[sid]['source']['sourceSha256'] == sha(e.O/f'clips/{sid}.mp4')
for ident, count in counts.items():
    ep = Episode(ident)
    assert len(read(ep.H/'gameplay-restoration.json')['scenes']) == count

catalog = read(B/'fhd-candidate-catalog.json')
candidate = catalog['5u3sUKuncSU']
reviews = candidate['approvedCutReviews']
for sid in ['05','08','LG02','LG03']:
    path = e.H/f'uncle-remaining-source-review-{sid}.json'
    review = read(path)
    assert review['status'] == 'passed-source-cut-inspection'
    assert review['rawClipSha256'] == sha(e.O/f'clips/{sid}.mp4')
    reviews = [r for r in reviews if (r['episode'],r['scene']) != ('M09',sid)]
    reviews.append({'episode':'M09','scene':sid,'path':rel(path),'sha256':sha(path)})
candidate['approvedCutReviews'] = reviews
candidate['fineReview']['cutApprovalEvidence'] = reviews
save(B/'fhd-candidate-catalog.json', catalog)

archive = B/'portal-archive-mirror-review.json'
blockers = read(B/'source-blockers.json')
restoration = read(B/'gameplay-restoration-status.json')
for ident, count in counts.items():
    item = blockers[ident]
    item.update(updatedAt=now, availableOriginalFhdRestored=count)
    if rel(archive) not in item['evidence']: item['evidence'].append(rel(archive))
blockers['M09'].update(shortStatus='게임5/6·표식 점검 완료 · Portal2 FHD 확보 중',
    candidateEvidence=rel(e.H/'available-guides-review.json'),
    specificGap='All five Uncle action slots restored as exact-frame native FHD cuts and limited source/guide/caption preflight completed. Only LG01 Portal2 official-demo native FHD remains missing. Whole-master audiovisual QA remains pending.',
    compositionEvidence=rel(e.H/'composition-polish.json'))
restoration['M09'].update(annotationPolish='available-scenes-partial-preflight-passed-full-master-pending',
    availableGuideReview=rel(e.H/'available-guides-review.json'))
save(B/'source-blockers.json', blockers)
save(B/'gameplay-restoration-status.json', restoration)

p = read(B/'checkpoint.json')
p.update(updatedAt=now, stage='eleven-ready-five-remaining-fhd-and-full-master-qa', active=[], currentJobs=[],
    nextAction='Remaining missing actual slots across M09/M10/M11/M12/M17 are Portal2 official-demo actions requiring native FHD under preserved narration. New archive mirrors reviewed this turn also list720p, not adopted. Do not retry unchanged blocked/low-resolution sources or upscale. Preserve eleven ready masters and all reviewed explanation clips. Before any eventual assembly register reviewed explanation inputs for M11/M12/M17; complete full encoded-master QA only after source gaps close.')
p['sourceReplacementDecision']['summaryKo']='11편 검수대기 유지. 나머지5편 설명 보강·검수 완료, FHD 게임 장면24개 복원. M09의 네 장면을 추가 교체하여 게임5/6·표식 사전 점검 및 기존 설명12장면과의 합성 입력 등록 완료. 남은 Portal2 공식 데모 FHD 확보와 전체 완성본 검수는 미완료.'
p['partialFhdRestoration'].update(restoredSlots=24, episodes=counts, masterCountAdded=0,
    fullMastersReady=11, remainingEpisodes=5)
p['cueGuideRepair'].update(reviewedAt=now,
    M09='Five exact-frame FHD gameplay cuts available. Four new cuts:183 captioned source states and52 dense target states inspected; dark/reset candidate intervals rejected. Current29 composited states and43 additional encoded states inspected; five new selected browser playback windows start/end observed. Five UI-clearance clips plus12 existing reviewed geometry clips registered. LG01 source and full-master QA pending.',
    additionalFullMasters=0)
p['candidateAcquisition'].update(activeWorker=False,
    latestCandidate={'id':'5u3sUKuncSU','status':'M09-four-additional-reviewed-cuts-adopted-partial-composition-registered',
        'review':rel(e.H/'available-guides-review.json'),'activeWorker':False})
p['sourceIssues']['portalArchiveMirrors'] = {'report':rel(archive),'sha256':sha(archive),
    'result':'Gamersyde page offers720p with reupload limitations; three HLPortal Steam mirrors list1280x720. No source adopted. These pages are not proof that every possible source lacks native FHD.'}
p['latestStatusReport'] = {'at':now,'ready':11,'incomplete':5,
    'restoredFhdSlotsWithinIncompleteEpisodes':24,'activeMediaWorkerObserved':False,'pendingNewWholeMasters':True}
p['completedJobs'].append('M09 scenes05/08/LG02/LG03 FHD and source/guide limited preflight completed;17 current composition inputs verified.24 restored gameplay slots across five incomplete episodes.11 whole masters remain ready; no new human approval.')
save(B/'checkpoint.json', p)
w = read(R/'shared/publishing/video-worklist.json')
for key in ['sourceReplacementDecision','partialFhdRestoration','cueGuideRepair']:
    w['privateMathPolish'][key] = p[key]
w['privateMathPolish']['updatedAt'] = now
save(R/'shared/publishing/video-worklist.json', w)
print('Verified17 M09 inputs;24 restored FHD slots;11 ready,5 incomplete; no additional master approval.')
