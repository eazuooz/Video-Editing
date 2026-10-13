"""Recognize each current mixed chapter once, then require direct comparison."""
import pathlib,json,hashlib,datetime,os,sys,collections
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01';F=P/'production/local/final-edit-v1';O=F/'mixed-asr'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def wr(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 assert not (O/'execution.json').exists(),'Preserve once-only recognition; inspect results.'
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['publishingAuthorization']['privateUploadForMobileReview']
 plan=rd(F/'plan.json');mix=rd(F/'mix-execution.json');assert mix['status']=='complete-awaiting-current-mixed-ASR' and mix['outputs']['final-mix.wav']==sh(F/'final-mix.wav')
 sys.path.insert(0,str(R/'qwen3-tts'))
 from gpu_tts_hold import check_gpu_tts_hold
 from gpu_handoff_guard import schedule_gpu_handoff
 check_gpu_tts_hold('game-lighting-history-01','cuda:0',False);schedule_gpu_handoff('game-lighting-history-01','cuda:0',False)
 import psutil,soundfile as sf,torch,torchaudio,numpy as np
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 state=dict(status='loading',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),cpuThreads=2,gpuJobs=1,planSha256=sh(F/'plan.json'),mixSha256=sh(F/'final-mix.wav'),expectedTextUsedAsPrompt=False,completed=[],fullDirectReviewComplete=False,humanListening='pending')
 def save():wr(O/'execution.json',state)
 save()
 try:
  modelpath=R/'qwen3-tts/models/whisper-large-v3-turbo';model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cuda:0');proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
  asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device='cuda:0')
  orig={f"{s['id']}-p{i+1}":v for s in rd(P/'script/narration.ko.json')['scenes'] for i,v in enumerate(s['lines'])}
  guides={g['id']:g['ko'] for g in rd(P/'production/native-guide-design-v2.json')['rows']}
  state['status']='running';save()
  with sf.SoundFile(F/'final-mix.wav') as audio:
   sr=audio.samplerate;assert sr==48000
   for i,ch in enumerate(plan['chapters']):
    end=plan['chapters'][i+1]['startFrame'] if i+1<len(plan['chapters']) else plan['frames']-600
    audio.seek(ch['startFrame']*800);data=audio.read((end-ch['startFrame'])*800,dtype='float32').mean(axis=1)
    keys=[]
    for v in sorted(plan['voice'],key=lambda v:v['startFrame']):
     if ch['startFrame']<=v['startFrame']<end and (not keys or keys[-1]!=v['key']):keys.append(v['key'])
    expected=' '.join((guides if k.startswith('g') else orig)[k] for k in keys)
    result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(data),48000,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
    wr(O/(ch['id']+'.json'),dict(chapter=ch['id'],startFrame=ch['startFrame'],endFrame=end,expectedKo=expected,orderedKeys=keys,mixSha256=state['mixSha256'],expectedTextUsedAsPrompt=False,directlyCompared=False,completedAt=now(),**result))
    state['completed'].append(ch['id']);save();print('DONE',ch['id'],flush=True)
  state.update(status='complete-awaiting-direct-review',endedAt=now(),exitCode=0);save()
 except BaseException as e:state.update(status='failed',error=repr(e),endedAt=now());save();raise
if __name__=='__main__':main()
