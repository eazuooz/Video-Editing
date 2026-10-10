"""Propose 66 complete current-AAC contexts; no model or review approval."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, wave
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/motion-sickness-games/production/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'measured-additive-plan-v1.json');mix=read(R/'current-mix-execution-v1.json')
whole=read(R/'current-mixed-whole-asr-execution-v1.json')
assert whole['exitCode']==0 and whole['completed']==whole['total']==14
dest=R/'current-mixed-independent-context-plan-proposed-v1.json'
assert not dest.exists(),'Preserve existing boundary proposal.'
source=ROOT/mix['decodedAac'];assert sha(source)==mix['decodedAacSha256']
contexts=[];boundaries=[]
for scene in plan['scenes']:
    sid=scene['id'];p=ROOT/scene['voice'];assert sha(p)==scene['audioSha256']
    with wave.open(str(p),'rb') as w:
        rate=w.getframerate();assert rate==24000 and w.getnchannels()==1
        samples=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)
    paragraphs=[p for p in plan['paragraphs'] if p['scene']==sid]
    words=read(R/f'current-mixed-whole-asr-v1/{sid}.json')['words']
    cuts=[0]
    for previous,following in zip(paragraphs,paragraphs[1:]):
        nominal=(previous['localEnd']+following['localStart'])/2
        # Search only beside the already reviewed paragraph junction. Read this
        # proposal and its nearby whole words before permitting context ASR.
        lo=max(0,round((nominal-.08)*rate));hi=min(len(samples),round((nominal+.08)*rate))
        half=96
        trials=[(float(np.sqrt(np.mean(samples[n-half:n+half]**2))),n)
                for n in range(lo+half,hi-half,24)]
        rms,n=min(trials,key=lambda v:v[0]+abs(v[1]/rate-nominal)*15)
        cuts.append(n)
        near=[dict(text=v['text'],start=max(0,v['timestamp'][0]-.3),
                   end=None if v['timestamp'][1] is None else v['timestamp'][1]-.3)
              for v in words if v['timestamp'][0]-.3<nominal+.8 and
              (v['timestamp'][1] is None or v['timestamp'][1]-.3>nominal-.8)]
        boundaries.append(dict(scene=sid,afterParagraph=previous['paragraph'],
          previousExpectedEnd=previous['ko'][-35:],followingExpectedStart=following['ko'][:35],
          nominalSeconds=nominal,sourceSample=n,sourceSeconds=n/rate,rms8ms=rms,
          nearbyCurrentWholeWords=near,directlyReviewed=False))
    cuts.append(len(samples));assert len(cuts)==len(paragraphs)+1
    for i,p in enumerate(paragraphs):
        contexts.append(dict(id=f'{sid}-p{p["paragraph"]:02d}',scene=sid,paragraph=p['paragraph'],
          sourcePath=mix['decodedAac'],sourceSha256=mix['decodedAacSha256'],
          startSample=scene['startFrame']*800+cuts[i]*2,
          endSample=scene['startFrame']*800+cuts[i+1]*2,
          localStartSample24k=cuts[i],localEndSample24k=cuts[i+1],
          localStart=cuts[i]/rate,localEnd=cuts[i+1]/rate,
          originalPcmPath=scene['voice'],originalPcmSha256=scene['audioSha256'],
          zeroPaddingSamplesEachSide=14400,expectedKo=p['ko'],expectedEn=p['en'],
          independentCompleteSentence=True,
          boundaryReason='Whole current words plus inspected quiet original PCM paragraph junction; full current AAC bytes, no internal silence removed.'))
assert len(contexts)==66 and len(boundaries)==52
value=dict(schemaVersion=1,recordedAt=datetime.now(timezone.utc).isoformat(),
  sourceSha256=sha(source),mixAacSha256=mix['mixAacSha256'],
  contextCount=66,boundaryCount=52,contexts=contexts,boundaries=boundaries,
  currentWholeWordsAndPcmBoundariesDirectlyCompared=False,
  all14WholeTextsDirectlyCompared=False,contextModelRun=False,humanListeningApproved=False)
dest.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(proposedContexts=66,quietJunctions=52,reviewApproval=False)))
