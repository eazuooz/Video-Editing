"""Finite low-cost native scene preflight; never final production or publication."""
from pathlib import Path
import argparse,json,subprocess,shutil,sys,hashlib
from scoped_context import authorization,assert_no_game_apps,ROOT,MEDIA
from batch_job_lock import SerialJobLock

def main():
 p=argparse.ArgumentParser();p.add_argument('topic');p.add_argument('--version',default='v1');a=p.parse_args()
 slug='shorts-'+a.topic
 batch=json.loads((Path(__file__).parent/'batch.json').read_text(encoding='utf-8-sig'))
 if slug not in {r['slug'] for r in batch['projects']}:raise RuntimeError('Outside selected ten')
 authorization(slug);assert_no_game_apps()
 if (ROOT/'shared/output/GPU_HANDOFF.json').exists():raise RuntimeError('Foreign GPU handoff preserved')
 free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(','))
 if free<4800 or util>=35:raise RuntimeError(f'GPU busy: {free}MiB free, {util}%')
 capture=MEDIA/'unity-capture';out=MEDIA/slug/'local'/('unity-preflight-'+a.version)
 if (out/'native-receipt.json').exists():raise RuntimeError('Preserve existing successful preview')
 source=Path(__file__).parent/'unity-source';dest=capture/'Assets/VideoScenes/tech-ten-shorts-20261030'
 with SerialJobLock(slug,'native-preflight'):
  hashes={str(p.relative_to(source)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.is_file()}
  treehash=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()
  snapshot=MEDIA/'native-source-snapshots'/treehash
  if not snapshot.exists():shutil.copytree(source,snapshot)
  shutil.copytree(source,dest,dirs_exist_ok=True)
  jobs=MEDIA/'capture-jobs';jobs.mkdir(exist_ok=True)
  job=jobs/(a.topic+'-preview-'+a.version+'.json')
  job.write_text(json.dumps(dict(topic=a.topic,mode='preview',output=out.as_posix(),stages=[0,1,2],sceneVersion='source-'+treehash[:12],sourceCode=hashes),indent=2))
  log=jobs/(a.topic+'-preview-'+a.version+'.log')
  exe='C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe'
  cmd=[exe,'-batchmode','-projectPath',str(capture),'-executeMethod','Yamyam.TechTen.Editor.TechTenCapture.Run','-techTenJob',str(job),'-logFile',str(log)]
  print(json.dumps({'stage':'native-preflight','topic':a.topic,'log':str(log),'mainEditorPreserved':True}),flush=True)
  r=subprocess.run(cmd,creationflags=subprocess.CREATE_NO_WINDOW)
  if r.returncode or not (out/'native-receipt.json').exists():
   text=log.read_text(encoding='utf-8',errors='replace') if log.exists() else ''
   errors=[s for s in text.splitlines() if any(w in s.lower() for w in ['error cs','exception:','compilation failed','shader error','error:'])]
   print(json.dumps({'exitCode':r.returncode,'errors':errors[-15:],'receipt':False}),flush=True)
   raise SystemExit(1)
  receipt=json.loads((out/'native-receipt.json').read_text())
  print(json.dumps({'success':receipt['success'],'frames':len([x for x in receipt['artifacts'] if x['path'].endswith('.jpg')]),'output':str(out)}),flush=True)
if __name__=='__main__':main()
