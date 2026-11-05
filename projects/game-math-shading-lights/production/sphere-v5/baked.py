"""Extra four actual lightmapped sphere studies: CPU baking in the same stopped M21-only editor."""
import hashlib,math,os,subprocess,sys
import psutil
from native import P,S,W,SB,BAKE,read,write
root=SB/'Assets/VideoScenes'/P.name;ed=root/'Editor/LightLabCapture.cs'
def main():
 q=read(W.parent/'render-v4/queue.json')
 for p in psutil.process_iter(['name','cmdline']):
  if (p.info['name'] or '').lower()=='unity.exe' and any(str(SB).lower()==x.lower() for x in p.info['cmdline'] or []):raise RuntimeError('Wait for existing M21 scene capture to finish')
 assert len(list((W/'native').glob('*/*/capture-success.json')))>=61
 t=ed.read_text(encoding='utf-8');t=t.replace('settings.lightmapper=LightingSettings.Lightmapper.UnityComputeGPU;', 'settings.lightmapper=(LightingSettings.Lightmapper)System.Enum.Parse(typeof(LightingSettings.Lightmapper),"ProgressiveCPU"); settings.denoiserTypeDirect=LightingSettings.DenoiserType.None; settings.denoiserTypeIndirect=LightingSettings.DenoiserType.None; settings.denoiserTypeAO=LightingSettings.DenoiserType.None;')
 ed.write_text(t,encoding='utf-8')
 f=root/'LightLabBakedRoom.cs';t=f.read_text(encoding='utf-8')
 if 'parent.name.StartsWith("Sun ·")' not in t:t=t.replace('if(renderer is null)continue;','if(renderer is null)continue;if(renderer.GetComponentInParent<Transform>()!=null && renderer.transform.parent!=null && renderer.transform.parent.name.StartsWith("Sun ·")){renderer.shadowCastingMode=UnityEngine.Rendering.ShadowCastingMode.Off;continue;}');f.write_text(t,encoding='utf-8')
 f=root/'LightLabStage.cs';t=f.read_text(encoding='utf-8').replace('움직이는 로봇:','움직이는 구:');f.write_text(t,encoding='utf-8')
 h=hashlib.sha256((ed.read_bytes()+f.read_bytes()+(root/'LightLabBakedRoom.cs').read_bytes())).hexdigest();(root/'LightLabBuildVersion.cs').write_text('namespace Yamyam.GameMath.LightLab {public static class LightLabBuildVersion {public const string Value="'+h+'";}}')
 write(SB/'M21_SANDBOX.json',{'fingerprint':h,'local':True})
 jobs=[]
 for path in q['jobs']:
  orig=read(path);sid=orig['sceneId']
  if int(sid) not in BAKE:continue
  cu=read(orig['cueFile']);id='m21-sphere-bake-'+sid;cu['id']=id;cue=W/'bake-jobs'/(sid+'-cue.json');write(cue,cu);n=orig['frames']
  start=round(cu['duration']*.4*60);samples=sorted({0,1,179,180,n-1}|set(range(start,min(n,start+183)))|set(range(0,n,12)) if int(sid)==70 else {0,1,179,180,n-1}|set(range(start,min(n,start+183))))
  dest=W/'baked'/h[:10]/sid;j=dict(orig,id=id,cueFile=str(cue),expectedFingerprint=h,output=str(dest),command='preflight',sampleFrames=samples);jp=W/'bake-jobs'/(sid+'.json');write(jp,j)
  if not (dest/'capture-success.json').is_file():jobs.append(str(jp))
 if jobs:
  batch=W/'bake-jobs/jobs.txt';batch.write_text('\n'.join(jobs));subprocess.run([q['unity'],'-batchmode','-force-d3d11','-force-driver-type-warp','-job-worker-count','2','-projectPath',str(SB),'-executeMethod','Yamyam.GameMath.LightLab.LightLabCapture.Batch','-logFile',str(W/'bake.log')],env=dict(os.environ,M21_SPHERE_JOB_LIST=str(batch)),creationflags=subprocess.CREATE_NO_WINDOW,check=True)
 for sid in sorted(BAKE):
  j=read(W/'bake-jobs'/f'{sid:03}.json');f=__import__('pathlib').Path(j['output']);e=read(f/'actual-bake.json');assert e['engineReturnedSuccess'] and e['lightIsBaked'] and e['lightmappedRenderers']>0 and (f/'capture-success.json').exists()
 write(W/'bake-override.json',{'verified':sorted(BAKE),'fingerprint':h})
if __name__=='__main__':main()
