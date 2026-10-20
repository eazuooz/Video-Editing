"""One approved-reference Qwen scene batch; no pacing inserts or automatic retakes."""
import argparse,hashlib,importlib.util,time
from pathlib import Path
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_audio_common',H/'audio-common.py');c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
def worker(token):
 plan=c.validate(preserve_pcm=True);c.lease_worker(token)
 c.wait_memory(plan['resources']['tts']['minimumFreeMiB'],'tts-worker')
 import numpy as np,soundfile as sf,torch
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2)
 torch.cuda.set_per_process_memory_fraction(plan['resources']['tts']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 tts=c.read(H/'voice-tts-manifest.json')['tts'];script=c.read(H/'voice-input.json')
 chunks=c.O/'chunks';chunks.mkdir(parents=True,exist_ok=True)
 receipt=c.O/'tts-current.json'
 done=c.read(receipt) if receipt.exists() else dict(schemaVersion=1,revision='v7-part1',part=1,scenes=[])
 existing={s['id']:s for s in done['scenes']};model=None;prompt=None
 identity=plan['identitySha256']
 for scene in script['scenes']:
  c.selected();text=' '.join(scene['lines']);text_hash=hashlib.sha256(text.encode('utf-8')).hexdigest()
  file=chunks/(scene['id']+'-scene.wav')
  if scene['id'] in existing:
   row=existing[scene['id']]
   assert row['textSha256']==text_hash and row['identitySha256']==identity and c.sha(file)==row['sha256'],'Preserve and inspect a mismatched successful chunk'
   print('Reused exact successful scene PCM',scene['id'],flush=True);continue
  assert not file.exists(),'Unreceipted output is preserved; inspect it rather than overwriting'
  if model is None:
   model=Qwen3TTSModel.from_pretrained(str(c.R/tts['model']),device_map='cuda:0',dtype=torch.bfloat16)
   prompt=model.create_voice_clone_prompt(ref_audio=str(c.R/tts['reference']),ref_text=(c.R/tts['referenceText']).read_text(encoding='utf-8').strip(),x_vector_only_mode=False)
  print('Rendering continuous scene',scene['id'],len(text),'characters',flush=True)
  started=time.time()
  audios,rate=model.generate_voice_clone(text=[text],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=tts['maxNewTokens'])
  raw=np.asarray(audios[0],dtype=np.float32)
  assert raw.ndim==1 and len(raw)>0 and np.isfinite(raw).all()
  sf.write(file,raw,rate,subtype='PCM_16')
  check,actual_rate=sf.read(file,dtype='float32')
  assert actual_rate==rate==24000 and len(check)==len(raw)
  row=dict(id=scene['id'],file=c.rel(file),sha256=c.sha(file),textSha256=text_hash,identitySha256=identity,sampleRate=rate,samples=len(raw),seconds=len(raw)/rate,rawFloatPeak=float(np.max(np.abs(raw))),rawOutOfPcm16RangeCount=int(np.sum(np.abs(raw)>=1)),encodedHardClipSampleCount=int(np.sum(np.abs(check)>=32766/32768)),peakAllocatedMiB=torch.cuda.max_memory_allocated()/1048576,peakReservedMiB=torch.cuda.max_memory_reserved()/1048576,elapsedSeconds=time.time()-started,generatedAt=time.time(),contentReview='pending complete source ASR and direct comparison',humanListening='pending')
  done['scenes'].append(row);done.update(status='partial',part=1,identitySha256=identity,sceneCount=len(done['scenes']));c.save(receipt,done)
  print('Completed',scene['id'],row['seconds'],'seconds',flush=True)
  del audios,raw,check
 c.validate(preserve_pcm=True)
 assert len(done['scenes'])==21
 done.update(status='complete-source-ASR-pending',sceneCount=21,humanWholeListening='pending')
 c.save(receipt,done)
 c.save(c.O/'current-pcm.json',dict(schemaVersion=1,part=1,revision='v7-part1',status='current21-source-ASR-pending',inputs=plan['immutableInputs'],scenes=done['scenes'],sourceSpeed=1,addedObservationSilenceSamples=0,sourcePcmAltered=False,humanWholeListening='pending'))
def main():
 a=argparse.ArgumentParser();a.add_argument('--gpu-approved',action='store_true');a.add_argument('--worker');x=a.parse_args()
 if x.worker:return worker(x.worker)
 assert x.gpu_approved,'Root serialized GPU-start message required'
 plan=c.validate();r=plan['resources']['tts']
 c.run_worker('tts',Path(__file__).resolve(),r['allocatorCapMiB'],r['minimumFreeMiB'])
if __name__=='__main__':main()

