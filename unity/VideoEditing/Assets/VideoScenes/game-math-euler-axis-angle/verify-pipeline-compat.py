"""CPU-only source compatibility checks; never opens a Unity editor/renderer."""
from pathlib import Path
import hashlib,importlib.util,json,re,sys

sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[5]
spec=importlib.util.spec_from_file_location('m04sync',OWN/'sync-baked-assets.py')
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    settings=[ROOT/'unity/VideoEditing/ProjectSettings'/f for f in ['GraphicsSettings.asset','QualitySettings.asset','ProjectSettings.asset']]
    before={str(p):sha(p) for p in settings}
    packages=ROOT/'unity/VideoEditing/Library/PackageCache'
    shaders={}
    for name,expected in [('Lit',sync.LIT),('Unlit',sync.UNLIT)]:
        found=[]
        for meta in packages.glob(f'com.unity.render-pipelines.universal@*/Shaders/{name}.shader.meta'):
            if re.search(r'^guid: '+expected+r'$',meta.read_text(),re.M):found.append(meta)
        if not found:raise AssertionError(f'InstalledURP{name}shaderGUIDnot found.')
        source=Path(str(found[0])[:-5])
        shader_text=source.read_text(encoding='utf8')
        assert f'Shader "Universal Render Pipeline/{name}"' in shader_text
        assert '"RenderPipeline" = "UniversalPipeline"' in shader_text
        for prop in ['_BaseMap','_BaseColor','_Surface','_Blend','_Cull','_ZWrite']:
            assert prop in shader_text,(name,prop)
        shaders[name]=dict(path=str(source.relative_to(ROOT)),guid=expected,sha256=sha(source))
    changed=0;materials=[]
    for mat in sorted((OWN/'Shared').glob('*.mat')):
        original=mat.read_text(encoding='utf8')
        text,shader=sync.convert_material(original)
        # This only updates the task-owned .mat source. GUIDs/shared references
        # and all project settings remain exactly as they were.
        if text!=original:mat.write_text(text,encoding='utf8');changed+=1
        again,_=sync.convert_material(text);assert again==text,'Conversion must be idempotent.'
        assert f'guid: {shader}' in text and '_BaseColor:' in text and '_BaseMap:' in text
        for prop,value in [('_Surface',0),('_Blend',0),('_AlphaClip',0),('_ZWrite',1)]:
            assert re.search(r'    - '+prop+r': '+str(value)+r'\n',text),(mat,prop)
        materials.append(dict(path=str(mat.relative_to(ROOT)),shaderGuid=shader,sha256=sha(mat)))
    scenes=[]
    for scene in sorted((OWN/'Scenes').glob('*.unity')):
        text=scene.read_text(encoding='utf8')
        for name in ['Generated lesson geometry','1080p60 fixed camera','Aircraft A','Fixed world axes',
            'Port hinged aileron','Starboard hinged aileron','Hinged elevator','Hinged rudder']:
            assert 'm_Name: '+name in text,(scene,name)
        scenes.append(dict(path=str(scene.relative_to(ROOT)),savedHierarchyCanBeRebound=True))
    after={str(p):sha(p) for p in settings};assert before==after
    report=dict(schemaVersion=1,scope='CPU structural/source validation; no renderedURPpreview claimed',
        installedShaderSources=shaders,canonicalSourceMaterialCount=len(materials),updatedOwnedMaterialCount=changed,
        materialSources=materials,sourceScenes=scenes,settingsUnchanged=True,settingsHashes=before,
        startupBehavior='Bind/reuse serialized or named saved hierarchy; clone only incompatible material instances. Do not automatically discard editable geometry.',
        currentRuntimeCompile='Must pass standalone installedUnity C#compiler; next coordinated editor bake persists new serialized references',
        visualURPPlayback='Pending a genuinely rendered URP view; no GPU/media job was launched for this CPU check.')
    (OWN/'pipeline-compatibility.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(status='passed',materials=len(materials),scenes=len(scenes),updatedOwnedMats=changed,
        projectSettingsUnchanged=True,gpuOrMediaJobsStarted=False),ensure_ascii=False))

if __name__=='__main__':main()
