"""Freeze clarity-v3 source only. Does not refresh Unity or submit a capture."""
from pathlib import Path
import argparse, hashlib, json

R=Path(__file__).resolve().parents[3]
H=Path(__file__).resolve().parent
U=R/'unity/VideoEditing'
C=U/'Assets/VideoScenes/design-25-29-clarity-v3'
STAGES={'limited-color-world':'D25ColorClarityStage','kind-to-beginners':'D29ClarityStage'}
PICTURE_INPUTS={
    'D25ColorClarityStage':[
        'projects/limited-color-world/production/local/batch-v1/visual-assets/'+name
        for name in ['puyo.jpg','puyo-filter-10.jpg','puyo-filter-11.jpg','mario.jpg']],
    'D29ClarityStage':['projects/kind-to-beginners/production/local/batch-v1/sources/mk8-official-035.jpg']}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def source_files(stage):
    assert stage in STAGES.values(), 'Only explicitly selected clarity stages are supported'
    paths=[C/'DesignClarityLessonStage.cs',C/'Editor/DesignClarityCapture.cs',C/'asset-map.json',
        C/(stage+'.cs'),U/'Packages/packages-lock.json',U/'ProjectSettings/ProjectVersion.txt',
        U/'ProjectSettings/GraphicsSettings.asset',U/'ProjectSettings/QualitySettings.asset']
    # Both stages read speech cue boundaries at runtime; they are capture inputs,
    # not merely documentation. A timing change must require a fresh fingerprint.
    slug = next(slug for slug, name in STAGES.items() if name == stage)
    paths.append(R/'projects'/slug/'production/clarity-v3/unity-cues.json')
    paths += [R/path for path in PICTURE_INPUTS[stage]]
    if stage=='D25ColorClarityStage':
        contrast_shader=U/'Assets/VideoScenes/limited-color-world/clarity-v3/Shaders/D25BackgroundContrast.shader'
        if contrast_shader.exists(): paths.append(contrast_shader)
        # The green-leaf variant is built from this exact owned palette at runtime.
        # Pin the original input bytes and import settings; never edit vendor files.
        palette=U/'Assets/ThirdParty/YamyamAssetLibrary/023-low-poly-stylized-tiny-forest/EmaceArt/Low Poly Tiny Forest/Textures/EA04_LPNP-Artefacts_Colorsheet_v1.psd'
        material=U/'Assets/ThirdParty/YamyamAssetLibrary/023-low-poly-stylized-tiny-forest/EmaceArt/Low Poly Tiny Forest/Materials/EA04_LPNP-Artefacts_Colorsheet_v1.mat'
        paths += [palette,Path(str(palette)+'.meta'),material,Path(str(material)+'.meta'),
            R/'projects/limited-color-world/production/local/clarity-v3/derived-inputs/tree-source-psd-merged.png']
    # Include new supporting code/shaders, but not the generated fingerprint or other stage.
    paths += [p for p in C.rglob('*') if p.suffix in ('.cs','.shader','.hlsl') and
        p.name!='DesignClarityBuildVersion.cs' and p.name not in [s+'.cs' for s in STAGES.values()] and
        'Generated' not in p.parts]
    return sorted(set(paths))
def records_for(stage):
    paths=source_files(stage)
    for p in paths: assert p.is_file(), 'Missing frozen input: '+str(p)
    return [{'path':p.relative_to(R).as_posix(),'sha256':digest(p)} for p in paths]
def fingerprint(records): return hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
def ensure_idle():
    for name in ['DesignVisualV2','DesignClarityV3']:
        assert not (U/'Library'/f'{name}.request.json').exists(),'Capture request pending: '+name
        status=U/'Library'/f'{name}.status.json'
        if status.exists(): assert read(status).get('status') not in ['building','capturing'],'Capture active: '+name

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=list(STAGES.values()),action='append');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    stages=a.stage or [s for s in STAGES.values() if (C/(s+'.cs')).exists()]
    assert stages,'No stage deployed yet; stage authors retain staging until parent copies their source'
    records={s:records_for(s) for s in stages};fps={s:fingerprint(records[s]) for s in stages}
    if a.check:
        frozen=read(H/'clarity-code-fingerprint.json')
        for s in stages:assert frozen['fingerprints'].get(s)==fps[s],'Source changed since freeze: '+s
        print(json.dumps({'status':'unchanged','fingerprints':fps}));return
    ensure_idle()
    auth=read(H/'authorization.json');assert {x['slug'] for x in auth['revisions']}==set(STAGES)
    code='namespace Yamyam.DesignVisualV2 { public static class DesignClarityBuildVersion { public static string For(string stage) { switch(stage) { '+''.join('case "'+s+'":return "'+h+'";' for s,h in fps.items())+'default:return "unknown";} } } }\n'
    target=C/'DesignClarityBuildVersion.cs'
    if not target.exists() or target.read_text('utf-8')!=code:target.write_text(code,encoding='utf-8')
    result={'schemaVersion':1,'scope':'D25/D29 clarity-v3 only','fingerprints':fps,'filesByStage':records,
        'generatedBuildVersion':target.relative_to(R).as_posix(),'generatedBuildVersionSha256':digest(target),
        'renderRequests':{'D25ColorClarityStage':'RenderPipeline.StandardRequest; world only, editorial UI composited separately',
                          'D29ClarityStage':'RenderPipeline.StandardRequest; unchanged single-camera stage with UI'},
        'refreshOrCaptureStarted':False}
    (H/'clarity-code-fingerprint.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(fps))
if __name__=='__main__':main()
