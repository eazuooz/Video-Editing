"""CPU/WARP Unity capture in an isolated checkout, leaving user editors untouched."""
import json,subprocess,shutil,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
TOPICS={'shorts-portal-teleport-momentum':'momentum','shorts-portal-seamless-traversal':'traversal'}
OWN=R/'unity/VideoEditing/Assets/VideoScenes/portal-traversal-shorts-20261025'
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def capture(slug,mode):
 auth=json.loads((R/'shared/publishing/video-production-control.json').read_text(encoding='utf8'))['portalTraversalShortsAuthorization'];assert auth['status']=='active' and slug in auth['slugs'] and auth['fullProductionAuthorized']
 p=R/'projects'/slug;L=p/'production/local';out=L/('capture-'+mode);assert not out.exists(),out
 if not mode.startswith('preview'):
  assert (p/'production/visual-timing.json').exists(),'Aligned finite timeline required before full capture'
  timeline=json.loads((p/'production/visual-timing.json').read_text(encoding='utf8'));assert timeline['frames']>0 and timeline['sections']
 iso=L/('unity-'+mode);dest=iso/'Assets/VideoScenes/portal-traversal-shorts-20261025';shutil.copytree(OWN,dest,dirs_exist_ok=True)
 shutil.copytree(R/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers',iso/'Assets/ThirdParty/KayKitAdventurers',dirs_exist_ok=True)
 save(iso/'Packages/manifest.json',{'dependencies':{'com.unity.modules.imageconversion':'1.0.0','com.unity.modules.animation':'1.0.0','com.unity.modules.physics':'1.0.0'}})
 (iso/'ProjectSettings').mkdir(exist_ok=True);shutil.copy2(R/'unity/VideoEditing/ProjectSettings/ProjectVersion.txt',iso/'ProjectSettings/ProjectVersion.txt')
 sections=json.loads((p/'production/section-plan.json').read_text(encoding='utf8'));save(out/'job.json',{'topic':TOPICS[slug],'mode':mode,'sections':[s['id'] for s in sections],'output':str(out),'timeline':str(p/'production/visual-timing.json')})
 cmd=['C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Unity.exe','-batchmode','-projectPath',str(iso),'-force-d3d11','-force-driver-type-warp','-job-worker-count','3','-shadercompiler-threads','2','-executeMethod','YamyamCoding.PortalTraversal.Editor.Capture.Run','-portalJob',str(out/'job.json'),'-logFile',str(out/'unity.log')]
 proc=subprocess.Popen(cmd,creationflags=subprocess.CREATE_NO_WINDOW);print('CAPTURE_START',slug,mode,proc.pid,flush=True)
 code=proc.wait();assert code==0,('Unity exit',code,str(out/'unity.log'));assert (out/'success.json').exists()
 for folder in ['Materials','Meshes','Scenes']:
  if (dest/folder).exists():shutil.copytree(dest/folder,OWN/folder,dirs_exist_ok=True)
 for meta in dest.rglob('*.meta'):
  target=OWN/meta.relative_to(dest)
  if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(meta,target)
 save(out/'execution.json',{'device':'CPU/WARP','sourceProject':'isolated owned capture project','foreignProcessesStopped':[],'exitCode':code})
 print('CAPTURE_DONE',slug,mode,flush=True)
if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'preview-v1';slugs=sys.argv[2:] or list(TOPICS)
 for slug in slugs:capture(slug,mode)
