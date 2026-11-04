from pathlib import Path
import subprocess,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
E=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data');SDK=E/'DotNetSdk'
CSC=[str(SDK/'dotnet.exe'),str(SDK/'sdk/8.0.318/Roslyn/bincore/csc.dll')]
sources=[P/'SkinNormalMath.cs',P/'KnightRigAdapter.cs',P/'SkinNormalTeachingStage.cs',P/'SkinNormalSceneBuilder.cs']
refs=list((E/'Managed/UnityEngine').glob('*.dll'))+[E/'NetStandard/ref/2.1.0/netstandard.dll',ROOT/'unity/VideoEditing/Library/ScriptAssemblies/UnityEngine.UI.dll']
compile=subprocess.run(CSC+['-nologo','-define:UNITY_EDITOR','-target:library','-langversion:latest','-out:'+str(P/'local-module.dll')]+['-r:'+str(r) for r in refs]+list(map(str,sources)),capture_output=True,text=True)
result={'csharpCompilation':{'exitCode':compile.returncode,'stdout':compile.stdout,'stderr':compile.stderr},'files':{s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sources+[P/'SkinNormalSurface.shader']},'scope':'CPU C# compile and independent numeric invariants only; no Unity invocation, shader compile, GPU/rendering, scene save, imported rig runtime, font or mobile QA.'}
if compile.returncode==0:
 netrefs=list((SDK/'packs/Microsoft.NETCore.App.Ref/8.0.21/ref/net8.0').glob('*.dll'))
 build=subprocess.run(CSC+['-nologo','-target:exe','-langversion:latest','-out:'+str(P/'local-checks.dll')]+['-r:'+str(r) for r in netrefs]+[str(P/'SkinNormalMath.cs'),str(P/'SkinNormalChecks.cs')],capture_output=True,text=True)
 (P/'local-checks.runtimeconfig.json').write_text(json.dumps({'runtimeOptions':{'tfm':'net8.0','framework':{'name':'Microsoft.NETCore.App','version':'8.0.21'}}}),encoding='utf-8')
 result['mathCheckCompilation']={'exitCode':build.returncode,'stdout':build.stdout,'stderr':build.stderr}
 if build.returncode==0:
  run=subprocess.run([str(SDK/'dotnet.exe'),str(P/'local-checks.dll')],capture_output=True,text=True);result['mathChecks']={'exitCode':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
  if run.returncode==0:result['numericEvidence']=json.loads(run.stdout)
(P/'compile-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(compile.returncode or result.get('mathCheckCompilation',{}).get('exitCode',1) or result.get('mathChecks',{}).get('exitCode',1))
