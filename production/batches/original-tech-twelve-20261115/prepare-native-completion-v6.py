"""CPU-only explicit source derivation and compilation for three recovery cases."""
from pathlib import Path
import copy,hashlib,importlib.util,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');RUN=MEDIA/'production-resume-20261115T055255Z';OUT=HERE/'native-completion-source-v6'
def pin(p):return dict(path=str(Path(p).resolve()),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,t):assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,'utf8')
def main():
 sink=HERE/'native-remaining-selected-storage-v5/LosslessFrameSink.cs';write(OUT/'LosslessFrameSink.cs',sink.read_text(encoding='utf8'));cases=[]
 for case,helper,receipt in [('placement','run-bounded-native-v3.py','native-bounded-static-v3'),('temporal','run-streamed-native-v2.py','native-stream-static-v2'),('remaining-seven','run-remaining-selected-native-v5.py','native-remaining-selected-static-v5')]:
  spec=importlib.util.spec_from_file_location('source_only_'+case,HERE/helper);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.configure(case);prep=m.prepare();replacements=[]
  f=next(x for x in prep['files']if Path(x['source']).name=='LosslessFrameSink.cs');replacements.append(dict(original=pin(f['source']),derived=pin(OUT/'LosslessFrameSink.cs')))
  if case=='remaining-seven':
   f=next(x for x in prep['files']if Path(x['source']).name=='RemainingCapture.cs');text=Path(f['source']).read_text(encoding='utf8');assert text.count('static void BeginCamera(){index=0;')==1;text=text.replace('static void BeginCamera(){index=0;','static bool primeCamera;static void BeginCamera(){primeCamera=true;index=0;');assert text.count('camera.targetTexture=rt;camera.Render();var previous=')==1;text=text.replace('camera.targetTexture=rt;camera.Render();var previous=','camera.targetTexture=rt;camera.Render();if(primeCamera){primeCamera=false;return;}var previous=');p=OUT/'RemainingCapture.cs';write(p,text);replacements.append(dict(original=pin(f['source']),derived=pin(p)))
  if case=='temporal':
   f=next(x for x in prep['files']if Path(x['source']).name=='TemporalReprojection.shader');original=Path(f['source']).read_text(encoding='utf-8-sig');text="// Upgrade NOTE: replaced 'mul(UNITY_MATRIX_MVP,*)' with 'UnityObjectToClipPos(*)'\n\n"+original.replace('mul(UNITY_MATRIX_MVP, IN.vertex)','UnityObjectToClipPos(IN.vertex)');p=OUT/'TemporalReprojection.shader';write(p,text);staged=Path(prep['project'])/f['target'];assert text.replace('\r','')==staged.read_text(encoding='utf-8-sig').replace('\r','');replacements.append(dict(original=pin(f['source']),derived=pin(p)))
  prior=next(x for x in read(RUN/receipt/'compile-receipt.json')['groups']if x['case']==case);response=Path(prior['responseFile']);rsp=response.read_text(encoding='utf-8-sig');folder=RUN/'native-completion-static-v6'/case;folder.mkdir(parents=True,exist_ok=False)
  # Response-file paths are compiler data, never shell interpolation.
  for x in replacements:
   if Path(x['original']['path']).suffix=='.cs':rsp=rsp.replace(x['original']['path'],x['derived']['path'])
  import re
  assert len(re.findall(r'(?m)^[-/]out:.*$',rsp))==1
  rsp=re.sub(r'(?m)^[-/]out:.*$',lambda _: '/out:"'+str(folder/'capture.dll')+'"',rsp);rspfile=folder/'compile.rsp';write(rspfile,rsp)
  dotnet=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data/NetCoreRuntime/dotnet.exe');csc=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data/DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll');r=subprocess.run([str(dotnet),str(csc),'@'+str(rspfile)],capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));write(folder/'compile.log',r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
  sources=[]
  for f in prep['files']:
   if Path(f['source']).suffix!='.cs':continue
   hit=next((x for x in replacements if Path(x['original']['path']).resolve()==Path(f['source']).resolve()),None);sources.append(hit['derived']if hit else pin(f['source']))
  cp=folder/'compile-receipt.json';write(cp,json.dumps(dict(case=case,staticCompilationPassed=True,sourceInputs=sources,originalModelSemanticProof=prep['originalModelSemanticProof'],responseFile=pin(rspfile),compileLog=pin(folder/'compile.log'),gpuUsed=False),indent=2)+'\n');cases.append(dict(case=case,replacements=replacements,compiler=pin(cp),changes=('Use new D output storage only. No placement model or sample-time change.'if case=='placement'else 'Only the pre-Unity540 inactive shader branch is upgraded; Unity6000 active branch and MIT notices are byte unchanged.'if case=='temporal'else 'Discard one startup render before recording each selected camera, allowing its unchanged sampled idle pose to settle. Recorded model frames remain0..719 at60fps, one sample per Editor callback. Fix only the observed DOOM frame0 startup pose discrepancy.')))
 write(OUT/'source-review.json',json.dumps(dict(cases=cases,legacyGuardUnchanged=True,thresholdsUnchanged=True,originalAndPartialCapturesPreserved=True,newNativeCaptureComplete=False),indent=2)+'\n');print(json.dumps(dict(prepared=pin(OUT/'source-review.json'),cases=len(cases))))
if __name__=='__main__':main()
