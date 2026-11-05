"""Isolated Unity URP captures on Microsoft's CPU D3D11 WARP device. No GPU lease, no outside editor mutation."""
import json,math,shutil,subprocess,os,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[2];R=P.parents[1];S=P/'production/unity-staging';B=P/'production/sphere-v5';W=P/'production/local/render-v5'; SB=W/'NativeProject'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def change(t,a,b):
 assert t.count(a)==1,a
 return t.replace(a,b)
# These lessons are narrated optical diagrams, rendered by the aligned sphere bench. Real baked room/UV/probe evidence remains actual engine footage.
HERO={1,2,3,4,7,8,9,10,11,16,17,20,51,55}
BAKE={70,74,75,76}
def native():
 q=read(W.parent/'render-v4/queue.json');src=S/'LocalUnity-v13'
 if not SB.exists():
  SB.mkdir(parents=True);shutil.copytree(src/'Packages',SB/'Packages');shutil.copytree(src/'ProjectSettings',SB/'ProjectSettings')
 root=SB/'Assets/VideoScenes'/P.name;ed=root/'Editor';ed.mkdir(parents=True,exist_ok=True)
 code={f.name:f.read_text(encoding='utf-8-sig') for f in S.glob('*.cs')};code['SphereSkin.cs']=(B/'SphereSkin.cs').read_text(encoding='utf-8')
 t=code['LightLabStage.cs'];i=t.index('objectRoot=InstantiateAsset(RobotPrefab');k=t.index('subjectRenderers=',i);t=t[:i]+'objectRoot=SphereSubject();\n   '+t[k:]
 i=t.index('lampRoot=InstantiateAsset(LampPrefab');k=t.index('var lightObject=',i);t=t[:i]+'lampRoot=SunMarker();\n   '+t[k:]
 t=t.replace('if(cue.glossReference){','if(false && cue.glossReference){')
 # Attach the sampled normal to the sphere. Changing tilt moves the point along the sphere (not around a removed sample disk).
 t=change(t,'surfaceProbe=probe.transform;', 'probe.GetComponent<Renderer>().enabled=false;surfaceProbe=probe.transform;surfaceProbe.position=objectRoot.position+Vector3.up*1.36f;')
 t=change(t,'Vector3 pos=Cue.lightPosition;', 'if(Cue.variable=="normalTilt")surfaceProbe.rotation=Quaternion.Euler(0,0,change);surfaceProbe.position=objectRoot.position+surfaceProbe.up*1.36f;Vector3 pos=Cue.lightPosition;')
 t=t.replace('lampRoot.rotation=Quaternion.LookRotation(direction)','lampRoot.rotation=RenderCamera.transform.rotation')
 t=t.replace('lr.widthMultiplier=.04f','lr.widthMultiplier=.062f').replace('d.normalized*1.1f','d.normalized*1.48f').replace('normalized*1.28f','normalized*1.61f')
 # Progressive construction of secondary-scene vector guides. Endpoint and head move together.
 t=t.replace('void SetArrow(LineRenderer line,','float vectorTime; void SetArrow(LineRenderer line,')
 t=t.replace('SetArrow(normal,p,n,Cue.normalArrow);','vectorTime=seconds;SetArrow(normal,p,n,Cue.normalArrow);')
 t=t.replace('Vector3 q=p+delta;','float reveal=Mathf.SmoothStep(0,1,Mathf.Clamp01((vectorTime-(line==towardLight?.55f:line==reflection?1.1f:line==towardViewer?1.55f:line==halfway?1.95f:0))/.95f));if(reveal<.02f){line.enabled=false;return;}delta*=reveal;Vector3 q=p+delta;')
 t=t.replace('vectorLabels[i].gameObject.SetActive(enabled[i]);','vectorLabels[i].gameObject.SetActive(enabled[i] && new[]{normal,towardLight,reflection,towardViewer,halfway}[i].enabled);')
 code['LightLabStage.cs']=t
 c=code['LightLabComparison.cs'];c=c.replace('-(shading?Vector3.zero:RenderCamera.transform.right*.48f)','');c=c.replace('if(!shading)BuildGlossReference(target+RenderCamera.transform.right*.5f,.92f,material);','');code['LightLabComparison.cs']=c
 code['LightLabSurfaceStorage.cs']=code['LightLabSurfaceStorage.cs'].replace('같은 로봇의','재질 구의')
 t=code['LightLabCapture.cs']; t=t.replace('public static void Run() {','static string[] batchFiles; static int batchIndex; public static void Batch(){batchFiles=File.ReadAllLines(Environment.GetEnvironmentVariable("M21_SPHERE_JOB_LIST"));if(!SystemInfo.graphicsDeviceName.ToLowerInvariant().Contains("basic render")&&!SystemInfo.graphicsDeviceName.ToLowerInvariant().Contains("warp"))throw new Exception("CPU WARP not active: "+SystemInfo.graphicsDeviceName); Next();} static void Next(){job=null;state=null;stage=null;cursor=0;prepared=false;locked=false;target=null;pixels=null;Environment.SetEnvironmentVariable("YAMYAM_M21_JOB",batchFiles[batchIndex++]);Run();} public static void Run() {')
 t=t.replace('job.command=="preflight"||cursor==0?2:0','cursor==0?2:0')
 t=t.replace('".png"),pixels.EncodeToPNG()', '".jpg"),pixels.EncodeToJPG(96)')
 t=t.replace('EditorApplication.Exit(e==null?0:1);','if(e==null && batchFiles!=null && batchIndex<batchFiles.Length){EditorApplication.delayCall+=Next;}else EditorApplication.Exit(e==null?0:1);')
 code['LightLabCapture.cs']=t
 h=hashlib.sha256((str(code)+(S/'ShadingLab.shader').read_text(encoding='utf-8-sig')).encode()).hexdigest()
 code['LightLabBuildVersion.cs']='namespace Yamyam.GameMath.LightLab {public static class LightLabBuildVersion {public const string Value="'+h+'";}}'
 for name,txt in code.items():(ed/name if name=='LightLabCapture.cs' else root/name).write_text(txt,encoding='utf-8')
 shutil.copy2(S/'ShadingLab.shader',root/'ShadingLab.shader');write(SB/'M21_SANDBOX.json',{'fingerprint':h,'local':True})
 jobs=[]
 for c in q['cuts']:
  s=int(c['scene'])
  if c['kind']!='explanation' or s in (HERO-{20,55})|BAKE|{78}:continue
  old=next(read(f) for f in q['jobs'] if read(f)['sceneId']==c['scene']);cu=read(old['cueFile']);start=round(c['sourceIn']*60);end=start+c['frames'];sid=c['scene'];o=W/'native'/h[:10]/sid
  # Discrete teaching states are held exactly until their cue; continuous numeric/geometry animation sampled at source-frame times.
  times={start,end-1}
  def key(t):
   f=math.ceil(t*60-.00001)
   if start<=f<end:times.add(f)
   if start<=f-1<end:times.add(f-1)
  for t0 in [0,cu.get('cardSeconds',2.5),*cu.get('stepTimes',[]),*cu.get('valueTimes',[])]:key(t0)
  def span(a,b,step):
   times.update(range(max(start,math.floor(a*60)),min(end,math.ceil(b*60))+0,step))
  if any(cu.get(n,False) for n in ['normalArrow','lightArrow','viewArrow','reflectionArrow','halfArrow']) or cu.get('lightType',0)>=2:span(0,3.15,1)
  vals=cu.get('valueTimes',[])
  if len(vals)>=2:span(vals[0],vals[-1],2)
  elif cu.get('variable','none') not in ['none',None] or s in {35,36,52,56}:span(start/60,end/60,2)
  if s in {24,29,34,69,71,77}:span(start/60,end/60,6)
  id='m21-sphere-'+sid; cu['id']=id; f=W/'native-jobs'/f'{sid}-cue.json';write(f,cu)
  j=dict(old,id=id,cueFile=str(f),expectedFingerprint=h,output=str(o),sampleFrames=sorted(times),command='preflight');jp=W/'native-jobs'/f'{sid}.json';write(jp,j)
  if not (o/'capture-success.json').is_file():jobs.append(str(jp))
 listing=W/'native-jobs/jobs.txt';listing.write_text('\n'.join(jobs),encoding='utf-8')
 if not jobs:return
 env=dict(os.environ,M21_SPHERE_JOB_LIST=str(listing))
 log=W/'native.log';res=subprocess.run([q['unity'],'-batchmode','-force-d3d11','-force-driver-type-warp','-job-worker-count','2','-projectPath',str(SB),'-executeMethod','Yamyam.GameMath.LightLab.LightLabCapture.Batch','-logFile',str(log)],env=env,creationflags=subprocess.CREATE_NO_WINDOW)
 if res.returncode: raise RuntimeError('Unity capture failed: '+str(log))
if __name__=='__main__':native()
