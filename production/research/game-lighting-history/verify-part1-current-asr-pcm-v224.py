"""Read-only PCM corroboration after the completed recognizer; no listening claim."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state=read(BASE/'part1-current-asr-results-v223.json')
if state.get('exitCode')!=0 or not state.get('endedAt') or len(state['completed'])!=74:raise RuntimeError('Complete original74 results required')
out=BASE/'part1-current-asr-pcm-corroboration-v224.json'
if out.exists():raise RuntimeError('Preserve corroboration')
file_hashes={};source_cache={};rows=[];records={}
for done in state['completed']:
 file=ROOT/done['result']
 if sha(file)!=done['sha256']:raise RuntimeError('Changed result '+done['label'])
 r=read(file);records[done['label']]=r;parts=[];ranges=[];offset=0
 for source in r['job']['sources']:
  p=ROOT/source['path'];key=(source['path'],*source['sampleRange'])
  if source['path'] not in file_hashes:file_hashes[source['path']]=sha(p)
  if file_hashes[source['path']]!=source['sha256']:raise RuntimeError('Source SHA changed')
  if key not in source_cache:
   with sf.SoundFile(p) as f:
    if f.samplerate!=24000 or f.channels!=1:raise RuntimeError('PCM format changed')
    first,last=source['sampleRange'];f.seek(first);part=f.read(last-first,dtype='float32')
   if len(part)!=last-first:raise RuntimeError('Incomplete PCM')
   source_cache[key]=part
  part=source_cache[key]
  if parts:
   gap=r['job'].get('gapSamples',0);parts.append(np.zeros(gap,dtype=np.float32));offset+=gap
  ranges.append(dict(id=source['id'],windowSampleRange=[offset,offset+len(part)],source=source,pcmFloat32Sha256=hashlib.sha256(part.tobytes()).hexdigest()))
  parts.append(part);offset+=len(part)
 signal=np.concatenate(parts)
 if ranges!=r['sourceRanges'] or len(signal)!=r['samples'] or hashlib.sha256(signal.tobytes()).hexdigest()!=r['pcmFloat32Sha256']:raise RuntimeError('Recognized window no longer matches current exact PCM')
 rows.append(dict(label=done['label'],result=done,sources=ranges,windowSamples=len(signal),currentSourceAndWindowFloat32Identical=True))
fan_whole=records['whole-tsr-rotation-vectors'];fan_context=records['context-tsr-rotation-vectors'];fan_follow=records['context-horizon-comparison-before']
fan=lambda r:next(x for x in r['sourceRanges'] if x['id']=='tsr-rotation-vectors')
if len({fan(r)['pcmFloat32Sha256'] for r in [fan_whole,fan_context,fan_follow]})!=1:raise RuntimeError('Fan contexts differ')
reverse=[dict(previous=fan_whole['chunks'][i-1],current=w) for i,w in enumerate(fan_whole['chunks']) if i and w['timestamp'][0]<fan_whole['chunks'][i-1]['timestamp'][0]]
barrier=records['context-geometry-barrier-views'];bw=records['whole-geometry-barrier-views'];br=next(x for x in barrier['sourceRanges'] if x['id']=='geometry-barrier-views')
if br['pcmFloat32Sha256']!=bw['sourceRanges'][0]['pcmFloat32Sha256']:raise RuntimeError('Barrier context differs')
source=br['source'];data=source_cache[(source['path'],*source['sampleRange'])];tail=data[-2880:]
observed=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),sourceExecution=dict(path='projects/game-lighting-history-04/production/part1-current-asr-results-v223.json',sha256=sha(BASE/'part1-current-asr-results-v223.json')),windowCount=74,rows=rows,all74ExactCurrentPcmCorroborated=True,
 recognizerAnomalies=[dict(label='whole-tsr-rotation-vectors',reversedEdges=reverse,identicalSourcePcmInThreeWindows=True,classification='recognizer chunk-boundary repetition',basis='Whole recognition reverses from29.98 to20seconds; both complete independent contexts use the identical37-second source PCM and contain all seven statements once.',audioChanged=False),dict(label='context-geometry-barrier-views',endingWords=barrier['chunks'][-4:],identicalWholePcm=True,wholeEndingWords=bw['chunks'][-4:],farewellAssignedSeconds=.12,twoFarewellWordsHaveZeroDuration=True,last120msPeak=float(np.max(np.abs(tail))),last120msRms=float(np.sqrt(np.mean(tail**2))),classification='zero-duration recognizer tail insertion',basis='The literal whole window ends with 지키겠습니다; identical complete-context PCM assigns nine extra farewell syllables to0.12seconds including two zero-duration words. This is a recognition discrepancy, not evidence of an actual spoken farewell.',audioChanged=False)],
 repairedOnsetApproval=True,allSpokenWordsConfirmed=None,humanWholeListening='pending',actualPronunciationApproved=False,currentMixApproved=False,allFinalPixelsReviewed=False,uploaded=False)
out.write_text(json.dumps(observed,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(windows=74,exactPcmCorroborated=True,fanReverseEdges=len(reverse),barrierTailPeak=observed['recognizerAnomalies'][1]['last120msPeak'],humanListening='pending',currentMixApproved=False)))
