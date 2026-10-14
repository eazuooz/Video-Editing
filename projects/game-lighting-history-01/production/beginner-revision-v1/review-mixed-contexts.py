"""Independent complete-utterance recognition only for ambiguous mixed text."""
import pathlib,json,datetime,hashlib,collections,runpy,os,uuid,subprocess
import psutil
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';H=pathlib.Path(__file__).parent;O=P/'production/local/continuity-v2';D=O/'mixed-contexts'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def main():
 runpy.run_path(str(H/'production-authority.py'))['require_selected_production']()
 assert not D.exists();D.mkdir()
 texts={f"{s['id']}-p{i+1}":v for s in rd(P/'script/narration.ko.json')['scenes'] for i,v in enumerate(s['lines'])}
 texts.update({g['id']:g['ko'] for g in rd(P/'production/native-guide-design-v2.json')['rows']});texts.update({r['key']:r['ko'] for r in rd(H/'changes.json')['rows']});texts.update({r['id']:r['ko'] for r in rd(H/'native-additions.json')['guideRows']});texts.update({r['key']:r['ko'] for pair in rd(H/'current-policy-changes.json')['pairs'] for r in pair['rows']})
 terms=['작은 색 칸','법선과','거울에 비칠','포톤 매핑','퀘이크의 조명','비스듬한 계단','벽 무늬를 섞어','가려낸 뒤','내부 계산','늘여','세는 방향','잃습니다','제곱 가중치','기여가','바위 요철','일을 보간','같은 광원 좌표','실제 면광원','색 경계','화면 위치별로','법선은 조명','현재 화면의 지버퍼','엔진 구현','직접광 그림자','이웃처럼']
 keys=[k for k,t in texts.items() if any(w in t for w in terms)]
 for k in ['g15','07-p7','09a-p10','08-p10']:
  if k not in keys:keys.append(k)
 plan=rd(O/'plan.json');groups=collections.defaultdict(list)
 for v in plan['voice']:groups[v['key']].append(v)
 assert all(k in groups for k in keys)
 state=dict(startedAt=now(),status='running',keys=keys,completed=[],expectedTextUsedAsPrompt=False,humanListening='pending')
 wr(D/'execution.json',state)
 import soundfile as sf,numpy as np,torch,torchaudio
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 modelpath=next(pathlib.Path('C:/Users/1/.cache/huggingface/hub/models--openai--whisper-large-v3-turbo/snapshots').iterdir())
 model=AutoModelForSpeechSeq2Seq.from_pretrained(str(modelpath),dtype=torch.float16,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to('cuda:0');proc=AutoProcessor.from_pretrained(str(modelpath),local_files_only=True)
 asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=torch.float16,device=0)
 with sf.SoundFile(O/'final-aac-decoded.wav') as f:
  for key in keys:
   parts=[]
   for v in sorted(groups[key],key=lambda v:v['utteranceStartSample']):
    f.seek(v['targetStartSample']*2);parts.append(f.read(v['samples']*2,dtype='float32').mean(axis=1))
   data=np.concatenate(parts);result=asr(dict(raw=torchaudio.functional.resample(torch.from_numpy(data),48000,16000).numpy(),sampling_rate=16000),generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   wr(D/(key+'.json'),dict(key=key,expectedKo=texts[key],completeUtterance=True,source='current final decoded AAC',decodedPcmSha256=hashlib.sha256(data.tobytes()).hexdigest(),pieces=groups[key],**result))
   state['completed'].append(key);wr(D/'execution.json',state);print('DONE',key,flush=True)
 state.update(status='complete-awaiting-direct-review',endedAt=now());wr(D/'execution.json',state)
if __name__=='__main__':
 lease=R/'shared/output/GPU_HANDOFF.json';assert not lease.exists(),'Foreign lease preserved.'
 me=psutil.Process();ancestry={p.pid for p in me.parents()}|{me.pid};visual=rd(O/'pair/visual-execution.json')
 owner=psutil.Process(visual['pid']);assert abs(owner.create_time()-visual['createTime'])<.01
 allowed=ancestry|{owner.pid}|{p.pid for p in owner.parents() if any('assemble-continuity-pair.py' in arg for arg in p.cmdline())}
 foreign=[dict(pid=p.pid,name=p.info['name']) for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower().startswith(('python','train','torchrun')) and p.pid not in allowed]
 assert not foreign,foreign
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip();assert int(raw)>6000,raw
 record=dict(token=str(uuid.uuid4()),project='game-lighting-history-01',state='gpu_granted_to_ambiguous_context_review',coordinator=dict(pid=me.pid,createTime=me.create_time()),researchPaused=False,parallelOwnedNvencPid=visual.get('active',{}).get('pid'))
 with lease.open('x',encoding='utf8') as f:json.dump(record,f,indent=2)
 try:main()
 finally:
  if lease.exists() and rd(lease).get('token')==record['token']:
   record.update(state='released',endedAt=now(),researchRestarts=0);wr(O/'mixed-contexts-gpu-lease.json',record);lease.unlink()
