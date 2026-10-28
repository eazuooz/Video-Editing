"""Sequential owned requests to the user's already-open Unity editor."""
from pathlib import Path
import argparse,hashlib,json,time,subprocess,os
R=Path(__file__).resolve().parents[3];U=R/'unity/VideoEditing';H=Path(__file__).resolve().parent
M=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--slug',required=True);ap.add_argument('--cut');ap.add_argument('--phase',choices=['preflight','render'],default='preflight');ap.add_argument('--revision',default='v1');ap.add_argument('--sample-frames');a=ap.parse_args()
 auth=load(H/'authorization.json');assert a.slug in auth['slugs']
 control=load(R/'shared/publishing/video-production-control.json')['finiteBatchAuthorizations'][H.name];assert control['localProductionAuthorized']
 alljobs=load(R/'projects'/a.slug/'production/unity-visual-v2/capture-jobs.json')['jobs'];jobs=[j for j in alljobs if j['slug']==a.slug and (not a.cut or j['cutId']==a.cut)];assert jobs
 request=U/'Library/DesignVisualV2.request.json';status=U/'Library/DesignVisualV2.status.json'
 for j in jobs:
  code=U/'Assets/VideoScenes/design-25-30-unity-v2';paths=[code/'DesignLessonStage.cs',code/(j['stageClass']+'.cs'),code/'Editor/DesignVisualCapture.cs',code/'asset-map.json']
  ih=hashlib.sha256(b''.join(p.read_bytes() for p in paths)+json.dumps(j,sort_keys=True).encode()).hexdigest()
  out=M/a.slug/a.phase/a.revision/j['cutId'];success=out/(a.phase+'-success.json');receipt=out/'request.json'
  if success.exists():
   assert receipt.exists() and load(receipt)['inputHash']==ih,'Existing capture belongs to changed source; select new revision directory'
   print('REUSED '+a.slug+' '+j['cutId'],flush=True);continue
  if a.phase=='render':
   free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(','))
   assert free>=2500 and util<=85,(free,util)
  assert not request.exists(),'Another owned request pending; no overwrite'
  if status.exists():assert load(status)['status'] not in ['building','capturing'],'Existing Unity capture active'
  frozen=load(H/'code-fingerprint.json')
  for src in frozen['files']:
   n=Path(src['path']).name
   if n.endswith('Stage.cs') and n not in ['DesignLessonStage.cs',j['stageClass']+'.cs']:continue
   assert hashlib.sha256((R/src['path']).read_bytes()).hexdigest()==src['sha256'],'Unity source changed after freeze: '+src['path']
  fingerprint=frozen['fingerprints'][j['stageClass']]
  raw={**j,'command':a.phase,'expectedFingerprint':fingerprint,'output':out.as_posix(),'sampleFrames':sorted(set([0, min(j['frames']-1,30),*[int((j['frames']-1)*v) for v in [.2,.4,.6,.8,1]]]))}
  if a.sample_frames:
   assert a.phase=='preflight' and a.cut
   raw['sampleFrames']=sorted(set(raw['sampleFrames']+[int(x) for x in a.sample_frames.split(',')]))
   assert all(0<=f<j['frames'] for f in raw['sampleFrames'])
  dump(receipt,{**raw,'inputHash':ih,'sourceFiles':[str(p.relative_to(R)) for p in paths],'startedAt':time.time(),'coordinatorPid':os.getpid()})
  request.parent.mkdir(parents=True,exist_ok=True)
  with request.open('x',encoding='utf8') as f:json.dump(raw,f)
  print('START '+a.slug+' '+j['cutId']+' '+a.phase+' '+str(j['frames']),flush=True)
  start=time.monotonic();last=-1
  while not success.exists():
   error=out/(a.phase+'-failure.json')
   if error.exists():raise RuntimeError(error.read_text(encoding='utf8'))
   if time.monotonic()-start>900:raise RuntimeError('Capture timeout; preserve active editor, inspect '+str(out))
   time.sleep(1)
   p=out/'progress.json'
   if p.exists():
    try:count=load(p)['completed']
    except (json.JSONDecodeError,KeyError):continue
    if count!=last and count%600==0:print('PROGRESS '+j['cutId']+' '+str(count),flush=True);last=count
  assert load(success)['compiledSourceFingerprint']==fingerprint,'Stale compiled Unity code refused'
  print('DONE '+a.slug+' '+j['cutId'],flush=True)
 print('ALL COMPLETE '+a.slug+' '+a.phase,flush=True)
if __name__=='__main__':main()
