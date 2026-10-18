"""Deterministic scene assets and isolated capture staging; never starts Unity."""
from pathlib import Path
import json, shutil, uuid

ROOT = Path(__file__).resolve().parents[5]
SOURCE = Path(__file__).resolve().parent
PROJECT = ROOT / 'projects/game-math-euler-axis-angle'
LOCAL = PROJECT / 'production/local/revision-v2'
ISOLATED = LOCAL / 'unity-capture'
REL = Path('Assets/VideoScenes/game-math-euler-axis-angle')

def guid(path):
    return uuid.uuid5(uuid.NAMESPACE_URL, 'yamyam-m04:' + str(path).replace('\\', '/')).hex

def metadata(path):
    meta = Path(str(path) + '.meta')
    if meta.exists():
        return next(line.split(':', 1)[1].strip() for line in meta.read_text().splitlines() if line.startswith('guid:'))
    relative = path.relative_to(SOURCE.parent)
    g = guid(relative)
    folder = 'folderAsset: yes\n' if path.is_dir() else ''
    importer = 'DefaultImporter' if path.is_dir() or path.suffix == '.unity' else 'MonoImporter' if path.suffix == '.cs' else 'AssemblyDefinitionImporter' if path.suffix == '.asmdef' else 'DefaultImporter'
    meta.write_text(f'fileFormatVersion: 2\nguid: {g}\n{folder}{importer}:\n  externalObjects: {{}}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n', encoding='utf8')
    return g

def main():
    SOURCE.joinpath('Scenes').mkdir(exist_ok=True)
    metadata(SOURCE)
    for p in sorted(SOURCE.rglob('*')):
        if p.suffix != '.meta': metadata(p)
    script_guid = metadata(SOURCE / 'EulerAircraftScene.cs')
    lesson_path = PROJECT/'production/revision-v2/lesson.json'
    if not lesson_path.exists():
        lesson_path = ROOT/'production/batches/game-math-part2-full-series/lessons/game-math-euler-axis-angle.json'
    lesson = json.loads(lesson_path.read_text(encoding='utf8'))
    scene_ids = {'03','04','06','07','09','10','12','16','18','19','21','22'}
    scenes = []
    for source in lesson['scenes']:
        if source['id'] not in scene_ids: continue
        sid, mode = source['id'], source['mode']
        pair = mode in {'extrinsic','order','aliases','gimbal-values','interpolation','axis-aliases','nonadd'}
        scene = SOURCE / f'Scenes/{sid}-{mode}.unity'
        if not scene.exists():
            # Editable deterministic source scene. The explicit builder bakes
            # its procedural children in the isolated editor, never the user's open scene.
            scene.write_text(f'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &1000
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: 1001}}
  - component: {{fileID: 1002}}
  m_Layer: 0
  m_Name: Yamyam M04 scene {sid}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &1001
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 1000}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: 0}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!114 &1002
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 1000}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}
  m_Name: 
  m_EditorClassIdentifier: 
  sceneId: '{sid}'
  lessonMode: {mode}
  durationSeconds: 30
  normalizedTime: 0
  playInRuntime: 0
  showWorldAxes: 1
  showBodyAxes: 1
  background: {{r: 1, g: 1, b: 1, a: 1}}
  cameraMathPosition: {{x: 7, y: 4.5, z: 8}}
  orthographicSize: {5.4 if pair else 4.9}
  cameraMathTarget: {{x: 0, y: -0.35, z: 0}}
--- !u!1660057539 &9223372036854775807
SceneRoots:
  m_ObjectHideFlags: 0
  m_Roots:
  - {{fileID: 1001}}
