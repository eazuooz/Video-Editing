"""Seal directly read raw motion and literal text; retain all final gates."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, time
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing');t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
 for i in range(40):
  try:os.replace(t,p);return
  except OSError:
   if i==39:raise
   time.sleep(.15)
target=BASE/'white-motion-caption-text-direct-review-v1.json'
assert not target.exists(),'Preserve completed direct review'
statePath=BASE/'white-measured-verification-v1.json';state=read(statePath)
assert state['exitCode']==0 and state['sessionId']==14031 and state['uniqueSampleFrames']==128 and len(state['boards'])==22
assert sha(ROOT/state['currentWhite']['path'])==state['currentWhite']['sha256']
for b in state['boards']:
 assert sha(ROOT/b['path'])==b['sha256']
 for e in b['entries']:assert sha(ROOT/e['path'])==e['sha256']
notes={
 '01-overview':'Question cube changes height; arena, mining and shared-play spatial routes appear in the promised order. Projected top/front/side faces and thick floor remain readable.',
 '02-familiar-action':'Two arenas and separate actors show familiar avoidance routes; question token transfers to the new experience. Not a universal ranking.',
 '03-patterns-not-ranking':'Long blue range versus nearby green directions and pillar heights change during the matching paragraphs. No weapon strength or win inference.',
 '04-mining-route':'Blue avatar travels around occluding rocks toward flag and mineral; green mineral token moves. Goal versus path is spatial.',
 '05-route-under-pressure':'Destination and red nearby-danger actors remain separate; blue/green paths and question transfer explain the decision.',
 '16-ore-and-projectile':'Actor route and orange effects are independent directions, with depth and moving spatial relations.',
 '15-corridor-to-open':'Blue actor crosses the narrow bridge into a broader plane; front/side faces, pillars and green actor remain distinct.',
 '07-purpose-combination':'Lower movement/attack plane and elevated purpose/space plane connect through growing blue and green arrows; occlusion and height are explicit.',
 '08-world-and-route':'Blue and ochre floors retain similar routes around different blocks; actors traverse each route and question transfers between spaces.',
 '09-combination-in-motion':'Approach and arrival are spatially contrasted; blue actor reaches destination while red/green actors remain around the second destination. No victory proof.',
 '19-visible-destination':'Blue actor approaches tall destination while red nearby actor changes relationship; marker and floor depth readable. No escape/win drawn.',
 '24-destination-and-danger':'Actor routes around occluding blocks into destination circle while nearby red/green positions remain visible. Arrival does not erase danger or prove victory.',
 '10-playing-together':'Single focused actor versus independently placed actors on a shared floor; route arrows and question token move to the shared-space comparison.',
 '21-read-before-ranking':'Question moves through action, situation and reason-to-choose spatial bases with growing arrows; heights do not encode popularity.',
 '11-several-appeals':'Three different projected pillars rise; star transfers across them during p2 and p4 with arrows. Explicit note rejects measured score/popularity interpretation.',
 '12-check-your-reason':'Question travels action→situation→experience during p1; p4 return check adds dashed return path. Three bases have readable thickness and occlusion.',
 '13-conclusion':'Actor transfers familiar action→distinct situation→own experience through p2/p3; question transfers to experience during p4. Reflection tail remains readable.'
}
stamp=datetime.now(timezone.utc).isoformat()
proof=dict(schemaVersion=1,reviewedAt=stamp,slug='similar-game-design',plan=state['plan'],white=state['currentWhite'],worker=dict(pid=47032,createTime=1791490011.7195861,sessionId=14031,actualExitObserved=True,exitCode=0),guiCompletionObserved=True,encoderExitCodeObserved=False,all22BoardsDirectlyRead=True,uniqueFrames=128,whiteParts=19,boards=[dict(path=b['path'],sha256=b['sha256'],directlyRead=True,scenes=sorted({o['scene']for e in b['entries']for o in e['observations']}))for b in state['boards']],notes=notes,allAnimatedMeasuredPixelsReviewed=True,captionPixelsReviewed=False,allFinalPixelsReviewed=False,finalTimingApproved=False,finalMixedAsrApproved=False,render=False,qa=False,collected=False,uploaded=False,humanListening='pending',humanPronunciation='pending')
capPath=BASE/'caption-candidate-v2/captions.json';cap=read(capPath)
assert len(cap['ko'])==400 and len(cap['en'])==148 and len(cap['paragraphs'])==73 and len(cap['readabilityChanges'])==44
assert cap['previousCandidate']['allInitialCueTextsDirectlyRead']
norm=lambda s:''.join(s.split())
for lang in ['ko','en']:
 for p in cap['paragraphs']:assert norm(''.join(c[lang]for c in cap[lang]if(c['scene'],c['paragraph'])==(p['scene'],p['paragraph'])))==norm(p[lang])
proof['captionTextReview']=dict(path=rel(capPath),sha256=sha(capPath),prior437Ko155EnFullTextDirectlyRead=True,all44ChangedMergedTextsDirectlyRead=True,all73KoEnParagraphsDirectlyRead=True,currentKoCues=400,currentEnCues=148,allLiteralParagraphsPreserved=True,allSourceSpeechBoundariesPreserved=True,minimumKoSeconds=cap['minimumKoCueSeconds'],minimumEnSeconds=cap['minimumEnCueSeconds'],currentCueTimingPixelApproval=False)
save(target,proof)
state.update(status='closed-measured-white-motion-directly-reviewed',actualExitObserved=True,actualExitObservedAt=stamp,allAnimatedMeasuredPixelsReviewed=True,directReview=rel(target))
for b in state['boards']:b['directlyRead']=True
save(statePath,state)
prepPath=BASE/'measured-spatial-preparation-v1.json';prep=read(prepPath);prep.update(rendered=True,allAnimatedMeasuredPixelsReviewed=True,directReview=rel(target),renderVerification=rel(statePath));save(prepPath,prep)
cp=read(BASE/'latest-checkpoint.json');cp.update(stage='current24-measured73-white-motion-reviewed-caption-inputs-next',currentSceneCount=24,currentParagraphCount=73,currentRawPcmSeconds=605.5400833333334,whiteMotionDirectReview=rel(target),captionTextDirectReview=rel(target),nextAction='Compile current selected50 native/19 white inputs once; inspect actual fixed ASS on every cue/cut and measured white paragraph. Final timing/mix/pair/QA/private remain false.',updatedAt=stamp)
cp['ownedJob'].update(workerExpectedRunning=False,exitCode=0,actualExitObserved=True)
cp['motionCanvas'].update(actualAnimatedPixelsReviewed=True,allAnimatedMeasuredPixelsReviewed=True,finalMeasuredPixelsReviewed=False)
save(BASE/'latest-checkpoint.json',cp)
qp=ROOT/'production/batches/sakurai-planning-game-design/queue.json';q=read(qp);item=next(x for x in q['items']if x['slug']=='similar-game-design');item.update(stage=cp['stage'],whiteMotionDirectReview=rel(target),captionTextDirectReview=rel(target),currentExecution=cp['ownedJob'],nextAction=cp['nextAction'],updatedAt=stamp);q['updatedAt']=stamp;save(qp,q)
print(json.dumps(dict(whiteParts=19,boards=22,frames=128,koCues=400,enCues=148,rawMotionReviewed=True,finalGates=False)))
