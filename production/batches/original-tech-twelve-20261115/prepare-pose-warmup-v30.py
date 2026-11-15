from pathlib import Path
import copy,hashlib,json,re,subprocess
H=Path(__file__).resolve().parent;R=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/production-resume-20261115T055255Z');O=H/'native-pose-warmup-v30'
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,t):assert not p.exists(),p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t,'utf8')
original=H/'native-completion-source-v6/RemainingCapture.cs';s=original.read_text(encoding='utf8');old='demo.Apply(frame);var camera=cameraIndex==0?demo.overview:demo.detail;';assert s.count(old)==1
s=s.replace(old,'demo.Apply(primeCamera?1:frame);var camera=cameraIndex==0?demo.overview:demo.detail;');derived=O/'RemainingCapture.cs';write(derived,s)
prior=read(H/'native-completion-source-v6/source-review-v2.json');entry=next(x for x in prior['cases']if x['case']=='remaining-seven');cp=Path(entry['compiler']['path']);c=read(cp);rsp=Path(c['responseFile']['path']).read_text(encoding='utf-8-sig').replace(str(original),str(derived));folder=R/'native-pose-static-v30';folder.mkdir(exist_ok=False)
rsp=re.sub(r'(?m)^[-/]out:.*$',lambda _:'/out:"'+str(folder/'capture.dll')+'"',rsp);rf=folder/'compile.rsp';write(rf,rsp)
u=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data');res=subprocess.run([str(u/'NetCoreRuntime/dotnet.exe'),str(u/'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll'),'@'+str(rf)],capture_output=True,text=True);write(folder/'compile.log',res.stdout+res.stderr);assert res.returncode==0,res.stdout+res.stderr
c=copy.deepcopy(c);c['sourceInputs']=[pin(derived)if Path(x['path'])==original else x for x in c['sourceInputs']];c.update(responseFile=pin(rf),compileLog=pin(folder/'compile.log'),compiledBinary=pin(folder/'capture.dll'));receipt=folder/'compile-receipt.json';write(receipt,json.dumps(c,indent=2)+'\n');entry=copy.deepcopy(entry)
for x in entry['replacements']:
 if Path(x['derived']['path'])==original:x['derived']=pin(derived)
entry['compiler']=pin(receipt);review=O/'source-review.json';write(review,json.dumps(dict(priorDerivation=pin(H/'native-completion-source-v6/source-review-v2.json'),cases=[entry],change='Warm up the animation at adjacent frame1, then sample actual frame0 in the next Editor callback, forcing the startup skeletal pose to update before capture. No recorded frame/time/model changes. Strict32-frame baseline and encoded RGB equality still required.',failedCapturePreserved=True,gpuUsedForPreparation=False),indent=2)+'\n')
s=(H/'run-native-completion-v6.py').read_text(encoding='utf8').replace('native-completion-v6','native-pose-warmup-v30').replace('native-completion-source-v6/source-review-v2.json','native-pose-warmup-v30/source-review.json').replace('smoke-visual-review-v6.json','smoke-visual-review-v30.json');s=s.replace("CONFIG={'placement'", "CONFIG={'placement'")
write(H/'run-native-pose-warmup-v30.py',s)
s=(H/'run-cooperative-native-v19.py').read_text(encoding='utf8').replace('run-native-completion-v6.py','run-native-pose-warmup-v30.py');write(H/'run-cooperative-native-pose-v30.py',s)
print(json.dumps(dict(sourceReview=pin(review),staticCompilationPassed=True)))
