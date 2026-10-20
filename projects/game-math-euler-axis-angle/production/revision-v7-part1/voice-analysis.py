"""CPU new-PCM paragraph clocks and source-level advisories; never edits audio."""
from pathlib import Path
import difflib,hashlib,importlib.util,math,re,runpy,sys
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_audio_common',H/'audio-common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64)))) if len(x) else 0.
def alignment_helpers():
 previous=sys.argv[:];sys.argv=[sys.argv[0],c.P.name]
 try:helpers=runpy.run_path(str(c.R/'production/batches/game-math-part2-full-series/align.py'),run_name='v7_numeric_alignment_helpers')
 finally:sys.argv=previous
 base=helpers['normalized']
 # Timing-only spelling equivalents. No wrong-word/error repair or numeral
 # replacement is allowed to act as a source-content review.
 aliases=[('엑스트린식 로테이션','extrinsic rotation'),('인트린식 로테이션','intrinsic rotation'),('오리엔테이션','orientation'),('오일러 각','euler angles'),('테이트–브라이언','tait bryan'),('테이트 브라이언','tait bryan'),('짐벌 락','gimbal lock'),('짐벌락','gimbal lock'),('헤딩','heading'),('피치','pitch'),('뱅크','bank'),('슈퍼플라이트','superflight')]
 def normalized(text):
  text=text.lower()
  for source,target in aliases:text=text.replace(source,target)
  return base(text)
 helpers['a'].normalized=normalized
 return helpers['a'],normalized
def low_runs(windows,median):
 selected=[x for x in windows if x['speechRmsDbfs']<median-6]
 groups=[]
 for row in selected:
  if groups and row['start']<=groups[-1]['end']+.101:
   groups[-1]['end']=row['end'];groups[-1]['minimumRelativeDb']=min(groups[-1]['minimumRelativeDb'],row['speechRmsDbfs']-median)
  else:groups.append(dict(start=row['start'],end=row['end'],minimumRelativeDb=row['speechRmsDbfs']-median))
 return [dict(x,duration=x['end']-x['start'],status='contextual-review-candidate; not automatic defect') for x in groups if x['end']-x['start']>=.5]
