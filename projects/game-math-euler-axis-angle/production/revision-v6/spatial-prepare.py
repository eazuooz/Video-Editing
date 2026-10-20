"""CPU-only V6 source/shot planning. Never starts Unity or a media process."""
from pathlib import Path
import argparse, copy, hashlib, json, re, shutil, uuid

ROOT = Path(__file__).resolve().parents[4]
P = ROOT / 'projects/game-math-euler-axis-angle'
H = P / 'production/revision-v6'
LOCAL = P / 'production/local/revision-v6'
OLD = ROOT / 'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle'
OWN = OLD / 'revision-v6'
ISO = LOCAL / 'unity-capture'
REL = Path('Assets/VideoScenes/game-math-euler-axis-angle/revision-v6')

def vector(v): return dict(zip(('x','y','z'), v))
def key(t, value=(0,0,0), position=(0,0,0), scale=(1,1,1)):
    return dict(t=t,value=vector(value),position=vector(position),scale=vector(scale))
def euler(*keys, linear=False):return dict(kind='euler',keys=list(keys),linear=linear)
def pose(h=0,p=0,b=0):return euler(key(0,(h,p,b)),key(1,(h,p,b)))
def move(a,b):return euler(key(0,a),key(1,b))
def rotvec(axis, degrees0, degrees1, linear=False):
    from math import radians
    return dict(kind='rotvec',keys=[key(0,tuple(radians(degrees0)*x for x in axis)),key(1,tuple(radians(degrees1)*x for x in axis))],axis=vector(axis),hasAxis=True,linear=linear)
def sequence(initial=(0,0,0), steps=(), linear=False):
    return dict(kind='sequence',initialEuler=vector(initial),steps=[dict(space=space,axis=vector(axis),degrees=deg,start=a,end=b) for space,axis,deg,a,b in steps],linear=linear)
X=(1,0,0);Y=(0,1,0);Z=(0,0,1)
def write_source(path,text):
    """Keep owned generated source/YAML free of insignificant line-end spaces."""
    path.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n',encoding='utf8')
def body_hpb(h,p,b):return sequence(steps=[('body',Y,h,0,.30),('body',X,p,.35,.65),('body',Z,b,.70,1)])
def fixed_bph(h,p,b):return sequence(steps=[('upright',Z,b,0,.30),('upright',X,p,.35,.65),('upright',Y,h,.70,1)])