''', encoding='utf8')
        metadata(scene)
        scenes.append(dict(id=sid, mode=mode, title=source['title'], scene=str(scene.relative_to(ROOT)).replace('\\','/'),
            geometry='Self-authored articulated propulsive aircraft; orientation illustration, not measured game simulation',
            pair=pair, cueCount=len(source['ko']), mathContract=lesson['contract'],
            before='Body axes aligned with world axes or explicitly labeled comparison starting pose',
            action=source['beats'], result=source['beats'][-1],
            timing='Measured narration -> capture keys frame/normalized; six default staged beats are editable, no fixed total runtime',
            labels='Parent composites canonical terms/formulas and axis names from anchors; fixed caption center 960,970,48px,max2lines',
            status='Source scene exists; first visual-system bake/preview completed. Updated layout and current narration profiles require fresh bake during coordinated capture.'))
    plan = dict(schemaVersion=1, slug=lesson['slug'], renderer='Unity', editorVersion='6000.6.0f1',
        canonicalPipeline='Main project URP17.6.0 PC quality; no settings changed',
        isolatedCapturePipeline='Built-in renderer in disposable isolated project, linear color, no shadows/postprocessing',
        palette=dict(background='#FFFFFF',aircraft='#F4BC33',cockpit='#2C4859',x='#D53442',y='#15854C',z='#2264C3'),
        axisConversion=dict(C='diag(1,1,-1)',point='pUnity=C pMath',rotation='RUnity=C RMath C',
            nose='math+z maps to Unity-z',triangleWinding='Swap triangle indices1/2 after reflected geometry',
            matrix='R=Ry(h)Rx(p)Rz(b),right-handed,column-vectors,local-to-world',
            sanity=['Rx(+90)*(0,0,1)=(0,-1,0)','Ry(+90)*(0,0,1)=(1,0,0)']),
        capture=dict(width=1920,height=1080,fps=60,audio=False,stream='RGB24 pipe -> x264, yuv420p, vertical flip',
            anchorCoordinates='top-left pixels at1920x1080; depth + inFrame. Occlusion is NOT a detector result; parent verifies/hides labels.',
            captionReserve=dict(center=[960,970],fontSize=48,maxLines=2,clearanceBottomY=890),
            cameraMathPosition=[7,4.5,8],cameraMathTarget=[0,-.35,0],orthographic=True,
            currentLayout=dict(singleCenter=[580,470],singleOrtho=3.6,pairCenters=[[560,470],[1320,470]],pairOrtho=3.9,pairScale=.8,
                note='Presentation translations preserve exact rotation matrices. Upper+Yaxis can occupy y90; place title away from that band. Currentlayout not yet GPUcaptured.')),
        lessonSource=str(lesson_path.relative_to(ROOT)).replace('\\','/'),
        measuredTimingAdapter='prepare-capture-job.py --timeline <revision-v2/timeline.json>; scenes{id,frames,seconds,lineStarts[]}',
        provenance=dict(author='Yamyam Coding procedural source',downloadedAssets=False,externalLicenseNeeded=False),scenes=scenes)
    (SOURCE/'scene-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    metadata(SOURCE/'scene-plan.json')
    dest = ISOLATED/REL
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree(SOURCE,dest,dirs_exist_ok=True)
    shutil.copy2(Path(str(SOURCE)+'.meta'),Path(str(dest)+'.meta'))
    (ISOLATED/'Packages').mkdir(exist_ok=True)
    for f in ['manifest.json','packages-lock.json']:
        shutil.copy2(ROOT/'unity/VideoEditing/Packages'/f,ISOLATED/'Packages'/f)
    (ISOLATED/'ProjectSettings').mkdir(exist_ok=True)
    for f in ['ProjectVersion.txt','ProjectSettings.asset','GraphicsSettings.asset','QualitySettings.asset','TagManager.asset','TimeManager.asset','EditorSettings.asset']:
        source = ROOT/'unity/VideoEditing/ProjectSettings'/f
        if source.exists(): shutil.copy2(source,ISOLATED/'ProjectSettings'/f)
    # Only copied local QualitySettings is de-referenced: the task-owned stage
    # deliberately does not copy unrelated project pipeline assets.
    quality=ISOLATED/'ProjectSettings/QualitySettings.asset'
    import re
    quality.write_text(re.sub(r'customRenderPipeline:.*', 'customRenderPipeline: {fileID: 0}',quality.read_text()),encoding='utf8')
    ffmpeg=shutil.which('ffmpeg')
    job=dict(outputDirectory=str(LOCAL/'unity-preview'),ffmpegPath=ffmpeg,renderPngPreviewsOnly=False,
        clips=[dict(sceneId='03',fileStem='03-rotation-sample',frames=180,startNormalized=0,endNormalized=1)])
    (LOCAL/'unity-preview-job.json').write_text(json.dumps(job,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(sceneCount=len(scenes),canonicalSource=str(SOURCE),isolated=str(ISOLATED),job=str(LOCAL/'unity-preview-job.json')),ensure_ascii=False))

if __name__ == '__main__': main()
