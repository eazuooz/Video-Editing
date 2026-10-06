from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules';MC=ROOT/'motion-canvas/src/projects/familiar-game-rules'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
plan=read(MC/'timed-white-reel-plan-v1.json');res=read(PROOF/'resource-observation-v31.json')
assert res['ownHeavyJobs']==0 and res['cpuLoadPercent']<85
assert (datetime.now(timezone.utc)-datetime.fromisoformat(res['observedAt'].replace('Z','+00:00'))).total_seconds()<240
notes=['01 overview: three games and promised roles in correct order; depth/arrow labels clear.',
       '03 grammar: input role, expected action and new decision clear; no measured learning result claim.',
       '05 remapping: A/B jump connection and combined-action check clear; actual settings claim excluded.',
       '14 umbrella: movement/tool state/attack direction separate; actual key bindings not inferred.',
       '07 device: press/release, continuous direction and function comparison clear; generic input comparison.',
       '17 body/target: moving body marker path and two target arrows have distinct roles.',
       '09 alternatives: direct/cycle/assist are hypothetical design choices; no existing Pedro feature claim.',
       '11 checklist: promise/connection/function clear. UI1262 corrected to1263 before rendering.']
dest=PROOF/'timed-white-input-preview-direct-review-v1.json';assert not dest.exists()
proof=dict(schemaVersion=1,slug='familiar-game-rules',reviewedAt=now,method='CUA browser preview at each independent scene75percent',
           planSha256=sha(MC/'timed-white-reel-plan-v1.json'),diagramHelperSha256=sha(MC/'timed-white-diagram-v1.tsx'),
           notes=[dict(id=r['id'],frames=r['frames'],directStillRead=True,note=n) for r,n in zip(plan['rows'],notes)],
           recalculatedFrames=[1460,1479,1580,149,1416,156,1637,1263],totalFrames=9140,
           all8StationaryPreviewsDirectlyRead=True,allEncodedCuePixelsReviewed=False,completeAnimationsReviewed=False,
           finalVideoApproved=False,productionGatesOpened=False,newGitImages=0,sourceMotionAndWordAlignment='pending')
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
state=dict(status='prepared-CUA-start-single-silent-white-input-render',resourceObservation='production/batches/sakurai-planning-game-design/proof-familiar-game-rules/resource-observation-v31.json',
           pid=None,actualEncoderCommandObserved=False,vitePid=7356,viteSession=8992,port=9224,cpuThreads=2,gpuRenderJobs=1,
           expectedFrames=9140,whiteScenes=8,output='shared/output/motion-canvas/familiar-game-rules-timed-white-v1.mp4',
           log='projects/familiar-game-rules/production/timed-white-exporter-v1.jsonl',
           previewReview=str(dest.relative_to(ROOT)).replace('\\','/'),allFinalCaptionPixelsReviewed=False,finalVideoApproved=False)
(PROOF/'timed-white-input-render-execution-v1.json').write_text(json.dumps(state,indent=2)+'\n','utf-8')
server=read(PROOF/'browser-word-action-review-server-v1.json');server.update(sessionId=48108,alive=True)
for path in [BASE/'latest-checkpoint.json',PROOF/'latest-checkpoint.json']:
    j=read(path);j.update(updatedAt=now,browserReviewServer=server,timedWhiteInputRender=state,
                        wordActionSourceCandidate='projects/familiar-game-rules/production/word-action-source-candidate-v3.json',
                        stage='single-timed-white-input-render-and-source-motion-review-pending',
                        nextAction='Complete8 silent-white inputs and full decode/encoded diagram cue review; independently finish all78 source/action words, reject new boss internal-cut transition if unsuitable. Final mix/ASR/pair/QA/collection/private remain false.')
    path.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
path=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(path);item=next(x for x in q['items'] if x['slug']=='familiar-game-rules')
item.update(browserReviewServer=server,timedWhiteInputRender=state,wordActionSourceCandidate='projects/familiar-game-rules/production/word-action-source-candidate-v3.json',stage='single-timed-white-input-render-and-source-motion-review-pending')
q['updatedAt']=now;path.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(previews=8,totalFrames=9140,productionGatesOpened=False,encoderNotYetStarted=True)))
