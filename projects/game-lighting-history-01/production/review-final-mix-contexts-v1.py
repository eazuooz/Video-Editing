"""Two complete mixed contexts for chunk-edge greetings; no whole-ASR repeat."""
import pathlib,json,hashlib,os,sys,datetime
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';O=P/'production/local/final-edit-v1';D=O/'mixed-contexts'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 assert not D.exists();assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(O/'mixed-asr/execution.json')['status']=='complete-awaiting-direct-review'
 sys.path.insert(0,str(R/'qwen3-tts'))
 from gpu_tts_hold import check_gpu_tts_hold
 from gpu_handoff_guard import schedule_gpu_handoff
 # GPU admission was refused before state/model creation; preserve foreign research.
 check_gpu_tts_hold('game-lighting-history-01','cpu',False)
 import psutil,torch,torchaudio,soundfile as sf,numpy as np
 from transformers import AutoProcessor,AutoModelForSpeechSeq2Seq,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1);D.mkdir()
 state=dict(status='running',pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),startedAt=now(),cpuThreads=2,gpuJobs=0,mixSha256=rd(O/'mixed-asr/execution.json')['mixSha256'],completed=[])
 wr(D/'execution.json',state)
 m=R/'qwen3-tts/models/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(str(m),dtype=torch.float32,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cpu');p=AutoProcessor.from_pretrained(str(m),local_files_only=True);asr=pipeline('automatic-speech-recognition',model=model,tokenizer=p.tokenizer,feature_extractor=p.feature_extractor,dtype=torch.float32,device='cpu')
 plan=rd(O/'plan.json');guides={g['id']:g['ko'] for g in rd(P/'production/native-guide-design-v2.json')['rows']}
 with sf.SoundFile(O/'final-mix.wav') as audio, sf.SoundFile(O/'placed-narration.wav') as voice:
  for key,offset in [('g25',0),('g30',39.5)]:
   v=next(v for v in plan['voice'] if v['key']==key);a=v['startFrame']/60+offset;z=v['startFrame']/60+v['samples']/24000+.22
   audio.seek(round(a*48000));data=audio.read(round((z-a)*48000),dtype='float32').mean(axis=1)
   result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(data),48000,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   # Verify narration-free region where whole recognition invented an ending.
   tail_a=v['startFrame']/60+v['samples']/24000;tail_z=55615/60 if key=='g25' else 80598/60
   voice.seek(round(tail_a*voice.samplerate));tail=voice.read(round((tail_z-tail_a)*voice.samplerate),dtype='int32')
   wr(D/(key+'.json'),dict(key=key,startSeconds=a,endSeconds=z,expectedContext=guides[key],mixSha256=state['mixSha256'],expectedTextUsedAsPrompt=False,narrationTailInterval=[tail_a,tail_z],narrationTailNonzeroSamples=int(np.count_nonzero(tail)),directlyCompared=False,**result));state['completed'].append(key);wr(D/'execution.json',state);print('DONE',key,flush=True)
 state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0);wr(D/'execution.json',state)
if __name__=='__main__':main()
