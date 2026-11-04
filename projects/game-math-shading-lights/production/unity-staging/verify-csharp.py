"""Compile M21 staging C# against installed Unity assemblies without starting Unity."""
from pathlib import Path
import subprocess,json,hashlib
STAGING=Path(__file__).resolve().parent
REPO=STAGING.parents[3]
EDITOR=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data')
ASSEMBLIES=REPO/'unity/VideoEditing/Library/ScriptAssemblies'
refs=list((EDITOR/'Managed/UnityEngine').glob('*.dll'))+[EDITOR/'NetStandard/ref/2.1.0/netstandard.dll']
refs += [ASSEMBLIES/name for name in ['UnityEngine.UI.dll','Unity.RenderPipelines.Universal.Runtime.dll','Unity.RenderPipelines.Core.Runtime.dll','Unity.Collections.dll','Unity.Mathematics.dll']]
files=[STAGING/name for name in ['LightLabStage.cs','LightLabCapture.cs','LightLabIllustrations.cs','LightLabMathIllustrations.cs','LightLabComparison.cs','LightLabGeometry.cs','LightLabBakedRoom.cs','LightLabBuildVersion.cs']]
args=['-nologo','-target:library','-define:UNITY_EDITOR','-langversion:latest','-out:'+str(STAGING/'local-compile.dll')]+['-r:'+str(p) for p in refs]+[str(p) for p in files]
p=subprocess.run([str(EDITOR/'DotNetSdk/dotnet.exe'),str(EDITOR/'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll'),*args],capture_output=True,text=True)
(STAGING/'compile-check.json').write_text(json.dumps({'exitCode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'scope':'C# compilation only; no Unity process, GPU work, shader compilation, runtime, saved-scene or visual QA'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(p.stdout,p.stderr)
raise SystemExit(p.returncode)
