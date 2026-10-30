"""Bounded no-focus Unity capture; preserves existing scenes and other requests."""
from pathlib import Path
import argparse, hashlib, json, subprocess, time, uuid

H=Path(__file__).resolve().parent
R=H.parents[3]
U=R/'unity/VideoEditing'
C=U/'Assets/VideoScenes/animation-series-v1'
L=U/'Library'
M=H.parent/'local/grid-v1'

def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def authorize():
 a=read(R/'shared/publishing/video-production-control.json')['finiteBatchAuthorizations']['animation-18-20261031']
 assert a['productionAuthorized'] and a['renderAuthorized'] and 'A01' in a['episodeIds']
 assert not a['youtubeAuthorized']
def idle():
 assert not list(L.glob('*.request')) and not list(L.glob('*.request.json')),'Preserve pending bridge requests'
 for p in L.glob('*.status.json'):
  d=read(p)
  assert d.get('status') not in ['building','capturing'],'Preserve active capture: '+p.name
 assert read(L/'YamyamAssetLibrary/state.json')['phase'] in ['complete','failed']
 assert not (L/'YamyamAssetLibrary/request.json').exists()
def freeze():
 files=[C/'AnimationLessonStage.cs',C/'AnimationGridStage.cs',C/'Editor/AnimationGridCapture.cs',C/'asset-map.json',H/'rasterize_unity_labels.py',U/'Packages/packages-lock.json',U/'ProjectSettings/ProjectVersion.txt']
 profile=C/'animation-grid-presentations.json'
 if profile.exists():files.append(profile)
 assets=read(C/'asset-map.json')['assets']
 for a in assets:
  files.extend([U/a['path'],Path(str(U/a['path'])+'.meta')])
 records=[{'path':p.relative_to(R).as_posix(),'sha256':sha(p)} for p in files]
 fp=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
 target=C/'AnimationGridBuildVersion.cs'
 text='namespace Yamyam.AnimationSeries { public static class AnimationGridBuildVersion { public static string For(string stage) { return stage=="AnimationGridStage"?"'+fp+'":"unknown"; } } }\n'
 if not target.exists() or target.read_text('utf8')!=text:target.write_text(text,encoding='utf8')
 record={'fingerprint':fp,'files':records}
 immutable=H/'source-snapshots'/fp/'manifest.json'
 if immutable.exists():
  assert read(immutable)==record,'Immutable source receipt changed'
 else:
  write(immutable,record)
  for p in files[:5]:
   snapshot=immutable.parent/p.name
   snapshot.write_bytes(p.read_bytes())
  if profile.exists():(immutable.parent/profile.name).write_bytes(profile.read_bytes())
 write(H/'source-fingerprint.json',record)
 return fp
def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['compile','preflight','render']);ap.add_argument('--cut',default='pose-versus-motion');ap.add_argument('--revision',default='prototype-v1');ap.add_argument('--frames',type=int,default=360);ap.add_argument('--samples',help='Exact comma-separated preflight frame numbers');ap.add_argument('--presentation',default='');a=ap.parse_args()
 authorize();idle()
 fp=freeze()
 if a.action=='compile':
  ack=L/'AnimationGridV1.compiled.json'
  if ack.exists():
   existing=read(ack)
   if any(x.get('fingerprint')==fp and x.get('typeAvailable') for x in existing.get('stages',[])):
    write(H/'compiled-ack.json',existing);print('REUSED matching compiled acknowledgement '+fp,flush=True);return
  nonce='animation-grid-'+uuid.uuid4().hex
  with (L/'YamyamAssetLibrary/request.json').open('x',encoding='utf8') as f:json.dump({'command':'probe','nonce':nonce},f)
  print('No-focus refresh requested '+nonce,flush=True)
  deadline=time.monotonic()+360
  while time.monotonic()<deadline:
   ack=L/'AnimationGridV1.compiled.json'
   if ack.exists():
    d=read(ack)
    if any(x.get('fingerprint')==fp and x.get('typeAvailable') for x in d.get('stages',[])):
     write(H/'compiled-ack.json',d);print('COMPILED '+fp,flush=True);return
   time.sleep(1)
  raise RuntimeError('No matching compiled acknowledgement; editor preserved')
 assert read(H/'compiled-ack.json')['stages'][0]['fingerprint']==fp,'Compile current source first'
 free,util=map(int,subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().splitlines()[0].split(','))
 assert free>=4096 and util<=85,('Preserve other GPU activity',free,util)
 assert a.cut in ['pose-versus-motion','walk-intent','idle-intent','motion-brief','motion-list','attack-timing','pose-document','reference-transfer','joint-limit','pose-connection'] and 1<=a.frames<=36000
 assert all(ch.isalnum() or ch in '-_' for ch in a.revision)
 out=M/a.action/a.revision/a.cut
 assert not out.exists(),'Prior output preserved; choose fresh revision'
 samples=sorted(set([0,a.frames//4,a.frames//2,3*a.frames//4,a.frames-1]))
 if a.samples:
  samples=sorted(set(int(x) for x in a.samples.split(',')))
  assert 1<=len(samples)<=50 and samples[0]>=0 and samples[-1]<a.frames
 job={'command':a.action,'slug':'animation-assigning','cutId':a.cut,'stageClass':'AnimationGridStage','output':out.as_posix(),'expectedFingerprint':fp,'frames':a.frames,'sampleFrames':samples}
 if a.presentation:
  assert a.presentation.startswith('A01-E') and a.presentation[5:].isdigit()
  job['presentationId']=a.presentation
 write(out/'request.json',job)
 write(H/'last-capture-request.json',{'job':job,'gpu':{'freeMiB':free,'utilizationPercent':util},'notHumanReview':True})
 with (L/'AnimationGridV1.request.json').open('x',encoding='utf8') as f:json.dump(job,f)
 print('REQUESTED '+str(out),flush=True)
 deadline=time.monotonic()+600
 while time.monotonic()<deadline:
  receipt=out/(a.action+'-success.json');failure=out/(a.action+'-failure.json')
  if receipt.exists():print('COMPLETE '+str(receipt),flush=True);return
  if failure.exists():raise RuntimeError(read(failure).get('error'))
  time.sleep(1)
 raise RuntimeError('Capture timed out; preserve pending job and inspect status')
if __name__=='__main__':main()
