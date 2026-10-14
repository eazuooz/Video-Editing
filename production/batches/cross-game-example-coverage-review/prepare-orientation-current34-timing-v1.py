"""Measured34-scene timeline and exact preserved PCM placement plan, not a final approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave,os
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,x):
 assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
def pcm(p):
 with wave.open(str(p),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
  return w.readframes(w.getnframes())
protected=read(O/'narration-07b-guide-repair-execution-v1.json')
for x in protected['protectedInputs']+protected['results']:assert sha(ROOT/x['path'])==x['sha256']
base=read(ROOT/'projects/game-math-orientation-matrices/production/timeline.json')
ko=read(ROOT/'projects/game-math-orientation-matrices/script/narration.ko.json');en=read(ROOT/'projects/game-math-orientation-matrices/script/narration.en.json')
ak=read(O/'script/additions.ko.json');ae=read(O/'script/additions.en.json')
ck=read(O/'script/cross-game-additions.current-guide-v1.ko.json');ce=read(O/'script/cross-game-additions.current-guide-v1.en.json')
scripts={lang:{x['id']:x for x in a['scenes']+c['scenes']+b['scenes']} for lang,a,c,b in [('ko',ak,ck,ko),('en',ae,ce,en)]}
rawbase=pcm(ROOT/'shared/output/game-math-orientation-matrices/narration-final.wav')
manim=read(O/'measured-manim-timing-v2.json');mr=read(O/'measured-manim-sampled-direct-review-v2.json')
assert mr['all181EncodedSamplesAnd34BoardsDirectlyRead']
pieces={};voices={};baselineproof=[]
for s in base['scenes']:
 p=ROOT/s['voice'];assert sha(p)==s['voiceSha256'];raw=pcm(p);n=len(raw)//2
 placements=[];cursor=0;dest=0
 for gap in s.get('observationPauses',[]):
  boundary=gap['rawSample'];assert cursor<boundary<n
  placements.append(dict(sourceStartSample=cursor,sourceEndSample=boundary,sceneStartSample=dest))
  dest+=boundary-cursor+gap['silenceSamples'];cursor=boundary
 placements.append(dict(sourceStartSample=cursor,sourceEndSample=n,sceneStartSample=dest))
 placed=bytearray(s['frames']*400*2)
 for row in placements:
  a=row['sourceStartSample'];b=row['sourceEndSample'];d=row['sceneStartSample'];assert d+b-a<=s['frames']*400
  placed[d*2:(d+b-a)*2]=raw[a*2:b*2]
 originalStart=round(s['start']*24000)
 assert bytes(placed)==rawbase[originalStart*2:(originalStart+s['frames']*400)*2],s['id']
 visual=next((x for x in mr['rows'] if x['id']==s['id']),None)
 pieces[s['id']]=dict(id=s['id'],frames=s['frames'],actualFrames=s['frames'] if s['classification']=='actual' else 0,explanationFrames=s['frames'] if s['classification']=='explanation' else 0,baseline=True,
  visual=None if visual is None else visual['output'],visualSha256=None if visual is None else visual['outputSha256'],originalSceneFramesPreserved=True,baselineFinalAnnotationsPending=s['classification']=='actual',baselineOriginalSlot=dict(start=s['start'],frames=s['frames']))
 voices[s['id']]=dict(path=s['voice'],sha256=s['voiceSha256'],samples=n,placements=placements)
 baselineproof.append(dict(id=s['id'],rawPcmSha256=hashlib.sha256(raw).hexdigest(),distributedPcmSha256=hashlib.sha256(placed).hexdigest(),exactBaselineDistributedBytesMatched=True,observationPauses=s.get('observationPauses',[])))
for s in manim['scenes']:
 if s['id'] in ['12','18']:continue
 id=s['id'];v=ROOT/s['voicePath'];raw=pcm(v);assert sha(v)==s['voiceSha256'];n=len(raw)//2
 r=next(x for x in mr['rows'] if x['id']==id);assert sha(ROOT/r['output'])==r['outputSha256']
 encoded=int(r['probe']['streams'][0]['nb_frames']);assert s['frames']-encoded==1
 pieces[id]=dict(id=id,frames=s['frames'],actualFrames=0,explanationFrames=s['frames'],baseline=False,visual=r['output'],visualSha256=r['outputSha256'],encodedFrames=encoded,explanationRoundingTailFrames=1,tailReason='One frame completes measured voice ceiling; not actual-footage quota.',finalPixelApproved=False)
 voices[id]=dict(path=s['voicePath'],sha256=s['voiceSha256'],samples=n,placements=[dict(sourceStartSample=0,sourceEndSample=n,sceneStartSample=0)])
for id,version in [('02a',1),('03b',1),('07b',2),('10b',1)]:
 plan=read(O/f'{id}-observation-track-plan-v1.json');render=read(O/f'{id}-tracked-render-execution-v{version}.json')
 assert render['actualOuterExitCode']==0 and render['workerDead'] and sha(ROOT/render['output'])==render['outputSha256']
 review=O/f'{id}-tracked-normal-playback-direct-review-v{version}.json';assert read(review)['normalRateEndpointPlaybackVerified']
 frames=plan.get('frames',plan.get('sceneFrames'));classification=plan.get('classification',{});actual=classification.get('actualFrames',frames);explanation=classification.get('explanationFrames',0)
 if id=='02a':actual=frames;explanation=0
 pieces[id]=dict(id=id,frames=frames,actualFrames=actual,explanationFrames=explanation,baseline=False,visual=render['output'],visualSha256=render['outputSha256'],segments=plan.get('segments',[]),normalReview=rel(review),finalPixelApproved=False)
 v=plan['voice'];raw=pcm(ROOT/v['path']);assert len(raw)//2==v['samples'] and sha(ROOT/v['path'])==v['sha256']
 voices[id]=dict(path=v['path'],sha256=v['sha256'],samples=v['samples'],placements=plan.get('voicePlacement',[dict(sourceStartSample=0,sourceEndSample=v['samples'],sceneStartSample=0)]))
ext=read(O/'02aext-tracked-render-execution-v1.json');extreview=O/'02aext-tracked-normal-playback-direct-review-v1.json'
assert ext['workerDead'] and ext['actualOuterExitCode']==0 and read(extreview)['normalRateEndpointPlaybackVerified'] and sha(ROOT/ext['output'])==ext['outputSha256']
pieces['02a']['continuedObservation']=dict(frames=486,visual=ext['output'],visualSha256=ext['outputSha256'],nativeIn=3960,nativeOutExclusive=4446,normalReview=rel(extreview),classification='actual')
pieces['02a']['frames']+=486;pieces['02a']['actualFrames']+=486
v=ROOT/'shared/output/narration/game-math-orientation-matrices/cross-game-repair-batch-v1/chunks/01b-scene.wav';raw=pcm(v);n=len(raw)//2;assert n==144000
voices['01b']=dict(path=rel(v),sha256=sha(v),samples=n,placements=[dict(sourceStartSample=0,sourceEndSample=n,sceneStartSample=0)])
pieces['01b']=dict(id='01b',frames=360,actualFrames=0,explanationFrames=360,baseline=False,visual=None,projectedOverviewRenderPending=True,finalPixelApproved=False)
before={'02':['01b','02a'],'06':['06a'],'09':['09a'],'13':['13a'],'16':['16a'],'21':['21a']};after={'03':['03b'],'07':['07b'],'10':['10b']}
order=[]
for s in base['scenes']:order+=before.get(s['id'],[])+[s['id']]+after.get(s['id'],[])
assert len(order)==len(pieces)==len(voices)==34 and len(set(order))==34
scenes=[];placements=[];cursor=120;combined={lang:[] for lang in ['ko','en']}
for id in order:
 s=dict(pieces[id]);s.update(title=scripts['ko'][id]['title'],frameIn=cursor,frameOut=cursor+s['frames'],startSeconds=cursor/60,voice=voices[id]['path'],voiceSha256=voices[id]['sha256'],voiceSamples=voices[id]['samples'])
 for lang in ['ko','en']:combined[lang].append(scripts[lang][id])
 for v in voices[id]['placements']:
  p=dict(v,scene=id,voice=voices[id]['path'],sha256=voices[id]['sha256'],destinationStartSample=cursor*400+v['sceneStartSample']);placements.append(p)
 scenes.append(s);cursor+=s['frames']
body=cursor-120;actual=sum(s['actualFrames'] for s in scenes);ex=sum(s['explanationFrames'] for s in scenes)
assert actual+ex==body and abs(actual-body*.4)<=1 and (body,actual,ex)==(65197,26079,39118)
assert [s for s in order if s.isdigit()]==[s['id'] for s in base['scenes']]
for lang,baseline in [('ko',ko),('en',en)]:
 assert all(scripts[lang][s['id']]==s for s in baseline['scenes'])
 assert sum(len(x['lines']) for x in combined[lang])==180
 save(O/f'script/current34-combined-v1.{lang}.json',dict(title=baseline['title'],scenes=combined[lang],original24ScenesAnd140LinesPreserved=True,current10AdditionsAnd40LinesRetained=True,sourceOrder=order,status='measured-mix-and-final-pixel-review-pending'))
data=dict(preparedAt=datetime.now(timezone.utc).isoformat(),fps=60,sampleRate=24000,samplesPerFrame=400,scenes=scenes,voicePlacements=placements,voiceCount=34,sceneCount=34,sceneOrder=order,totalFrames=cursor+600,seconds=(cursor+600)/60,bodyFrames=body,actualFrames=actual,explanationFrames=ex,ratioErrorFrames=actual-body*.4,ratioContract='Legacy lecture actual40:explanation60; body only, one-frame rounding tolerance.',introFrames=120,outroFrames=600,noBgm=True,noSourceAudio=True,all24BaselineScenesAndPcmRetained=True,baselineDistributedPcmProof=baselineproof,current10AdditionsPcmAllSamplesMappedExactly=True,sourceBaselineTimeline=rel(ROOT/'projects/game-math-orientation-matrices/production/timeline.json'),sourceBaselineTimelineSha256=sha(ROOT/'projects/game-math-orientation-matrices/production/timeline.json'),baselineNarrationSha256=sha(ROOT/'shared/output/game-math-orientation-matrices/narration-final.wav'),baselineUnchangedRootProjectSha256=sha(ROOT/'projects/game-math-orientation-matrices/project.json'),currentMixedAudioApproved=False,finalRatioApproved=False,allFinalPixelsApproved=False,privateSaved=False,newImageGit=0)
for x in protected['protectedInputs']+protected['results']:assert sha(ROOT/x['path'])==x['sha256']
save(O/'current34-measured-timing-plan-v1.json',data)
print(json.dumps(dict(scenes=34,paragraphsEach=180,placements=len(placements),totalFrames=cursor+600,bodyFrames=body,actualFrames=actual,explanationFrames=ex,ratioErrorFrames=data['ratioErrorFrames'],baselineDistributedExact=24,preparedOnly=True)))
