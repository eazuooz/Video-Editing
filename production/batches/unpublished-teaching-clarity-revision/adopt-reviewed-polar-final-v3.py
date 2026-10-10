"""Adopt only directly reviewed final media; preserve baseline records first.

The script is prepared while review is pending. It never uploads or schedules.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/game-math-polar-3d'
OUT=PROJECT/'revision-teaching-clarity-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
now=datetime.now(timezone.utc).isoformat()
pair=read(OUT/'final-pair-execution-v3.json');assert pair['exitCode']==0 and pair['protectedBaselineUnchanged']
pixels=read(OUT/'final-pixel-direct-review-v2.json')
assert pixels['allListedSamplesDirectlyRead'] and pixels['allFinalCueCutPixelsApproved'] and not pixels['unresolved']
assert pixels['sourceSha256']==pair['pair'][1]['sha256']
flow=read(OUT/'final-flow-playback-direct-review-v3.json')
assert flow['wholeNormalSpeedPlaybackReachedEnd'] and flow['sampledContinuousFlowApproved'] and not flow['unresolved']
assert flow['sourceSha256']==pair['pair'][1]['sha256']
audio=read(OUT/'current-aac-complete-comparison-v2.json');assert audio['all44CompleteContextsDirectlyCompared']
assert pair['currentAudioComparisonPreservedByIdenticalAacAndPcm']
for v in pair['pair']:assert sha(ROOT/v['path'])==v['sha256'] and v['all54115Pts1500Verified'] and v['wholeDecodeExitCode']==0
snapshot=read(OUT/'baseline-protected-sha-v1.json')
assert all(sha(ROOT/v['path'])==v['sha256'] for v in snapshot['files'])
receipt=OUT/'final-media-adoption-v3.json';assert not receipt.exists()
history=OUT/'baseline-records-before-adoption-v1';history.mkdir(exist_ok=False)
names=['project.json','production/timeline.json','production/qa.json','production/delivery-output.json','sources/gameplay-cuts.json','sources/game-candidates.json','planning/outline.md','rebuild.json','publishing/youtube-upload.json']
saved=[]
for name in names:
    source=PROJECT/name;dest=history/name;dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,dest);assert sha(source)==sha(dest)
    saved.append({'original':rel(source),'preserved':rel(dest),'sha256':sha(dest)})
jobs=[{'scene':'02','globalStartFrame':1669,'frames':3403,'plan':rel(OUT/'scene02-editorial-annotations-v3.json')}]
jobs.extend(j for j in read(OUT/'six-moving-pilots-execution-v4.json')['jobs'] if j['scene'] not in ['11','16'])
jobs.extend(read(OUT/'minus-glyph-moving-pilots-execution-v5.json')['jobs']);jobs.sort(key=lambda j:j['globalStartFrame'])
assert sum(j['frames'] for j in jobs)==21358
plans={j['scene']:read(ROOT/j['plan']) for j in jobs}
manifest=read(PROJECT/'project.json')
manifest.update(status='teaching-clarity-revision-local-reviewed-private-settings-pending',publishReady=False)
manifest['paths'].update(videoClean=pair['pair'][0]['path'],videoBurnedCaptions=pair['pair'][1]['path'],renderReport=rel(PROJECT/'production/qa.json'),teachingClarityRevision=rel(receipt))
manifest['editing']['teachingClarityRevision']={'version':'on-footage-math-v3','scope':'user-authorized unpublished scheduled baseline revision',
 'baselineVideoId':'ZLOewk8JHXA','baselinePreserved':True,'baselineRecords':rel(history),
 'openingOverviewRetained':True,'wholeScriptOrderAndApprovedPcmRetained':True,'gameFootageReplacedOnlyWhereClarityNeeded':True,
 'annotationPlans':[j['plan'] for j in jobs],'sourceSelectionReview':rel(OUT/'whole-content-and-source-direct-review-v1.json'),
 'flowReview':rel(OUT/'causal-flow-and-primary-reference-review-v1.json'),'finalFlowReview':rel(OUT/'final-flow-playback-direct-review-v3.json'),
 'finalPixelReview':rel(OUT/'final-pixel-direct-review-v2.json'),'currentWholeAudioReview':rel(OUT/'current-aac-complete-comparison-v2.json'),
 'narratedRoleColorsAndLabels':True,'gameWorldNumbersMeasured':False,'meaning':'Projected relations and illustrative numeric models; never asserted as measured proprietary engine state.'}
manifest['finalRender'].update(status='teaching-clarity-revision-local-reviewed',qa=rel(PROJECT/'production/qa.json'),
 currentPair=rel(OUT/'final-pair-execution-v3.json'),currentWholeAudioAndPcmUnchanged=True)
manifest['approvals']['visualPixelReview']='current listed final cue/cut/annotation samples directly reviewed'
manifest['approvals']['privateUpload']='User-authorized reviewed private replacement; daily alternating09:00 scheduling only after new actual settings/Git verification.'
write(PROJECT/'project.json',manifest)
timeline=read(PROJECT/'production/timeline.json')
for sc in timeline['scenes']:
    if sc['id'] in plans:
        job=next(j for j in jobs if j['scene']==sc['id'])
        sc['teachingClarityRevision']={'annotationPlan':job['plan'],'annotationPlanSha256':sha(ROOT/job['plan']),
          'gameplayChanged':True,'approvedPcmChanged':False,'framesChanged':False,'currentFootageCuts':plans[sc['id']]['cuts']}
timeline['currentTeachingClarityPair']=rel(OUT/'final-pair-execution-v3.json');write(PROJECT/'production/timeline.json',timeline)
cuts=read(PROJECT/'sources/gameplay-cuts.json')
for cut in cuts['cuts']:
    sid=cut['scene'];plan=plans[sid]
    segments=[{'in':p['sourceInFrame']/60,'frames':p['frames'],'seconds':p['frames']/60,
      'nativeStartFrame':p['sourceInFrame'],'nativeEndFrameExclusive':p['sourceInFrame']+p['frames'],
      'nativeTimebase':'1/15360','nativeStartPts':p['sourceInFrame']*256,
      'nativeEndPtsExclusive':(p['sourceInFrame']+p['frames'])*256,'sceneStartFrame':p['sceneStartFrame']} for p in plan['cuts']]
    cut.update(in_=segments[0]['in'],segments=segments,sourceSegments=segments,maxSeconds=sum(v['frames'] for v in segments)/60,
      inspection='2026-10-10 first-viewer clarity comparison and exactnative/action pixels, then current moving annotations and final cue/cut coverage; original narration preserved.',
      annotationPlan=next(j['plan'] for j in jobs if j['scene']==sid),finalPixelReview=rel(OUT/'final-pixel-direct-review-v2.json'))
    cut['in']=cut.pop('in_')
cuts['currentRevisionReviewedAt']=now;cuts['currentRevisionApprovalScope']='Listed final cue/cut/annotation coverage; human listening and final public rights remain pending.'
write(PROJECT/'sources/gameplay-cuts.json',cuts)
candidates=read(PROJECT/'sources/game-candidates.json')
candidates['currentRevision']={'reviewedAt':now,'baselineSelectionRetainedAsHistory':True,
 'firstTimeViewerComparison':rel(OUT/'whole-content-and-source-direct-review-v1.json'),
 'selectedExactNativePlans':[j['plan'] for j in jobs],'finalMovingPixelEvidence':rel(OUT/'final-pixel-direct-review-v2.json'),
 'sourceReuseVsClarity':'Keep the coherent downhill bicycle example, replace unclear clips and use visible narrated relations. Different rides are explicitly announced; no repeated clips, slow motion or source audio.',
 'publicRightsApproved':False}
write(PROJECT/'sources/game-candidates.json',candidates)
outline=PROJECT/'planning/outline.md';text=outline.read_text(encoding='utf-8')
assert '2026-10-10 공개 전 이해도 수정' not in text
text+='\n## 2026-10-10 공개 전 이해도 수정\n\n원래25.2초 도입과19씬 설명 순서·승인PCM·한영206큐·화이트 설명은 보존했다. 같은 자전거 사례에서 높이와 수평 성분을 나눈 뒤, 방향/자세/카메라를 구별하고 실제 화면 위 색 선과 짧은 라벨로 계산의 의미를 짚는다. 다른 주행 발췌로 바뀌는 지점은 원래 해설과 별도 표시로 구분한다. 화면의 모델 값과 투영 관계를 게임 엔진의 실측 좌표로 주장하지 않는다.\n\n'
chain=read(OUT/'causal-flow-and-primary-reference-review-v1.json')['chapterChain']
for c in chain:text+=f"- {c['scene']}: {c['incomingQuestion']} → {c['reasonAndResult']}\n"
text+='\n새 도형은02/05/08/11/14/16/18의 독립 편집 계획에 유지한다. 첫 시청자 후보 비교,44완결음성문맥,현재 모든 자막/컷/도형 표본과 정상1배속 전체 재생의 근거는 revision-teaching-clarity-v1에 있다. 현재 본편실제21358/설명32037은 사용자 강의40:60 예외이며, 원본고양이120/회원600은 제외한다. 사람 청취·발음·공개권리는 계속 미완료다. 새 비공개 설정/Git/예약은 별도 실제 증거가 필요하다.\n'
outline.write_text(text,encoding='utf-8')
qa={'reviewedAt':now,'frames':54115,'seconds':54115/60,'fullDecodePassed':True,'videos':pair['pair'],
 'allPts1500Verified':True,'identicalReviewedWholeAacAndPcm':True,'measurement':pair['measurement'],
 'bodyFrames':53395,'actualFrames':21358,'explanationFrames':32037,'actualShare':0.4,'explanationShare':0.6,'ratioErrorFrames':0,
 'originalIntroFrames':120,'originalMembershipFrames':600,'captionCount':206,'captionCounts':{'ko':206,'en':206},
 'pixelEvidence':rel(OUT/'final-pixel-direct-review-v2.json'),'normalSpeedFlowEvidence':rel(OUT/'final-flow-playback-direct-review-v3.json'),
 'mixedAudioEvidence':rel(OUT/'current-aac-complete-comparison-v2.json'),'narrationChanged':False,
 'allListedFinalPixelsDirectlyReviewed':True,'humanListeningApproved':False,'pronunciationApproved':False,'publicRightsApproved':False,
 'currentUploadId':None,'privateSettingsVerified':False,'gitDelivered':False,'scheduled':False}
write(PROJECT/'production/qa.json',qa)
intended={rel(PROJECT/n) for n in ['project.json','production/timeline.json','sources/gameplay-cuts.json','sources/game-candidates.json']}
assert all(sha(ROOT/v['path'])==v['sha256'] for v in snapshot['files'] if v['path'] not in intended)
write(receipt,{'adoptedAt':now,'status':'reviewed-local-media-adopted-collection-private-git-schedule-pending',
 'baselineRecords':saved,'intentionallyChangedProtectedRecords':sorted(intended),'allOtherProtectedInputsUnchanged':True,
 'clean':pair['pair'][0],'captioned':pair['pair'][1],'narrationChanged':False,'humanListeningApproved':False,
 'publicRightsApproved':False,'uploaded':False,'gitDelivered':False,'scheduled':False,'actualId':None})
print(json.dumps({'reviewedLocalMediaAdopted':True,'frames':54115,'originalPcmPreserved':True,'collectionPending':True,'actualId':None}))
