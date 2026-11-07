"""Finite sequential pacing jobs, with a shared GPU lease and restartable receipts."""
from pathlib import Path
import sys,os,json,uuid,subprocess,time,shutil
from datetime import datetime,timezone
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=B/'local/pacing-v3';L.mkdir(exist_ok=True)
sys.path.insert(0,str(B/'local/pacing-v3/python-deps'))
import render
read=render.read;save=render.save
episodes=[f'A{i:02}' for i in range(1,19) if i!=2]
def main():
 mode=sys.argv[1];selected=sys.argv[2:] or episodes
 control=read(R/'shared/publishing/video-production-control.json')['animationPacingRevision20261107']
 assert set(selected)<=set(control['episodes']) and control['a02ReplacementComplete']
 lease=R/'shared/output/GPU_HANDOFF.json';token=str(uuid.uuid4())
 with lease.open('x',encoding='utf-8') as f:json.dump(dict(owner='animation-pacing-v3',pid=os.getpid(),token=token,stage=mode,episodes=selected,createdAt=datetime.now(timezone.utc).isoformat()),f)
 try:
  for ep in selected:
   control=read(R/'shared/publishing/video-production-control.json')['animationPacingRevision20261107'];assert ep in control['episodes']
   assert shutil.disk_usage(R).free>5*1024**3,'Free space too low; preserve all baselines'
   log=L/(ep+'-'+mode+'.log')
   if mode=='prepare':cmd=[sys.executable,'-X','utf8',str(H/'prepare_rest.py'),ep]
   else:
    row=next(x for x in read(B/'real-clips-v2/review-manifest.json')['records'] if x['id']==ep)
    cmd=[sys.executable,'-X','utf8',str(H/'render.py'),str(R/'projects'/row['slug']/'production/pacing-v3/edit-plan.json')]
   save(L/'active-job.json',dict(episode=ep,mode=mode,pid=os.getpid(),log=str(log),startedAt=datetime.now(timezone.utc).isoformat()))
   print(ep,mode,'START',flush=True)
   with log.open('wb') as f:subprocess.run(cmd,stdout=f,stderr=f,check=True)
   if mode=='render':
    project=R/'projects'/row['slug'];local=(project/'production/local/pacing-v3').resolve()
    with (L/(ep+'-final-samples.log')).open('wb') as f:subprocess.run([sys.executable,'-X','utf8',str(H/'inspect_pacing.py'),ep,'final'],stdout=f,stderr=f,check=True)
    manifest=read(local/'delivery/output'/row['slug']/'delivery-manifest.json')
    assert manifest['narrationAllSamplesPreserved'] and len(manifest['files'])==4
    # Only new rebuildable intermediates, after validated delivery. Never touch
    # baseline/preview sources, final WAV, final masters or another task's staging.
    for target in (local/'parts',local/'picture.mp4'):
     resolved=target.resolve();assert resolved.parent==local
     if resolved.is_dir():shutil.rmtree(resolved)
     elif resolved.exists():resolved.unlink()
   print(ep,mode,'DONE',flush=True)
 finally:
  if lease.exists() and read(lease).get('token')==token:lease.unlink()
if __name__=='__main__':main()
