"""Recognize each changed utterance once; untouched PCM keeps its prior review."""
import pathlib, json, hashlib, datetime, os, sys, argparse
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01'
O=P/'production/local/beginner-revision-v1/voice-asr'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 global O
 parser=argparse.ArgumentParser();parser.add_argument('--device',choices=['cpu','cuda:0'],default='cpu');parser.add_argument('--repairs',action='store_true');parser.add_argument('--native',action='store_true');args=parser.parse_args()
 assert not (args.repairs and args.native)
 if args.native:
  O=P/'production/local/beginner-revision-v1/native-guides-asr'
  assert rd(P/'production/local/beginner-revision-v1/native-guides/execution.json')['status']=='complete-exit0'
 if args.repairs:
  O=P/'production/local/beginner-revision-v1/voice-asr-repairs'
  assert rd(P/'production/local/beginner-revision-v1/terminology-r1/execution.json')['status']=='complete-exit0'
 assert not (O/'execution.json').exists(),'Inspect saved recognition; do not repeat successful work.'
 assert rd(P/'production/local/beginner-revision-v1/tts/execution.json')['status']=='complete-exit0'
 assert rd(R/'shared/publishing/video-production-control.json')['mode']=='one-video-autonomous-until-private-upload'
 assert rd(P/'production/checkpoint.json')['beginnerRevision']['privateUploadAuthorized']
 changes=rd(P/'production/beginner-revision-v1/changes.json');assert changes['completeKoEnDirectReview']
 sys.path.insert(0,str(R/'qwen3-tts'))
 from gpu_tts_hold import check_gpu_tts_hold
 from gpu_handoff_guard import schedule_gpu_handoff
 check_gpu_tts_hold('game-lighting-history-01',args.device);schedule_gpu_handoff('game-lighting-history-01',args.device)
 import torch,torchaudio,soundfile as sf,psutil
 from transformers import AutoModelForSpeechSeq2Seq,AutoProcessor,pipeline
 torch.set_num_threads(2);torch.set_num_interop_threads(1)
 state=dict(status='loading',pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),startedAt=now(),device=args.device,gpuJobs=int(args.device.startswith('cuda')),cpuThreads=2,completed=[],expectedTextUsedAsPrompt=False,directReviewComplete=False,humanListening='pending')
 def save():write(O/'execution.json',state)
 save()
 ck=rd(P/'production/checkpoint.json');ck.update(stage='beginner-changed-voice-asr',activeOwnedHeavyJob={**state,'execution':(O/'execution.json').relative_to(R).as_posix()});write(P/'production/checkpoint.json',ck)
 try:
  path=R/'qwen3-tts/models/whisper-large-v3-turbo'
  dtype=torch.float16 if args.device.startswith('cuda') else torch.float32
  model=AutoModelForSpeechSeq2Seq.from_pretrained(str(path),dtype=dtype,low_cpu_mem_usage=True,use_safetensors=True,local_files_only=True).to(args.device)
  proc=AutoProcessor.from_pretrained(str(path),local_files_only=True)
  asr=pipeline('automatic-speech-recognition',model=model,tokenizer=proc.tokenizer,feature_extractor=proc.feature_extractor,dtype=dtype,device=args.device)
  state['status']='running';save()
  rows=[r for r in changes['rows'] if r.get('audioRepair')] if args.repairs else changes['rows']
  if args.native:rows=[dict(key=r['id'],ttsSceneId=r['id'],ko=r['ko']) for r in rd(P/'production/beginner-revision-v1/native-additions.json')['guideRows']]
  if args.repairs:assert {r['key'] for r in rows}=={'07-p6','09-p9','g29'}
  for row in rows:
   file=R/row['replacementAudioPath'] if args.repairs else R/f"shared/output/narration/game-lighting-history-01/beginner-revision-v1/chunks/{row['ttsSceneId']}-scene.wav"
   if args.native:file=R/f"shared/output/narration/game-lighting-history-01/beginner-native-additions/chunks/{row['ttsSceneId']}-scene.wav"
   data,sr=sf.read(file,dtype='float32');assert data.ndim==1 and sr==24000
   audio=torchaudio.functional.resample(torch.from_numpy(data),sr,16000).numpy()
   result=asr({'raw':audio,'sampling_rate':16000},generate_kwargs={'language':'korean','task':'transcribe'},return_timestamps='word')
   write(O/(row['key']+'.json'),dict(key=row['key'],ttsSceneId=row['ttsSceneId'],audioPath=file.relative_to(R).as_posix(),audioSha256=sha(file),seconds=len(data)/sr,samples=len(data),sampleRate=sr,expectedKo=row['ko'],expectedTextUsedAsPrompt=False,directlyCompared=False,**result))
   state['completed'].append(row['key']);save();print('DONE',row['key'],flush=True)
  state.update(status='complete-awaiting-direct-review',finishedAt=now(),exitCode=0);save()
 except BaseException as exc:state.update(status='failed',error=repr(exc),finishedAt=now());save();raise
 finally:
  ck=rd(P/'production/checkpoint.json')
  if (ck.get('activeOwnedHeavyJob') or {}).get('pid')==state['pid']:
   ck['activeOwnedHeavyJob']=None;ck['beginnerRevision']['voiceAsrExecution']=(O/'execution.json').relative_to(R).as_posix();write(P/'production/checkpoint.json',ck)
if __name__=='__main__':main()