def specs():
    """Physical geometry only; arithmetic/terminology stays in the root's2D renderer."""
    s={}
    def add(sid,beat,a,b=None,**kw):
        s[(f'v6-{sid:02}',beat)]=dict(a=a,b=b,pair=b is not None,**kw)
    add(1,1,sequence(steps=[('upright',Y,45,0,.42),('upright',X,20,.50,1)]),sequence(steps=[('upright',X,20,0,.42),('upright',Y,45,.50,1)]),axes=False)
    add(2,1,euler(key(0),key(.28,position=(1.2,0,0)),key(.53),key(1,(0,0,35))),pose(),axes=False)
    add(2,2,move((0,0,0),(25,15,20)))
    add(2,3,move((25,15,20),(0,0,0)))
    add(3,2,move((0,0,0),(90,0,0)),activeAxis='uprightY',arcDegrees=90)
    add(4,1,move((0,0,0),(45,0,0)),activeAxis='uprightY',arcDegrees=45)
    add(4,2,move((0,0,0),(45,0,0)),cameraPosition=(0,11,.001),activeAxis='uprightY',arcDegrees=45)
    add(5,1,move((45,0,0),(45,20,0)),activeAxis='pitchX',arcDegrees=20)
    add(5,2,move((45,0,0),(45,20,0)),sequence((45,0,0),[('upright',X,20,0,1)]))
    add(6,1,move((45,20,0),(45,20,30)),activeAxis='bodyZ',arcDegrees=30)
    add(6,2,body_hpb(45,20,30))
    add(7,1,move((0,0,0),(0,0,90)),cameraPosition=(0,.001,-11),activeAxis='bodyZ',arcDegrees=90)
    add(7,2,pose(0,0,45),cameraPosition=(5,3,-9),cameraEndPosition=(5,3,9),moveCamera=True,activeAxis='bodyZ',arcDegrees=45)
    add(8,1,pose(45,20,0),move((45,20,0),(45,20,35)))
    add(10,1,body_hpb(45,20,30))
    add(10,2,body_hpb(45,20,30),fixed_bph(45,20,30))
    add(11,1,sequence(steps=[('body',Y,30,0,.43),('body',X,20,.55,1)]),pose())
    add(11,2,pose(30,20,0),sequence(steps=[('upright',X,20,0,.43),('upright',Y,30,.55,1)]))
    add(11,3,sequence(steps=[('upright',X,90,0,.43),('upright',Y,90,.55,1)]),sequence(steps=[('upright',Y,90,0,.43),('upright',X,90,.55,1)]))
    add(12,1,move((0,0,0),(0,90,0)))
    add(12,2,sequence((0,90,0),[('body',Y,90,0,1)]),sequence((0,90,0),[('upright',Y,90,0,1)]))
    add(13,1,move((30,20,35),(30,50,35)),sequence((30,20,35),[('body',X,30,0,1)]))
    add(13,2,sequence((0,30,0),steps=[('upright',Y,55,0,.35),('body',X,20,.42,.65),('body',Y,150,.72,1)]),model='top')
    add(15,1,euler(key(0),key(.45,(30,0,0)),key(1,(30,10,0))))
    add(18,1,move((0,0,0),(720,0,0)),linear=True)
    add(18,2,move((0,0,0),(0,135,0)),move((0,0,0),(180,45,180)))
    add(20,1,euler(key(0,(0,45,0)),key(.5,(0,80,0)),key(1,(0,90,0))),gimbals=True)
    add(20,2,euler(key(0,(30,90,10)),key(.45,(20,90,0)),key(.55,(45,90,0)),key(1,(45,90,0))),euler(key(0,(20,90,0)),key(.45,(20,90,0)),key(.55,(0,90,-45)),key(1,(0,90,-45))),gimbals=True)
    add(20,3,move((30,-90,10),(40,-90,0)),pose(40,-90,0),gimbals=True)
    add(27,1,move((0,80,0),(5,90,5)),gimbals=True)
    add(27,2,move((0,0,0),(0,135,0)),move((0,0,0),(180,45,180)),linear=True)
    add(27,3,move((0,0,0),(90,60,90)),linear=True)
    from math import sqrt, sin, cos, asin, atan2, degrees, radians
    n=(1/sqrt(3),1/sqrt(3),1/sqrt(3))
    c=cos(radians(80));ss=sin(radians(80));t=1-c;x,y,z=n
    h=degrees(atan2(z*x*t+y*ss,c+z*z*t));pp=degrees(asin(-(z*y*t-x*ss)));b=degrees(atan2(x*y*t+z*ss,c+y*y*t))
    add(30,1,body_hpb(h,pp,b),rotvec(n,0,80))
    add(30,2,rotvec(n,0,80),activeAxis='custom',customAxis=n,arcDegrees=80)
    add(31,2,rotvec(Y,0,90),activeAxis='uprightY',arcDegrees=90)
    add(32,2,rotvec(Y,90,180),activeAxis='uprightY',arcDegrees=180)
    add(34,1,euler(key(0,(90,0,0)),key(.42,(30,0,0)),key(.55,(0,0,0)),key(1,(238.5,0,0))),activeAxis='uprightY',arcDegrees=238.5)
    add(34,2,rotvec(Y,90,-90),activeAxis='uprightY',arcDegrees=-90)
    add(36,2,rotvec(Y,0,90),rotvec((0,-1,0),0,-90))
    add(37,1,rotvec(Y,0,90),rotvec(Y,0,-270))
    add(37,2,rotvec(Z,0,720,True),rotvec(Z,0,1080,True),model='wheel')
    add(38,1,rotvec(Y,0,90),rotvec((0,-1,0),0,270))
    add(38,2,rotvec((0,-1,0),0,270),rotvec(Y,0,90))
    add(38,3,rotvec(Y,0,180),rotvec((0,-1,0),0,180))
    add(39,2,sequence(steps=[('upright',X,90,0,.43),('upright',Y,90,.55,1)]),rotvec((1/sqrt(2),1/sqrt(2),0),0,180/sqrt(2)))
    add(39,3,sequence(steps=[('upright',X,90,0,.43),('upright',Y,90,.55,1)]),sequence(steps=[('upright',Y,90,0,.43),('upright',X,90,.55,1)]))
    add(40,1,sequence(steps=[('upright',X,2,0,.43),('upright',Y,2,.55,1)]),rotvec((1/sqrt(2),1/sqrt(2),0),0,2*sqrt(2)))
    add(40,3,pose(90,0,0))
    return s

