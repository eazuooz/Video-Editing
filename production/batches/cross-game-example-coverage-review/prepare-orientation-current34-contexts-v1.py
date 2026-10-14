"""Prepare paragraph diagnostics from the current AAC; no automatic content approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
out=O/'current34-mixed-independent-context-proposal-v1.json'
assert not out.exists()
whole=rd(O/'current34-mixed-whole-asr-execution-v1.json')
assert whole['exitCode']==whole['actualOuterExitCode']==0 and whole['workerDead']
assert whole['completed']==whole['total']==34
mix=rd(O/'current34-mix-execution-v2.json');plan=rd(O/'current34-measured-timing-plan-v1.json')
source=ROOT/mix['decodedAac'];source_sha=sha(source);assert source_sha==mix['decodedAacSha256']==whole['decodedAacSha256']
scripts={lang:{s['id']:s['lines'] for s in rd(O/f'script/current34-combined-v1.{lang}.json')['scenes']} for lang in ['ko','en']}
baseline={s['id']:s for s in rd(ROOT/plan['sourceBaselineTimeline'])['scenes']}
old={}
for name in ['additions-independent-context-plan-v1.json','cross-game-independent-context-plan-v2.json']:
 for row in rd(O/name)['contexts']:
  sid=row['sceneId']
  if sid not in old:old[sid]=row['boundaryEvidence']
spans={s['id']:sorted([v for v in plan['voicePlacements'] if v['scene']==s['id']],key=lambda v:v['sourceStartSample']) for s in plan['scenes']}
def mapped(sid,n):
 # Both images are retained at an exact allocation junction. Their average is
 # the intentional quiet observation gap, not an interpolated speech timestamp.
 images=[(v['destinationStartSample']+n-v['sourceStartSample'])*2 for v in spans[sid] if v['sourceStartSample']<=n<=v['sourceEndSample']]
 assert images,(sid,n)
 return round(sum(images)/len(images)),images
contexts=[];boundaries=[]
with wave.open(str(source),'rb') as aac:
 assert (aac.getframerate(),aac.getnchannels(),aac.getsampwidth())==(48000,2,2)
 for s in plan['scenes']:
  sid=s['id'];ko=scripts['ko'][sid];en=scripts['en'][sid]
  wp=O/f'current34-mixed-whole-asr-v1/{sid}.json';wr=rd(wp);assert wr['exactSourceStereoPcmBytesMatched'] and wr['expectedKo']==ko
  original=ROOT/s['voice'];assert sha(original)==s['voiceSha256']
  with wave.open(str(original),'rb') as w:
   assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
   raw=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)
  first=mapped(sid,0)[0];last=mapped(sid,len(raw))[0]
  core=[first];reasons=[];sourcecuts=[]
  if sid in baseline:
   b=baseline[sid];assert len(b['cues'])==len(ko)
   # Existing paragraph cue junctions include the original observation pauses.
   # Keep a midpoint between the prior cue end and next cue start, rather than
   # assigning a raw insertion seam to a sentence which can span that seam.
   for prev,nxt in zip(b['cues'],b['cues'][1:]):
    nominal=(prev['end']+nxt['start'])/2
    core.append(first+round(nominal*48000));sourcecuts.append(None)
    reasons.append('Retained original distributed paragraph cue junction including existing observation gaps; current-word and PCM comparison required before independent execution.')
  else:
   cuts=[r['boundarySample'] for r in old.get(sid,[])]
   if sid=='21a':cuts=[129840,278160]
   assert len(cuts)==len(ko)-1,(sid,cuts,len(ko))
   for n in cuts:
    c,images=mapped(sid,n);core.append(c);sourcecuts.append(n)
    reasons.append('Exact approved source diagnostic boundary mapped through current PCM placements. Both timeline images of an observation seam retained; splice21a uses candidate quiet gap and byte-preserved subsequent paragraph.')
  core.append(last);assert len(core)==len(ko)+1 and all(a<b for a,b in zip(core,core[1:])),sid
  for i,n in enumerate(core[1:-1],1):
   local=(n-first)/48000
   near=[dict(text=v['text'],start=v['timestamp'][0]-.3,end=None if v['timestamp'][1] is None else v['timestamp'][1]-.3) for v in wr['words'] if v['timestamp'][0]-.3<local+.75 and (v['timestamp'][1] is None or v['timestamp'][1]-.3>local-.75)]
   aac.setpos(n-192);data=np.frombuffer(aac.readframes(384),dtype='<i2').astype(float)
   sn=sourcecuts[i-1];energy=None
   if sn is not None:
    window=raw[max(0,sn-96):min(len(raw),sn+96)]
    energy=dict(sourceBoundarySample24k=sn,source8msRms=float(np.sqrt(np.mean(window**2))),source8msPeak=float(np.max(np.abs(window))),timelineImages=mapped(sid,sn)[1])
   boundaries.append(dict(scene=sid,afterParagraph=i,currentAacBoundarySample=n,currentTimelineLocalSeconds=local,current8msRms=float(np.sqrt(np.mean(data**2))),current8msPeak=float(np.max(np.abs(data))),previousExpected=ko[i-1],followingExpected=ko[i],nearbyCurrentWholeWords=near,sourceEvidence=energy,reason=reasons[i-1],directlyReviewed=False,exactPhoneticBoundaryApproved=False))
  for i,(a,b) in enumerate(zip(core,core[1:]),1):
   # Small disclosed overlap protects a full ending/start around approximate
   # recognizer junctions. Adjacent edge words are diagnostic context, not a
   # fabricated repeat. The non-overlapping core covers every current voice byte.
   overlap=7200
   start=max(first,a-(overlap if i>1 else 0));end=min(last,b+(overlap if i<len(ko) else 0))
   contexts.append(dict(id=f'{sid}-p{i:02d}',scene=sid,paragraph=i,sourcePath=rel(source),sourceSha256=source_sha,startSample=start,endSample=end,coreStartSample=a,coreEndSample=b,boundaryContextOverlapSamples=overlap,zeroPaddingSamplesEachSide=14400,expectedKo=ko[i-1],expectedEn=en[i-1],originalPcmPath=rel(original),originalPcmSha256=s['voiceSha256'],wholeResult=rel(wp),wholeResultSha256=sha(wp),expectedWasRecognizerPrompt=False,completeParagraphDiagnostic=True,boundaryScope='Complete current-AAC paragraph plus disclosed150ms adjoining context;300ms zero padding. Not exact caption or human pronunciation approval.'))
assert len(contexts)==180 and len(boundaries)==146
assert sha(source)==source_sha
value=dict(preparedAt=datetime.now(timezone.utc).isoformat(),sourcePath=rel(source),sourceSha256=source_sha,mixAacSha256=mix['mixAacSha256'],wholeExecution=rel(O/'current34-mixed-whole-asr-execution-v1.json'),wholeExecutionSha256=sha(O/'current34-mixed-whole-asr-execution-v1.json'),contexts=contexts,boundaries=boundaries,contextCount=180,boundaryCount=146,currentWholeWordsAndPcmBoundariesDirectlyCompared=False,all34WholeTextsDirectlyCompared=False,modelExecuted=False,currentMixedAudioApproved=False,humanListeningApproved=False,humanPronunciationApproved=False,finalCaptionTimingApproved=False)
out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(contexts=180,boundaries=146,preparedOnly=True,modelRun=False)))
