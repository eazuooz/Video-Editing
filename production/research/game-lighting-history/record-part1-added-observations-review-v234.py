"""Seal the four directly read results and exact PCM; do not grant mixed/pixel approval."""
from pathlib import Path
import json,hashlib,os
from datetime import datetime,timezone
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[3];B=R/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e=read(B/'part1-added-observations-asr-execution-v233.json')
t=read(B/'part1-added-observations-tts-execution-v232.json')
assert e['exitCode']==0 and len(e['completed'])==4 and t['exitCode']==0
rows=[]
for item in e['completed']:
 p=R/item['result'];assert sha(p)==item['sha256'];a=read(p);parts=[]
 for s in a['sourceRanges']:
  q=R/s['source']['path'];assert sha(q)==s['source']['sha256'];v,sr=sf.read(q,dtype='float32');assert sr==24000
  assert hashlib.sha256(v.tobytes()).hexdigest()==s['pcmFloat32Sha256']
  if parts:parts.append(np.zeros(a['job']['gapSamples'],dtype='float32'))
  parts.append(v)
 signal=np.concatenate(parts);assert len(signal)==a['samples'] and hashlib.sha256(signal.tobytes()).hexdigest()==a['pcmFloat32Sha256']
 rows.append(dict(label=item['label'],result=item,expected=[s['ko']for s in a['job']['sources']],actualFullText=a['text'],allWordTimestampsDirectlyRead=True,allSentencesAndEndingCompared=True,pcmExact=True))
out=B/'part1-added-observations-direct-review-v234.json';assert not out.exists()
out.write_text(json.dumps(dict(reviewedAt=datetime.now(timezone.utc).isoformat(),reviewer='Codex direct reading in task',executionSha256=sha(B/'part1-added-observations-asr-execution-v233.json'),rows=rows,allFourFullTextsDirectlyCompared=True,wholeAndIndependentContextApproval=True,missingSentences=False,unintendedRepetition=False,unintendedFarewell=False,notes=['Cyber whole/context ASR genitives 바닥에/표면에 and 켜진/꺼진 retained; expected meaning and comparison conditions preserved. Actual pronunciation remains human-pending.','Rivalry full result preserves all four sentences; context old/new timestamp overlap retained, never used to trim PCM. New caption clocks use the monotonic whole window.'],humanWholeListening='pending',humanPronunciation='pending',finalMixedAsrApproved=False,allFinalPixelsReviewed=False,uploaded=False),ensure_ascii=False,indent=2)+'\n','utf-8')
take=next(x for x in t['results']if x['id']=='rivalry-surface-observation');v,sr=sf.read(R/take['path'],dtype='int16');assert sr==24000 and len(v)==503040
lo=1006*400;tail=v[lo:];assert len(tail)==100640
target=R/'production/research/game-lighting-history/local/part1-observation-bridge-v236/audio/episode04-part1-observation-bridge-v236.wav';assert not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
sf.write(target,np.pad(tail,(0,252*400-len(tail))),sr,subtype='PCM_16');back,sr=sf.read(target,dtype='int16');assert np.array_equal(back[:len(tail)],tail)
proof=dict(source=take,sourceSampleRange=[lo,len(v)],frames=252,audio=target.relative_to(R).as_posix(),audioSha256=sha(target),paddingSamples=160,allInt16SamplesExact=True,previousWordEndSeconds=16.64,nextWordStartSeconds=16.88,boundarySeconds=lo/24000,gapPeakNormalized=float(np.max(np.abs(v[399360:405120].astype('float32')))/32768),finalMixedAsrApproved=False)
pp=B/'part1-added-observations-bridge-pcm-v234.json';assert not pp.exists();pp.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(directWindows=4,unmixedApproved=True,bridgeFrames=252,exactSamples=True,finalApproved=False)))
