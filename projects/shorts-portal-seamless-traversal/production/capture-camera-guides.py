"""Capture only the requested camera explanation, reusing all unchanged v2 frames."""
import json,subprocess,shutil,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
OWN=R/'unity/VideoEditing/Assets/VideoScenes/portal-traversal-shorts-20261025'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
mode=sys.argv[1];auth=read(R/'shared/publishing/video-production-control.json')['portalTraversalShortsAuthorization']
assert auth['status']=='active' and auth['fullProductionAuthorized'] and P.name in auth['activeSlugs']
out=L/('capture-'+mode);assert not out.exists();out.mkdir()
iso=L/'unity-full-v2';assert (iso/'Library').exists()
dest=iso/'Assets/VideoScenes/portal-traversal-shorts-20261025';shutil.copytree(OWN,dest,dirs_exist_ok=True)
job={'topic':'traversal','mode':mode,'sections':['camera','screen'],'renderSections':['camera','screen'],'output':str(out),'timeline':str(P/'production/visual-timing.json')};save(out/'job.json',job)
if not mode.startswith('preview'):
 for folder in ['frames','player']:
  shutil.copytree(L/'capture-full-v2'/folder,out/folder)
cmd=['C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','-batchmode','-projectPath',str(iso),'-force-d3d11','-force-driver-type-warp','-job-worker-count','3','-shadercompiler-threads','2','-executeMethod','YamyamCoding.PortalTraversal.Editor.Capture.Run','-portalJob',str(out/'job.json'),'-logFile',str(out/'unity.log')]
proc=subprocess.Popen(cmd,creationflags=subprocess.CREATE_NO_WINDOW);print('CAMERA_CAPTURE',mode,proc.pid,flush=True);code=proc.wait()
assert code==0 and (out/'success.json').exists(),str(out/'unity.log')
if not mode.startswith('preview'):
 partial=read(out/'readback.json');save(out/'changed-readback.json',partial)
 base=read(L/'capture-full-v2/readback.json');changed={v['frame']:v for v in partial['records']}
 base['records']=[changed.get(v['frame'],v) for v in base['records']];base['changedSections']=['camera','screen'];base['changedFrameCount']=len(changed)
 save(out/'readback.json',base);save(out/'success.json',{'frames':base['frames'],'width':1080,'height':1080,'changedFrames':len(changed),'reusedCapture':'full-v2'})
for section in ['camera','screen']:
 for suffix in ['.unity','.unity.meta']:
  shutil.copy2(dest/'Scenes/traversal'/(section+suffix),OWN/'Scenes/traversal'/(section+suffix))
for p in (dest/'Materials').glob('*camera*'):
 shutil.copy2(p,OWN/'Materials'/p.name)
for p in [dest/'CameraGuide.cs.meta']:
 if p.exists():shutil.copy2(p,OWN/p.name)
save(out/'execution.json',{'exitCode':code,'device':'CPU/WARP','sections':['camera','screen'],'preservedAudio':True,'foreignProcessesStopped':[]})
print('CAMERA_CAPTURE_DONE',mode,flush=True)