def meta(path):
    target=Path(str(path)+'.meta')
    if target.exists():
        text=target.read_text()
        if path.suffix in ['.json','.txt'] and 'DefaultImporter:' in text:
            target.write_text(text.replace('DefaultImporter:','TextScriptImporter:'),encoding='utf8')
        return re.search(r'^guid: (\w+)',text,re.M)[1]
    g=uuid.uuid5(uuid.NAMESPACE_URL,'yamyam-m04-v6:'+str(path.relative_to(OWN)).replace('\\','/')).hex
    importer='MonoImporter' if path.suffix=='.cs' else 'AssemblyDefinitionImporter' if path.suffix=='.asmdef' else 'TextScriptImporter' if path.suffix in ['.json','.txt'] else 'DefaultImporter'
    folder='folderAsset: yes\n' if path.is_dir() else ''
    write_source(target,f'fileFormatVersion: 2\nguid: {g}\n{folder}{importer}:\n  externalObjects: {{}}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n')
    return g

def generate_runtime():
    source=(OLD/'EulerAircraftScene.cs').read_text(encoding='utf-8-sig')
    start=source.index('        private Transform BuildAircraft(')
    end=source.index('        private void ClearOwned()',start)
    geometry=source[start:end].replace('EulerMathContract','EulerV6Math').replace('if (showBodyAxes)','if (shot.axes)')
    geometry=geometry.replace('BuildAxes(axes, 2.7f, .038f, 1f);','BuildAxes(axes, BodyAxisLength, .038f, 1f);')
    geometry=geometry.replace('// Reflection reverses triangle winding, so compensate when mapping authored RH geometry.','// V6 geometry is rebuilt directly in native +Z-forward coordinates; no reflection.')
    geometry=re.sub(r'            for \(int i = 0; i < mathTriangles.Length; i \+= 3\)\s*\{ int swap = mathTriangles\[i \+ 1\]; mathTriangles\[i \+ 1\] = mathTriangles\[i \+ 2\]; mathTriangles\[i \+ 2\] = swap; \}\s*','',geometry)
    template=(H/'spatial-runtime.cs.in').read_text(encoding='utf8')
    assert '// __REUSED_DETAILED_GEOMETRY_METHODS__' in template
    text=template.replace('        // __REUSED_DETAILED_GEOMETRY_METHODS__',geometry)
    text=text.replace('float h=l.text.GetComponent<MeshFilter>().sharedMesh.bounds.size.y;','float h=renderer.localBounds.size.y;')
    write_source(OWN/'EulerV6Scene.cs',text)
    return hashlib.sha256((OLD/'EulerAircraftScene.cs').read_bytes()).hexdigest(),hashlib.sha256(geometry.encode()).hexdigest()

