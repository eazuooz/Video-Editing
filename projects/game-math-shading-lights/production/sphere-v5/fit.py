"""Keep distance/solid-angle geometry below the title with actual camera framing, not an image crop."""
from pathlib import Path
import hashlib,os,subprocess
import psutil
from native import P,W,SB,read,write
def main():
 assert (W/'bake-override.json').exists()
 for p in psutil.process_iter(['name','cmdline']):
  if (p.info['name'] or '').lower()=='unity.exe' and any(str(SB).lower()==x.lower() for x in p.info['cmdline'] or []):raise RuntimeError('Do not touch a running editor')
 root=SB/'Assets/VideoScenes'/P.name;stage=root/'LightLabStage.cs';s=stage.read_text(encoding='utf-8')
 needle='if(cue.diagram=="specularGrid"||cue.diagram=="shadingComparison"||cue.diagram=="triangle-highlight")floor.SetActive(false);'
 insert='if(cue.id.StartsWith("m21-fit-")){RenderCamera.transform.position+=RenderCamera.transform.up*1.1f;RenderCamera.orthographicSize*=1.15f;}'
 if insert not in s:assert s.count(needle)==1;s=s.replace(needle,insert+'\n   '+needle);stage.write_text(s,encoding='utf-8')
 h=hashlib.sha256((stage.read_bytes()+(root/'Editor/LightLabCapture.cs').read_bytes())).hexdigest();(root/'LightLabBuildVersion.cs').write_text('namespace Yamyam.GameMath.LightLab {public static class LightLabBuildVersion {public const string Value="'+h+'";}}')
 write(SB/'M21_SANDBOX.json',{'fingerprint':h,'local':True});files=[]
 for sid in ['053','056','058']:
  j=read(W/'native-jobs'/(sid+'.json'));cu=read(j['cueFile']);cu['id']='m21-fit-'+sid;cp=W/'fit-jobs'/(sid+'-cue.json');write(cp,cu)
  j.update(id=cu['id'],cueFile=str(cp),expectedFingerprint=h,output=str(W/'fit'/h[:10]/sid));jf=W/'fit-jobs'/(sid+'.json');write(jf,j)
  if not (Path(j['output'])/'capture-success.json').is_file():files.append(str(jf))
 if files:
  listing=W/'fit-jobs/jobs.txt';listing.write_text('\n'.join(files),encoding='utf-8');q=read(W.parent/'render-v4/queue.json')
  subprocess.run([q['unity'],'-batchmode','-force-d3d11','-force-driver-type-warp','-job-worker-count','2','-projectPath',str(SB),'-executeMethod','Yamyam.GameMath.LightLab.LightLabCapture.Batch','-logFile',str(W/'fit.log')],env=dict(os.environ,M21_SPHERE_JOB_LIST=str(listing)),creationflags=subprocess.CREATE_NO_WINDOW,check=True)
 write(W/'fit-override.json',{'scenes':[53,56,58],'fingerprint':h})
if __name__=='__main__':main()