def main():
 plan=c.validate(preserve_pcm=True);source=c.read(c.O/'tts-current.json');asr_review=c.read(c.O/'source-asr-review.json')
 assert source['sceneCount']==21 and source['status']=='complete-source-ASR-pending' and asr_review['complete']
 script=c.read(H/'voice-input.json');spoken={s['id']:s for s in script['scenes']}
 signature=dict(voiceInputSha256=c.sha(H/'voice-input.json'),ttsReceiptSha256=c.sha(c.O/'tts-current.json'),sourceAsrReviewSha256=c.sha(c.O/'source-asr-review.json'),implementationSha256=c.sha(Path(__file__)))
 final=c.O/'voice-handoff.json'
 if final.exists() and c.read(final).get('inputs')==signature:
  print('Reused exact current PCM/ASR successful CPU analysis');return
 align,normalize=alignment_helpers();aligned=[];levels=[];pending=[];all_levels=[]
 for row in source['scenes']:
  sid=row['id'];file=c.R/row['file'];assert c.sha(file)==row['sha256']
  asr_file=c.O/'asr'/(sid+'.json');cached=c.read(asr_file);assert cached['audio_sha256']==row['sha256']
  x,rate=sf.read(file,dtype='float32');assert rate==24000 and x.ndim==1 and len(x)==row['samples'];duration=len(x)/rate
  valid=[w for w in cached['words'] if w.get('timestamp') and all(t is not None for t in w['timestamp']) and w['timestamp'][1]>w['timestamp'][0]]
  mask=np.zeros(len(x),bool)
  for word in valid:
   a,b=word['timestamp'];mask[max(0,round(a*rate)):min(len(x),round(b*rate))]=True
  windows=[]
  for a in range(0,len(x)-round(.4*rate)+1,round(.1*rate)):
   b=a+round(.4*rate);active=x[a:b][mask[a:b]]
   if len(active)>=round(.15*rate):windows.append(dict(start=a/rate,end=b/rate,speechRmsDbfs=db(rms(active)),speechMaskSamples=len(active)))
  median=float(np.median([w['speechRmsDbfs'] for w in windows])) if windows else None
  local=dict(id=sid,file=row['file'],sha256=row['sha256'],samples=len(x),sampleRate=rate,seconds=duration,peakDbfs=db(np.max(np.abs(x))),hardClipSampleCount=int(np.sum(np.abs(x)>=32766/32768)),sourceSpeechRmsDbfs=db(rms(x[mask])),windowMedianDbfs=median,windows=windows,lowRuns=low_runs(windows,median) if median is not None else [],humanListening='pending')
  paragraphs=[]
  try:
   start,end,coverage=align.align_characters(' '.join(spoken[sid]['lines']),cached['words'],duration)
   cursor=0
   for i,line in enumerate(spoken[sid]['lines'],1):
    count=len(normalize(line));a=float(start[cursor]);b=float(end[cursor+count-1]);low=max(0,round(a*rate));high=min(len(x),round(b*rate));active=x[low:high][mask[low:high]]
    paragraphs.append(dict(line=i,rawStart=a,rawEnd=b,characterStarts=[float(v) for v in start[cursor:cursor+count]],characterEnds=[float(v) for v in end[cursor:cursor+count]],speechRmsDbfs=db(rms(active)),speechSamples=len(active)))
    cursor+=count
   assert cursor==len(start)==len(end)
   aligned.append(dict(id=sid,sourceFile=row['file'],sourceSha256=row['sha256'],asrFile=c.rel(asr_file),asrSha256=c.sha(asr_file),samples=len(x),sampleRate=rate,seconds=duration,matchedCharacterCoverage=coverage,lines=paragraphs,captionTimingOnly=True,sourceWordsChanged=False,sourcePcmChanged=False))
  except (ValueError,AssertionError) as error:
   pending.append(dict(id=sid,reason=str(error),action='Direct full-text/context review before using these paragraph clocks; no invented timing.'))
  adjacent=[]
  for a,b in zip(paragraphs,paragraphs[1:]):
   delta=b['speechRmsDbfs']-a['speechRmsDbfs']
   if abs(delta)>=3:adjacent.append(dict(afterLine=a['line'],nextLine=b['line'],differenceDb=delta,status='source-prosody/decay candidate; contextual review required'))
  local['paragraphs']=[{k:v for k,v in p.items() if k not in ['characterStarts','characterEnds']} for p in paragraphs]
  local['adjacentParagraphCandidates']=adjacent;local['sustainedParagraphSpanDb']=max((p['speechRmsDbfs'] for p in paragraphs),default=0)-min((p['speechRmsDbfs'] for p in paragraphs),default=0)
  levels.append(local);all_levels.extend(w['speechRmsDbfs'] for w in windows)
  print('Analyzed current source',sid,'paragraphs',len(paragraphs),'raw seconds',round(duration,3),flush=True)
 mapping=dict(schemaVersion=1,part=1,revision='v7-part1',inputs=signature,scenes=aligned,pending=pending,sceneCount=len(aligned),paragraphCount=sum(len(s['lines']) for s in aligned),status='complete-current-word-alignment' if not pending else 'partial-unresolved-alignment',insertedObservationSilenceSamples=0,sourceSpeed=1,rawWordsAndSourcePcmUnchanged=True,characterInterpolationIsNotContentOrListeningApproval=True)
 c.save(c.O/'source-alignment.json',mapping)
 level_report=dict(schemaVersion=1,part=1,revision='v7-part1',inputs=signature,sceneCount=len(levels),scenes=levels,method='Current ASR-word mask;400ms local windows/100ms steps, minimum150ms timestamp-active samples; timestamp activity is not phonetic proof or blanket silence trim.',triggers=dict(localDropDb=6,minimumDurationSeconds=.5,adjacentParagraphOrSceneDb=3),sourceOnly=True,mixContinuityStatus='pending actual processed narration and encoded mix; old V6 measurements not reused',humanWholeListening='pending',naturalPaceWithMovingOutput='pending')
 c.save(c.O/'source-level-review.json',level_report)
 handoff=dict(schemaVersion=1,part=1,revision='v7-part1',inputs=signature,status='current21-PCM-and-ASR-ready; direct-content/listening and final timing review pending' if not pending else 'current-source-alignment-needs-review',sceneCount=21,paragraphCount=135,sourceRawSeconds=sum(s['seconds'] for s in source['scenes']),sourceFiles=source['scenes'],currentPcm=c.rel(c.O/'current-pcm.json'),currentPcmSha256=c.sha(c.O/'current-pcm.json'),sourceAlignment=c.rel(c.O/'source-alignment.json'),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json'),sourceLevels=c.rel(c.O/'source-level-review.json'),sourceLevelsSha256=c.sha(c.O/'source-level-review.json'),sourceAsrReview=c.rel(c.O/'source-asr-review.json'),sourceAsrReviewSha256=c.sha(c.O/'source-asr-review.json'),pendingAlignment=pending,noFixedObservationSilence=True,sceneGapSeconds=0,sourceSpeed=1,finalMixAsr='pending; source ASR cannot replace encoded-mix review',finalLevelContinuity='pending; source→processed-stem→encoded must be aligned',humanWholeListening='pending')
 c.save(final,handoff);print('CPU source handoff ready; unresolved alignment scenes',len(pending),flush=True)
if __name__=='__main__':main()

