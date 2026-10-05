"""Build the final narration timeline from the preserved placed PCM, without TTS."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;FINAL=BASE/'final-v1';WORK=BASE/'measured-edit-v6'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
plan=read(FINAL/'plan.json');placed=read(WORK/'placed-voice-index.json')
assert plan['finalTimingApproved'] and plan['bodyRatioApproved'] and placed['all15CurrentPcmPreserved']
out=FINAL/'narration-timed.wav';assert not out.exists()
y=np.zeros((plan['finalFrames']*400,1),dtype=np.int16);rows=[]
for s in plan['scenes']:
 r=next(r for r in placed['results'] if r['sceneId']==s['id']);assert sha(ROOT/r['path'])==r['sha256'] and sha(ROOT/s['audio'])==s['audioSha256']
 x,sr=sf.read(ROOT/r['path'],dtype='int16',always_2d=True);assert sr==24000 and len(x)==s['frames']*400
 start=s['startFrame']*400;y[start:start+len(x)]=x
 rows.append(dict(sceneId=s['id'],startFrame=s['startFrame'],frames=s['frames'],startSample=start,endSampleExclusive=start+len(x),placedPath=r['path'],placedSha256=r['sha256'],currentPcmSha256=s['audioSha256'],allPlacedSamplesIdentical=True))
sf.write(out,y,24000,subtype='PCM_16');z,rate=sf.read(out,dtype='int16',always_2d=True);assert rate==24000 and np.array_equal(y,z)
assert np.count_nonzero(z[:48000])==0 and np.count_nonzero(z[-240000:])==0
state=dict(createdAt=datetime.now(timezone.utc).isoformat(),planSha256=sha(FINAL/'plan.json'),sampleRate=24000,samples=len(z),seconds=len(z)/24000,
 voicePath=rel(out),voiceSha256=sha(out),placedIndexSha256=sha(WORK/'placed-voice-index.json'),scenes=rows,all15PlacedPcmSamplesIdentical=True,sourceCurrentPcmSamples=11406244,
 newTts=0,introNarrationSilent=True,membershipNarrationSilent=True,finalMixBuilt=False,humanWholeListening='pending')
(FINAL/'pcm-timeline-preservation.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(seconds=state['seconds'],samples=len(z),scenes=15,allPlacedSamplesIdentical=True,newTts=0)))
