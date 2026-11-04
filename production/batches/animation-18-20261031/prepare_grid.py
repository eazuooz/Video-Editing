"""Prepare isolated A01 grid sources from the existing verified capture engine.

No editor refresh, capture, TTS or publishing is performed by this preparation.
Existing BOTW sources and vendor assets are read-only inputs.
"""
from pathlib import Path
import hashlib, json, shutil

R = Path(__file__).resolve().parents[3]
B = Path(__file__).resolve().parent
H = R/'projects/animation-assigning/production/grid-v1'
U = R/'unity/VideoEditing'
C = U/'Assets/VideoScenes/animation-series-v1'
OLD = U/'Assets/VideoScenes/design-d29-botw-v4'
POLD = R/'projects/kind-to-beginners/production/botw-v4'

def save(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists() or p.read_text('utf8') != text:
        p.write_text(text, encoding='utf8')

def dump(p, obj): save(p,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')

def main():
    policy=json.loads((R/'shared/publishing/video-production-control.json').read_text('utf8'))
    grant=policy['finiteBatchAuthorizations']['animation-18-20261031']
    assert grant['productionAuthorized'] and 'A01' in grant['episodeIds']
    H.mkdir(parents=True,exist_ok=True)
    original={}
    transforms={
        'DesignBotwLessonStage':'AnimationLessonStage',
        'DesignBotwCapture':'AnimationGridCapture',
        'DesignBotwBuildVersion':'AnimationGridBuildVersion',
        'DesignBotwV4':'AnimationGridV1',
        'D29BotwStage':'AnimationGridStage',
        'Yamyam.DesignVisualV2':'Yamyam.AnimationSeries',
        'design-d29-botw-v4':'animation-series-v1',
        'projects/kind-to-beginners/production/botw-v4':'projects/animation-assigning/production/grid-v1',
        'projects/kind-to-beginners/production/local/botw-v4':'projects/animation-assigning/production/local/grid-v1',
        'kind-to-beginners':'animation-assigning',
        '/botw-v4/':'/grid-v1/',
    }
    for src,dest in [('DesignBotwLessonStage.cs','AnimationLessonStage.cs'),('Editor/DesignBotwCapture.cs','Editor/AnimationGridCapture.cs')]:
        raw=(OLD/src).read_bytes(); original[str((OLD/src).relative_to(R))]=hashlib.sha256(raw).hexdigest()
        text=raw.decode('utf8')
        for a,b in transforms.items():text=text.replace(a,b)
        if 'LessonStage' in src:
            text=text.replace('camera.transform.position=new Vector3(0,7,-14);camera.transform.LookAt(new Vector3(0,1,0));camera.orthographic=true;camera.orthographicSize=5.5f;',
              'camera.transform.position=new Vector3(0,1.8f,-14);camera.transform.LookAt(new Vector3(0,1.8f,0));camera.orthographic=true;camera.orthographicSize=3.2f;')
            text=text.replace('camera.backgroundColor=Color.black;', 'camera.backgroundColor=Hex("EDEDEB");')
            text=text.replace('Box("Dark stage",new Vector3(0,-.18f,0),new Vector3(18,.28f,8),Hex("151A1D"));',
              'Box("Light grid floor",new Vector3(0,-.12f,0),new Vector3(18,.2f,8),Hex("D2D4D3"));')
            text=text.replace('File.ReadAllText(Root+"/AnimationGridStage.cs")+File.ReadAllText(Path.Combine(production,"unity-cues.json"))','File.ReadAllText(Root+"/AnimationGridStage.cs")')
            text=text.replace('Path.Combine(repo,"qwen3-tts/.venv/Scripts/python.exe")','"C:/Python/python.exe"')
        else:
            text=text.replace('new[]{"DesignVisualV2","DesignClarityV3"}', 'new[]{"DesignVisualV2","DesignClarityV3","DesignBotwV4"}')
            text=text.replace('return Directory.GetFiles(Library,"*.request",SearchOption.TopDirectoryOnly).Length>0;',
              'return Directory.GetFiles(Library,"*.request",SearchOption.TopDirectoryOnly).Length>0 || Directory.GetFiles(Library,"*.request.json",SearchOption.TopDirectoryOnly).Any(p=>p!=Request);')
            text=text.replace('Editable BOTW teaching lesson', 'Editable Animation teaching lesson')
            text=text.replace('Only the explicitly selected D29 botw-v4 revision is supported.', 'Only selected A01 animation-assigning is supported by this capture revision.')
        save(C/dest,text)
    assets=json.loads((OLD/'asset-map.json').read_text('utf8'))
    assets['assets']=[x for x in assets['assets'] if x['key'] in ['hero','heroAlt']]
    assets['scope']='A01 grid-v1 prototype: existing product011 licensed rigs, no vendor asset modifications. Runtime and new grid-camera QA pending.'
    dump(C/'asset-map.json',assets)
    raster=(POLD/'rasterize_unity_labels.py').read_text('utf8').replace('isolated BOTW Unity stage','isolated Animation Unity stage')
    save(H/'rasterize_unity_labels.py',raster)
    dump(H/'capture-provenance.json',{'reusedSourceFiles':original,'preservedOriginals':True,'vendorAssetsModified':False,'editorRefreshPerformed':False,'renderPerformed':False})
    dump(H/'authorization.json',{'episode':'A01','slug':'animation-assigning','revision':'grid-v1','batch':'animation-18-20261031','localProductionAuthorized':True,'platformMutation':False,'noUiOrFocus':True})
    print(json.dumps({'prepared':str(C),'editorRefreshPerformed':False}))

if __name__=='__main__': main()
