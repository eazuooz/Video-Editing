"""Compile capture transport without starting Unity or touching GPU jobs."""
from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parent;R=P.parents[2];E=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data')
S=R/'projects/game-math-skinning-normal-map/production/unity-staging/LocalUnity-v2'
refs=list((E/'Managed/UnityEngine').glob('*.dll'))+[E/'NetStandard/ref/2.1.0/netstandard.dll']
libs=R/'unity/VideoEditing/Library/ScriptAssemblies'
refs += [libs/n for n in ['UnityEngine.UI.dll','Unity.RenderPipelines.Core.Runtime.dll','Unity.RenderPipelines.Core.Runtime.Shared.dll','Unity.RenderPipelines.Universal.Runtime.dll','Unity.RenderPipelines.Universal.Editor.dll']]
cmd=[str(E/'DotNetSdk/dotnet.exe'),str(E/'DotNetSdk/sdk/8.0.318/Roslyn/bincore/csc.dll'),'-nologo','-target:library','-langversion:latest','-define:UNITY_EDITOR','-out:'+str(P/'local-capture-transport.dll')]+['-r:'+str(x) for x in refs]+[str(P/'UnityLectureCapture.cs'),str(S/'Assets/VideoScenes/game-math-skinning-normal-map/Editor/LectureBuildVersion.cs')]
r=subprocess.run(cmd,capture_output=True,text=True)
record={'exitCode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'sourceSha256':hashlib.sha256((P/'UnityLectureCapture.cs').read_bytes()).hexdigest(),'unityStarted':False,'runtimeValidation':False}
(P/'capture-transport-compile.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2));raise SystemExit(r.returncode)
