"""CPU exact paragraph origins, current ASR clocks and localized level evidence."""
from pathlib import Path
import hashlib,importlib.util,json,math,re,sys
import numpy as np
import soundfile as sf
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_voice_analysis_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_timing_normalizer',H/'voice-normalize.py');n=importlib.util.module_from_spec(s);s.loader.exec_module(n)
sys.path.insert(0,str(c.R/'qwen3-tts'))
import align_project_subtitles as align
align.normalized=n.normalized
def db(x):return 20*math.log10(max(float(x),1e-12))
def rms(x):return float(np.sqrt(np.mean(np.square(x,dtype=np.float64))))if len(x)else 0.
def monotonic_word_view(raw):
 """Resolve decoder chunk clock restarts, without editing raw ASR or audio.

 A later chunk re-recognizes the same source time. Retain its replacement
 word interval, removing the earlier chunk tail from that source time.
 The decision uses only clocks, never expected script text.
 """
 out=[];events=[]
 for i,w in enumerate(raw):
  a,b=w['timestamp']
  if a is None or b is None or b<=a:continue
  item=dict(w,rawAsrWordIndex=i,timestamp=[float(a),float(b)])
  if out and a<out[-1]['timestamp'][0]-.04:
   removed=[]
   while out and out[-1]['timestamp'][0]>=a-.001:removed.append(out.pop())
   events.append(dict(atRawWordIndex=i,restartSeconds=a,discardedEarlierChunkTailRawIndices=[z['rawAsrWordIndex']for z in reversed(removed)],
    reason='Same source-time interval reappeared after a backward chunk-clock reset; later chunk retained. Raw ASR unchanged.'))
  if out:item['timestamp'][0]=max(item['timestamp'][0],out[-1]['timestamp'][1])
  if item['timestamp'][1]>item['timestamp'][0]:out.append(item)
 merged=[]
 for w in out:
  if merged and re.fullmatch(r'\s*[PQRpqr]\s*',merged[-1]['text'])and re.match(r"\s*['′]",w['text']):
   previous=merged[-1];events.append(dict(kind='split-prime-word-merge',rawIndices=[previous['rawAsrWordIndex'],w['rawAsrWordIndex']],
    reason='ASR separated an axis label and its written prime into two tokens; combined only for timing normalization. Raw text and PCM unchanged.'))
   previous['text']=previous['text']+w['text'];previous['timestamp'][1]=w['timestamp'][1]
  else:merged.append(w)
 return merged,events
def scoped_pronunciation_view(words,row,sid):
 alias=row.get('qaSelection',{}).get('pronunciationAlias')
 if not alias:return words,None
 assert sid=='m07'and row['line']==2 and alias['displayPhrase']=='이분의 일입니다'and alias['spokenPhrase']=='영 점 오입니다'
 assert c.sha(c.R/alias['file'])==alias['sha256'];matches=[]
 for i in range(len(words)):
  for j in range(i+1,min(len(words),i+4)+1):
   spelling=re.sub(r'\s','', ''.join(w['text']for w in words[i:j])).rstrip('.,!?')
   if spelling in ['0.5입니다','0점5입니다','영점오입니다','영점5입니다']:
    matches.append((i,j,spelling))
 assert len(matches)==1,'Scoped1/2=0.5 spoken alias needs one actual decimal word anchor, never a guessed numeric repair'
 i,j,spelling=matches[0];replacement=dict(text=alias['displayPhrase'],timestamp=[words[i]['timestamp'][0],words[j-1]['timestamp'][1]])
 evidence=dict(scope='Onlym07.L02',displayPhrase=alias['displayPhrase'],spokenPhrase=alias['spokenPhrase'],recognizedSpelling=spelling,
  exactValueProof='1/2=0.5',sourceWordRange=[i,j],timestamp=replacement['timestamp'],aliasFile=alias['file'],aliasSha256=alias['sha256'],
  method='Same-value display timing mapped over the actual decimal ASR interval. This is not phoneme-by-phoneme correspondence or a global number equivalence.')
 return words[:i]+[replacement]+words[j:],evidence
