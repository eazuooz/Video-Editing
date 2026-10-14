"""Record directly read51 scoped samples; do not approve moving/final pixels."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,psutil
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(R).as_posix();now=lambda:datetime.now(timezone.utc).isoformat()
def proof(p):return {'path':rel(p),'sha256':sha(p)}
def write(p,j):
 assert not p.exists(),p
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
refs=[]
for folder,ep,sid in [('episode04-hair-chapter-v30',P/'hair-chapter-review-execution-v30.json',28637),('episode04-hair-encoded-v30',R/'production/research/game-lighting-history/local/episode04-hair-encoded-v30/execution.json',53196)]:
 s=read(ep);w=s['worker'];assert s['active'] is None and all(c['exitCode']==0 for c in s['commands'])
 try:assert abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01,'Original worker still alive'
 except psutil.NoSuchProcess:pass
 dest=R/'production/research/game-lighting-history/local'/folder/'session.json'
 write(dest,{'sessionId':sid,'worker':w,'terminalCompletionObserved':True,'exitCode':0,'completedAt':s['endedAt'],'verifiedAt':now(),'execution':proof(ep),'originalWorkerAlive':False})
 refs.append(proof(dest))
b=P/'hair-chapter-review-build-v30.json';build=read(b)
for o in build['outputs']:assert sha(R/o['path'])==o['sha256']
assert build['identicalAacPayloadAndPtsAndDuration'] and build['reusedEncodedCuts']==11
ex=read(R/'production/research/game-lighting-history/local/episode04-hair-encoded-v30/execution.json');assert(len(ex['items']),len(ex['boards']))==(51,13)
boards=[]
for board in ex['boards']:
 assert sha(R/board['path'])==board['sha256']
 boards.append({**board,'directlyViewed':True,'reviewedAt':now()})
j={'reviewedAt':now(),'scope':'51 changed-cut/cue229 samples on13 boards directly read; unchanged11 clean encoded cuts reuse v29 sampled review. Captioned unaffected cues still require final encoded QA.','build':proof(b),'plan':build['plan'],'sessions':refs,'boards':boards,'sampleCount':51,'allPlannedScopedSamplesDirectlyViewed':True,'sampledAnnotationApproved':True,'sampledCaptionClearanceApproved':True,'rejected':False,'priorRejectedReview':proof(P/'hair-encoded-direct-review-v29.json'),'boundaryResolution':proof(P/'hair-clean-captioned-boundary-audit-v32.json'),'findings':['Yellow box now surrounds MelaninMainColor, cyan marks visibly changing strands in all selected native frames817–826.32s. Original editor value including negative input is observation only, not a physically valid prescription.','Cue229 keeps 영 점 오 together, exact spoken words/times preserved; alpha0.5 contributions .5/.25 retain order.','Original142.96s PCM and AAC preserved;11 clean encoded cuts reused byte-identically. Exact1920x1080 boundary reread plus v32 audit resolved the earlier apparent mismatch; no retiming required.'],'allFinalPixelsReviewed':False,'allMovingPixelsReviewed':False,'finalMixedAsrApproved':False,'wholeEpisode60to40Approved':False,'qaApproved':False,'uploaded':False,'newTts':0,'newGitImages':0}
dest=P/'hair-encoded-direct-review-v30.json';write(dest,j)
cp=R/'production/research/game-lighting-history/checkpoint.json';c=read(cp)
c['episode04HairEncodedDirectReviewV30']={**proof(dest),'sampleCount':51,'boards':13,'rejected':False,'allFinalPixelsReviewed':False}
c['ownedActiveWork']={'status':'no-active-owned-media-worker','next':'Remaining DLSS/postprocess/RenderDoc/conclusion review, then additive actual60:40 allocation and approximately20-minute conceptual deliveries; final moving/audio/upload gates remain false.'}
c['updatedAt']=now();tmp=cp.with_suffix('.hair-seal-v30.tmp');tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({'review':rel(dest),'scopedSamples':51,'boards':13,'movingFinalApproved':False}))
