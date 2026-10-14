"""Record completed direct sample reviews and prepare the next CPU chapter."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, math, psutil
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
def proof(p): return {'path':rel(p),'sha256':sha(p)}
def write(p,j):
 assert not p.exists(),f'Preserve existing record: {p}'
 p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
gates={k:False for k in ['allFinalPixelsReviewed','allMovingPixelsReviewed','causalFlowApproved','finalMixedAsrApproved','wholeEpisode60to40Approved','qaApproved','collected','uploaded']}

# Twelve changed boards were viewed directly;169 matching image bytes inherit
# the historical complete216-image sample review, never a moving review.
comparisonPath=P/'upscaling-encoded-pixel-comparison-v15.json'
comparison=read(comparisonPath)
oldPath=P/'upscaling-encoded-direct-review-v13.json';old=read(oldPath)
currentPath=ROOT/'production/research/game-lighting-history/local/episode04-upscaling-encoded-v15/execution.json'
current=read(currentPath)
assert current['status']=='encoded-samples-ready' and comparison['changedImages']==47 and comparison['unchangedImages']==169
assert old['all216SamplesDirectlyRead'] and old['all55BoardsDirectlyRead']
for i in comparison['items']:
 assert sha(ROOT/i['currentPath'])==i['currentSha256']
 assert sha(ROOT/i['previousPath'])==i['previousSha256']
 assert i['byteIdenticalImage']==(i['currentSha256']==i['previousSha256'])
changed=[]
for b in comparison['boardsContainingChangedImages']:
 assert sha(ROOT/b['path'])==b['sha256']
 changed.append({**b,'directlyViewed':True,'reviewedAt':stamp()})
upReview=P/'upscaling-encoded-direct-review-v15.json'
write(upReview,{'reviewedAt':stamp(),'scope':'Current repaired chapter sample review; no continuous/final approval',
 'build':proof(P/'upscaling-chapter-review-build-v15.json'),'execution':proof(currentPath),
 'comparison':proof(comparisonPath),'historicalDirectRead':proof(oldPath),
 'changedImagesDirectlyRead':47,'changedBoardsDirectlyRead':changed,
 'byteIdenticalImagesCarriedFromDirectRead':169,'items':comparison['items'],
 'all216SamplesCoveredByDirectReadOrExactImageIdentity':True,'captionCuesReviewed':list(range(45,74)),
 'sampledCaptionClearanceApproved':True,'sourceConditionLabelApproved':True,
 'findings':['Literal50% input/Epic AA label present in before/native/held-analysis samples. Text fits and remains distinct from foreground/background labels.',
 'Captioned28-35 directly read: cue64 continues across the native-to-analysis boundary,65-67 max2lines bottom-center clear. No new surface label/caption collision.',
 'Red conditional wrong-history label absent5747 and visible5748 with cue66. Held analyses explicitly labelled; no claim of an induced ghosting experiment.',
 'All other169 PNG image bytes match the complete historical direct review; numerical examples and four separate measures retain their prior findings.'],
 **gates,'newGitImages':0,'humanWholeListening':'pending'})

nativePath=ROOT/'production/research/game-lighting-history/local/episode04-mobile-native-v16/execution.json'
native=read(nativePath);assert native['status']=='samples-ready' and len(native['samples'])==11
assert len(native['commands'])==11 and all(x['exitCode']==0 for x in native['commands'])
try:
 proc=psutil.Process(native['worker']['pid'])
 same=abs(proc.create_time()-native['worker']['createTime'])<.01
except psutil.NoSuchProcess: same=False
assert not same,'Extraction worker still alive'
boards=[]
for b in native['boards']:
 assert sha(ROOT/b['path'])==b['sha256']
 boards.append({**b,'directlyRead':True,'reviewedAt':stamp()})
mobileReview=P/'mobile-native-direct-review-v16.json'
write(mobileReview,{'reviewedAt':stamp(),'execution':proof(nativePath),'boards':boards,
 'all11SamplesDirectlyRead':True,'source':{'path':'production/research/game-lighting-history/local/episode04-native-v1/rivalry-mobile-2014.mp4','sha256':'7668158e1bda2defb6c180d75b1ce2ce5c45147a2ad877888200052e897e0d1f','url':'https://www.youtube.com/watch?v=X-tAZtbDZ8E'},
 'plannedLocalInterval':[8,25.75],
 'findings':['8s wide corridor with two armored figures,9-12s approach/face and metal surfaces under wall light,14-22s gestures and alternating camera positions,24s motion blur during pan,25.733s returns to the opposing figure. No presenter, desktop, title slide or other demo in these11 samples.',
 'Full-frame mobile engine demonstration, not proof of the later Unreal mobile deferred implementation or actual tile-memory transfers. Existing narration states that limitation explicitly.',
 'No invented engine counters, game-world measurements, frame-rate comparison or same-camera ON/OFF claim. Surface/lighting observation only. Final caption clearance and normal-speed continuous playback pending.'],
 'sampledNativeContentSuitable':True,'allMovingFramesReviewed':False,'finalEncodedPixelsReviewed':False,
 'workerEndedObserved':True,'workerIdentity':native['worker'],'sessionId':None,'sessionIdUnavailable':True,
 'unifiedExecExitObserved':False,'all11RecordedChildExitCodesZero':True,'newGitImages':0})
sessionPath=nativePath.with_name('session.json')
if not sessionPath.exists():
 write(sessionPath,{'observedAt':stamp(),'sessionId':None,'sessionIdUnavailable':True,
 'worker':native['worker'],'workerEndedObserved':True,'executionStatus':native['status'],
 'allRecordedChildExitCodesZero':True,'unifiedExecExitObserved':False,
 'note':'Original orchestrator output omitted session metadata. No invented session or overall exit code; worker identity absence and11 recorded child exits observed.'})

selectionPath=P/'clean-source-selection-v8.json';selection=read(selectionPath)
assemblyPath=P/'additive-unmixed-review-assembly-v2.json';assembly=read(assemblyPath)
captionPath=P/'local/caption-word-draft-v2.json';caption=read(captionPath)
entries=[e for e in assembly['entries'] if e['start']>=328.55 and e['end']<=547.69]
assert len(entries)==15 and entries[0]['id']=='original-18a-1' and entries[-1]['id']=='original-18m-6'
start=327.84;end=547.68;roundFrame=lambda t:math.floor(t*60+.5)
firstFrame=roundFrame(start);lastFrame=roundFrame(end);N=lastFrame-firstFrame
assert(firstFrame,lastFrame,N)==(19670,32861,13191)
byId={s['id']:s for s in selection['selected']}
previous=read(P/'upscaling-chapter-review-build-v15.json')['outputs'][0]
cuts=[]
def add(id,a,b,kind,**kwargs):
 gf,gt=roundFrame(a),roundFrame(b)
 c={'id':id,'from':round(a-start,9),'to':round(b-start,9),'fromFrame':gf-firstFrame,'toFrame':gt-firstFrame,
    'globalFromFrame':gf,'globalToFrame':gt,'frames':gt-gf,'kind':kind,**kwargs}
 assert c['frames']>0
 if cuts: assert cuts[-1]['toFrame']==c['fromFrame']
 cuts.append(c)
add('preserved-original-silent-boundary',start,entries[0]['start'],'explanation',
    path=previous['path'],sha256=previous['sha256'],sourceStart=(previous['frames']-1)/60,
    freezeFrameOnly=True,reason='Original0.72s PCM silence; held last upscaling frame is explanation')
for i,e in enumerate(entries):
 if i and e['start']>entries[i-1]['end']+.00001:
  m=byId[entries[i-1]['id']]
  add('preserved-visibility-mobile-silence',entries[i-1]['end'],e['start'],'explanation',
      path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=(m['mediaSpanFrames'][1]-1)/60,
      freezeFrameOnly=True,shiftUpPixels=60,reason='Original0.72s PCM silence; held model frame not action')
 if e['id']=='09-guide-mobile-limits':
  add(e['id'],e['start'],e['end'],'actual',entryId=e['id'],**read(mobileReview)['source'],
      sourceStart=8,sourceEnd=25.75,normalSpeed=True,loop=False,slowdown=False,sourceAudio=False,
      label='Rivalry · 공식 모바일 엔진 시연 · 2014',
      secondaryLabel='완성 화면 관찰 · 타일 메모리 왕복 횟수는 측정하지 않음',
      sourceSampleReview=proof(mobileReview),allMovingFramesReviewed=False)
 else:
  m=byId[e['id']];span=m['mediaSpanFrames']
  assert m['sourceSamplePixelsApproved']
  f=roundFrame(e['end'])-roundFrame(e['start']);assert abs(f-m['frames'])<=1
  add(e['id'],e['start'],e['end'],'explanation',entryId=e['id'],
      path=m['media']['path'],sha256=m['media']['sha256'],sourceStart=span[0]/60,sourceSpanFrames=span,
      sourceSampleReview=m['sourceSampleReview'],verification=m['verification'],shiftUpPixels=60,
      padRoundingAtMostOneFrame=True,completeModelMeaningRetained=True)
assert len(cuts)==17 and cuts[-1]['toFrame']==N
ids={e['id'] for e in entries};cues=[]
for c in caption['cues']:
 if c['entryId'] not in ids: continue
 f,t=round(c['from']-start,9),round(c['to']-start,9)
 cues.append({'id':c['id'],'entryId':c['entryId'],'text':c['text'],'from':f,'to':t,
              'firstFrame':math.ceil(f*60-1e-7),'exclusiveEndFrame':math.ceil(t*60-1e-7),
              'sourceGlobalSeconds':[c['from'],c['to']],'encodedPixelsReviewed':False})
assert [c['id'] for c in cues]==list(range(74,124)) and len(cues)==50
audio={**assembly['audio'],'firstSample':round(start*24000),'exclusiveEndSample':round(end*24000),
       'samplesInChapter':round((end-start)*24000),'secondsInChapter':round(end-start,9)}
assert(audio['firstSample'],audio['exclusiveEndSample'],audio['samplesInChapter'])==(7868160,13144320,5276160)
actual=sum(c['frames'] for c in cuts if c['kind']=='actual')
plan={'preparedAt':stamp(),'scope':'Visibility buffer and mobile chapter review pair; original15 KO/EN paragraphs and PCM; final episode allocation pending',
 'selection':proof(selectionPath),'assembly':proof(assemblyPath),'captionDraft':proof(captionPath),'nativeReview':proof(mobileReview),
 'audio':audio,'entries':entries,'cuts':cuts,'cues':cues,
 'totals':{'frames':N,'globalFromFrame':firstFrame,'globalToFrame':lastFrame,'videoSeconds':N/60,
           'pcmSeconds':audio['secondsInChapter'],'roundingErrorFrames':N-audio['secondsInChapter']*60,
           'actualFrames':actual,'explanationFrames':N-actual,'body60to40Approved':False},
 'causalPlan':['Recall G-buffer contents, then compare identity storage and later reconstruction.',
 'Triangle7 attributes/interpolation → explicitly new equal-perspective small UV example → derivatives/mip at triangle boundaries.',
 'Reduced attribute bandwidth introduces geometry/reconstruction cost; layout/cache/MSAA conditions decide the tradeoff.',
 'Stored data/responsibility comparison → independent question of tiled hardware memory location; forward/deferred order is not Forward+ or hardware tile storage.',
 'Two independent choices → same-tile producer/consumer avoids a possible round trip → supported Unreal paths and platform conditions.',
 '2014 mobile engine visual example observes camera/surfaces only; no proof of later mobile deferred or internal transfers → API/pass constraints → transparent forward path → coexistence rather than universal winner.'],
 'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'fontSize':48,'maxLines':2,
 'sourceModelsRerendered':0,'newTts':0,'newGitImages':0,**gates,'humanWholeListening':'pending',
 'next':'SingleCPU2 clean/captioned chapter build; full decode/PTS/identicalAAC; all50 encoded cues/cuts direct sample review. Whole episode allocation/mix/continuous review remains pending.'}
planPath=P/'mobile-chapter-review-plan-v16.json';write(planPath,plan)
cp=ROOT/'production/research/game-lighting-history/checkpoint.json';j=read(cp)
j['episode04UpscalingSampleReviewV15']={'path':rel(upReview),'sha256':sha(upReview),'sampledCaptionClearanceApproved':True,'sourceConditionLabelApproved':True,**gates}
j['episode04MobileNativeV16']={'execution':rel(nativePath),'directReview':rel(mobileReview),'status':'samples-directly-read','workerEndedObserved':True,'allMovingFramesReviewed':False}
j['episode04MobileChapterV16']={'plan':rel(planPath),'status':'prepared-only','frames':N,'pcmSeconds':audio['secondsInChapter'],**gates}
j['ownedActiveWork']={'status':'no-active-owned-media-worker','next':plan['next']};j['updatedAt']=stamp()
tmp=cp.with_suffix('.mobile-v16.tmp');tmp.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(cp)
print(json.dumps({'plan':rel(planPath),'cuts':len(cuts),'entries':len(entries),'cues':len(cues),'frames':N,'actualFrames':actual,'newMediaCreated':0,'finalApproved':False}))
