"""One explicitly handed-off finished V8 AAC recognition; never a source rerun."""
from pathlib import Path
from fractions import Fraction
import argparse,difflib,importlib.util,json,subprocess,sys,time,uuid
import psutil
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_final_audio_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_final_whisper_utilities',c.P/'production/revision-v7-part1/voice-review.py');u=importlib.util.module_from_spec(s);s.loader.exec_module(u)
def run(args):
 p=subprocess.run([str(x)for x in args],cwd=c.R,capture_output=True);assert p.returncode==0,p.stderr.decode(errors='replace')[-2400:];return p.stdout.decode(errors='replace')
def payload(file):
 value=run(['ffmpeg','-v','error','-nostdin','-i',file,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).strip();assert value.startswith('SHA256=');return value[7:]
def worker(token):
 plan=c.validate();c.lease_worker(token);inp=H/'audio-final-input.json';selected=c.read(inp)
 master=c.R/selected['master'];assert c.sha(master)==selected['masterSha256'];assert selected['approvedScriptSha256']==c.APPROVED
 timeline=c.R/selected['timeline'];assert c.sha(timeline)==selected['timelineSha256'];t=c.read(timeline)
 report=c.R/selected['mixReport'];assert c.sha(report)==selected['mixReportSha256']
 measured=c.R/selected['measuredAac'];assert c.sha(measured)==selected['measuredAacSha256']
 receipt=c.O/'final-aac-asr.json'
 if receipt.exists():
  previous=c.read(receipt);assert previous['inputSha256']==c.sha(inp)and previous['masterSha256']==selected['masterSha256']
  assert c.sha(c.R/previous['actualMasterAac'])==previous['actualMasterAacSha256'];print('Exact successful final AAC recognition reused; no second inference',flush=True);return
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-of','json',master]));video=next(x for x in probe['streams']if x['codec_type']=='video');audio=next(x for x in probe['streams']if x['codec_type']=='audio')
 assert(video['width'],video['height'])==(1920,1080)and Fraction(video['avg_frame_rate'])==60 and int(video['nb_frames'])==t['totalFrames']
 assert audio['codec_name']=='aac'and int(audio['sample_rate'])==48000 and audio['channels']==2
 extracted=c.O/'actual-final-aac.m4a';assert not extracted.exists(),'Preserve and inspect unreceipted extracted AAC'
 run(['ffmpeg','-v','warning','-nostdin','-n','-i',master,'-map','0:a:0','-vn','-c:a','copy','-movflags','+faststart',extracted])
 digest=payload(master);assert digest==payload(extracted)==payload(measured),'Current master must contain measured AAC payload without another encode'
 c.save(c.O/'final-aac-provenance.json',dict(master=c.rel(master),masterSha256=selected['masterSha256'],actualMasterAac=c.rel(extracted),actualMasterAacSha256=c.sha(extracted),
  measuredAac=selected['measuredAac'],measuredAacSha256=c.sha(measured),aacPacketPayloadSha256=digest,threePayloadsIdentical=True,inputSha256=c.sha(inp),timelineSha256=c.sha(timeline),mixReportSha256=c.sha(report)))
 c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'])
 import torch
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.cuda.set_per_process_memory_fraction(plan['resources']['sourceAsr']['allocatorCapMiB']*1048576/torch.cuda.get_device_properties(0).total_memory)
 local=u.model_path();assert c.sha(local/'config.json')==plan['asrIdentity']['configSha256']
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(local),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,attn_implementation='eager',local_files_only=True)
 u.suppress_unused_encoder_attention_retention(model);model.to('cuda:0');processor=AutoProcessor.from_pretrained(str(local),local_files_only=True)
 recognizer=pipeline('automatic-speech-recognition',model=model,tokenizer=processor.tokenizer,feature_extractor=processor.feature_extractor,dtype=torch.float16,device='cuda:0',chunk_length_s=25,stride_length_s=3,batch_size=1)
 print('Recognizing actual complete final AAC once; no expected prompt',flush=True)
 result=recognizer(str(extracted),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
 expected=' '.join(p for scene in c.read(H/'voice-input.json')['scenes']for p in scene['lines']);a,b=u.normalized(expected),u.normalized(result['text']);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
 c.save(receipt,dict(revision='orientation-matrix-v8',master=selected['master'],masterSha256=selected['masterSha256'],inputSha256=c.sha(inp),approvedScriptSha256=c.APPROVED,
  actualMasterAac=c.rel(extracted),actualMasterAacSha256=c.sha(extracted),aacPacketPayloadSha256=digest,mixReportSha256=c.sha(report),
  configuration=u.CONFIG,recognizer=plan['asrIdentity'],expected=expected,text=result['text'],words=result['chunks'],similarity=matcher.ratio(),
  differences=[dict(kind=tag,expected=a[i:j],recognized=b[k:l])for tag,i,j,k,l in matcher.get_opcodes()if tag!='equal'],
  expectedPrompt=None,sourceAsrNotUsedAsFinalMixApproval=True,wholeFinalRecognitionCount=1,full76ParagraphDirectReview='pending',humanWholeListening='pending',recognizedAt=time.time()))
 print('Final AAC cached; full76paragraph direct comparison and encoded levels pending',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--worker');p.add_argument('--gpu-approved',action='store_true');x=p.parse_args()
 if x.worker:return worker(x.worker)
 assert x.gpu_approved,'Explicit finished-master SHA and root GPU handoff required';plan=c.validate();assert(H/'audio-final-input.json').exists()
 assert not c.LEASE.exists(),'Preserve another finite GPU owner';before=c.wait_memory(plan['resources']['sourceAsr']['minimumFreeMiB'])
 me=psutil.Process();token=str(uuid.uuid4());state=dict(token=token,project=c.P.name,revision='orientation-matrix-v8',purpose='One finite actual finished AAC recognition',
  coordinator=dict(pid=me.pid,createTime=me.create_time()),state='running',startedAt=time.time(),gpuBefore=before,inputSha256=c.sha(H/'audio-final-input.json'),implementationSha256=c.sha(Path(__file__)),foreignJobsChanged=False)
 with c.LEASE.open('x',encoding='utf8')as f:json.dump(state,f)
 child=None;finished=False
 try:
  with(c.O/'final-aac-asr-worker.log').open('ab')as log:
   child=subprocess.Popen([sys.executable,'-u','-X','utf8',str(Path(__file__).resolve()),'--worker',token],cwd=c.R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   state['workerPid']=child.pid;c.save(c.O/'final-aac-asr-execution.json',state);code=child.wait();state['returnCode']=code
  assert code==0,'Preserve successful cache/extracted audio; inspect actual failed final phase';finished=True
 finally:
  live=child is not None and child.poll()is None;state.update(state='complete'if finished else'owned-worker-still-running'if live else'failed',endedAt=time.time())
  c.save(c.O/'final-aac-asr-execution.json',state)
  if c.LEASE.exists()and c.read(c.LEASE).get('token')==token:
   if live:c.save(c.LEASE,state)
   else:c.LEASE.unlink()
if __name__=='__main__':main()