def write_recipe(path,sid,shot_id,script_guid,catalog_guid):
    if path.exists():return  # Preserve a real later Editor bake or manual source edits.
    write_source(path,f'''%YAML 1.1
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
  m_Name: Yamyam M04 V6 {sid} source recipe - geometry bake pending
  m_TagString: Untagged
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
  m_Children: []
  m_Father: {{fileID: 0}}
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
  sceneId: {sid}
  selectedShotId: {shot_id}
  shotCatalog: {{fileID: 4900000, guid: {catalog_guid}, type: 3}}
  normalizedTime: 0
  playInRuntime: 0
  background: {{r: 0.03137255, g: 0.04313726, b: 0.0509804, a: 1}}
--- !u!1660057539 &9223372036854775807
SceneRoots:
  m_ObjectHideFlags: 0
  m_Roots:
  - {{fileID: 1001}}
''')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage',action='store_true');args=ap.parse_args()
    OWN.mkdir(parents=True,exist_ok=True);(OWN/'Editor').mkdir(exist_ok=True);(OWN/'Scenes').mkdir(exist_ok=True)
    d=json.loads((P/'script/revision-v6-article-flow/narration.ko.json').read_text(encoding='utf-8-sig'))
    definitions=specs();shots=[];scenes=[]
    for scene in d['scenes']:
        row=dict(id=scene['id'],title=scene['title'],testbedScene='unity/VideoEditing/'+str(REL/'Scenes/testbed.unity').replace('\\','/'),beats=[])
        for number,beat in enumerate(scene['teachingBeats'],1):
            bid=beat.get('id',f'{scene["id"]}.B{number:02}')
            spec=copy.deepcopy(definitions.get((scene['id'],number)))
            base=dict(id=bid,afterLine=beat['visual']['afterLine'],narrationLines=beat['speech']['lineNumbers'],targetActionResult=beat['visual']['targetActionResult'],plannedMotionSeconds=beat['visual'].get('plannedMotionSeconds'),plannedHoldSeconds=beat.get('hold',{}).get('plannedSeconds'),timingStatus='planned; retime via measured timeline teachingBeats visualStart/visualEnd/holdEnd')
            if spec:
                seconds=beat['visual'].get('plannedMotionSeconds') or (9 if scene['id'] in ['v6-18','v6-37','v6-38'] else 8)
                shot=dict(sceneId=scene['id'],id=bid,model='aircraft',activeAxis='none',axes=True,gimbals=False,cameraPosition=vector((7,4.5,8)),motionSeconds=seconds,**{k:v for k,v in spec.items() if k not in ['model','activeAxis','axes','gimbals','cameraPosition']})
                for name in ['model','activeAxis','axes','gimbals','cameraPosition']:
                    if name in spec:shot[name]=vector(spec[name]) if name=='cameraPosition' else spec[name]
                if 'cameraEndPosition' in shot:shot['cameraEndPosition']=vector(shot['cameraEndPosition'])
                if 'customAxis' in shot:shot['customAxis']=vector(shot['customAxis'])
                if spec.get('linear'):
                    shot.pop('linear',None);shot['a']['linear']=True
                    if shot.get('b'):shot['b']['linear']=True
                shots.append(shot)
                base.update(renderer='Unity',rendererReason='Physical moving-axis/orientation/depth relation requires a genuine3D model. Same detailed aircraft and fixed camera reused.',implementationKind='conceptual-illustration with exact authored rotation math',scenePath='unity/VideoEditing/'+str(REL/f'Scenes/{scene["id"]}.unity').replace('\\','/'),clipFile=str((LOCAL/'spatial-clips'/f'{bid}.mp4').relative_to(ROOT)).replace('\\','/'),firstFrame=str((LOCAL/'spatial-clips'/f'{bid}.first.png').relative_to(ROOT)).replace('\\','/'),lastFrame=str((LOCAL/'spatial-clips'/f'{bid}.last.png').relative_to(ROOT)).replace('\\','/'),durationFrames=round(seconds*60),stateBefore={'t':0,'programA':shot['a'],'programB':shot.get('b')},stateAfter={'t':1,'programA':shot['a'],'programB':shot.get('b')},measurementKind='our-implementation; pedagogical model, not a flight simulation or observed commercial-game orientation')
            else:
                actual=beat['visual'].get('plannedMotionSeconds') is None and ('독립 영상' in beat['visual']['targetActionResult'] or '독립영상' in beat['visual']['targetActionResult'])
                base.update(renderer='independent-gameplay' if actual else 'root-2D',rendererReason='Observed independent footage' if actual else 'Terminology, arithmetic, code, range or relationship is clearer in2D over the shared dimmed testbed.',sharedBackground='projects/game-math-euler-axis-angle/production/local/revision-v6/spatial-clips/testbed-still.png',noDuplicate3DImplementation=True)
            row['beats'].append(base)
        row['sceneSaveStatus']='Recipe/source planned; actual Editor-baked geometry pending coordinated sample job' if any(b['renderer']=='Unity' for b in row['beats']) else '2D uses shared testbed; no duplicate spatial scene required'
        scenes.append(row)
    scenes[0]['heroOpeningFrame']=next(b['lastFrame'] for b in scenes[0]['beats'] if b['renderer']=='Unity')
    scenes[0]['heroOpeningUse']='After branding show the final order contrast while stating the question; return to first state for the finite demonstration. Keep the same testbed; no title reset.'
    scenes[-1]['recapGrid']={'kind':'same-testbed evidence reuse, composed by parent','sourceBeatIds':['v6-11.B03','v6-20.B01','v6-31.B02','v6-39.B02'],'use':'Reuse existing final states/crops for order, gimbal, axis-angle and finite-composition comparison; no duplicate3D scene/render.'}
    primary_shot_count=len(shots)
    auxiliary_id='v6-41.answer-y90'
    auxiliary_shot=dict(sceneId='v6-41',id=auxiliary_id,model='aircraft',activeAxis='uprightY',axes=True,gimbals=False,cameraPosition=vector((7,4.5,8)),motionSeconds=3,a=move((0,0,0),(90,0,0)),b=None,pair=False,arcDegrees=90)
    shots.append(auxiliary_shot)
    auxiliary=dict(id=auxiliary_id,sceneId='v6-41',renderer='Unity',auxiliary=True,afterLine=6,beforeLine=7,durationFrames=180,observationFrames=240,plannedMotionSeconds=3,plannedHoldSeconds=4,
        scenePath='unity/VideoEditing/'+str(REL/'Scenes/v6-41.unity').replace('\\','/'),
        clipFile=str((LOCAL/'spatial-clips'/f'{auxiliary_id}.mp4').relative_to(ROOT)).replace('\\','/'),firstFrame=str((LOCAL/'spatial-clips'/f'{auxiliary_id}.first.png').relative_to(ROOT)).replace('\\','/'),lastFrame=str((LOCAL/'spatial-clips'/f'{auxiliary_id}.last.png').relative_to(ROOT)).replace('\\','/'),
        stateBefore={'t':0,'programA':auxiliary_shot['a'],'programB':None},stateAfter={'t':1,'programA':auxiliary_shot['a'],'programB':None},
        purpose='After the spoken axis/angle answer show the same aircraft nose +Z to +X; root reuses its one final pose for the Euler/axis-angle/rotation-vector closing comparison. Extra180f+240f does not alter the106primary beats or their527s holds.')
    (OWN/'spatial-shots.json').write_text(json.dumps({'shots':shots},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    oldsha,geometrysha=generate_runtime()
    script_guid=meta(OWN/'EulerV6Scene.cs');catalog_guid=meta(OWN/'spatial-shots.json')
    for scene in scenes:
        chosen=next((b for b in scene['beats'] if b['renderer']=='Unity'),None)
        if chosen:
            write_recipe(OWN/f'Scenes/{scene["id"]}.unity',scene['id'],chosen['id'],script_guid,catalog_guid)
            scene['sceneSaveStatus']='Editable source-recipe .unity exists; detailed Editor-saved hierarchy pending coordinated isolated bake'
    write_recipe(OWN/'Scenes/v6-41.unity','v6-41',auxiliary_id,script_guid,catalog_guid)
    scenes[-1]['auxiliarySceneSaveStatus']='Editable auxiliary source-recipe .unity exists; detailed Editor-saved hierarchy pending coordinated isolated bake'
    write_recipe(OWN/'Scenes/testbed.unity','testbed','v6-04.B01',script_guid,catalog_guid)
    plan=dict(schemaVersion=1,slug='game-math-euler-axis-angle',revision='article-flow-v6',status='CPU source/plan ready; no V6 Editor/GPU job launched',editor='6000.6.0f1',canonicalPipeline='URP17.6.0; existing main settings unchanged',isolatedPipeline='Built-in, linear color,2xMSAA, no postprocessing/shadows; source materials will be adapted to canonical URP on sync',coordinateContract=d['speechContract']['coordinateConvention'],engineMapping={'point':'identity numeric x/y/z, no Z reflection','rowMatrix':'R=Rz_row(b) Rx_row(p) Ry_row(h)','engineColumnMatrix':'R.transpose','sanity':['heading+90:Z->X','pitch+90:Z->-Y','bank+90:Y->-X'],'objectOrigin':'upright shares object origin; each comparison has its own translated origin; presentation translation is not rotation'},testbed={'model':'Detailed tapered aircraft, cockpit, nose, tapered wings, ailerons, elevator, rudder, tail fin, intakes/exhaust','background':'#080b0d; selected V6 technical-explainer grammar; prior white V5 unchanged','axisPalette':{'X':'#ef5a63','Y':'#6cce8e','Z':'#73acf5','activeGuide':'#f39a4b'},'geometryReuseSource':str((OLD/'EulerAircraftScene.cs').relative_to(ROOT)).replace('\\','/'),'sourceSha256':oldsha,'extractedGeometrySha256':geometrysha,'downloadedAssets':False,'camera':{'projection':'orthographic','position':[7,4.5,8],'target':[0,-.15,0],'singleCenter':[650,500],'pairCenters':[[535,500],[1350,500]],'singleOrtho':3.95,'pairOrtho':4.25,'pairScale':.78},'sameSceneBackground':'spatial-clips/testbed-still.png','specialCameraScenes':['v6-04 top observation','v6-07 opposite observer positions'],'captionReserve':{'yMin':880,'center':[960,970],'fontPx':48,'maxLines':2},'termCardReserve':[96,64,700,160],'pictureLabelAnchor':[1824,64],'singleRightMathPane':[1100,300,1824,780],'pairedShortValueY':760},axisGuides={'x':'red/X','y':'green/Y','z':'blue/Z','upright':'dashed; same center, fixed directions','body':'solid; rotates with object','activeRotation':'progressive3D arc with explicit positive-axis convention','labelPlacement':'Stable callout lanes with2.4px background-color outline; leaders attached to actual exported axis endpoints; labels are explanatory overlays','occlusion':'3D geometry obeys the depth buffer. Text/leader overlay is marked editorial, not a detector or measured internal-game value.'},timelineContract={'file':'production/revision-v6/timeline.json','scenes':['id','frames','seconds','lineStarts','lineEnds','teachingBeats'],'beatTimes':['id','speechStart','visualStart','visualEnd','holdEnd'],'capture':'native60finite clip per physical beat; first/last PNG; no whole-narration disk frames','retime':'Root holds first while explaining, native motion during visual interval, last during observation/result. Required motion frames come from visualEnd-visualStart; no ratio padding.'},sceneCount=len(scenes),beatCount=sum(len(s['beats']) for s in scenes),spatialShotCount=len(shots),sceneSaveStatus='Editable recipe assets to be baked and saved in isolated project; not claimed as saved detailed scenes yet',scenes=scenes)
    plan['spatialShotCount']=primary_shot_count
    plan['auxiliarySpatialShotCount']=1
    plan['auxiliaryClips']=[auxiliary]
    plan['timelineContract']['auxiliaryVisuals']='Optional separate top-level/scene auxiliaryVisuals: id,visualStartFrame,visualEndFrame,holdEndFrame; not added to106primary teachingBeats.'
    (H/'spatial-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OWN/'Yamyam.GameMath.EulerAxisAngle.V6.asmdef').write_text(json.dumps(dict(name='Yamyam.GameMath.EulerAxisAngle.V6',rootNamespace='YamyamCoding.GameMath.EulerAxisAngle.V6',references=[],autoReferenced=True),indent=2)+'\n',encoding='utf8')
    for path in [OWN]+sorted(OWN.rglob('*')):
        if path.suffix!='.meta':meta(path)
    if args.stage:
        dest=ISO/REL;dest.mkdir(parents=True,exist_ok=True);shutil.copytree(OWN,dest,dirs_exist_ok=True)
        for folder in ['Packages','ProjectSettings']:(ISO/folder).mkdir(exist_ok=True)
        for name in ['manifest.json','packages-lock.json']:shutil.copy2(ROOT/'unity/VideoEditing/Packages'/name,ISO/'Packages'/name)
        for name in ['ProjectVersion.txt','ProjectSettings.asset','GraphicsSettings.asset','QualitySettings.asset','TagManager.asset','TimeManager.asset','EditorSettings.asset']:
            source=ROOT/'unity/VideoEditing/ProjectSettings'/name
            if source.exists():shutil.copy2(source,ISO/'ProjectSettings'/name)
        for name in ['GraphicsSettings.asset','QualitySettings.asset']:
            f=ISO/'ProjectSettings'/name;txt=f.read_text(encoding='utf-8-sig');txt=re.sub(r'(m_CustomRenderPipeline|customRenderPipeline):.*',r'\1: {fileID: 0}',txt);f.write_text(txt,encoding='utf8')
    print(json.dumps(dict(scenes=len(scenes),beats=plan['beatCount'],spatialShots=primary_shot_count,auxiliaryShots=1,isolated=str(ISO),editorStarted=False),ensure_ascii=False))

if __name__=='__main__':main()
