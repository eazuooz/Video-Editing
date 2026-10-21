"""One explicitly authorized m07L02 value-preserving pronunciation repair."""
from pathlib import Path
import argparse,hashlib,importlib.util,random,time
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_alias_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_alias_levels',H/'voice-render.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
def worker(token):
 plan=c.validate();c.lease_worker(token);selection=c.read(H/'voice-pronunciation-alias.json');source=c.read(c.O/'tts-current.json');original=source['scenes'][6]['lines'][1]
 assert selection['scene']=='m07'and selection['line']==2 and selection['approvedScriptSha256']==c.APPROVED and selection['sourceReceiptSha256']==c.sha(c.O/'tts-current.json')
 script=c.read(H/'voice-input.json')['scenes'][6]['lines'][1];assert script.count(selection['displayPhrase'])==1 and selection['displayPhrase']=='이분의 일입니다'and selection['spokenPhrase']=='영 점 오입니다'
 text=script.replace(selection['displayPhrase'],selection['spokenPhrase']);ident='m07.L02.alias1';file=c.O/'repairs/m07.L02'/(ident+'.wav');assert not file.exists()
 c.wait_memory(plan['resources']['tts']['minimumFreeMiB'])
 import numpy as np,soundfile as sf,torch
 from qwen_tts import Qwen3TTSModel
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['tts']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 tts=c.read(H/'voice-tts-manifest.json')['tts'];model=Qwen3TTSModel.from_pretrained(str(c.R/tts['model']),device_map='cuda:0',dtype=torch.bfloat16)
 prompt=model.create_voice_clone_prompt(ref_audio=str(c.R/tts['reference']),ref_text=(c.R/tts['referenceText']).read_text(encoding='utf8').strip(),x_vector_only_mode=False)
 seed=selection['seed'];random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);torch.cuda.manual_seed_all(seed);began=time.time()
 print('Generate exactly one scoped1/2=0.5 pronunciation-alias candidate',ident,'seed',seed,flush=True)
 audio,rate=model.generate_voice_clone(text=[text],language='Korean',voice_clone_prompt=prompt,non_streaming_mode=True,max_new_tokens=tts['maxNewTokens'])
 raw=np.asarray(audio[0],dtype=np.float32);assert rate==24000 and np.isfinite(raw).all();sf.write(file,raw,rate,subtype='FLOAT');before=v.level_measure(raw,rate,tts['lineLevelEqualization'])
 gain=float(np.clip(-22-before['speechFrameMedianDbfs'],-12,12));processed=raw*np.float32(10**(gain/20));after=v.level_measure(processed,rate,tts['lineLevelEqualization'])
 row=dict(id=ident,scene='m07',line=2,attempt='one separately authorized value-preserving pronunciation repair after2same-phrase candidates',seed=seed,
  file=c.rel(file),sha256=c.sha(file),textSha256=original['textSha256'],ttsTextSha256=hashlib.sha256(text.encode()).hexdigest(),ttsText=text,
  pronunciationAlias=dict(file=c.rel(H/'voice-pronunciation-alias.json'),sha256=c.sha(H/'voice-pronunciation-alias.json'),displayPhrase=selection['displayPhrase'],spokenPhrase=selection['spokenPhrase'],
   scope='Onlym07.L02;exact1/2=0.5;not a general wrong-number normalization',displayTextUnchanged=True),
  originalTake=original['takeFile'],originalTakeSha256=original['takeSha256'],originalSeed='not explicitly set/captured; no exact-seed claim',identitySha256=plan['identitySha256'],
  samples=len(raw),sampleRate=rate,seconds=len(raw)/rate,originalSeconds=(original['endSample']-original['startSample'])/rate,
  actualDurationRatio=len(raw)/(original['endSample']-original['startSample']),gainDb=gain,before=before,after=after,
  rawFloatPeak=float(abs(raw).max()),normalizedFloatPeak=float(abs(processed).max()),normalizedSamplesOutsideUnitRange=int(np.sum(abs(processed)>=1)),
  generationParameters=dict(language='Korean',nonStreaming=True,maxNewTokens=tts['maxNewTokens'],batchSize=1),sourceSpeed=1,elapsedSeconds=time.time()-began,selected=False,humanListening='pending')
 data=c.read(c.O/'retake-candidates.json');assert len(data['candidates'])==2;data['candidates'].append(row);data['additionalPronunciationRepair']=row['pronunciationAlias'];c.save(c.O/'retake-candidates.json',data)
 print('Scoped alias candidate complete',row['seconds'],'seconds',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--worker',required=True);x=p.parse_args();worker(x.worker)
