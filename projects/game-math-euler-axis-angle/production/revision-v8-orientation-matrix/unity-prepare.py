"""Prepare V8's exact spatial interface and isolated source files; never render."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,math,shutil

sp=importlib.util.spec_from_file_location('v8_unity_specs',Path(__file__).with_name('unity-specs.py'))
S=importlib.util.module_from_spec(sp);sp.loader.exec_module(S)
ROOT,P,H,O,ISO,ASSET=S.ROOT,S.P,S.H,S.O,S.ISO,S.ASSET
APPROVED='2cfce716a62d3b951a81a5022dd216ac4cbaafb7b73ffa20e9d0765798e789c3'

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def authorized():
    ctl=read(ROOT/'shared/publishing/video-production-control.json');claim=ctl['scopedProductionAuthorizations'][P.name]
    auth=read(H/'authorization.json')
    assert claim['revision']==auth['revision']=='orientation-matrix-v8'
    assert claim['status']=='authorized-production-v8' and claim['fullProductionAuthorized'] and claim['renderAuthorized']
    assert auth['scriptApproved'] and auth['renderAuthorized'] and not auth['platformMutation']
    assert claim['approvedScriptSha256']==auth['approvedScriptSha256']==APPROVED==sha(S.SCRIPT)
    return dict(authorization=rel(H/'authorization.json'),authorizationSha256=sha(H/'authorization.json'),approvedScriptSha256=APPROVED)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage-isolated',action='store_true');a=ap.parse_args()
    approval=authorized();script=read(S.SCRIPT);assert len(script['scenes'])==13
    assert sum(len(x['paragraphs'])for x in script['scenes'])==76
    assert len({x['id']for x in S.SHOTS})==len(S.SHOTS)
    shots={x['id']:x for x in S.SHOTS};rows=[];cuefindings=[]
    for scene in script['scenes']:
        assert len(scene['paragraphs'])==len(S.PARAGRAPHS[scene['id']]),scene['id']
        for line,(text,original)in enumerate(zip(scene['paragraphs'],S.PARAGRAPHS[scene['id']]),1):
            visual=copy.deepcopy(original)
            for sub in visual.get('secondary',[]):
                assert sub['asset']in shots
                subcue=sub.get('cue');suboffset=text.find(subcue)if subcue else 0
                if subcue and suboffset<0:cuefindings.append(dict(scene=scene['id'],line=line,cue=subcue,secondary=True))
                sub['cueSourceKoOffset']=suboffset
                sub['sourceFrames']=shots[sub['asset']]['frames']
            assert visual['asset']in shots
            cue=visual.get('cue');offset=text.find(cue)if cue else 0
            if cue and offset<0:cuefindings.append(dict(scene=scene['id'],line=line,cue=cue))
            native=shots[visual['asset']]
            row=dict(sceneId=scene['id'],paragraphId=scene['id']+f'.L{line:02}',line=line,textSha256=hashlib.sha256(text.encode()).hexdigest(),
                **visual,sourceFrames=native['frames'],nativeFps=60,cueSourceKoOffset=offset,
                actualFiles={'clip':rel(O/'native'/(native['id']+'.mp4')),'first':rel(O/'native'/(native['id']+'.first.png')),
                'last':rel(O/'native'/(native['id']+'.last.png')),'anchors':rel(O/'native'/(native['id']+'.anchors.ndjson'))},
                timing='Speech overlaps actual target/action/result. Exact current state retained during continuous definitions; no automatic silence, loop or runtime padding.',
                holdDefaultSeconds=0,actualCaptureStatus='not started',currentCaptionReserved=True)
            rows.append(row)
    assert not cuefindings,cuefindings
    prepared=O/'prepared-unity';(prepared/'Editor').mkdir(parents=True,exist_ok=True);(prepared/'Scenes').mkdir(exist_ok=True)
    runtime=(H/'unity-runtime.cs.in').read_text(encoding='utf8').replace('//__OWNER_GEOMETRY_FRAGMENT__',(H/'unity-geometry.cs.in').read_text(encoding='utf8'))
    assert 'EulerV6'not in runtime and 'gimbal'not in runtime.lower()
    (prepared/'OrientationMatrixV8Scene.cs').write_text(runtime,encoding='utf8')
    shutil.copy2(H/'unity-capture.cs.in',prepared/'Editor/OrientationMatrixV8Capture.cs')
    shutil.copy2(H/'unity-guide.shader.in',prepared/'DiagramGuideOverlay.shader')
    save(prepared/'spatial-shots.json',dict(shots=S.SHOTS))
    save(prepared/'Yamyam.GameMath.OrientationMatrix.V8.asmdef',dict(name='Yamyam.GameMath.OrientationMatrix.V8',references=[],autoReferenced=True))
    save(prepared/'Editor/Yamyam.GameMath.OrientationMatrix.V8.Editor.asmdef',dict(name='Yamyam.GameMath.OrientationMatrix.V8.Editor',references=['Yamyam.GameMath.OrientationMatrix.V8'],includePlatforms=['Editor'],autoReferenced=True))
    sceneShots=['bank','home-y90','basis-y90','point-sum','point-fixed','target-right','projection','basis-rows','arm-hand-sword','pose-context','complex-pose','creep-exaggerated','recap-bank']
    assert [shots[x]['sceneId']for x in sceneShots]==[s['id']for s in script['scenes']]
    inputs={rel(p):sha(p)for p in [S.SCRIPT,H/'authorization.json',H/'unity-prepare.py',H/'unity-capture.py',H/'unity-validate.py',H/'unity-specs.py',H/'unity-runtime.cs.in',H/'unity-geometry.cs.in',H/'unity-capture.cs.in',H/'unity-guide.shader.in',*sorted(p for p in prepared.rglob('*')if p.is_file())]}
    catalog=read(ROOT/'shared/assets/unity-asset-library.json')
    candidate=next(x for x in catalog['products']if x['id']=='026')
    consultation=dict(catalog='shared/assets/unity-asset-library.json',catalogSha256=sha(ROOT/'shared/assets/unity-asset-library.json'),guide='docs/UNITY_ASSET_LIBRARY.md',productCount=84,
        importedRootsConsulted=['unity/VideoEditing/Assets/ThirdParty/YamyamAssetLibrary'],
        relevantCandidate=dict(productId='026',title=candidate['title'],assetPath=candidate['actualAssetPath'],source=candidate['publicProductUrl'],licenseStatus=candidate['licenseStatus'],adopted=False,
        reason='Ships/boats do not clarify the designated aircraft body axes. No aircraft/rig product matches in the84-product catalog. Reuse our own recognizable aircraft rather than importing an unrelated asset. No vendor originals changed.'),
        adoptedAssets=[dict(kind='self-authored geometry source reuse',file='unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v6/EulerV6Scene.cs',sha256=sha(ROOT/'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v6/EulerV6Scene.cs'),scope='Tapered fuselage, actual thickness wings/control surfaces, canopy/intake, articulated tail only; new asymmetrical F mark and new matrix-only runtime. No old narration/layout/rotation program adopted.',thirdPartyAssets=False)])
    human=next(x for x in catalog['products']if x['id']=='011')
    consultation['mannequinCandidate']=dict(productId='011',title=human['title'],assetPath=human['actualAssetPath'],source=human['publicProductUrl'],licenseStatus=human['licenseStatus'],adopted=False,
        reason='Cartoon city character identity/rig does not provide the neutral15-reference teaching model assumption. Catalog license remains unverified; do not force a vendor asset. Self-author recognizable head/torso/pelvis/arms/hands/legs/feet and actual parent references without touching vendor originals.')
    consultation['adoptedAssets'].append(dict(kind='new self-authored articulated mannequin and arm/hand/tool geometry',file=rel(H/'unity-runtime.cs.in'),sha256=sha(H/'unity-runtime.cs.in'),thirdPartyAssets=False,parts=15,
        assumption='head+torso+pelvis3 and upperarm/forearm/hand/thigh/calf/foot pairs12; exactly15 parent-relative orientations, not a claim about every humanoid rig standard'))
    job=dict(approval=approval,outputDirectory=str(O/'native'),ffmpegPath=shutil.which('ffmpeg'),sampleOnly=False,bakeScenes=True,sceneShots=sceneShots,
        clips=[dict(shotId=x['id'],frames=x['frames'],stillFrames=([0,120,180,360]if x['id']=='projection'else[0,90,180]if x['id']=='point-sum'else[0,x['frames']-1]))for x in S.SHOTS],immutableInputs=inputs,width=1000,height=700,fps=60)
    save(O/'capture-job.json',job)
    plan=dict(schemaVersion=1,revision='orientation-matrix-v8',status='CPU source preparation; actual capture not started',approval=approval,script=rel(S.SCRIPT),scriptSha256=APPROVED,
        native=dict(width=1000,height=700,fps=60,frames=sum(x['frames']for x in S.SHOTS),clipCount=len(S.SHOTS),speed=1,loops=False,normalization='frame/(frames-1); deterministic native controlled program',pipeline='isolated built-in linear2xMSAA; canonical URP shader-compatible saved materials to be verified after actual bake'),
        composition=dict(fullCanvas=[1920,1080],modelRect=[40,180,1000,700],mathRect=[1080,180,800,700],captions=[960,970],camera='Fixed orthographic projection for one coherent model; native panel aspect, no full-frame shrinking; explicit fixed-target camera-roll exception only.',
        rootOwnedLabels='Large names/readouts/formulas/term chips composed from actual top-left pixel anchors. Axis colors X#ef5a63,Y#6cce8e,Z#66b9ed with labels. No native labels; root fixed captions protected.'),
        convention=dict(frame='left handed, +X east/right +Y up +Z north/forward',row='vO R=vU',matrix='Each row is object/input basis in upright/output coordinates; native column transform is transposed for serialization.',referenceRows=[[0,0,-1],[0,1,0],[1,0,0]],pointObject=[1,0,2],pointUpright=[2,0,-1],
        drawingScale='A fixed2.2 rendered-world units per one logical coordinate unit is applied equally to basis glyphs, unit anchors, P, weighted paths and projections. Actual displayed point world=origin+2.2*(vObject R); State.uprightPoint is logical, not raw world distance. The dimensionless orientation matrix and normalized basisLengths remain unscaled.',
        diagramLimits='All numbers are authored model implementation values. No hidden game-engine values. The point stays physically fixed while coordinates are re-expressed. Matrix creep is an explicitly exaggerated illustration, not a measured accumulation run.',
        armScope='A tool/sword input → B hand intermediate → C body output reference at the fixed shoulder origin. Internal arm-named matrices export ORIENTATION only; separated joint origins are visualization. Translation is excluded from the narrated rotation-only composition.'),
        shots=S.SHOTS,paragraphs=rows,paragraphCount=len(rows),sceneCount=13,sceneShots=sceneShots,
        plannedEditableScenes=[str(Path('unity/VideoEditing')/ASSET/'Scenes'/(s['id']+'.unity')).replace('\\','/')for s in script['scenes']],
        plannedTestbed=str(Path('unity/VideoEditing')/ASSET/'Scenes/testbed.unity').replace('\\','/'),savedSceneStatus='planned; no claim of files existing until actual native bake receipt',
        finiteProgramDetails=dict(projection=dict(sourceFrames=361,angleFrameFormula='angle=frame/2 degrees',exactFrames={'0degrees':0,'60degrees':120,'90degrees':180,'180degrees':360},component='cos(angle); signed uprightX component of unit objectX',motionUse='L01/L04 exact state recall; L02 uses separate short native turns in narration order',shortTurns=[{'id':'projection-turn90','frames':91,'motionIntervalSeconds':1.5,'angle':[0,90],'arriveBeforeCue':'직각에서는'},{'id':'projection-to60','frames':61,'motionIntervalSeconds':1,'angle':[90,60],'cue':'육십 도를 벌리면'}]),
        reflection=dict(sourceFrames=2,first='identity',last='diag(-1,1,1)',interpolation='none: exact two-state comparison; do not imply singular scaling is a rotation'),
        pointPath=dict(sourceFrames=181,firstContribution=[0,90],secondContribution=[90,180],point='same physical[2,0,-1] visible throughout trace; no new point motion',cursor='Gold activeContributionCursor traverses origin→1*bodyX→P. This is an editorial contribution-tracing cursor, not motion of P; it makes first contribution visible while the full red unit-basis reference stays fixed.'),
        creep=dict(actualMatrixRows=[[1.18,0,0],[.22,.95,0],[.05,0,1.08]],amplified=True,normalization='Normalize each row separately, leaving nonzero pair dots',orthonormalization='For this triangular example row Gram-Schmidt gives identity with determinant+1. Interpolated visual repair is an illustration, not a numerical algorithm animation.')),
        anchors=dict(format='NDJSON one row per native frame; x/y top-left native1000x700, z camera depth',screen='origin, objectXYZ, uprightXYZ, basisUnitXYZ, point, weightedXEnd, projectionFoot, nose; armOrigin/handOrigin/swordOrigin/swordTip plus bodyCXYZ/handBXYZ/toolAXYZ for articulated example. ToolY follows the blade; do not rename it Z/forward. pose-context exports15 part.<reference>.origin anchors and orientationReferences[name,parent,rowParentOrientation].',
        numeric='Actual objectToUpright row matrix, inverse, Gram matrix, basis lengths, three pair dots, determinant, same point in both frames, signed projection and camera pose; arm orientation composition.',
        visibility='inViewport only; this flag is NOT a complete depth-occlusion detector. modelPixelBounds conservatively projects the actual deformed mesh AABB corners, not an object detector or exact silhouette. Root actual moving inspection is required before drawn guides are adopted.'),
        gizmos=dict(body='RGB solid unit axes; X#ef5a63 Y#6cce8e Z#66b9ed; root attaches names at true unit endpoints',upright='gray#8f969c dashed axes and gray heads; same origin, logical unit length1',activeArcShots=['home-y90','basis-y90','intro-orientation'],activeArc='One progressive gold arc and tangent arrow around the actual commanded uprightY or forwardZ axis only; no decorative global rings',
        depth='Axis/path/projection/point guides are explicitly editorial projected overlays rendered with owner-authored Yamyam/DiagramGuideOverlay ZTestAlways/ZWriteOff. Their actual world/pixel anchors are unchanged. Aircraft/mannequin/tool meshes retain ordinary3D depth/occlusion. This fixes actualsample e3140a42d36a hiding bodyZ and the first basis contribution inside the opaque aircraft; it does not claim engine measurements or detector visibility.',
        nominalWidthsAtNative1000x700=dict(bodyAxisDiameterPx=2*.027*700/(2*2.95),uprightDashDiameterPx=2*.012*700/(2*2.95),arcAndWeightedPathPx=.05*700/(2*2.95),projectionSecondaryPx=.025*700/(2*2.95)),actualPixelQuality='pending actual native and final375 inspection'),
        importedAssetConsultation=consultation,sourceHashes=inputs,sourcePreparationOnly=True,gpuStarted=False,
        pending=['Root handoff after audio GPU slot','Actual native endpoint samples and model/camera inspection','Actual full finite native capture and editable scene save','URP-only canonical material derivation audit','Actual spoken-cue timing and composed1080/375 visual review'])
    save(H/'unity-plan.json',plan)
    interfacePath=H/'unity-output-interface.json'
    interface=read(interfacePath)if interfacePath.exists()else{'schemaVersion':1}
    interface.update(status='planned interface; actual files exist only after successful finite capture',sourcePlan=rel(H/'unity-plan.json'),sourcePlanSha256=sha(H/'unity-plan.json'),nativeSize=[1000,700],fps=60,
        fullCanvasRect=[40,180,1000,700],actualCaptureStarted=False,
        shots=[dict(id=x['id'],sceneId=x['sceneId'],frames=x['frames'],pointObject=x['pointObject'],originFrom=x['originFrom'],originTo=x['originTo'],
            file=rel(O/'native'/(x['id']+'.mp4')),first=rel(O/'native'/(x['id']+'.first.png')),last=rel(O/'native'/(x['id']+'.last.png')),
            middle=rel(O/'native'/(x['id']+('.last.png'if x['frames']==2 else'.middle.png'))),anchors=rel(O/'native'/(x['id']+'.anchors.ndjson')),
            frameStills={str(f):rel(O/'native'/(x['id']+'.frame-'+str(f).zfill(4)+'.png'))for f in next(y for y in job['clips']if y['shotId']==x['id'])['stillFrames']})for x in S.SHOTS])
    save(interfacePath,interface)
    save(O/'source-preparation.json',dict(plan=rel(H/'unity-plan.json'),planSha256=sha(H/'unity-plan.json'),job=rel(O/'capture-job.json'),jobSha256=sha(O/'capture-job.json'),immutableInputs=inputs,captureStarted=False))
    if a.stage_isolated:
        import psutil
        target=str(ISO).lower().replace('\\','/')
        assert not any((p.info['name']or'').lower()=='unity.exe'and target in' '.join(p.info['cmdline']or[]).lower().replace('\\','/')for p in psutil.process_iter(['name','cmdline'])),'Own isolated project is already in use; preserved'
        shutil.copytree(prepared,ISO/ASSET,dirs_exist_ok=True)
    print(json.dumps(dict(plan=rel(H/'unity-plan.json'),paragraphs=len(rows),shots=len(S.SHOTS),nativeFrames=plan['native']['frames'],nativeSeconds=plan['native']['frames']/60,captureStarted=False),ensure_ascii=False))

if __name__=='__main__':main()
