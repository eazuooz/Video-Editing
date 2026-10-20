"""Two sentence-only constant gains at measured quiet joins; no new AAC/ASR."""
from pathlib import Path
import copy,importlib.util,json,math,shutil
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_sentence_gain_prepare',H/'audio-prepare.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
def curve(row,length):
 out=np.ones(length,np.float32);lo,li,ro,ri=row['gainRangeSamples48'];gain=row['gainDb']
 out[lo:li]=10**(np.linspace(0,gain,li-lo,dtype=np.float32)/20)
 out[li:ro]=10**(gain/20);out[ro:ri]=10**(np.linspace(gain,0,ri-ro,dtype=np.float32)/20)
 return out
def main():
 c.validate(preserve_pcm=True);build_file=c.O/'narration-build.json';old=c.read(build_file)
 assert not old.get('sentenceGainRefinement'),'Selected refinement already applied; do not repeat'
 oldfile=c.R/old['narrationFile'];assert any(x['sha256']==c.sha(oldfile)for x in old['outputs'])
 t=c.read(H/'timeline.json');timeline={x['id']:x for x in t['scenes']};al={x['id']:x for x in c.read(c.O/'source-alignment.json')['scenes']}
 continuity=c.read(c.O/'narration-continuity-review.json');byid={x['scene']:x for x in continuity['scenes']}
 captions=c.read(c.O.parent/'captions/captions.json');rows=[]
 with sf.SoundFile(oldfile)as audio:
  for sid,line,sentence,requested in [('v7-a05',2,3,4.5),('v7-a14',1,3,3.0)]:
   scene=timeline[sid];metric=next(x for x in byid[sid]['sentences']if x['line']==line and x['sentence']==sentence)
   selected=[x for x in captions['cues']if x['scene']==sid and x['line']==line and x['sentence']==sentence]
   text=' '.join(x['sourceKo']for x in selected);cached=c.read(c.R/al[sid]['asrFile']);words=[w for w in cached['words']if all(v is not None for v in w['timestamp'])]
   begin=min(range(len(words)),key=lambda i:abs(words[i]['timestamp'][0]-metric['rawStart']))
   end=min(range(len(words)),key=lambda i:abs(words[i]['timestamp'][1]-metric['rawEnd']))
   _,normalize=a.a.alignment_helpers()
   assert normalize(' '.join(w['text']for w in words[begin:end+1]))==normalize(text),'Full sentence lexical span must match'
   assert begin>0 and end+1<len(words)
   raw,rate=sf.read(c.R/scene['rawVoiceFile'],dtype='float32');assert rate==24000
   audio.seek(scene['startFrame']*800);actual=audio.read(len(raw)*2,dtype='float32',always_2d=True)[:,0]
   before=[words[begin-1]['timestamp'][1],words[begin]['timestamp'][0]]
   after=[words[end]['timestamp'][1],words[end+1]['timestamp'][0]]
   b=a.quiet_window(actual,48000,*before,a.rms(actual));e=a.quiet_window(actual,48000,*after,a.rms(actual))
   assert b and e,'No complete80ms quiet window; no word-internal gain edit permitted'
   for q in [b,e]:
    low,high=[round(v/2)for v in q['quietWindowSamples']];ref=a.rms(raw)
    assert a.rms(raw[low:high])<=min(.01,max(ref*.08,1e-6))and np.max(abs(raw[low:high]))<=min(.04,max(ref*.30,1e-5))
   lo,li=b['quietWindowSamples'];ro,ri=e['quietWindowSamples'];assert lo<li<ro<ri
   tp=a.db(np.max(abs(resample_poly(actual[lo:ri],4,1))));gain=requested
   rows.append(dict(scene=sid,line=line,sentence=sentence,text=text,rawStart=metric['rawStart'],rawEnd=metric['rawEnd'],
    gainDb=gain,requestedGainDb=requested,localTruePeakBeforeDbtp=tp,localPredictedTruePeakAfterDbtp=tp+gain,
    gainRangeSamples48=[lo,li,ro,ri],globalGainRangeSamples48=[scene['startFrame']*800+v for v in [lo,li,ro,ri]],
    beforeQuiet=b,afterQuiet=e,sourceWords=words[begin:end+1],precedingWord=words[begin-1],followingWord=words[end+1],
    beforeSentenceSpeechDbfs=metric['processedSpeechDbfs'],predictedSentenceSpeechDbfs=metric['processedSpeechDbfs']+gain,
    explanation='Only this complete weak sentence is boosted; no syllable leveling, speech fade or timing change. If required, peak safety is restricted to this quiet-bounded range.'))
 clips={};clipfolder=c.O/'sentence-refinement-inputs';clipfolder.mkdir(exist_ok=True)
 with sf.SoundFile(oldfile)as audio:
  for row in rows:
   lo,li,ro,ri=row['globalGainRangeSamples48'];audio.seek(lo);original=audio.read(ri-lo,dtype='float32',always_2d=True)
   points=np.arange(lo,ri);gain=np.full(len(points),row['gainDb'],np.float32);pre=points<li;post=points>=ro
   gain[pre]=row['gainDb']*(points[pre]-lo)/(li-lo-1);gain[post]=row['gainDb']*(1-(points[post]-ro)/(ri-ro-1))
   boosted=original*(10**(gain/20))[:,None]
   file=clipfolder/(row['scene']+'-boosted.wav');safe=clipfolder/(row['scene']+'-safe.wav')
   assert not file.exists()and not safe.exists(),'Preserve prior local candidate'
   sf.write(file,boosted,48000,subtype='FLOAT');required=row['localPredictedTruePeakAfterDbtp']>-2.05
   if required:
    ceiling=10**(-2.8/20)
    a.run(['-threads','2','-filter_threads','2','-i',file,'-af',f'alimiter=limit={ceiling:.12f}:attack=5:release=50:level=0:latency=1','-c:a','pcm_f32le',safe],row['scene']+'-sentence-transient-safety')
    processed,rate=sf.read(safe,dtype='float32',always_2d=True);assert rate==48000 and processed.shape==boosted.shape
   else:processed=boosted;sf.write(safe,processed,48000,subtype='FLOAT')
   assert np.max(abs(processed)-abs(boosted)*(1+.001))<=0
   assert np.max(abs(processed[:240]-original[:240]))<.002 and np.max(abs(processed[-240:]-original[-240:]))<.002
   clips[row['scene']]=processed
   row['localPeakSafety']=dict(enabled=required,ceilingDbfs=-2.8,attackMs=5,releaseMs=50,automaticLevel=False,latencyCompensated=True,
    boostedFile=c.rel(file),boostedSha256=c.sha(file),safeFile=c.rel(safe),safeSha256=c.sha(safe),
    attenuatedMonoSamples=int(np.sum(abs(processed[:,0])<abs(boosted[:,0])-2e-6)),
    currentLocalTruePeakDbtp=a.db(np.max(abs(resample_poly(processed[:,0],4,1)))))
 newfile=c.O/'narration-refined-48k.wav';assert not newfile.exists(),'Preserve an existing refinement candidate before retry'
 total=old['totalSamples'];position=0
 with sf.SoundFile(oldfile)as inp,sf.SoundFile(newfile,'w',samplerate=48000,channels=2,subtype='FLOAT')as out:
  for block in inp.blocks(blocksize=480000,dtype='float32',always_2d=True):
   for row in rows:
    lo,li,ro,ri=row['globalGainRangeSamples48'];left=max(position,lo);right=min(position+len(block),ri)
    if left>=right:continue
    block[left-position:right-position]=clips[row['scene']][left-lo:right-lo]
   out.write(block);position+=len(block)
 assert position==total
 maximum_error=0.;unchanged_error=0.;position=0
 with sf.SoundFile(oldfile)as before,sf.SoundFile(newfile)as after:
  for x,y in zip(before.blocks(blocksize=480000,dtype='float32',always_2d=True),after.blocks(blocksize=480000,dtype='float32',always_2d=True)):
   expected=x.copy();touched=np.zeros(len(x),bool)
   for row in rows:
    lo,li,ro,ri=row['globalGainRangeSamples48'];left=max(position,lo);right=min(position+len(x),ri)
    if left>=right:continue
    expected[left-position:right-position]=clips[row['scene']][left-lo:right-lo];touched[left-position:right-position]=True
   maximum_error=max(maximum_error,float(np.max(abs(expected-y))))
   if (~touched).any():unchanged_error=max(unchanged_error,float(np.max(abs(x[~touched]-y[~touched]))))
   position+=len(x)
 assert maximum_error<2e-6 and unchanged_error==0
 stats=a.loudness(newfile,'narration-refined-loudness')
 assert float(stats['input_tp'])<=-1.5 and -17<=float(stats['input_i'])<=-15
 archive=c.O/'history/pre-sentence-refinement';archive.mkdir(parents=True,exist_ok=True);history=[]
 for name in ['narration-build.json','narration-continuity-review.json','narration-context-flags.json']:
  f=c.O/name;dst=archive/name;assert not dst.exists();shutil.copy2(f,dst);assert c.sha(f)==c.sha(dst);history.append(dict(file=c.rel(dst),sha256=c.sha(dst)))
 join_decisions=[]
 for left,right in [('v7-a04','v7-a05'),('v7-a15','v7-a16'),('v7-a17','v7-a18'),('v7-a19','v7-a20')]:
  row=byid[left];last=row['sentences'][-1];raw,rate=sf.read(c.R/timeline[left]['rawVoiceFile'],dtype='float32')
  start,end=round(last['rawStart']*rate),round(last['rawEnd']*rate);cached=c.read(c.R/al[left]['asrFile']);mask=a.speech_mask(len(raw),rate,cached['words'])
  midpoint=(start+end)//2;parts=[]
  with sf.SoundFile(oldfile)as audio:
   audio.seek(timeline[left]['startFrame']*800);x=audio.read(len(raw)*2,dtype='float32',always_2d=True)[:,0]
  for lo,hi in [(start,midpoint),(midpoint,end)]:
   active=mask[lo:hi];current=np.repeat(active,2)
   parts.append(dict(sourceSpeechDbfs=a.db(a.rms(raw[lo:hi][active])),processedSpeechDbfs=a.db(a.rms(x[lo*2:hi*2][current]))))
  join_decisions.append(dict(previous=left,next=right,finalSentence=last,actualHalfSentenceSpeechLevels=parts,
    decision='No automatic gain change at this scene join: complete paragraph means differ by less than3dB, and last-sentence ending variation originates in the source. Source quiet and source cadence remain; no added scene speech fade exists. Contextual listening remains pending.',gainAppliedDb=0,humanListening='pending'))
 proof=dict(schemaVersion=1,part=1,previousNarrationFile=c.rel(oldfile),previousNarrationSha256=c.sha(oldfile),
  previousBuildSha256=history[0]['sha256'],currentNarrationFile=c.rel(newfile),currentNarrationSha256=c.sha(newfile),
  implementationSha256=c.sha(Path(__file__)),refinements=rows,joins=join_decisions,history=history,
  maximumGainTransferError=maximum_error,allSamplesOutsideTwoQuietBoundedRangesByteEquivalent=True,
  outsideRangesMaximumSampleDifference=unchanged_error,totalSamples=total,voiceSpeed=1,sourcePcmChanged=False,
  additionalPeakLimiter='Only the two quiet-bounded boosted sentences where measured local peaks required it; no global re-limiting.',addedSpeechFade=False,addedSilenceSamples=0,currentMeasurement=stats,
  largestOldCounterfactualAttenuation='9.08dB was source-peak suppression; actual current speech at that window was3.80dB above adjacent median, not a new low region. The unaffected range is sample-identical.',
  humanListening='pending',finalMasterAsr='pending finished captioned master handoff; no new AAC/ASR generated')
 c.save(c.O/'sentence-refinement-review.json',proof)
 updated=copy.deepcopy(old);updated.update(narrationFile=c.rel(newfile),actualNarrationMeasurement=stats,
  sentenceGainRefinement=dict(proof=c.rel(c.O/'sentence-refinement-review.json'),proofSha256=c.sha(c.O/'sentence-refinement-review.json'),implementationSha256=c.sha(Path(__file__)),refinements=rows,originalBuild=history[0]),
  sourceToStemGain=old['sourceToStemGain']+' Two additional complete weak sentences use measured80ms quiet-only constant-gain joins; all other processed samples are exact copies.')
 updated['outputs'].append(dict(file=c.rel(newfile),sha256=c.sha(newfile)));c.save(build_file,updated)
 print(json.dumps(dict(refinedSentences=[dict(scene=x['scene'],line=x['line'],sentence=x['sentence'],gainDb=x['gainDb'])for x in rows],actual=stats,otherSamplesUnchanged=True,joinGainsApplied=0,humanListening='pending')))
if __name__=='__main__':main()
