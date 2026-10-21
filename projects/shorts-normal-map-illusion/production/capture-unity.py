"""Finite preview of this selected normal-mapping implementation. No live project launch."""
from pathlib import Path
import argparse,json,uuid,shutil,subprocess,time,hashlib
import psutil
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parents[1];L=P/'production/local'
OWN=R/'unity/VideoEditing/Assets/VideoScenes'/P.name;ISO=L/'unity-capture';LEASE=R/'shared/output/GPU_HANDOFF.json'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',nargs='?',choices=['preview','full'],default='preview');ap.add_argument('--revision',default='v1');a=ap.parse_args()
 c=read(R/'shared/publishing/video-production-control.json');assert c.get('selectedShortVideo')==P.name and c.get('shortsDirectSelection',{}).get('selectedRevision')=='normal-map-v1','Selected Short changed'
 plan=read(P/'planning/production-plan.json');assert plan.get('previewAuthorization',{}).get('allowed') is True,'Preview not authorized'
 timeline=P/'production/visual-timing.json'
 if a.mode=='full':
  assert c.get('shortsDirectSelection',{}).get('fullProductionAuthorized') is True,'Full production not authorized'
  timing=read(timeline);captions=read(P/'script/captions.json');assert timing['frames']==captions['frames'] and timing.get('voiceDurationSeconds',0)>0,'Final audio timeline missing'
 assert not LEASE.exists(),'Foreign GPU lease preserved'
 assert not any((p.info['name'] or '').lower()=='unity.exe' and str(ISO).lower() in ' '.join(p.info['cmdline'] or []).replace('\\','/').lower() for p in psutil.process_iter(['name','cmdline'])),'Owned isolated editor already running'
 out=L/f'capture-{a.mode}-{a.revision}';assert not out.exists(),'Preserve prior capture attempts';out.mkdir(parents=True)
 for p in [OWN,*[x for x in OWN.rglob('*') if x.is_dir()]]:
  m=Path(str(p)+'.meta')
  if not m.exists():m.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n')
 for p in [*OWN.rglob('*.cs'),*OWN.rglob('*.shader')]:
  m=Path(str(p)+'.meta')
  if not m.exists():m.write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\n'+('MonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n' if p.suffix=='.cs' else 'ShaderImporter:\n  externalObjects: {}\n  defaultTextures: []\n  nonModifiableTextures: []\n')+'  userData:\n  assetBundleName:\n  assetBundleVariant:\n')
 shutil.copytree(OWN,ISO/'Assets/VideoScenes'/P.name,dirs_exist_ok=True)
 shutil.copytree(R/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers',ISO/'Assets/ThirdParty/KayKitAdventurers',dirs_exist_ok=True)
 save(ISO/'Packages/manifest.json',dict(dependencies={f'com.unity.modules.{x}':'1.0.0' for x in ['imageconversion','animation','particlesystem']}))
 settings=ISO/'ProjectSettings';settings.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'unity/VideoEditing/ProjectSettings/ProjectVersion.txt',settings/'ProjectVersion.txt')
 job=out/'job.json';save(job,dict(mode=a.mode,output=str(out.resolve()),timeline=str(timeline.resolve())))
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=memory.free,memory.total,utilization.gpu','--format=csv,noheader,nounits'],text=True);free,total,util=map(int,raw.splitlines()[0].replace(' ','').split(','));assert free>=2560 and util<30,('Foreign GPU activity preserved',free,util)
 me=psutil.Process();token=str(uuid.uuid4());record=dict(schemaVersion=1,project=P.name,state='capture_running',token=token,coordinator=dict(pid=me.pid,createTime=me.create_time()),requestedAt=time.time(),gpuFreeMiB=free,gpuMiBBudget=2560,foreignProcessesPaused=[],mode=a.mode,allocationBound='Monitored total-memory delta conservatively; own finite capture only')
 with LEASE.open('x') as f:json.dump(record,f)
 process=None;peak=0
 try:
  cmd=['C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','-batchmode','-projectPath',str(ISO.resolve()),'-force-d3d11','-job-worker-count','4','-shadercompiler-threads','2','-executeMethod','YamyamCoding.Shorts.NormalMap.Editor.NormalMapCapture.Run','-normalMapJob',str(job.resolve()),'-logFile',str((out/'unity.log').resolve())]
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  process=subprocess.Popen(cmd,cwd=R,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW);record['unityPid']=process.pid;save(out/'execution.json',record);print(json.dumps(dict(pid=process.pid,output=str(out))),flush=True)
  deadline=time.time()+900
  while process.poll() is None:
   time.sleep(4)
   nowfree=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0]);delta=max(0,free-nowfree);peak=max(peak,delta)
   assert delta<=2560,('Conservative GPU memory budget exceeded; terminating own preview only',delta)
   assert time.time()<deadline,'Own preview timeout'
  assert process.returncode==0,('Unity failed',process.returncode,str(out/'unity.log'))
  success=read(out/'success.json');assert (success.get('states')==12 and success.get('actualMeshReadback')) if a.mode=='preview' else (success.get('frames')==timing['frames'] and success.get('frozenSourceAssetsLoaded'))
  src=ISO/'Assets/VideoScenes'/P.name
  if a.mode=='preview':
   for folder in ['Generated','Materials','Meshes','Scenes']:
    shutil.copytree(src/folder,OWN/folder,dirs_exist_ok=True)
    m=Path(str(src/folder)+'.meta')
    if m.exists():shutil.copy2(m,Path(str(OWN/folder)+'.meta'))
  for meta in src.rglob('*.meta'):
   target=OWN/meta.relative_to(src)
   if not target.exists() and Path(str(target)[:-5]).exists():shutil.copy2(meta,target)
  for p in OWN.rglob('*'):
   if p.is_file() and p.suffix in ['.cs','.shader','.unity','.mat','.meta','.asset']:
    data=p.read_bytes()
    if b'\x00' not in data:
     text=data.decode('utf8');p.write_text('\n'.join(x.rstrip() for x in text.splitlines())+'\n',encoding='utf8')
  record.update(status='captured',peakConservativeGpuMemoryDeltaMiB=peak,sourceHashes=[dict(path=str(p.relative_to(R)).replace('\\','/'),sha256=sha(p)) for p in OWN.rglob('*') if p.is_file()],finishedAt=time.time());save(out/'execution.json',record);print(json.dumps(dict(status='captured',peakConservativeGpuMemoryDeltaMiB=peak,**success)),flush=True)
 finally:
  if process and process.poll() is None:process.terminate();process.wait(timeout=30)
  if LEASE.exists() and read(LEASE).get('token')==token:LEASE.unlink()
if __name__=='__main__':main()
