"""Repair reviewed scenes only, retaining other PCM and its complete-ASR evidence."""
from pathlib import Path
import argparse,json,hashlib,subprocess,sys,os,time,uuid,shutil
import psutil
import soundfile as sf
import numpy as np
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
p=argparse.ArgumentParser();p.add_argument('--scenes',required=True);p.add_argument('--initial-readback',action='store_true');args=p.parse_args()
ids=sorted({s.strip().zfill(2) for s in args.scenes.split(',')});tag='-'.join(ids)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):subprocess.run(args,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
control=read(ROOT/'shared/publishing/video-production-control.json');assert control['selectedVideo']==SLUG
if args.initial_readback:
 assert read(ROOT/f'shared/output/{SLUG}/narration-job/status.json')['status']=='failed'
 assert not list((ROOT/f'shared/output/{SLUG}/unity-production').glob('*/unity.mp4'))
else:
 assert read(ROOT/f'shared/output/{SLUG}/unity-production/job-status.json')['status']=='complete-pending-visual-review'
m=read(ROOT/f'projects/{SLUG}/project.json');out=ROOT/m['tts']['outputDir'];stem=m['tts']['filenameStem']
script=read(ROOT/m['paths']['script']);known=[s['id'] for s in script['scenes']];assert set(ids)<=set(known)
work=ROOT/f'shared/output/{SLUG}/narration-repair-{tag}';work.mkdir(exist_ok=True)
assert not (work/'receipt.json').exists(),'Repair already recorded; inspect rather than repeat'
before=work/'before';before.mkdir(exist_ok=True)
snapshot={sid:sha(out/'chunks'/f'{sid}-scene.wav') for sid in known}
if not args.initial_readback:
 for sid in known:assert read(out/'asr'/f'{sid}.json')['audio_sha256']==snapshot[sid]
for suffix in ['.wav','.timing.json','.asr-review.txt','.asr-review.timestamps.json','.srt','.en.srt']:
 f=out/(stem+suffix)
 if args.initial_readback and not f.exists():continue
 if (before/f.name).exists():assert sha(before/f.name)==sha(f),'Prior repair snapshot differs; inspect interrupted job'
 else:shutil.copy2(f,before/f.name)
if not args.initial_readback:
 for sid in ids:
  src=out/'asr'/f'{sid}.json';dst=before/f'{sid}-asr.json'
  if dst.exists():assert sha(src)==sha(dst),'Prior ASR snapshot differs'
  else:shutil.copy2(src,dst)
lease=ROOT/'shared/output/GPU_HANDOFF.json';assert not lease.exists()
me=psutil.Process();ancestors={x.pid for x in me.parents()};foreign=[x.pid for x in psutil.process_iter(['pid','name']) if (x.info['name'] or '').lower().startswith(('python','train','torchrun')) and x.pid!=me.pid and x.pid not in ancestors];assert not foreign,foreign
gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,memory.total,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip().split(',')
name,total,free,util=[x.strip() for x in gpu]
# Desktop/Unity compositor activity on this workstation remains around24%
# after all12 captures finish. No foreign Python/training job is present above.
# Preserve11GB free memory and reject a busy compute device; do not stop apps.
assert '5070 Ti' in name and int(total)>=16000 and int(free)>=11000 and int(util)<40
token=str(uuid.uuid4());record={'schemaVersion':1,'token':token,'project':SLUG,'state':'gpu_granted_to_tts','coordinator':{'pid':me.pid,'createTime':me.create_time()},'researchPaused':False,'noForeignTrainingProcess':True,'gpuBefore':{'freeMiB':int(free),'utilizationPercent':int(util)},'requestedAt':time.time()}
with lease.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
try:
 run([sys.executable,'-X','utf8','production/'+SLUG+'/run-narration.py','--render-child','--force-scenes='+','.join(ids)])
 after={sid:sha(out/'chunks'/f'{sid}-scene.wav') for sid in known}
 assert all(after[sid]==snapshot[sid] for sid in known if sid not in ids),'Unselected PCM changed'
 run([sys.executable,'-X','utf8','qwen3-tts/review_project_narration.py','--project',SLUG]+([] if args.initial_readback else ['--scenes',','.join(ids)]))
 run([sys.executable,'-X','utf8','qwen3-tts/build_translated_srt.py','--project',SLUG,'--language','en'])
 run([sys.executable,'-X','utf8','qwen3-tts/build_project_timing.py','--project',SLUG])
 timing=read(out/(stem+'.timing.json'));oldtiming=read(before/(stem+'.timing.json'));chunks=[];texts=[];evidence=[]
 retained=[]
 with sf.SoundFile(before/(stem+'.wav')) as oldaudio,sf.SoundFile(out/(stem+'.wav')) as newaudio:
  assert oldaudio.samplerate==newaudio.samplerate
  for sid in known:
   if sid in ids:continue
   oldorigin=next(e['start'] for e in oldtiming['entries'] if e['scene_id']==sid)
   neworigin=next(e['start'] for e in timing['entries'] if e['scene_id']==sid)
   count=sf.info(out/'chunks'/f'{sid}-scene.wav').frames
   oldaudio.seek(round(oldorigin*oldaudio.samplerate));newaudio.seek(round(neworigin*newaudio.samplerate))
   a=oldaudio.read(count,dtype='int16');b=newaudio.read(count,dtype='int16');assert np.array_equal(a,b),'Retained decoded PCM differs: '+sid
   retained.append({'scene':sid,'oldOrigin':oldorigin,'newOrigin':neworigin,'samples':count,'decodedPcmSha256':hashlib.sha256(a.tobytes()).hexdigest(),'exactEqual':True})
 for sid in known:
  cache=read(out/'asr'/f'{sid}.json');assert cache['audio_sha256']==after[sid]
  origin=next(e['start'] for e in timing['entries'] if e['scene_id']==sid)
  for w in cache['words']:
   a,b=w['timestamp'];assert a is not None and b is not None
   chunks.append({'text':w['text'],'timestamp':[a+origin,b+origin]})
  texts.append(cache['text']);evidence.append({'scene':sid,'pcmSha256':after[sid],'asrCacheSha256':sha(out/'asr'/f'{sid}.json'),'status':'initial-complete-scene-readback' if args.initial_readback else 'repaired-and-retranscribed' if sid in ids else 'unchanged-PCM-complete-ASR-reused','origin':origin})
 transcript=' '.join(texts);current={'audio_sha256':sha(out/(stem+'.wav')),'audio':str(out/(stem+'.wav')),'timestampMode':'word','text':transcript,'chunks':chunks,'method':'initial complete read-back in complete scene contexts after monolithic native crash' if args.initial_readback else 'complete prior read-back retained for identical PCM; new ASR for repaired scenes only','previousCompleteAsrSha256':None if args.initial_readback else sha(before/(stem+'.asr-review.timestamps.json')),'sceneEvidence':evidence}
 (out/(stem+'.asr-review.timestamps.json')).write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (out/(stem+'.asr-review.txt')).write_text(transcript+'\n',encoding='utf-8')
 (work/'receipt.json').write_text(json.dumps({'scenes':ids,'beforeHashes':snapshot,'afterHashes':after,'retainedPcmUnchanged':True,'decodedRetainedRanges':retained,'completeTextReview':'pending','sceneEvidence':evidence},indent=2)+'\n',encoding='utf-8')
 if args.initial_readback:
  statuspath=ROOT/f'shared/output/{SLUG}/narration-job/status.json';status=read(statuspath);status['initialFailure']=status.pop('error');status.update(status='complete-pending-content-review',stage='done',wavSha256=sha(out/(stem+'.wav')),recovery=str(work.relative_to(ROOT)).replace('\\','/'));statuspath.write_text(json.dumps(status,indent=2)+'\n',encoding='utf-8')
 print('Repair complete; review current full text and affected joins before alignment.')
finally:
 if lease.exists() and read(lease).get('token')==token:
  record.update(state='released',finishedAt=time.time(),researchRestarts=0);(work/'gpu-lease-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');lease.unlink()
