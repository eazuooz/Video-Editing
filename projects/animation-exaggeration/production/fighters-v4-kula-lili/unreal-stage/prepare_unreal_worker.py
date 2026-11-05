"""Prepare an isolated editor workspace; vendor directories are reference-only.

The user's open GameAnimationSample editor, project descriptor and assets are
never modified. Generated assets live only beneath /Game/YamyamA02 in the worker.
"""
from pathlib import Path
import json, subprocess, hashlib

H = Path(__file__).resolve().parent
R = H.parents[4]
L = H.parents[1] / 'local/fighters-v4-kula-lili'
SOURCE = R / 'GameAnimationSample'
WORKER = L / 'unreal-worker'

def main():
    auth=json.loads((H.parent/'authorization.json').read_text(encoding='utf-8'))
    assert auth['localProductionAuthorized'] and auth['revision']=='fighters-v4-kula-lili'
    source_project=SOURCE/'GameAnimationSample.uproject'
    descriptor=json.loads(source_project.read_text(encoding='utf-8-sig'))
    assert descriptor['EngineAssociation']=='5.8'
    (WORKER/'Content').mkdir(parents=True,exist_ok=True)
    links=[]
    for directory in sorted((SOURCE/'Content').iterdir()):
        if not directory.is_dir() or directory.name.startswith('Yamyam'):continue
        target=WORKER/'Content'/directory.name
        if target.exists():
            assert target.resolve()==directory.resolve(),str(target)
        else:
            # Both paths are fixed descendants of the inspected source/workspace.
            def ps(s):return "'"+str(s).replace("'","''")+"'"
            subprocess.run(['powershell','-NoProfile','-Command',
                'New-Item -ItemType Junction -Path '+ps(target)+' -Target '+ps(directory)+' | Out-Null'],check=True)
        links.append({'worker':str(target),'source':str(directory),'usage':'read-only reference; generator writes only YamyamA02'})
    worker_descriptor={
        'FileVersion':3,'EngineAssociation':'5.8','Category':'Video production',
        'Description':'A02 isolated production worker referencing user-installed sample assets.',
        'Plugins':descriptor['Plugins']+[
            {'Name':'PythonScriptPlugin','Enabled':True},
            {'Name':'SequencerScripting','Enabled':True},
            {'Name':'MovieRenderPipeline','Enabled':True},
            {'Name':'ControlRig','Enabled':True}
        ]}
    (WORKER/'A02Worker.uproject').write_text(json.dumps(worker_descriptor,indent=2)+'\n',encoding='utf-8')
    (WORKER/'Config').mkdir(exist_ok=True)
    (WORKER/'Config/DefaultEngine.ini').write_text('''[/Script/Engine.RendererSettings]
r.DynamicGlobalIlluminationMethod=0
r.ReflectionMethod=0
r.RayTracing=False
r.Shadow.Virtual.Enable=0
r.SkinCache.CompileShaders=True
r.DefaultFeature.AutoExposure=False
r.DefaultFeature.MotionBlur=False

[/Script/EngineSettings.GameMapsSettings]
EditorStartupMap=/Engine/Maps/Templates/Template_Default
GameDefaultMap=/Engine/Maps/Templates/Template_Default

[/Script/PythonScriptPlugin.PythonScriptPluginSettings]
bRemoteExecution=False
''',encoding='utf-8')
    (L/'unreal').mkdir(parents=True,exist_ok=True)
    record={'sourceProject':str(source_project),'sourceProjectSha256':hashlib.sha256(source_project.read_bytes()).hexdigest(),
        'workerProject':str(WORKER/'A02Worker.uproject'),'sourceEditorTouched':False,
        'ownedAssetRoot':'/Game/YamyamA02','vendorJunctions':links,
        'engine':'5.8','reason':'Preserve user editor state and source assets; CLI worker writes isolated owned assets.'}
    (H/'unreal-workspace.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'worker':record['workerProject'],'referenceDirectories':len(links)}))

if __name__=='__main__':main()
