"""Finite owned Unity capture, no live-editor modification or foreign lease removal."""
from pathlib import Path
import json,uuid,shutil,subprocess,sys,time,os,argparse,hashlib
import psutil
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];S=P.name;L=P/'production/local'
OWN=R/f'unity/VideoEditing/Assets/VideoScenes/{S}';ISO=L/'unity-capture';LEASE=R/'shared/output/GPU_HANDOFF.json'
FF='C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['preview','full']);a.add_argument('--revision',default='v1');args=a.parse_args()
 assert read(R/'shared/publishing/video-production-control.json')['shortsRecurringAuthorization']['selectedShort']==S
 assert not LEASE.exists(),'Existing GPU lease preserved'
 for p in psutil.process_iter(['name','cmdline']):
  if (p.info['name'] or '').lower()=='unity.exe' and str(ISO).lower() in ' '.join(p.info['cmdline'] or []).replace('\\','/').lower():raise RuntimeError('Own isolated editor is still running')
 out=L/f'capture-{args.mode}-{args.revision}';assert not (out/'success.json').exists(),'Preserve successful capture'
 assert not out.exists() or not list(out.glob('*.png')),'Partial capture requires inspection'
 out.mkdir(parents=True,exist_ok=True)
 for p in [OWN,*[x for x in OWN.rglob('*') if x.is_dir()]]:
  meta=Path(str(p)+'.meta')
  if not meta.exists():meta.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
 for p in OWN.rglob('*.cs'):
  meta=Path(str(p)+'.meta')
  if not meta.exists():meta.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\nMonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
 shutil.copytree(OWN,ISO/f'Assets/VideoScenes/{S}',dirs_exist_ok=True)
 shutil.copytree(R/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers',ISO/'Assets/ThirdParty/KayKitAdventurers',dirs_exist_ok=True)
 save(ISO/'Packages/manifest.json',dict(dependencies={f'com.unity.modules.{x}':'1.0.0' for x in ['physics','imageconversion','animation']}))
 settings=ISO/'ProjectSettings';settings.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'unity/VideoEditing/ProjectSettings/ProjectVersion.txt',settings/'ProjectVersion.txt')
 timing=L/'visual-timing.json'
 if timing.exists():shots=read(timing)['shots']
 else:shots=[dict(id='01-hook',start=0,end=3.5,attackStart=.2,attackSeconds=1.8,width=.86),dict(id='02-reveal',start=3.5,end=13,attackStart=8,attackSeconds=3,width=.86),dict(id='03-wide',start=13,end=18,attackStart=13.5,attackSeconds=2.2,width=1.4),dict(id='04-narrow',start=18,end=30,attackStart=18.5,attackSeconds=2.2,width=.86)]
 job=out/'job.json';save(job,dict(mode=args.mode,output=str(out.resolve()),ffmpeg=FF,shots=shots))
 free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip());assert free>=2048
 me=psutil.Process();token=str(uuid.uuid4());record=dict(schemaVersion=1,project=S,state='render_running',token=token,coordinator=dict(pid=me.pid,createTime=me.create_time()),requestedAt=time.time(),gpuFreeMiB=free,foreignProcessesPaused=[])
 with LEASE.open('x') as f:json.dump(record,f)
 process=None
 try:
  command=['C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','-batchmode','-projectPath',str(ISO.resolve()),'-force-d3d11','-job-worker-count','4','-shadercompiler-threads','2','-executeMethod','YamyamCoding.Shorts.ForgivingHitbox.Editor.HitboxCapture.Run','-hitboxJob',str(job.resolve()),'-logFile',str((out/'unity.log').resolve())]
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  process=subprocess.Popen(command,cwd=R,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW);record['unityPid']=process.pid;save(out/'execution.json',record);print(json.dumps(dict(pid=process.pid,output=str(out))),flush=True)
  code=process.wait(timeout=1500);assert code==0,('Unity failed',code,str(out/'unity.log'))
  success=read(out/'success.json');assert success['frames']==(1800 if args.mode=='full' else 8)
  src=ISO/f'Assets/VideoScenes/{S}'
  for folder in ['Baked','Scenes']:
   shutil.copytree(src/folder,OWN/folder,dirs_exist_ok=True)
   if Path(str(src/folder)+'.meta').exists():shutil.copy2(Path(str(src/folder)+'.meta'),Path(str(OWN/folder)+'.meta'))
  for meta in src.rglob('*.meta'):
   relative=meta.relative_to(src);target=OWN/relative
   if not target.exists() and Path(str(target)[:-5]).exists():shutil.copy2(meta,target)
  record.update(status='captured',frames=success['frames'],sourceHashes=[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in OWN.rglob('*') if p.is_file()],finishedAt=time.time())
  save(out/'execution.json',record);print(json.dumps(dict(status='captured',frames=success['frames'])),flush=True)
 finally:
  if process and process.poll() is None:process.terminate();process.wait(timeout=30)
  if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
if __name__=='__main__':main()
