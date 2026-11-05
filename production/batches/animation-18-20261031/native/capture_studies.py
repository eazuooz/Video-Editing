"""Capture the selected studies offscreen in a separate worker; never focus the user's editor."""
from pathlib import Path
import subprocess,json,shutil,sys,os,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];batch=H.parent
sys.path.insert(0,str(batch))
from gpu_slot import idle_slot
ep=sys.argv[1];work=json.loads((R/'shared/publishing/video-worklist.json').read_text(encoding='utf-8-sig'));row=next(x for x in work['rows'] if x['id']==ep)
assert ep in json.loads((batch/'batch.json').read_text('utf-8'))['episodeIds']
P=R/'projects'/row['slug'];L=P/'production/local/series-v1';W=L/'unreal-worker';src=R/'GameAnimationSample'
job=json.loads((L/'study-job.json').read_text('utf-8'));assert job['episode']==ep
exe=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe')
template=R/'projects/animation-assigning/production/local/unreal-kit-v2/unreal-worker'
descriptor=W/(ep+'Worker.uproject');(W/'Content').mkdir(parents=True,exist_ok=True);(W/'Config').mkdir(exist_ok=True)
shutil.copyfile(template/'A01Worker.uproject',descriptor);shutil.copyfile(template/'Config/DefaultEngine.ini',W/'Config/DefaultEngine.ini')
for folder in (src/'Content').iterdir():
 if not folder.is_dir() or folder.name=='YamyamAnimationSeries':continue
 dst=W/'Content'/folder.name
 if not dst.exists():
  q=lambda p:"'"+str(p).replace("'","''")+"'"
  subprocess.run(['powershell','-NoProfile','-Command','New-Item -ItemType Junction -Path '+q(dst)+' -Target '+q(folder)+' | Out-Null'],check=True)
 assert dst.resolve()==folder.resolve()
(W/'build-job.json').write_text(json.dumps(dict(job,local=str(L))),encoding='utf-8')
def run(args,name):
 with (L/(name+'.log')).open('wb') as log:
  subprocess.run([exe,descriptor,*args,'-unattended','-nosound','-nosplash','-NoLiveCoding','-abslog='+str(L/(name+'.engine.log'))],stdout=log,stderr=subprocess.STDOUT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
error=L/'stage-error.txt'
if error.exists():error.rename(L/('stage-error-'+str(error.stat().st_mtime_ns)+'.txt'))
inputs=[H/'build_level.py',W/'build-job.json',*[L/'poses'/(key+'.json') for key in job['keys']]]
fingerprint=hashlib.sha256(b''.join(hashlib.sha256(p.read_bytes()).digest() for p in inputs)).hexdigest()
ready=L/'native-build-receipt.json'
complete=all((L/(key+'-build.json')).is_file() and (W/'Content/YamyamAnimationSeries'/ep/'Levels'/(key+'.umap')).is_file() for key in job['keys'])
if not ready.is_file() or json.loads(ready.read_text('utf-8')).get('fingerprint')!=fingerprint or not complete:
 run(['-run=pythonscript','-script='+str(H/'build_level.py'),'-nullrhi'],'stage-build')
 if error.exists():raise RuntimeError(error.read_text('utf-8'))
 for key in job['keys']:
  assert (L/(key+'-build.json')).is_file()
 ready.write_text(json.dumps(dict(fingerprint=fingerprint,keys=job['keys'])),'utf-8')
def sync_scene_assets():
 origin=W/'Content/YamyamAnimationSeries'/ep;target=src/'Content/YamyamAnimationSeries'/ep
 receipt=L/'scene-assets.json'
 previous=json.loads(receipt.read_text('utf-8')) if receipt.is_file() else {}
 planned={}
 for path in origin.rglob('*'):
  if not path.is_file() or path.suffix not in ('.umap','.uasset'):continue
  name=path.relative_to(origin).as_posix();dest=target/name
  assert dest.resolve().is_relative_to(target.resolve())
  wanted=hashlib.sha256(path.read_bytes()).hexdigest();planned[name]=wanted
  if dest.is_file():
   current=hashlib.sha256(dest.read_bytes()).hexdigest()
   assert current in (wanted,previous.get(name)),f'Existing scene changed outside this worker: {name}'
  dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file() or current!=wanted:shutil.copy2(path,dest)
 receipt.write_text(json.dumps(planned,indent=2),'utf-8')
sync_scene_assets()
if '--build-only' in sys.argv:sys.exit(0)
capture_receipt=L/'captured-inputs.json'
captures=json.loads(capture_receipt.read_text('utf-8')) if capture_receipt.exists() else {}
for key in job['keys']:
 meta=json.loads((L/(key+'-build.json')).read_text());folder=L/'frames'/key
 capture_inputs=(H/'build_level.py',W/'build-job.json',W/'Config/DefaultEngine.ini',L/'poses'/(key+'.json'))
 signature=hashlib.sha256(b''.join(hashlib.sha256(f.read_bytes()).digest() for f in capture_inputs)).hexdigest()
 if captures.get(key)!=signature or len(list(folder.glob('*.png')))!=meta['frames']:
  with idle_slot(ep+'-animation-capture',wait=True):
   run([meta['level'],'-game','-LevelSequence='+meta['sequence'],'-MoviePipelineConfig='+meta['config'],'-RenderOffscreen','-NoScreenMessages','-NoLoadingScreen','-notexturestreaming','-resx=1920','-resy=1080'],'render-'+key)
 assert len(list(folder.glob('*.png')))==meta['frames'],key
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','60','-i',str(folder/'%06d.png'),'-frames:v',str(meta['frames']),'-c:v','h264_nvenc','-preset','p4','-cq','17','-b:v','0','-pix_fmt','yuv420p',str(L/(key+'.mp4'))],check=True)
 captures[key]=signature
 capture_receipt.write_text(json.dumps(captures,indent=2),'utf-8')
 print('Rendered',key,flush=True)
