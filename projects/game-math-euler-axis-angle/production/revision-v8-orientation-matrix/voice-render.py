"""One approved Qwen paragraph batch; constant line gains, exact scene origins."""
from pathlib import Path
import argparse,hashlib,importlib.util,time
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_paragraph_tts_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def level_measure(x,rate,eq):
 import numpy as np
 n=round(rate*eq['frameMs']/1000);assert len(x)>=n
 frames=x[:len(x)//n*n].reshape(-1,n)
 values=20*np.log10(np.maximum(np.sqrt(np.mean(frames.astype(np.float64)**2,axis=1)),1e-12))
 gate=float(values.max()-eq['gateBelowPeakDb']);active=values>=gate;indices=np.flatnonzero(active)
 return dict(speechFrameMedianDbfs=float(np.median(values[active])),energyGateDbfs=gate,
  activeFrameCount=int(active.sum()),frameCount=len(values),energyGateLeadingSeconds=float(indices[0]*n/rate),
  energyGateTrailingSeconds=float((len(x)-(indices[-1]+1)*n)/rate),
  warning='Relative energy gate is only a level statistic; not phonetic silence, a trim command, or listening approval.')
def worker(token):
 plan=c.validate();c.lease_worker(token);c.wait_memory(plan['resources']['tts']['minimumFreeMiB'])
 import numpy as np,soundfile as sf,torch
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2);cap=plan['resources']['tts']['allocatorCapMiB']
 torch.cuda.set_per_process_memory_fraction(cap*1048576/torch.cuda.get_device_properties(0).total_memory)
 tts=c.read(H/'voice-tts-manifest.json')['tts'];script=c.read(H/'voice-input.json');raw_dir=c.O/'takes';raw_dir.mkdir(parents=True,exist_ok=True)
 receipt=c.O/'paragraph-takes.json';done=c.read(receipt)if receipt.exists()else dict(revision='orientation-matrix-v8',identitySha256=plan['identitySha256'],takes=[])
 assert done['identitySha256']==plan['identitySha256'];existing={r['id']:r for r in done['takes']};model=None;prompt=None
 for scene in script['scenes']:
  for number,text in enumerate(scene['lines'],1):
   c.selected();sid=f"{scene['id']}.L{number:02}";file=raw_dir/(sid+'.wav');text_sha=hashlib.sha256(text.encode()).hexdigest()
   if sid in existing:
    old=existing[sid];assert old['textSha256']==text_sha and c.sha(file)==old['sha256'];print('Reused successful exact paragraph',sid,flush=True);continue
   assert not file.exists(),'Preserve unreceipted take; inspect before a selected repair'
   if model is None:
    model=Qwen3TTSModel.from_pretrained(str(c.R/tts['model']),device_map='cuda:0',dtype=torch.bfloat16)
    prompt=model.create_voice_clone_prompt(ref_audio=str(c.R/tts['reference']),ref_text=(c.R/tts['referenceText']).read_text(encoding='utf8').strip(),x_vector_only_mode=False)
   print('Generating paragraph',sid,len(text),'characters',flush=True);started=time.time()
   audios,rate=model.generate_voice_clone(text=[text],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=tts['maxNewTokens'])
   raw=np.asarray(audios[0],dtype=np.float32);assert raw.ndim==1 and len(raw)>0 and np.isfinite(raw).all()and rate==24000
   sf.write(file,raw,rate,subtype='FLOAT');check,actual_rate=sf.read(file,dtype='float32')
   assert actual_rate==rate and np.array_equal(check,raw)
   row=dict(id=sid,scene=scene['id'],line=number,file=c.rel(file),sha256=c.sha(file),textSha256=text_sha,
    samples=len(raw),sampleRate=rate,seconds=len(raw)/rate,rawFloatPeak=float(abs(raw).max()),rawSamplesOutsideUnitRange=int(np.sum(abs(raw)>=1)),
    peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576,peakReservedMiB=torch.cuda.max_memory_reserved()/1048576,
    elapsedSeconds=time.time()-started,generatedAt=time.time(),sourcePcmPreserved=True,humanListening='pending')
   done['takes'].append(row);existing[sid]=row;done.update(status='partial',takeCount=len(done['takes']));c.save(receipt,done)
   print('Completed paragraph',sid,round(row['seconds'],3),'seconds;',len(done['takes']),'/76',flush=True)
   del audios,raw,check
 assert len(done['takes'])==76;c.validate();done.update(status='complete',takeCount=76);c.save(receipt,done)
 # Separate raw takes stay unchanged. These complete-line constant gains do not
 # modify syllable envelopes, time stretch speech or use an audio limiter.
 eq=tts['lineLevelEqualization'];scenes=[];levels=[];gap=round(tts['lineGapSeconds']*24000);scene_dir=c.O/'scenes';scene_dir.mkdir(exist_ok=True)
 for scene in script['scenes']:
  parts=[];lines=[];cursor=0
  for number,text in enumerate(scene['lines'],1):
   raw=existing[f"{scene['id']}.L{number:02}"];file=c.R/raw['file'];assert c.sha(file)==raw['sha256'];x,rate=sf.read(file,dtype='float32')
   before=level_measure(x,rate,eq);gain=float(np.clip(eq['targetSpeechFrameMedianDbfs']-before['speechFrameMedianDbfs'],-eq['maxGainDb'],eq['maxGainDb']))
   out=x*np.float32(10**(gain/20));after=level_measure(out,rate,eq)
   gap_before=gap if number>1 else 0
   if gap_before:parts.append(np.zeros(gap_before,dtype=np.float32));cursor+=gap_before
   row=dict(line=number,takeFile=raw['file'],takeSha256=raw['sha256'],textSha256=raw['textSha256'],startSample=cursor,endSample=cursor+len(out),
    gapBeforeSamples=gap_before,gainDb=gain,before=before,after=after,processedFloatPeak=float(abs(out).max()),
    gainLimited=abs(gain-(eq['targetSpeechFrameMedianDbfs']-before['speechFrameMedianDbfs']))>1e-6)
   lines.append(row);levels.append(dict(scene=scene['id'],**row));parts.append(out);cursor+=len(out)
  assembled=np.concatenate(parts);target=scene_dir/(scene['id']+'-scene.wav');assert len(assembled)==cursor
  if target.exists():
   old,rate=sf.read(target,dtype='float32');assert rate==24000 and np.array_equal(old,assembled),'Preserve mismatched existing scene'
  else:sf.write(target,assembled,24000,subtype='FLOAT')
  scenes.append(dict(id=scene['id'],file=c.rel(target),sha256=c.sha(target),sampleRate=24000,samples=cursor,seconds=cursor/24000,lines=lines,
   paragraphCount=len(lines),floatPeak=float(abs(assembled).max()),sourceSpeed=1,rawTakesPreserved=True))
  print('Assembled scene',scene['id'],round(cursor/24000,3),'seconds',flush=True)
 before=[x['before']['speechFrameMedianDbfs']for x in levels];after=[x['after']['speechFrameMedianDbfs']for x in levels]
 c.save(c.O/'line-levels.json',dict(revision='orientation-matrix-v8',policy='line-level-takes-v1',parameters=eq,lineGapSeconds=tts['lineGapSeconds'],
  method='50ms frame RMS; active frames are at least maximum frame RMS minus25dB. One constant gain per complete approved paragraph, capped±12dB. Raw FLOAT takes unchanged; assembled FLOAT can retain over-range peaks for explicit downstream headroom review.',
  lineCount=76,lines=levels,lineMedianRangeDb=dict(before=max(before)-min(before),after=max(after)-min(after)),
  maximumProcessedFloatPeak=max(x['processedFloatPeak']for x in levels),voiceSpeed=1,insertedObservationSilenceSamples=0,humanListening='pending'))
 c.save(c.O/'tts-current.json',dict(schemaVersion=1,revision='orientation-matrix-v8',status='complete-source-ASR-pending',sceneCount=13,paragraphCount=76,
  identitySha256=plan['identitySha256'],approvedScriptSha256=c.APPROVED,scenes=scenes,sourceRawSeconds=sum(r['seconds']for r in scenes),
  rawParagraphTakes=c.rel(receipt),rawParagraphTakesSha256=c.sha(receipt),lineLevels=c.rel(c.O/'line-levels.json'),lineLevelsSha256=c.sha(c.O/'line-levels.json'),
  sourceSpeed=1,sceneGapSeconds=0,lineGapSeconds=tts['lineGapSeconds'],addedObservationSilenceSamples=0,humanWholeListening='pending'))
 print('All76 raw paragraphs and13 current scene WAVs ready',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',required=True);x=p.parse_args();worker(x.worker)
