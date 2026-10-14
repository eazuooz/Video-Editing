"""Record directly read boards; still samples never certify moving/final pixels."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, psutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def ref(p):return {'path':rel(p),'sha256':sha(p)}
def observed_worker(w):
 try:
  proc=psutil.Process(w['pid']);same=abs(proc.create_time()-w['createTime'])<.01
  return {'checkedAt':stamp(),'sameProcessAlive':same,'currentCommandLine':proc.cmdline(),'pidReuseObserved':not same}
 except psutil.NoSuchProcess:return {'checkedAt':stamp(),'sameProcessAlive':False,'pidReuseObserved':False}
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
v38path=ROOT/'production/research/game-lighting-history/local/episode04-inspection-encoded-v38/execution.json'
v42path=ROOT/'production/research/game-lighting-history/local/episode04-inspection-numeric-v42/execution.json'
old=read(v38path);new=read(v42path)
assert old['status']==new['status']=='encoded-samples-ready'
assert len(old['items'])==523 and len(old['boards'])==131
assert len(new['items'])==70 and len(new['boards'])==18
reviewpath=P/'inspection-encoded-sample-direct-review-v43.json'
assert not reviewpath.exists()
for record in [old,new]:
 for item in record['items']+record['boards']:
  assert sha(ROOT/item['path'])==item['sha256']
review={'reviewedAt':stamp(),'method':'All listed 2x2 local encoded boards directly read with view_image across the continuous review; full-resolution frames retained. No inferred moving approval.',
 'historicalV38':{'execution':ref(v38path),'all131BoardsDirectlyRead':True,'sampleCount':523,'cleanBoards':25,'captionedBoards':106,'boards':old['boards'],
  'rejectedCuts':['original-22r-5','original-22rb-6'],'rejection':ref(P/'inspection-numeric-math-rejection-v40.json')},
 'correctedV41ScopedV42':{'execution':ref(v42path),'build':ref(P/'inspection-chapter-review-build-v41.json'),'all18BoardsDirectlyRead':True,'sampleCount':70,'cleanBoards':5,'captionedBoards':13,'boards':new['boards'],'sampledNumericAndCaptionClearanceApproved':True},
 'findings':[
  {'scope':'guide24/RenderDoc','finding':'Observed draw/input/code source explicitly labelled our RenderDoc triangle inspection, not another game lighting-pass evidence. Red return input.color and teal COLOR input outlines do not obscure the sampled code/values or fixed captions.'},
  {'scope':'original-22r-5 corrected','finding':'Fixed d and 1-d heights retain their labelled values at .1/.25/.5/.75/.9, with opacity reveal only. near1/far100 finite mapping d=100/99-100/(99z); z1/2/10/100 gives d0/.505/.909/1 and reverse1/.495/.091/0. Zero values are flat top faces, not padded numeric bars.'},
  {'scope':'original-22r-6','finding':'Normal (0,0,1) maps to display(.5,.5,1), marked distinct from albedo; actual G-buffer packing requires engine documentation.'},
  {'scope':'original-22r-7/8','finding':'Projected light-space depth example and screen-information/fallback example remain explicit independent explanations, not unverified source-pass assertions.'},
  {'scope':'original-22rb volume','finding':'Two illustrative transparent-layer transmissions .8*.5=.4, spatial rays and boxes; not a claimed measured GPU diagram.'},
  {'scope':'original-22rb temporal','finding':'Previous/current object states, motion correspondence and depth/occlusion/history validity caveat remain legible with fixed bottom cues.'},
  {'scope':'original-22rb output/resource','finding':'HDR/reconstruction/display/UI planes marked as role connections rather than universal pipeline order; producer/shared-resource/consumer labels clear.'},
  {'scope':'original-22rb performance','finding':'Structural capture and normal-condition performance measurement separated. Role-only bars expressly not timing/GPU profiler reproduction.'},
  {'scope':'original-22rb-6 corrected','finding':'Six fixed zero-baseline 12px/ms bars8/10/9/11/8/10 revealed by opacity; N6 mean9.33ms range8-11ms. Preparation/loading/cache/camera and exclusion conditions retain their caution. New ms label is clear.'},
  {'scope':'conclusion all five entries','finding':'Coexisting brightness/bake/shadow/screen-grid/ray-cache/reconstruction roles, stored inputs and limits, calculation timing and final questions remain spatial/legible. Last cue374 through f20031 clear.'},
  {'scope':'captions/cut edges','finding':'All69 cues read first/middle/last/before/after using v38 plus changed v42 scopes. Bottom(960,970) white/forest box at most2 lines does not cover sample UI/formulas. ASS centisecond boundary rounding can retain one frame at a nominal after label; do not claim every after label is blank.'}
 ],
 'reuse':{'24UnchangedV41CutsReuseEncodedV38Bytes':True,'onlyTwoChangedNumericCutsReplaced':True,'approvedPcmPreserved':True,'chapterFrames':20032,'sameAacInReviewPair':True},
 'sourceAuthoringPreview':{'tab':39,'url':'http://127.0.0.1:9269/','playAtNormalSpeedObserved':True,'audioUnmutedObserved':True,'loopDisabledObserved':True,'observedStartFrame':2,'laterStatePausedAtFrame':0,'allMotionDirectlyReviewed':False,'scope':'Authoring preview, not encoded final movie approval'},
 'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False,'humanListeningApproved':False,'finalMixedAsrApproved':False,'bodyRatioApproved':False,'outputCollected':False,'uploaded':False,'newGitImages':0,
 'next':'Select and normally play additional relevant engine/game intervals; add independent KO/EN observation narration and physical-part openings/conclusions, then safe exclusive TTS and complete final QA/upload.'}
for group in [review['historicalV38'],review['correctedV41ScopedV42']]:
 for board in group['boards']:board['directlyViewed']=True
write(reviewpath,review)
for version,sessionid,execution,outputdir in [('v41',10894,P/'inspection-chapter-review-execution-v41.json',ROOT/'production/research/game-lighting-history/local/episode04-inspection-chapter-v41'),('v42',59679,v42path,ROOT/'production/research/game-lighting-history/local/episode04-inspection-numeric-v42')]:
 state=read(execution);obs=observed_worker(state['worker']);assert not obs['sameProcessAlive']
 write(outputdir/'session-v43.json',{'recordedAt':stamp(),'unifiedSession':sessionid,'reportedExitCode':0,'execution':ref(execution),'worker':state['worker'],'workerObservation':obs,'historicalActiveChildren':state.get('commands',[]),'restartRequired':False})
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j['episode04InspectionSampleReviewV43']={'record':ref(reviewpath),'historicalSamples':523,'correctedNumericSamples':70,'historicalBoards':131,'correctedBoards':18,'scopedCorrectedSampleClearance':True,'allMovingPixelsReviewed':False,'allFinalPixelsReviewed':False}
j['episode04InspectionChapterV41']['workerAlive']=False;j['episode04InspectionNumericExtractionV42']['workerAlive']=False
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':review['next']};j['updatedAt']=stamp();write(cp,j)
print(json.dumps({'review':rel(reviewpath),'sampledNumericAndCaptionClearance':True,'allMovingPixelsReviewed':False,'uploaded':False}))
