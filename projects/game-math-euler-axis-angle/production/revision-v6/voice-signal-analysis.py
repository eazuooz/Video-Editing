"""Read-only source pacing/level advisories; no ASR, DSP or PCM modification.

Energy-active seconds are a proxy, not recognized speech or a listening pass.
Never use these energy windows alone as safe insertion/seam evidence.
"""
from pathlib import Path
import hashlib,json,math,re,sys,time
import numpy as np
import soundfile as sf
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;V=P/'production/local/revision-v6/voice'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64)))) if len(x) else 0.
def main():
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 source=read(H/'voice-input.ko.json');script={s['id']:s for s in source['scenes']};completed=read(V/'tts-current.json')
 path=V/'source-signal-analysis.json';prior=read(path) if path.exists() else {};cache={s['id']:s for s in prior.get('scenes',[])}
 implementation=sha(Path(__file__));rows=[]
 for item in completed['scenes']:
  old=cache.get(item['id'])
  if old and old['sourceSha256']==item['sha256'] and old['implementationSha256']==implementation:rows.append(old);continue
  file=R/item['file'];assert sha(file)==item['sha256'];pcm,rate=sf.read(file,dtype='float32',always_2d=True);assert pcm.shape[1]==1
  mono=pcm[:,0];size=round(rate*.02);count=len(mono)//size;frames=mono[:count*size].reshape(count,size)
  energy=np.sqrt(np.mean(frames.astype(np.float64)**2,axis=1));threshold=max(.001,rms(mono)*.12);active_frames=energy>threshold
  mask=np.repeat(active_frames,size);mask=np.pad(mask,(0,len(mono)-len(mask)))
  active=float(active_frames.sum())*.02;text=' '.join(script[item['id']]['lines']);syllables=len(re.findall('[가-힣]',text));raw_seconds=len(mono)/rate
  windows=[]
  for a in range(0,len(mono)-round(.4*rate)+1,round(.1*rate)):
   b=a+round(.4*rate);submask=mask[a:b]
   if submask.sum()>=.15*rate:windows.append(dict(rawStart=a/rate,rawEnd=b/rate,energyActiveRmsDbfs=db(rms(mono[a:b][submask])),allSamplesRmsDbfs=db(rms(mono[a:b])),energyActiveFraction=float(submask.mean())))
  levels=[w['energyActiveRmsDbfs'] for w in windows];median=float(np.median(levels)) if levels else None
  low=[dict(w,relativeToSceneMedianDb=w['energyActiveRmsDbfs']-median) for w in windows if w['energyActiveRmsDbfs']<median-6] if median is not None else []
  rows.append(dict(id=item['id'],sourceFile=item['file'],sourceSha256=item['sha256'],implementationSha256=implementation,
   scriptedHangulSyllables=syllables,scriptedEojeol=len(text.split()),rawSeconds=raw_seconds,
   scriptedHangulSyllablesPerRawSecond=syllables/raw_seconds,energyActiveEstimatedSeconds=active,
   scriptedHangulSyllablesPerEnergyActiveSecond=syllables/max(active,.001),
   energyProxy=dict(frameSeconds=.02,thresholdRms=threshold,thresholdPolicy='max0.001 or12percent of clipRMS; estimate only, not VAD/ASR, excludes quiet consonants/breaths'),
   peakDbfs=db(np.max(np.abs(mono))),hardClipSampleCount=int(np.sum(np.abs(mono)>=32766/32768)),
   sourceEnergyActiveRmsDbfs=db(rms(mono[mask])),sourceWindowMedianDbfs=median,
   proposedConstantSceneGainDb=-20-db(rms(mono[mask])),proposalApplied=False,
   sourceWindows=windows,lowSourceWindows=low,localWindowSizeSeconds=.4,localWindowStepSeconds=.1,
   actualWordsOrParagraphsMatched=False,humanPaceListening='pending',doNotUseEnergyProxyAsSafeSeam=True))
 rates=[s['scriptedHangulSyllablesPerRawSecond'] for s in rows];median_rate=float(np.median(rates)) if rates else 0
 for row in rows:row['relativeRawRateToCompletedMedian']=row['scriptedHangulSyllablesPerRawSecond']/max(median_rate,.001)
 result=dict(schemaVersion=1,revision='article-flow-v6',sourceBatchStatus=completed['status'],scenes=rows,completedSceneCount=len(rows),
  scriptSha256=sha(H/'voice-input.ko.json'),implementationSha256=implementation,
  scope='Current completed PCM only; no ASR, synthesis, gain, stretching, trim, final voice approval or final timing.',
  rawRateMedian=median_rate,relativePaceInspectionCandidates=[dict(id=s['id'],rawSyllablesPerSecond=s['scriptedHangulSyllablesPerRawSecond'],ratio=s['relativeRawRateToCompletedMedian']) for s in rows if s['relativeRawRateToCompletedMedian']>1.15],
  relativeTrigger='More than15percent above this completed-set median is a contextual inspection candidate, not an external speech-rate standard or automatic failure.',
  denseMathSourceScenes=[s['id'] for s in rows if int(s['id'][-2:]) in [14,16,18,19,20,21,23,24,25,26,27,31,33,37,38,39,40,41]],
  plannedPacing=dict(primaryObservationSeconds=527,auxiliaryObservationSeconds=4,primaryFiniteMotionFrames=40820,auxiliaryMotionFrames=180,
   contract='Explain→finite visualization→observation→confirmation; source natural PCM unchanged; no blanket slowdown or per-sentence fixed silence.'),
  actualSpeechActivePacingReview='pending once-only current source ASR/full direct comparison and word-aligned dense-paragraph breathing',humanWholeListening='pending',createdAt=time.time())
 path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(completed=len(rows),medianRawSyllablesPerSecond=median_rate,minimum=min(rates),maximum=max(rates),relativeOutliers=result['relativePaceInspectionCandidates'],hardClipSamples=sum(s['hardClipSampleCount'] for s in rows),sourceOnly=True),ensure_ascii=False))
if __name__=='__main__':main()