def main():
 plan=c.validate();source=c.read(c.O/'tts-current.json');review=c.read(c.O/'source-asr-review.json');assert review['complete']and source['paragraphCount']==76
 script={s['id']:s for s in c.read(H/'voice-input.json')['scenes']};scenes=[];levels=[];pending=[];paragraph_count=0;reused=[]
 old_alignment=c.read(c.O/'source-alignment.json')if(c.O/'source-alignment.json').exists()else{}
 old_levels=c.read(c.O/'source-level-review.json')if(c.O/'source-level-review.json').exists()else{}
 cached_align={x['id']:x for x in old_alignment.get('scenes',[])};cached_levels={x['scene']:x for x in old_levels.get('scenes',[])}
 implementation=c.sha(Path(__file__));normalizer=c.sha(H/'voice-normalize.py')
 for scene in source['scenes']:
  sid=scene['id'];file=c.R/scene['file'];assert c.sha(file)==scene['sha256']
  asr_file=c.R/scene['asrFile']if scene.get('asrFile')else c.O/'asr'/(sid+'.json');cached=c.read(asr_file);assert cached['audio_sha256']==scene['sha256']
  origins=hashlib.sha256(json.dumps(scene['lines'],sort_keys=True).encode()).hexdigest()
  base_inputs=dict(sourceSha256=scene['sha256'],asrSha256=c.sha(asr_file),lineOriginsSha256=origins,implementationSha256=implementation)
  alignment_inputs=dict(base_inputs,normalizerSha256=normalizer)
  for line in scene['lines']:assert c.sha(c.R/line['takeFile'])==line['takeSha256']
  if sid in cached_align and sid in cached_levels and cached_align[sid].get('inputs')==alignment_inputs and cached_levels[sid].get('inputs')==base_inputs:
   scenes.append(cached_align[sid]);levels.append(cached_levels[sid]);paragraph_count+=len(scene['lines']);reused.append(sid);print('Reused unchanged PCM/ASR source evidence',sid,flush=True);continue
  x,rate=sf.read(file,dtype='float32');assert rate==24000 and len(x)==scene['samples']
  raw_words=cached['words'];words,chunk_restarts=monotonic_word_view(raw_words);mask=np.zeros(len(x),bool);backward=[]
  for i,w in enumerate(raw_words):
   lo,hi=w['timestamp']
   if lo is None or hi is None:continue
   mask[max(0,round(lo*rate)):min(len(x),round(hi*rate))]=True
   if i and raw_words[i-1]['timestamp'][0]is not None and lo<raw_words[i-1]['timestamp'][0]-.04:backward.append(dict(wordIndex=i,previous=raw_words[i-1],current=w))
  word_levels=[]
  for i,w in enumerate(words):
   lo,hi=w['timestamp']
   if lo is None or hi is None or hi-lo<.04:continue
   a=max(0,round(lo*rate));b=min(len(x),round(hi*rate))
   if b<=a:continue
   containing=next((line for line in scene['lines']if a>=line['startSample']and b<=line['endSample']),None)
   value=db(rms(x[a:b]))
   word_levels.append(dict(asrWordIndex=i,text=w['text'],start=a/rate,end=b/rate,processedWordRmsDbfs=value,
    line=containing['line']if containing else None,sourceEquivalentPreGainDbfs=value-containing['gainDb']if containing else None,
    preGainMethod='Exact complete-line constant-gain inverse on the same timestamp interval; not phonetic isolation'))
  windows=[]
  for lo in range(0,len(x)-9600+1,2400):
   hi=lo+9600;active=mask[lo:hi]
   if active.sum()<3600:continue
   windows.append(dict(start=lo/rate,end=hi/rate,speechRmsDbfs=db(rms(x[lo:hi][active])),timestampActiveSamples=int(active.sum())))
  line_rows=[];line_levels=[]
  for row,text in zip(scene['lines'],script[sid]['lines']):
   paragraph_count+=1;lo,hi=row['startSample'],row['endSample'];start,end=lo/rate,hi/rate
   raw,raw_rate=sf.read(c.R/row['takeFile'],dtype='float32');assert raw_rate==rate and c.sha(c.R/row['takeFile'])==row['takeSha256']
   expected=raw*np.float32(10**(row['gainDb']/20));assert np.array_equal(x[lo:hi],expected),'Current paragraph must equal its preserved raw take and single constant gain'
   chosen=[]
   for w in words:
    a,b=w['timestamp']
    if a is None or b is None or b<=a:continue
    overlap=max(0,min(b,end)-max(a,start))
    if overlap and (max(a,start)+min(b,end))/2>=start:
     best=max(scene['lines'],key=lambda z:max(0,min(b,z['endSample']/rate)-max(a,z['startSample']/rate)))
     if best['line']==row['line']:chosen.append(dict(text=w['text'],timestamp=[max(a,start)-start,min(b,end)-start]))
   active=mask[lo:hi];value=db(rms(x[lo:hi][active]))if active.any()else None;raw_value=db(rms(raw[active]))if active.any()else None
   line_levels.append(dict(line=row['line'],takeStart=start,takeEnd=end,sourceSpeechDbfs=raw_value,processedSpeechDbfs=value,
    actualConstantTransferDb=value-raw_value if value is not None else None,documentedGainDb=row['gainDb'],speechTimestampSamples=int(active.sum()),timestampMaskEmpty=not bool(active.any()),
    constantGainPcmExact=True,beforeFrameMedianDbfs=row['before']['speechFrameMedianDbfs'],afterFrameMedianDbfs=row['after']['speechFrameMedianDbfs'],
    energyGateLeadingSeconds=row['before']['energyGateLeadingSeconds'],energyGateTrailingSeconds=row['before']['energyGateTrailingSeconds'],gapBeforeSamples=row['gapBeforeSamples']))
   try:
    timing_words,spoken_alias=scoped_pronunciation_view(chosen,row,sid)
    a,b,coverage=align.align_characters(text,timing_words,end-start)
    assert len(a)==len(b)==len(n.normalized(text))and len(a)>0
    line_rows.append(dict(line=row['line'],rawStart=float(a[0]+start),rawEnd=float(b[-1]+start),takeStart=start,takeEnd=end,
     characterStarts=[float(v+start)for v in a],characterEnds=[float(v+start)for v in b],matchedCharacterCoverage=coverage,
     paragraphOriginExact=True,characterTiming='ASR-word anchored interpolation, not phoneme measurement',sourcePcmUnchanged=True,scopedPronunciationTimingAlias=spoken_alias))
   except(ValueError,AssertionError)as error:
    pending.append(dict(scene=sid,line=row['line'],takeRange=[start,end],reason=str(error),action='Read complete raw transcript/context; retain exact paragraph origins; no invented character clocks'))
  if len(line_rows)==len(scene['lines']):
   scenes.append(dict(id=sid,inputs=alignment_inputs,sourceFile=scene['file'],sourceSha256=scene['sha256'],samples=len(x),sampleRate=rate,seconds=len(x)/rate,
    asrFile=c.rel(asr_file),asrSha256=c.sha(asr_file),lines=line_rows,backwardWordClockEvents=backward,derivedClockRestartRepairs=chunk_restarts))
  median=float(np.median([w['speechRmsDbfs']for w in windows]))if windows else None
  low=[w for w in windows if median is not None and w['speechRmsDbfs']<median-6];groups=[]
  for w in low:
   if groups and w['start']<=groups[-1]['end']+.101:groups[-1]['end']=w['end'];groups[-1]['minimumRelativeDb']=min(groups[-1]['minimumRelativeDb'],w['speechRmsDbfs']-median)
   else:groups.append(dict(start=w['start'],end=w['end'],minimumRelativeDb=w['speechRmsDbfs']-median))
  groups=[dict(g,duration=g['end']-g['start'],status='overlapping-window candidate, not an exact continuous phonetic drop or automatic defect')for g in groups if g['end']-g['start']>=.5]
  word_values=[w['processedWordRmsDbfs']for w in word_levels]
  levels.append(dict(scene=sid,inputs=base_inputs,paragraphs=line_levels,words=word_levels,wordRmsP90MinusP10Db=float(np.percentile(word_values,90)-np.percentile(word_values,10))if word_values else None,
   wordStatistic='ASR intervals of at least40ms; no level-based deletion of quiet words. Natural prosody/breath and timestamp uncertainty remain; percentile span is not a defect threshold.',
   windows=windows,windowMedianDbfs=median,relativeLowCandidates=groups,
   floatPeak=float(abs(x).max()),floatSamplesOutsideUnitRange=int(np.sum(abs(x)>=1)),backwardWordClockEvents=backward,derivedClockRestartRepairs=chunk_restarts,humanListening='pending'))
  print('Analyzed',sid,'aligned',len(line_rows),'of',len(scene['lines']),'paragraphs',flush=True)
 assert paragraph_count==76
 signature=dict(voiceInputSha256=c.sha(H/'voice-input.json'),sourceReceiptSha256=c.sha(c.O/'tts-current.json'),asrReviewSha256=c.sha(c.O/'source-asr-review.json'),normalizerSha256=c.sha(H/'voice-normalize.py'),implementationSha256=c.sha(Path(__file__)))
 c.save(c.O/'source-alignment.json',dict(revision='orientation-matrix-v8',inputs=signature,sceneCount=len(scenes),paragraphCount=sum(len(s['lines'])for s in scenes),scenes=scenes,pending=pending,reusedUnchangedScenes=reused,sourceSpeed=1,addedObservationSilenceSamples=0,status='complete'if not pending else'pending-selected-alignment-review'))
 joins=[]
 for left,right in zip(levels,levels[1:]):
  a,b=left['paragraphs'][-1],right['paragraphs'][0]
  delta=b['processedSpeechDbfs']-a['processedSpeechDbfs']if a['processedSpeechDbfs']is not None and b['processedSpeechDbfs']is not None else None
  joins.append(dict(previous=left['scene'],next=right['scene'],processedParagraphDeltaDb=delta,afterFrameMedianDeltaDb=b['afterFrameMedianDbfs']-a['afterFrameMedianDbfs'],humanListening='pending'))
 c.save(c.O/'source-level-review.json',dict(revision='orientation-matrix-v8',inputs=signature,sceneCount=13,paragraphCount=76,
  method='All preserved raw takes→current constant-gain scene PCM verified sample-exact.400ms/100ms windows require150ms ASR timestamp-active samples. The50ms relative energy-gated median is a different statistic; neither is phonetic or listening proof.',
  scenes=levels,joins=joins,sourceSpeed=1,voiceDucking=False,voiceSpeechFades=False,addedObservationSilenceSamples=0,
  triggers=dict(adjacentDb=3,relativeLowDb=6,minimumCandidateSpanSeconds=.5),humanWholeListening='pending',actualMovingPace='pending',finalEncodedMix='not yet built; separate QA later'))
 c.save(c.O/'voice-handoff.json',dict(revision='orientation-matrix-v8',inputs=signature,sceneCount=13,paragraphCount=76,
  sourceRawSeconds=sum(s['seconds']for s in source['scenes']),sourceFiles=source['scenes'],sourceAlignment=c.rel(c.O/'source-alignment.json'),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json'),
  sourceLevels=c.rel(c.O/'source-level-review.json'),sourceLevelsSha256=c.sha(c.O/'source-level-review.json'),sourceAsrReview=c.rel(c.O/'source-asr-review.json'),sourceAsrReviewSha256=c.sha(c.O/'source-asr-review.json'),
  pendingAlignment=pending,directFullTextComparison='pending separate review',sourceSpeed=1,addedObservationSilenceSamples=0,
  humanWholeListening='pending',actualVoiceVisualPace='pending',finalMixAsr='pending current final encoded AAC once'))
 print(json.dumps(dict(scenes=len(scenes),paragraphs=paragraph_count,pending=len(pending))))
if __name__=='__main__':main()
