"""Checkpoint inspected partial repairs without declaring blocked masters ready."""
import datetime
from polish_common import *

now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for ident in ['M11','M12','M17']:
 e=Episode(ident);e.authorized()
 composition=read(e.H/'composition-polish.json');preflight=read(e.H/'observed-guide-preflight.json')
 assert preflight['status']=='passed-still-preflight'
 assert composition['planSha256']==sha(R/composition['plan'])==preflight['planSha256']
 assert composition['globalAssSha256']==sha(R/composition['globalAss'])==preflight['assSha256']
 clearance=read(e.H/'observed-ui-clearance.json')
 for sid,item in composition['inputs'].items():
  assert item['sha256']==sha(R/item['path'])==clearance[sid]['sha256']
  assert clearance[sid]['source']['sourceSha256']==sha(e.O/f'clips/{sid}.mp4')
  e.verify(R/item['path'],next(s['frames'] for s in e.T['scenes'] if s['id']==sid))
 composition['partialPreflightEvidence']={'status':'registered-current-inputs-after-limited-preflight','checkedAt':now,
  'stillReview':rel(e.H/'observed-guide-preflight.json'),'stillReviewSha256':sha(e.H/'observed-guide-preflight.json'),
  'movingReview':rel(e.H/'moving-available-guide-preflight.json'),'movingReviewSha256':sha(e.H/'moving-available-guide-preflight.json'),
  'scope':'Same verified scale/pad and ASS as inspected partial previews; encoded full master QA remains pending. No human approval.'}
 save(e.H/'composition-polish.json',composition)

e=Episode('M10');e.authorized();path=e.H/'village-source-review.json';v=read(path)
assert len(v['samples'])==102 and sha(R/v['source'])==v['sourceSha256']
for frame in v['samples']:assert sha(R/frame['image'])==frame['sha256']
v.update(status='source-stills-inspected-exact-cue-selection-pending',reviewedAt=now,
 directInspection='All102 one-second states on9 sheets inspected for228–308s and391–411s. Wooden posts, fence rails and bridges are present; conversation and grappling interrupt the village walk. No continuous motion review or final adoption yet.',
 observedWindows=[{'seconds':[243,248],'visible':'Wooden fence near seated figures'},
  {'seconds':[259,265],'visible':'Wooden bridge crossing and turn'},
  {'seconds':[266,281],'visible':'Wooden columns, cloth stall and hut/bridge views; some static conversation'},
  {'seconds':[392,399],'visible':'Hut and fence walk'},
  {'seconds':[403,407],'visible':'Raised timber hut from varying angles; grapple action overlaps'}],
 remaining='Match the same structure across viewpoint changes during the preserved opening19.79s and choose an exact3781-frame scene without unrelated conversation/action padding.',
 cutApproved=False,fullMasterReady=False)
save(path,v)
catalog=read(B/'fhd-candidate-catalog.json');c=catalog['oU__wsOyeiY'];acq=read(B/'fhd-candidate-acquisition.json')['oU__wsOyeiY']
c['selectionStatus']='decoded-FHD-and-source-stills-inspected-await-exact-cut-review'
c['decodedFormat']={k:acq[k] for k in ['width','height','fps','duration','sha256']}
c['requiredAction']='M10 scene19: same wooden village structure viewed from different angles, matched to unchanged narration; no inferred world bounds.'
c['fineReview']={'report':rel(B/'oU__wsOyeiY-candidate-samples.json'),'sampleCount':154,'sheets':13,
 'observed':'All154 five-second source states on13 sheets inspected; village woodwork present but many dialogue/travel intervals. No full continuous playback claim.',
 'denseReview':rel(path),'denseReviewSha256':sha(path),'cutApproved':False}
save(B/'fhd-candidate-catalog.json',catalog)
sample=read(B/'oU__wsOyeiY-candidate-samples.json');sample.update(reviewStatus='all-generated-five-second-stills-inspected',reviewedAt=now,cutApproved=False,denseReview=rel(path));save(B/'oU__wsOyeiY-candidate-samples.json',sample)

blockers=read(B/'source-blockers.json')
for ident in ['M10','M11','M12','M17']:blockers[ident]['updatedAt']=now
blockers['M10'].update(shortStatus='마을 FHD 확보 · 대사별 컷 선정 중',candidateEvidence=rel(path),
 specificGap='Portal2 genuine FHD source still unresolved. New Uncle village recording is decoded1080p60 and154+102 still states inspected; exact same-structure viewpoint cue mapping is not yet adopted.')
for ident,sid in [('M11','08'),('M12','14')]:
 ep=Episode(ident);blockers[ident].update(shortStatus='새 장면 표식 점검 완료 · 나머지 FHD 확보 중',
  specificGap=f'Uncle scene{sid} replacement and guide/caption partial preflight completed; current UI-clearance inputs registered. Remaining Portal2 FHD sources and full encoded-master QA pending.',
  compositionEvidence=rel(ep.H/'composition-polish.json'))
blockers['M17'].update(shortStatus='회전·확대 대사 대응 수정 · 나머지 FHD 확보 중',
 additionalCueGap='Resolved in scene14 using original-source647–727s and735–757.6s; retained6156frames. Limited captioned still/playback preflight passed, complete master review pending.',
 cameraCueRepairReview='projects/game-math-camera-projection/production/private-polish-v1/camera-cue-repair-review.json')
save(B/'source-blockers.json',blockers)
p=read(B/'checkpoint.json');p.update(updatedAt=now,stage='eleven-ready-five-remaining-fhd-and-full-master-qa',active=[],currentJobs=[],
 nextAction='Select M10 scene19 same-structure village viewpoint cuts from inspected FHD source; continue unresolved Portal2 FHD actions. Current M11/M12/M17 guides/UI-clearance are registered. Preserve eleven ready masters and unchanged narration/timelines; full masters require all source replacements and final QA.')
p['sourceReplacementDecision']['summaryKo']='11편 검수대기 유지. 나머지5편 설명 보강·검수 완료, FHD 게임 장면18개 복원. M11·M12 새 장면 표식 사전 점검 및 M17 회전·확대 대사 대응 수정 완료. M10 마을 FHD는 확보·화면 확인 후 컷 선정 중. 나머지 FHD·전체 합성 검수 미완료.'
p['cueGuideRepair'].update(reviewedAt=now,M11='Scene08 new-source glyph/endpoint guides:30 captioned states and selected playback start/end observed; current UI-clearance registered.',
 M12='Scene14 mapped glyph/endpoint guides:31 captioned states and selected playback start/end observed; current UI-clearance registered.',
 M17='Scene14 orbit/zoom cue repair adopted without timeline/audio changes:103 source states,33 dense target states and33 composited states; selected playback start/end observed. UI-clearance registered.',additionalFullMasters=0)
p['candidateAcquisition']['latestCandidate']={'id':'oU__wsOyeiY','status':'FHD-acquired-stills-inspected-cuts-not-adopted','review':rel(path),'activeWorker':False}
p['latestStatusReport']={'at':now,'ready':11,'incomplete':5,'restoredFhdSlotsWithinIncompleteEpisodes':18,'activeMediaWorkerObserved':False,'pendingNewWholeMasters':True}
save(B/'checkpoint.json',p)
w=read(R/'shared/publishing/video-worklist.json')
for key in ['sourceReplacementDecision','partialFhdRestoration','cueGuideRepair']:
 w['privateMathPolish'][key]=p[key]
w['privateMathPolish']['updatedAt']=now
save(R/'shared/publishing/video-worklist.json',w)
print('Current partial evidence and checkpoint recorded;11 ready,5 incomplete; no additional full-master approval.')
