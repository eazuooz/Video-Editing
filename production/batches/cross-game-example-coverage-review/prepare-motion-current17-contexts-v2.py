"""Prepare complete current-AAC paragraph boundaries; direct review remains required."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
OLD=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=R/'current17-mixed-independent-context-plan-proposed-v2.json'
assert not out.exists(),'Never overwrite boundary evidence.'
whole=read(R/'current17-mixed-whole-asr-execution-v1.json')
closure=read(R/'current17-mixed-whole-asr-execution-v1.session.json')
assert whole['exitCode']==closure['actualOuterExitCode']==0 and not closure['workerCurrentlyAlive']
assert whole['completed']==whole['total']==17
plan=read(R/'measured-current17-plan-v1.json');mix=read(R/'current-mix-execution-v1.json')
assert whole['decodedAacSha256']==mix['decodedAacSha256']==sha(ROOT/mix['decodedAac'])
old=read(OLD/'current-mixed-independent-context-plan-v1.json')
ko={s['id']:s['lines'] for s in read(R/'script/additions.ko.json')['scenes']}
en={s['id']:s['lines'] for s in read(R/'script/additions.en.json')['scenes']}
contexts=[];boundaries=[]
for scene in plan['scenes']:
 sid=scene['id'];path=ROOT/scene['voice'];assert sha(path)==scene['audioSha256']
 with wave.open(str(path),'rb') as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(24000,1,2)
  pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)
 words=read(R/f'current17-mixed-whole-asr-v1/{sid}.json')['words']
 if scene['retainedBaseline']:
  rows=[v for v in old['contexts'] if v['scene']==sid]
  assert rows and all(v['originalPcmSha256']==scene['audioSha256'] for v in rows)
  cuts=[rows[0]['localStartSample24k']]+[v['localEndSample24k'] for v in rows]
  texts=[v['expectedKo'] for v in rows];english=[v['expectedEn'] for v in rows]
  mapped=[scene['startFrame']*800+c*2 for c in cuts]
  reasons=['Retained approved original PCM junction; current mixed whole words still need direct comparison.']*(len(cuts)-2)
 else:
  texts=ko[sid];english=en[sid]
  if sid=='07b':nominal=[8.32,17.66,26.28,34.56,42.33]
  elif sid=='08b':nominal=[8.68,17.32,25.70,32.60]
  else:
   nominal=[read(R/f'additions-diagnostic-contexts-v1/{sid}-p{i:02d}.json')['endSample']/24000 for i in range(1,4)]
  assert len(nominal)==len(texts)-1
  cuts=[0];reasons=[]
  for t in nominal:
   if sid in ['07b','08b']:
    # Do not move a cross-placement source junction into the next spoken word.
    # Exact allocation boundaries have both left/right timeline mappings; their
    # midpoint lies in the intentional observation gap when such a gap exists.
    cuts.append(round(t*24000));reasons.append('Exact approved source paragraph/allocation junction; retain both adjacent voice spans and bisect the actual observation gap, rather than shifting into the next placed voice.')
    continue
   a=max(96,round((t-.08)*24000));b=min(len(pcm)-96,round((t+.08)*24000))
   trials=[(float(np.sqrt(np.mean(pcm[n-96:n+96]**2))),n) for n in range(a,b,24)]
   rms,n=min(trials,key=lambda x:x[0]+abs(x[1]/24000-t)*15)
   cuts.append(n);reasons.append('Prepared quiet PCM junction within80ms of the source paragraph proposal; current mixed words and this boundary are not approved automatically.')
  cuts.append(len(pcm));mapped=[]
  spans=sorted(scene['voicePlacements'],key=lambda x:x['sourceStartSample'])
  for c in cuts:
   adjacent=[]
   for v in spans:
    if v['sourceStartSample']<=c<=v['sourceEndSample']:
     adjacent.append((v['destinationStartSample']+c-v['sourceStartSample'])*2)
   assert adjacent,(sid,c)
   # An exact source junction may straddle an intentional observation pause.
   # Both sides are silence at that junction; retain the intervening AAC bytes.
   mapped.append(round(sum(adjacent)/len(adjacent)))
 assert len(cuts)==len(texts)+1 and len(mapped)==len(cuts)
 for i,c in enumerate(cuts[1:-1],1):
  timeline=(mapped[i]-scene['startFrame']*800)/48000
  near=[dict(text=v['text'],start=v['timestamp'][0]-.3,end=None if v['timestamp'][1] is None else v['timestamp'][1]-.3) for v in words if v['timestamp'][0]-.3<timeline+.9 and (v['timestamp'][1] is None or v['timestamp'][1]-.3>timeline-.9)]
  boundaries.append(dict(scene=sid,afterParagraph=i,sourceSample24k=c,sourceSeconds=c/24000,currentTimelineLocalSeconds=timeline,currentAacBoundarySample=mapped[i],rms8ms=float(np.sqrt(np.mean(pcm[c-96:c+96]**2))),previousExpectedEnd=texts[i-1][-70:],followingExpectedStart=texts[i][:70],nearbyCurrentWholeWords=near,boundaryReason=reasons[i-1],directlyReviewed=False))
 for i,(a,b) in enumerate(zip(mapped,mapped[1:]),1):
  assert a<b and scene['startFrame']*800<=a<b<=scene['endFrame']*800
  contexts.append(dict(id=f'{sid}-p{i:02d}',scene=sid,paragraph=i,sourcePath=mix['decodedAac'],sourceSha256=mix['decodedAacSha256'],startSample=a,endSample=b,localStartSample24k=cuts[i-1],localEndSample24k=cuts[i],localStart=cuts[i-1]/24000,localEnd=cuts[i]/24000,originalPcmPath=scene['voice'],originalPcmSha256=scene['audioSha256'],zeroPaddingSamplesEachSide=14400,expectedKo=texts[i-1],expectedEn=english[i-1],independentCompleteSentence=True,boundaryReason='Complete current AAC paragraph with observation pauses retained; no audio removed and no expected recognition prompt.'))
assert len(contexts)==81 and len(boundaries)==64
value=dict(schemaVersion=2,preparedAt=datetime.now(timezone.utc).isoformat(),sourceSha256=mix['decodedAacSha256'],mixAacSha256=mix['mixAacSha256'],wholeExecutionSha256=sha(R/'current17-mixed-whole-asr-execution-v1.json'),contextCount=81,boundaryCount=64,contexts=contexts,boundaries=boundaries,currentWholeWordsAndPcmBoundariesDirectlyCompared=False,all17WholeTextsDirectlyCompared=False,contextModelRun=False,humanListeningApproved=False,heldPreviousProposal='current17-mixed-independent-context-plan-proposed-v1.json',heldReason='Quiet minimization in07b/08b shifted exact cross-placement junctions into the next placed speech, including08b paragraph4->5. Retain that unapproved proposal; use exact source mapping and actual observation gaps.')
out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(preparedContexts=81,preparedJunctions=64,reviewApproval=False,modelRun=False)))
