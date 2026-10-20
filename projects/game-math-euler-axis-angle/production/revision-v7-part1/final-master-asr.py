"""Once-only ASR of the finished captioned master's actual packet-copied AAC."""
from pathlib import Path
import argparse,difflib,hashlib,importlib.util,json,subprocess,time
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v7_final_source_recognizer',H/'voice-review.py');r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
def run(args):
 q=subprocess.run([str(x)for x in args],cwd=c.R,capture_output=True)
 assert q.returncode==0,q.stderr.decode(errors='replace')[-2400:]
 return q.stdout.decode(errors='replace')
def packet_hash(file):
 text=run(['ffmpeg','-v','error','-nostdin','-i',file,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).strip()
 assert text.startswith('SHA256=');return text[7:]
def worker(token):
 plan=c.validate(preserve_pcm=True);c.lease_worker(token)
 input_file=H/'final-asr-input.json';selected=c.read(input_file);master=c.R/selected['master']
 assert(master.name.endswith('.captioned.mp4')or master.name=='part1-captioned.mp4')and c.sha(master)==selected['masterSha256'],'Exact finished captioned master required'
 script=c.P/'script/revision-v7-two-part/part-01.ko.json';assert c.sha(script)==selected['scriptSha256']
 receipt=c.O/'final-master-asr.json'
 if receipt.exists():
  old=c.read(receipt);assert old['masterSha256']==selected['masterSha256']and old['inputSha256']==c.sha(input_file),'Preserve recognition of another final master'
  assert c.sha(c.R/old['extractedAudioFile'])==old['extractedAudioSha256'];print('Reused successful exact-master ASR; no recognition repeated',flush=True);return
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',master]))
 video=next(s for s in probe['streams']if s['codec_type']=='video');audio=next(s for s in probe['streams']if s['codec_type']=='audio')
 assert(video['width'],video['height'],video['r_frame_rate'])==(1920,1080,'60/1')
 assert audio['codec_name']=='aac'and int(audio['sample_rate'])==48000 and audio['channels']==2
 mix_receipt=c.O/'audio-build.json';mix=c.read(mix_receipt);assert c.sha(mix_receipt)==selected['audioBuildSha256']
 measured=c.R/mix['encodedAudio'];assert any(x['file']==mix['encodedAudio']and c.sha(measured)==x['sha256']for x in mix['outputs'])
 extracted=c.O/'final-master-audio.m4a';assert not extracted.exists(),'Inspect preserved unreceipted master audio before a selected retry'
 run(['ffmpeg','-hide_banner','-loglevel','warning','-nostdin','-n','-i',master,'-map','0:a:0','-vn','-c:a','copy','-movflags','+faststart',extracted])
 payload_master=packet_hash(master);payload_extracted=packet_hash(extracted);payload_measured=packet_hash(measured)
 assert payload_master==payload_extracted==payload_measured,'The finished master must contain the actually measured AAC payload, without re-encoding'
 c.save(c.O/'final-master-audio-provenance.json',dict(master=c.rel(master),masterSha256=selected['masterSha256'],extractedAudio=c.rel(extracted),extractedSha256=c.sha(extracted),measuredMix=c.rel(measured),measuredMixSha256=c.sha(measured),packetPayloadSha256=payload_master,threePacketPayloadsIdentical=True,audioBuildSha256=c.sha(mix_receipt),videoDimensions=[1920,1080],fps=60,audioCodec='aac',sampleRate=48000,channels=2))
 c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'],'final-master-ASR-worker')
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 local=r.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
 r.suppress_unused_encoder_attention_retention(model);model.to('cuda:0');processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
 transcriber=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
 print('Recognizing actual final-master AAC once; expected transcript is not supplied to the model',flush=True)
 result=transcriber(str(extracted),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 expected=' '.join(line for scene in c.read(script)['scenes']for line in scene['lines']);a,b=r.normalized(expected),r.normalized(result['text']);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
 c.save(receipt,dict(schemaVersion=1,part=1,kind='Current final captioned master AAC whole-file recognition; separate from source ASR',
  inputSha256=c.sha(input_file),master=c.rel(master),masterSha256=selected['masterSha256'],extractedAudioFile=c.rel(extracted),extractedAudioSha256=c.sha(extracted),
  aacPacketPayloadSha256=payload_master,audioBuildSha256=c.sha(mix_receipt),approvedScriptSha256=c.sha(script),recognizer=plan['asrIdentity'],configuration=r.CONFIG,
  expected=expected,text=result['text'],words=result['chunks'],similarity=matcher.ratio(),
  differences=[dict(kind=t,expected=a[i:j],recognized=b[k:l])for t,i,j,k,l in matcher.get_opcodes()if t!='equal'],
  recognizedAt=time.time(),expectedTextPrompt=None,sourceAsrNotUsedAsFinalMixApproval=True,completeDirectFinalTextReview='pending',humanWholeListening='pending',actualVoiceVisualPace='pending'))
 print('Whole current-master ASR cached; direct complete text comparison and encoded continuity remain pending',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--gpu-approved',action='store_true');p.add_argument('--worker');x=p.parse_args()
 if x.worker:return worker(x.worker)
 assert x.gpu_approved,'Finished-master handoff from root required'
 plan=c.validate();s=plan['resources']['sourceAsr'];c.run_worker('final-master-asr',Path(__file__).resolve(),s['allocatorCapMiB'],s['minimumFreeMiB'])
 final=c.O/'final-master-asr-execution.json';d=c.read(final);d['state']='complete'if d.get('returnCode')==0 else'failed';d['terminalStateFinalizedFromReturnCode']=True;c.save(final,d)
if __name__=='__main__':main()
