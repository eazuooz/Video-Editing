"""Measure every retained source junction; RMS alone never approves speech cuts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,wave,numpy as np
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(R/'measured-current17-plan-v2.json');mix=read(R/'current-mix-execution-v2.json');rows=[]
for s in plan['scenes']:
 if s['retainedBaseline']:continue
 p=ROOT/s['voice'];assert sha(p)==s['audioSha256']
 with wave.open(str(p),'rb') as w:assert w.getframerate()==24000;raw=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)
 spans=sorted(s['voicePlacements'],key=lambda v:v['sourceStartSample'])
 for a,b in zip(spans,spans[1:]):
  n=a['sourceEndSample'];assert n==b['sourceStartSample']
  rms=lambda x,y:float(np.sqrt(np.mean(raw[x:y]**2)))
  rows.append(dict(scene=s['id'],sourceSha256=s['audioSha256'],sourceBoundarySample24k=n,sourceBoundarySeconds=n/24000,destinationLeftEndSample24k=a['destinationStartSample']+n-a['sourceStartSample'],destinationRightStartSample24k=b['destinationStartSample'],gapSeconds=(b['destinationStartSample']-a['destinationStartSample']-n+a['sourceStartSample'])/24000,before10msRms=rms(n-240,n),after10msRms=rms(n,n+240),junction8msRms=rms(n-96,n+96),previousPart=a['partId'],nextPart=b['partId'],acousticOrPronunciationApproval=False,currentWholeAndIndependentWordsStillRequired=True))
assert len(rows)==12
out=R/'current17-placement-boundary-rms-audit-v2.json';assert not out.exists()
out.write_text(json.dumps(dict(recordedAt=datetime.now(timezone.utc).isoformat(),mixAacSha256=mix['mixAacSha256'],planSha256=sha(R/'measured-current17-plan-v2.json'),junctionCount=12,junctions=rows,allSourcePcmBytesPreserved=True,firstRepairJunctionExactlyZero=True,allSpeechCutsApproved=False,interpretation='Small RMS or approximate recognizer timing alone cannot prove a cut is between complete words. Review current whole and complete independent contexts, including every long observation gap; keep human listening and pronunciation pending.'),ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(junctions=12,firstRepairZero=True,allSpeechCutsApproved=False,modelRuns=0)))
