"""Same approved model/reference on CPU; never acquire or touch the foreign GPU."""
import os,sys,argparse,time
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ['OMP_NUM_THREADS']='8'
from prepare import *
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--only',nargs='*',default=[]);args=ap.parse_args()
 ctl=read(ROOT/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['conceptExamplesRevision20261116'];assert ctl['ttsAuthorized']
 sys.path.insert(0,str(ROOT/'qwen3-tts'));import render_narration as q
 q.load_tts_dependencies();q.torch.set_num_threads(8);q.INFERENCE_DEVICE='cpu';q.MAX_RENDER_ATTEMPTS=4;q.MAX_NEW_TOKENS=512
 q.MODEL_DIR=ROOT/'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base';q.REFERENCE=ROOT/'shared/voice-reference/reference-15-35s.wav';q.REFERENCE_TEXT_PATH=ROOT/'shared/voice-reference/reference-15-35s.ko.txt';q.CHUNK_DIR=HERE/'local/voice/raw'
 texts=read(HERE/'local/voice/take-texts.json') if (HERE/'local/voice/take-texts.json').exists() else {};previous={x['key']:x for x in read(HERE/'voice.json')['items']};history=HERE/'local/voice/history';history.mkdir(exist_ok=True)
 rows=[s for e in read(HERE/'plan.json')['episodes'] for s in e['inserts'] if not args.only or s['key'] in args.only];items=[]
 for s in rows:
  path=q.CHUNK_DIR/(s['key']+'.wav');text=' '.join(s['ko']);record=texts.get(s['key'],{})
  current=path.exists() and record.get('sha256')==sha(path) and record.get('text')==text
  stale=previous[s['key']].get('contentCurrent',True)==False and not current
  if path.exists() and (stale or q.needs_render(path)):
   target=history/(s['key']+'-'+sha(path)[:16]+'.wav');assert path.resolve().is_relative_to(HERE.resolve()) and target.resolve().is_relative_to(HERE.resolve())
   if not target.exists():path.rename(target)
   else:path.unlink()
  items.append(q.RenderItem(s['key'],text,path))
 before_hashes={i.key:sha(i.path) if i.path.exists() else None for i in items}
 before=time.time();q.render_chunks(items,1)
 for item in items:
  digest=sha(item.path);device=texts.get(item.key,{}).get('device','cuda-initial-take') if before_hashes[item.key]==digest else 'cpu'
  texts[item.key]=dict(text=item.text,sha256=digest,device=device,model=str(q.MODEL_DIR),referenceSha256=sha(q.REFERENCE))
 save(HERE/'local/voice/take-texts.json',texts)
 save(HERE/'cpu-voice.json',dict(status='selected-takes-generated',keys=[i.key for i in items],wallSeconds=time.time()-before,device='cpu',cudaVisibleDevices='',sameApprovedModel=True,originalLectureVoiceUntouched=True))
 print('CPU bridge checkpoint saved',round(time.time()-before,1),'seconds',flush=True)
if __name__=='__main__':main()
