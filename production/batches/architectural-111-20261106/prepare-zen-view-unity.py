"""07.04 CPU preflight/staging only. Never launches Unity, GPU, model or capture.

Default is read-only. --stage installs this episode's source and the existing
licensed Knight inputs in an isolated C-media project, preserving any changed
file. A resource-gated external runner may later call the documented entry.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
PROJECT=MEDIA/'unity-zen-view-capture';SOURCE=HERE/'zen-view-unity-source'
ASSET=ROOT/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers'
FOLDER='Assets/VideoScenes/architectural-111-20261106/07-04'
REPORT=ROOT/'projects/shorts-leveldesign-07-04/unity-preparation-v1.json'
ENTRY='Yamyam.Architectural111.ZenView.Editor.ZenViewBuilder.Capture'
AUTH='explicitArchitectural111Batch20261106'

def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def clear_to_target(c,eye_x,width,target_x=None):
    """Segment crosses two faces of a convex, linear-sided channel: exact CPU geometry, not Unity evidence."""
    target_x=c['targetX'] if target_x is None else target_x
    for z,center in ((c['frontZ'],c['frontCenterX']),(c['backZ'],c['backCenterX'])):
        t=(z-c['pathZ'])/(c['targetZ']-c['pathZ'])
        x=eye_x+(target_x-eye_x)*t;y=c['eyeHeight']+(c['targetY']-c['eyeHeight'])*t
        if not center-width*.5<=x<=center+width*.5 or not c['openingBottom']<=y<=c['openingTop']:return False
    direction=math.atan2(target_x-eye_x,c['targetZ']-c['pathZ'])
    yaw=math.atan2(c['backCenterX']-c['frontCenterX'],c['backZ']-c['frontZ'])
    half_h=math.atan(math.tan(math.radians(c['verticalFieldOfView'])*.5)*c['width']/c['height'])
    return abs(direction-yaw)<=half_h

def visible_interval(c,width):
    low,high=-math.inf,math.inf
    for z,center in ((c['frontZ'],c['frontCenterX']),(c['backZ'],c['backCenterX'])):
        t=(z-c['pathZ'])/(c['targetZ']-c['pathZ'])
        low=max(low,(center-width*.5-t*c['targetX'])/(1-t))
        high=min(high,(center+width*.5-t*c['targetX'])/(1-t))
    return [low,high]

def geometry_smoke(c):
    assert (c['frames'],c['fps'],c['width'],c['height'])==(480,60,1920,1080)
    assert c['frontZ']<c['backZ']<c['targetZ'] and c['pathZ']<c['frontZ']
    assert c['openingBottom']<c['eyeHeight']<c['openingTop']<c['wallHeight']
    results={}
    for mode in ('narrow','wide'):
        width=c[mode+'Width'];interval=visible_interval(c,width)
        frames=[i for i in range(c['frames']) if clear_to_target(c,c['pathStartX']+(c['pathEndX']-c['pathStartX'])*i/(c['frames']-1),width)]
        results[mode]=dict(openingWidth=width,analyticCenterTargetEyeXInterval=interval,
            predictedVisibleFrames=len(frames),predictedFirstFrame=frames[0] if frames else None,predictedLastFrame=frames[-1] if frames else None)
    assert results['narrow']['analyticCenterTargetEyeXInterval']==[-3.25,-2.75]
    assert results['narrow']['predictedVisibleFrames']==30 and results['wide']['predictedVisibleFrames']==480
    assert not clear_to_target(c,c['pathStartX'],c['narrowWidth']) and not clear_to_target(c,c['pathEndX'],c['narrowWidth'])
    assert clear_to_target(c,-3.,c['narrowWidth'])
    # One mouth alone is insufficient: this point satisfies the farther mouth
    # but is blocked at the nearer mouth. Also confirm width-only monotonicity.
    eye=-3.275;t=(c['backZ']-c['pathZ'])/(c['targetZ']-c['pathZ']);back_x=eye+(c['targetX']-eye)*t
    assert abs(back_x-c['backCenterX'])<c['narrowWidth']/2 and not clear_to_target(c,eye,c['narrowWidth'])
    previous=None
    for width in (.4,1.,2.,6.8):
        interval=visible_interval(c,width)
        if previous:assert interval[0]<=previous[0] and interval[1]>=previous[1]
        previous=interval
    return dict(status='analytic-geometry-smoke-passed-actual-Unity-raycasts-not-run',modes=results,
        onlyVariable='opening width',test='Both mouths/FOV, brief narrow reveal then hide, broad path coverage, far-mouth-only counterexample and monotonic width interval',
        measurementsAreOriginalIllustrativeValues=True,actualUnityConfirmed=False)

def preflight():
    control=read(ROOT/'shared/publishing/video-production-control.json')[AUTH]
    assert control['userEvidence']=='111개 전체 제작 들어가줘' and control['status'] not in ('paused','stopped','cancelled')
    assert control['automaticAdvanceWithinExactList'] and not control['automaticAdvanceOutsideList'] and not control['youtubeAuthorized']
    project=read(ROOT/'projects/shorts-leveldesign-07-04/project.json');assert project['topicId']=='07.04' and project['localFinalReviewOnly']
    config=read(SOURCE/'capture-config.json');smoke=geometry_smoke(config)
    library=read(ROOT/'shared/assets/unity-asset-library.json');assert library['targetEditorVersion']=='6000.6.0f1'
    provenance=read(ASSET/'provenance.json');assert provenance['license']=='CC0'
    records=[]
    for row in provenance['files']:
        source=ASSET/row['path'];assert sha(source)==row['sha256']
        for path in (source,Path(str(source)+'.meta')):
            if path.exists():records.append(dict(source=path.relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/'+path.name,sha256=sha(path)))
    records.append(dict(source=(ASSET/'provenance.json').relative_to(ROOT).as_posix(),target='Assets/ThirdParty/KayKitAdventurers/provenance.json',sha256=sha(ASSET/'provenance.json')))
    for path in sorted(SOURCE.rglob('*')):
        if path.is_file():records.append(dict(source=path.relative_to(ROOT).as_posix(),target=FOLDER+'/'+path.relative_to(SOURCE).as_posix(),sha256=sha(path)))
    compiler_path=MEDIA/'shorts-leveldesign-07-04/unity-cpu-preflight/compile.json';compiler=None
    if compiler_path.is_file():
        checked=read(compiler_path);assert checked['compilerExitCode']==0
        for name,expected in checked['sourceHashes'].items():assert sha(SOURCE/name)==expected,'Static compiler proof is stale: '+name
        compiler=dict(path=str(compiler_path),sha256=sha(compiler_path),compilerExitCode=0,scope=checked['scope'])
    result=dict(schemaVersion='07-04-unity-preparation-v1',topicId='07.04',project=str(PROJECT),editorVersion='6000.6.0f1',
        renderPipeline='Isolated Built-in capture; original portable shader. MainURP import/visual QA not performed',
        config=config,files=records,assetProvenance=provenance,staticCompilerPreflight=compiler,preparerSHA256=sha(Path(__file__)),
        assetLibraryConsulted=dict(catalog='shared/assets/unity-asset-library.json',sha256=sha(ROOT/'shared/assets/unity-asset-library.json'),productCount=library['productCount'],
            choice='Reuse the already selected/provenance-bound CC0 KayKit articulated Knight and actual Walking_A clip for visual continuity; original simple fixed ocean/island/lighthouse geometry needs no vendor pack/code'),
        intendedScenes=[FOLDER+'/S02-ZenView-Narrow.unity',FOLDER+'/S03-ZenView-Wide.unity'],
        captureEntry=ENTRY,cliKeys=['-zenViewOutput','-zenViewFingerprint','-zenViewModes'],
        captureContract=dict(frames=config['frames'],fps=60,width=1920,height=1080,cameras=['player','observer'],modes=['narrow','wide']),
        geometrySmoke=smoke,actualSceneFilesSaved=False,unityLaunched=False,captureStarted=False,
        resourceGate='External root-owned runner must authorize exact111/07.04, acquire scoped singleton/shared GPU lease and recheck apps/editor/model/media/headroom immediately before launch; this preparer never launches',
        outputContract=dict(modeFiles=['mode-complete.json','capture-config.json','trace.csv','rays.jsonl','projected-anchors.jsonl','player/0000.jpg..0479.jpg','observer/0000.jpg..0479.jpg'],
            rootFiles=['scene-record.json'],sceneRecord='Actual saved scene/owned07.04 subtree+root.meta file paths/SHA/bytes and shared Knight dependency pins; only exists after Unity runs'),
        sourceKind='Original Unity visibility implementation, not commercial game footage',humanReview=False)
    result['fingerprint']=digest(dict(topicId='07.04',config=config,sourcePins=records,editorVersion=result['editorVersion'],captureContract=result['captureContract']))
    return result

def stage(result):
    assert result['staticCompilerPreflight'],'Static C# API compile is required before source staging'
    packages=dict(dependencies={key:'1.0.0' for key in ('com.unity.modules.physics','com.unity.modules.animation','com.unity.modules.imgui','com.unity.modules.jsonserialize','com.unity.modules.imageconversion')})
    generated={'Packages/manifest.json':(json.dumps(packages,indent=2)+'\n').encode(),
        'ProjectSettings/ProjectVersion.txt':b'm_EditorVersion: 6000.6.0f1\n'}
    # Validate every destination before the first write. Never refresh/import,
    # erase a Library, replace changed files or touch first03.02 staging.
    for row in result['files']:
        path=PROJECT/row['target'];assert not path.exists() or sha(path)==row['sha256'],'Preserve changed staged input: '+str(path)
    for name,data in generated.items():
        path=PROJECT/name;assert not path.exists() or path.read_bytes()==data,'Preserve changed project settings: '+str(path)
    for row in result['files']:
        path=PROJECT/row['target'];path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():shutil.copyfile(ROOT/row['source'],path)
        assert sha(path)==row['sha256']
    for name,data in generated.items():
        path=PROJECT/name;path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():path.write_bytes(data)
    result['sourceStageComplete']=True
    data=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode();temp=REPORT.with_name(REPORT.name+'.tmp')
    assert not temp.exists();temp.write_bytes(data);os.replace(temp,REPORT)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--stage',action='store_true');args=parser.parse_args()
    result=preflight()
    if args.stage:stage(result)
    print(json.dumps(dict(ready=True,topicId='07.04',fingerprint=result['fingerprint'],geometrySmoke=result['geometrySmoke'],
        staged=args.stage,preparationReport=str(REPORT) if args.stage else None,project=str(PROJECT),captureEntry=ENTRY,
        unityLaunched=False,actualSceneFilesSaved=False),ensure_ascii=False))
if __name__=='__main__':main()
