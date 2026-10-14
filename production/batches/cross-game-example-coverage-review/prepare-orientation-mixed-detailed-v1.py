"""Record the three remaining generic EX replacements; prepare static previews."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image,ImageDraw
from orientation_detailed_projected_subjects_v1 import frame_03b,frame_07b,frame_10b
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
LOCAL=ROOT/'shared/output/unpublished-teaching-clarity-revision/orientation/current34-mixed-detailed-preparation-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
assert not LOCAL.exists();LOCAL.mkdir(parents=True)
samples=[];rows=[];boards=[]
for sid,version,fn,frames in [('03b',1,frame_03b,[0,120,1270,1336,1402,1480,1600]),
                             ('07b',2,frame_07b,[742,830,944,1891,1960,2079]),
                             ('10b',1,frame_10b,[0,1428,1575,1720,1900])]:
 p=O/f'{sid}-observation-track-plan-v1.json';plan=read(p)
 statep=O/f'{sid}-tracked-render-execution-v{version}.json';state=read(statep)
 assert state['workerDead'] and state['actualOuterExitCode']==0
 assert sha(ROOT/state['output'])==state['outputSha256']
 replacement=[x for x in plan['segments'] if x['classification']=='explanation' and not x.get('freezeNative')]
 rows.append(dict(scene=sid,source=state['output'],sourceSha256=state['outputSha256'],originalExecution=rel(statep),originalExecutionSha256=sha(statep),plan=rel(p),planSha256=sha(p),frames=plan['frames'],replaceExplanationSegments=replacement,preserveOtherSegments=[x for x in plan['segments'] if x not in replacement]))
 for f in frames:
  fp=LOCAL/f'{sid}-f{f:04d}.png';fn(f).save(fp)
  samples.append(dict(scene=sid,frame=f,path=rel(fp),sha256=sha(fp)))
 for n in range(0,len(frames),3):
  board=Image.new('RGB',(1920,1140),'#f5f5f5');d=ImageDraw.Draw(board)
  for i,f in enumerate(frames[n:n+3]):
   im=Image.open(LOCAL/f'{sid}-f{f:04d}.png');im.thumbnail((960,540));x=i%2*960;y=i//2*570
   board.paste(im,(x,y));d.text((x+10,y+542),f'{sid} frame {f}',fill='black')
  bp=LOCAL/f'{sid}-board-{n//3+1:02d}.png';board.save(bp);boards.append(dict(path=rel(bp),sha256=sha(bp)))
samplep=O/'current34-detailed-explanations-sampled-direct-review-v1.json'
normalp=O/'current34-detailed-explanations-normal-direct-review-v1.json'
guidep=O/'current34-baseline-guides-direct-review-v1.json'
assert read(samplep)['all605SamplesDirectlyRead'] and read(normalp)['all17NormalStartEndObserved'] and read(guidep)['all562SamplesDirectlyRead']
out=O/'current34-mixed-detailed-subject-replacement-plan-v1.json';assert not out.exists()
save(out,dict(recordedAt=datetime.now(timezone.utc).isoformat(),reason='Final binding audit found generic bicycle/aircraft/landing-part illustrations in mixed03b/07b/10b. Replace only their existing explanation-model frames under the detailed-subject policy.',subjectPolicy='shared/publishing/illustrative-subject-detail-policy.json',subjectPolicySha256=sha(ROOT/'shared/publishing/illustrative-subject-detail-policy.json'),editableModule=rel(B/'orientation_detailed_projected_subjects_v1.py'),editableModuleSha256=sha(B/'orientation_detailed_projected_subjects_v1.py'),rows=rows,preparedSamples=samples,preparedBoards=boards,allStaticPreviewsDirectlyRead=False,gameplaySourceAcquisition=0,gameplayAnnotationRegeneration=0,originalPcmChanges=0,newTts=0,newAsr=0,newMix=0,newImageGit=0,unchangedFrameContract='Decode the reviewed prior encoded mixed video once. Pass all actual and frozen-prerequisite decoded RGB bytes unchanged to the new encoder; compare input SHA. New H264 compression is not claimed byte-identical to old encoded or decoded media.',geometryContract='Preserve original illustrative rotation curves, coordinate conventions, semantic colors, reveal times and scene frames. 03b bicycle moves upward during late flipped illustration to preserve the fixed-caption reserved area; no engine pose measurement.',detailRequirements={'03b':['helmet/face','articulated rider/hands/feet/clothing','open tubular frame/fork/handlebar','thick tires/rims/spokes','crank/chain/pedals'], '07b':['tapered hull/cockpit glass','swept wings/ailerons','tailplane/fin','paired engine nacelles/inlets'], '10b':['detailed aircraft','chamfered landing pad','mounting plate/bolts/pivots','actuator shaft/twin cylinders/hose']},sampled17Review=rel(samplep),sampled17ReviewSha256=sha(samplep),normal17Review=rel(normalp),normal17ReviewSha256=sha(normalp),guide8Review=rel(guidep),guide8ReviewSha256=sha(guidep),assemblyV2PreparedButHeld=True,final244CaptionPixelsApproved=False))
cp=read(O/'latest-checkpoint.json');cp.update(recordedAt=datetime.now(timezone.utc).isoformat(),stage='current34-detailed17-and-guides8-reviewed-mixed3-detail-preparation',detailed17SampleReview=rel(samplep),detailed17NormalReview=rel(normalp),baselineGuideReview=rel(guidep),mixedDetailedReplacementPlan=rel(out),activeOwnedWorkers=0,ownedJob=None,next='Review static detail previews; render one EX-only replacement batch from prior encoded03b/07b/10b, verify and inspect new EX pixels, then bind assemblyV3. No new TTS/ASR/mix.')
save(O/'latest-checkpoint.json',cp)
q=read(B/'queue.json');q['currentOrientationReview'].update(stage=cp['stage'],mixedDetailedReplacementPlan=rel(out),detailed17SampleReview=rel(samplep),detailed17NormalReview=rel(normalp),baselineGuideReview=rel(guidep),activeOwnedWorkers=0,ownedJob=None,next=cp['next']);save(B/'queue.json',q)
print(json.dumps(dict(previewSamples=len(samples),previewBoards=len(boards),replacementPlan=rel(out),renderStarted=False)))
