"""Prepare one Part1 right-pane asset package without starting expensive jobs.

Default: read source receipts, produce the complete paragraph/asset plan and
stageable isolated Unity sources. --stage-isolated copies only these new owned
sources into the existing task-local capture project; never the main editor.
Actual engine/ffmpeg movie rendering is deliberately a separate root handoff.
"""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, math, re, shutil
from PIL import ImageFont

spec = importlib.util.spec_from_file_location('right_specs',Path(__file__).with_name('right-specs.py'))
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
ROOT,P,H,O,V6,ENGINE,ISO = S.ROOT,S.P,S.H,S.O,S.V6,S.ENGINE,S.ISO
PLAN=P/'planning/revision-v7-two-part/part-01-right-explanation-plan.json'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def vec(x,y,z): return dict(x=x,y=y,z=z)
def k(t,h=0,p=0,b=0,x=0,y=0,z=0):
    return dict(t=t,value=vec(h,p,b),position=vec(x,y,z),scale=vec(1,1,1))
def source_file(value):
    p=Path(value)
    return p if p.is_absolute() else ROOT/p

def motion_contract(shot,frames,anchors=None):
    """Native normalized programs and finite, inclusive source-frame windows.

    An Euler key window may alter several parameters; never infer an axis-angle
    measurement for a commercial game from these controlled lesson programs.
    Before/after snapshots reference actual NDJSON rows once captured.
    """
    windows=[]
    for prefix in ['a','b']if shot.get('pair')else['a']:
        program=shot[prefix]
        if program.get('kind')=='sequence':
            spans=[(s['start'],s['end'],{'step':i,'space':s['space'],'axis':s['axis'],'degrees':s['degrees']})for i,s in enumerate(program['steps'],1)]
        else:
            keys=program.get('keys',[])
            spans=[(a['t'],b['t'],{'keyInterval':i,'beforeInput':a,'afterInput':b})for i,(a,b)in enumerate(zip(keys,keys[1:]),1)]
        for start,end,description in spans:
            a=max(0,min(frames-1,math.ceil(start*(frames-1))))
            b=max(a,min(frames-1,math.floor(end*(frames-1))))
            before=max(0,min(frames-1,math.floor(start*(frames-1))))
            after=max(0,min(frames-1,math.ceil(end*(frames-1))))
            if program.get('kind')=='sequence':a,b=before,after
            windows.append({'object':prefix,**description,'normalizedInterval':[start,end],
                'nativeMotionFrames':[a,b],'frameRangeInclusive':True,'nativeSpeed':1,
                'stateBeforeFrame':before,'stateAfterFrame':after,
                'stateBefore':{'file':anchors,'ndjsonRow0Based':before},
                'stateAfter':{'file':anchors,'ndjsonRow0Based':after}})
    return {'sourceBeatId':shot['id'],'nativeFrameCount':frames,'nativeFPS':60,
        'nativeNormalizedTime':'frame/(frameCount-1); exact captured model states, no gameplay data',
        'programA':shot['a'],'programB':shot.get('b'),'motionWindows':windows,
        'pair':shot.get('pair',False),'isConcurrentSource':bool(shot.get('pair')and shot.get('a')and shot.get('b')),
        'pairRecomposition':'If narration advances A then B, hold A at its exact last state and play B within its own pane. Never restart A merely to repeat the simultaneous source.',
        'speechBinding':'Use targetParagraph actionCuePhrases and actual ASR word time; retain before/action/result during continuous speech; no paragraph-start autoplay.'}

def authorized():
    ctl=read(ROOT/'shared/publishing/video-production-control.json')
    auth=read(H/'authorization.json')
    assert auth['selectedPart']==1 and auth['parentVideo']=='game-math-euler-axis-angle'
    assert auth['approvedScriptSha256']==sha(S.SCRIPT),'Approved Part1 script changed.'
    claim=ctl.get('scopedProductionAuthorizations',{}).get(P.name,{})
    direct=ctl.get('selectedVideo')==P.name and ctl.get('newProductionAuthorization',{}).get('fullProductionAuthorized')
    scoped=(claim.get('status')=='explicit-human-authorized-active' and claim.get('part')==1 and
            claim.get('fullProductionAuthorized') and claim.get('authorizationSha256')==sha(H/'authorization.json') and
            claim.get('approvedScriptSha256')==sha(S.SCRIPT))
    assert direct or scoped,'Preserve the unrelated primary; no active Part1 claim.'
    return {'authorization':rel(H/'authorization.json'),'authorizationSha256':sha(H/'authorization.json'),
            'approvedScriptSha256':sha(S.SCRIPT),'scopedClaim':bool(scoped)}

def native_sources():
    receipt=read(V6/'spatial-clips/spatial-capture-receipt.json')
    outputs={x['id']:x for x in receipt['outputs']}
    result={}
    for key in sorted({key for pairs in S.SPECS.values() for key,_ in pairs if key.startswith('v6-')}):
        x=outputs[key];fs=x['files']
        clip=source_file(fs['clip']['path']); first=source_file(fs['firstFrame']['path']);last=source_file(fs['lastFrame']['path']);anchors=source_file(fs['anchors']['path'])
        assert all(p.exists() for p in [clip,first,last,anchors]),key
        result[key]={'sourceBeatId':key,'renderer':'Unity6000.6.0f1','sourceKind':'authored controlled3D model',
            'clip':rel(clip),'clipSha256':fs['clip']['sha256'],'frames':x['frames'],'firstFrame':rel(first),
            'firstFrameSha256':fs['firstFrame']['sha256'],'lastFrame':rel(last),'lastFrameSha256':fs['lastFrame']['sha256'],
            'anchors':rel(anchors),'anchorsSha256':fs['anchors']['sha256'],'nativeDimensions':[1920,1080],
            'fps':60,'recordedSourceBytes':clip.stat().st_size,
            'hashStatus':'prior complete receipt retained; --verify-source-hashes recomputes actual files before new movie job',
            'originalReceipt':rel(V6/'spatial-clips/spatial-capture-receipt.json')}
    return result

def generated_sources(source_keys):
    src=ENGINE/'EulerV6Scene.cs';text=src.read_text(encoding='utf-8-sig')
    original=sha(src)
    text=text.replace('namespace YamyamCoding.GameMath.EulerAxisAngle.V6\n',
        'using YamyamCoding.GameMath.EulerAxisAngle.V6;\nnamespace YamyamCoding.GameMath.EulerAxisAngle.V7\n')
    text=text.replace('EulerV6Scene','EulerV7PanelScene')
    assert text.count('CreateAxisLabels();Evaluate(normalizedTime);')==1
    text=text.replace('CreateAxisLabels();Evaluate(normalizedTime);',
        '// Old small labels/leaders are omitted, never painted over geometry.\n            Evaluate(normalizedTime);')
    marker='            if(shot.model=="wheel")'
    assert text.count(marker)==1
    text=text.replace(marker,'            if(shot.model=="sail"||shot.model=="hook"||shot.model=="log")\n            {\n                l=r=e=u=null;return BuildMatchedObject(name);\n            }\n'+marker)
    extra=(H/'right-matched-models.cs.in').read_text(encoding='utf8')
    marker='        private void SetCamera(Vector3 pos)'
    assert text.count(marker)==1
    text=text.replace(marker,extra+'\n'+marker)
    marker='            fixedA.position=aircraftA.position;'
    assert text.count(marker)==1
    text=text.replace(marker,'            if(matchedReference!=null){matchedReference.position=focusA+EulerV6Math.ToUnity(new Vector3(0,0,.68f));matchedReference.rotation=Quaternion.identity;}\n'+marker)
    marker='            Vector3[] axes={Vector3.right,Vector3.up,Vector3.forward};\n            for(int i=0;i<3;i++){AddAnchor'
    assert text.count(marker)==1
    text=text.replace(marker,'            if(prefix=="a"&&matchedReference!=null){AddAnchor(list,"a.referenceOrigin",matchedReference.position,body);AddAnchor(list,"a.referenceEndA",matchedReference.TransformPoint(Vector3.left*1.5f),body);AddAnchor(list,"a.referenceEndB",matchedReference.TransformPoint(Vector3.right*1.5f),body);AddAnchor(list,"a.referenceUp",matchedReference.TransformPoint(Vector3.up*.34f),body);AddAnchor(list,"a.referenceDown",matchedReference.TransformPoint(Vector3.down*.34f),body);}\n'+marker)
    text=text.replace(marker,'            if(prefix=="a"&&(shot.model=="sail"||shot.model=="log"||shot.model=="hook")){bool found=false;Bounds bounds=new Bounds();foreach(Renderer rr in generated.GetComponentsInChildren<Renderer>(true)){if(!rr.enabled||!rr.gameObject.activeInHierarchy)continue;if(!found){bounds=rr.bounds;found=true;}else bounds.Encapsulate(rr.bounds);}if(found){int corner=0;for(int x=-1;x<=1;x+=2)for(int y=-1;y<=1;y+=2)for(int z=-1;z<=1;z+=2)AddAnchor(list,"a.geometryCorner"+(corner++),bounds.center+Vector3.Scale(bounds.extents,new Vector3(x,y,z)),body);}}\n'+marker)
    # These shapes have a geometric mast/up direction rather than an aircraft nose.
    text=text.replace('prefix+".nose",body.TransformPoint(new Vector3(0,0,2.1f))',
        'prefix+(shot.model=="aircraft"?".nose":".frontProbe"),body.TransformPoint(new Vector3(0,0,2.1f))')
    out=O/'prepared-unity';out.mkdir(parents=True,exist_ok=True)
    runtime=out/'EulerV7PanelScene.cs';runtime.write_text(text,encoding='utf8')
    bridge=(ENGINE/'Editor/EulerV6Capture.cs').read_text(encoding='utf-8-sig')
    bridge=bridge.replace('namespace YamyamCoding.GameMath.EulerAxisAngle.V6.Editor','namespace YamyamCoding.GameMath.EulerAxisAngle.V7.Editor')
    bridge=bridge.replace('EulerV6Capture','EulerV7RightCapture').replace('EulerV6Scene','EulerV7PanelScene')
    bridge=bridge.replace('using UnityEngine.SceneManagement;','using UnityEngine.SceneManagement;\nusing YamyamCoding.GameMath.EulerAxisAngle.V6;')
    bridge=bridge.replace('revision-v6"','revision-v7-part1"').replace('-m04V6Job','-m04V7Job')
    bridge=bridge.replace('m04-v6-scenes-saved.json','m04-v7-part1-scenes-saved.json')
    # V6's Scenes folder already existed. This independently saved V7 stage
    # must create/import its own folder before the first real SaveScene call.
    bake_marker='            var data=JsonUtility.FromJson<V6Catalog>(catalog.text);'
    assert bridge.count(bake_marker)==1
    bridge=bridge.replace(bake_marker,'            Directory.CreateDirectory(Root+"/Scenes");AssetDatabase.Refresh();\n'+bake_marker)
    bridge=bridge.replace('public bool bakeScenes,captureTestbed,bakeOnly;public Clip[] clips;',
        'public bool bakeScenes,captureTestbed,bakeOnly;public Clip[] clips;public string[] bakeShotIds;')
    bridge=bridge.replace('if(job.bakeScenes)Bake(catalog,true);',
        'if(job.bakeScenes){if(job.bakeShotIds!=null&&job.bakeShotIds.Length>0)BakeSelected(job,catalog);else Bake(catalog,true);}')
    bridge=bridge.replace('        private static void Persist(EulerV7PanelScene owner)', '''        private static void BakeSelected(Job job,TextAsset catalog)
        {
            var data=JsonUtility.FromJson<V6Catalog>(catalog.text);var saved=new List<string>();
            foreach(string id in job.bakeShotIds)
            {
                V6Shot selected=null;foreach(var candidate in data.shots)if(candidate.id==id){selected=candidate;break;}
                if(selected==null)throw new ArgumentException("Missing selected shot: "+id);
                var sc=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
                EditorUtility.UnloadUnusedAssetsImmediate();
                var owner=new GameObject("Yamyam M04 V7 "+selected.sceneId).AddComponent<EulerV7PanelScene>();
                owner.shotCatalog=catalog;owner.LoadShot(selected.id);owner.Build();owner.Evaluate(0);owner.PrimeTextGeometry();Persist(owner);
                string dest=Root+"/Scenes/"+selected.sceneId+".unity";
                if(!EditorSceneManager.SaveScene(sc,dest))throw new IOException("Could not save "+dest);saved.Add(dest);
            }
            AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            File.WriteAllText(Path.Combine(job.outputDirectory,"selected-scenes-saved.json"),"{\\"sceneCount\\":"+saved.Count+",\\"scope\\":\\"selected patch only\\",\\"editor\\":\\""+Application.unityVersion+"\\"}");
        }
        private static void Persist(EulerV7PanelScene owner)''')
    # The only permitted project remains the existing task-local isolated clone.
    # Preserve this path guard rather than broadening it to the main Unity project.
    assert 'EndsWith("/production/local/revision-v6/unity-capture"' in bridge
    dest=out/'Editor/EulerV7RightCapture.cs';dest.parent.mkdir(exist_ok=True);dest.write_text(bridge,encoding='utf8')
    data=read(ENGINE/'spatial-shots.json');shots=[]
    for x in data['shots']:
        if x['id'] not in source_keys:continue
        x=copy.deepcopy(x);x['sceneId']='v7-a'+x['sceneId'].split('-')[-1];shots.append(x)
        if x['id']=='v6-11.B03':
            # New V7 authored timing, not commercial-footage retiming. A
            # preserves its original seven seconds. B's two90° stages each
            # take54native frames with12frames between, and end atframe120.
            # Capture still stores420frames; the edit selectsB0..120 at1x.
            for step,start,end in zip(x['b']['steps'],[0,66/419],[54/419,120/419]):step.update(start=start,end=end)
            x['v7ProgramChange']={'object':'b','originalSourceBeatId':'v6-11.B03','sourceFrames':[0,120],
                'stepEndFrames':[54,120],'stepStartFrames':[0,66],'sameAnglesAndAxisOrder':True,
                'reason':'Keep both reversed fixed-axis actions visible inside the actual short spoken comparison; A retains its complete original motion.'}
    template=copy.deepcopy(next(x for x in data['shots']if x['id']=='v6-04.B01'))
    for key,scene,model,keys in [
       ('v7-sail-move','v7-a02','sail',[k(0,p=90),k(1,p=90,x=1.1)]),
       ('v7-sail-raise','v7-a02','sail',[k(0,p=90,x=1.1),k(1,p=0,x=1.1)]),
       ('v7-log-align','v7-a15','log',[k(0,h=25,x=1.1),k(.5,h=25),k(1)]),
       ('v7-hook-rotate','v7-a03','hook',[k(0),k(1,h=90)])]:
        x=copy.deepcopy(template);x.update(id=key,sceneId=scene+'-'+key[3:],model=model,axes=False,pair=False,activeAxis='uprightY'if model=='hook'else'none',motionSeconds=.5 if key=='v7-sail-raise'else 6)
        x['a']=dict(kind='euler',keys=keys);x['b']=None;shots.append(x)
    # Each script scene has a separately editable testbed even when its current
    # proof is a2D board. Shared source meshes/materials are persisted once.
    seen={x['sceneId']for x in shots}
    for n in range(1,22):
        sid=f'v7-a{n:02}'
        if sid in seen:continue
        x=copy.deepcopy(template);x.update(id=sid+'.context',sceneId=sid,axes=False,activeAxis='none',motionSeconds=0)
        x['a']=dict(kind='euler',keys=[k(0,h=30,p=10,b=15),k(1,h=30,p=10,b=15)]);x['b']=None;shots.append(x)
    catalog=out/'spatial-shots.json';save(catalog,dict(shots=shots))
    sail_move=next(x for x in shots if x['id']=='v7-sail-move')
    sail_raise=next(x for x in shots if x['id']=='v7-sail-raise')
    assert {k:v for k,v in sail_move['a']['keys'][-1].items()if k!='t'}=={k:v for k,v in sail_raise['a']['keys'][0].items()if k!='t'}
    assert {k:v for k,v in sail_move.items()if k not in ['id','sceneId','a','motionSeconds']}=={k:v for k,v in sail_raise.items()if k not in ['id','sceneId','a','motionSeconds']}
    # Assembly references the already present V6 math contract explicitly.
    save(out/'Yamyam.GameMath.EulerRight.asmdef',{'name':'Yamyam.GameMath.EulerRight','references':['Yamyam.GameMath.EulerAxisAngle.V6'],'autoReferenced':True})
    save(out/'Editor/Yamyam.GameMath.EulerRight.Editor.asmdef',{'name':'Yamyam.GameMath.EulerRight.Editor','references':['Yamyam.GameMath.EulerRight','Yamyam.GameMath.EulerAxisAngle.V6'],'includePlatforms':['Editor'],'autoReferenced':True})
    return {'generatedRuntime':rel(runtime),'generatedRuntimeSha256':sha(runtime),'baseRuntime':rel(src),'baseRuntimeSha256':original,
        'mathSource':rel(ENGINE/'EulerV6Math.cs'),'mathSourceSha256':sha(ENGINE/'EulerV6Math.cs'),
        'generatedBridge':rel(dest),'generatedBridgeSha256':sha(dest),'catalog':rel(catalog),'catalogSha256':sha(catalog),
        'method':'V6 detailed geometry/math/programs reused except explicitly recorded V7 short B timing in11.B03; omit old TextMesh labels/leaders; add separate authored sail/log/hook geometry',
        'plannedSceneDirectory':'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v7-part1/Scenes',
        'savedSceneStatus':'planned only until actual Unity save files/receipts exist','scriptSceneCount':21,'supplementaryMotionSceneCount':4,'sceneCount':25,
        'isolatedProject':rel(ISO),'mainEditorOpenedOrChanged':False,'sourceReferencePipeline':'canonicalURP17.6 compatible copied materials via recorded adaptation; existing isolated built-in linear2xMSAA native source assets/pixels remain unchanged',
        'mainURPRuntimeReview':'not claimed: no unrelated main editor manipulated; compatible serialized shader references and source paths are recorded'}

def label_contract(n):
    return {'fontSize':68,'minimumKeyFontSize':64,'maximumVisibleAxisLabels':3 if n==2 else 2,
        'axes':S.ACTIVE_AXES.get(n,[]),'axisColors':{'X':'#ef5a63','Y':'#6cce8e','Z':'#73acf5'},
        'worldBodyConvention':'left-handed; row; object-to-upright; intrinsicY-X-Z, R=Rz(b)Rx(p)Ry(h)',
        'meaning':'Only model values/anchors are numerical implementation data. Left game guides are editorial screen observations.',
        'sourceLabelPolicy':'Use new label-free source when possible; never paint black boxes over moving geometry.',
        'fixedCaptionPosition':[960,970],'fullFrameContentBottom':850}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--stage-isolated',action='store_true');ap.add_argument('--verify-source-hashes',action='store_true');a=ap.parse_args()
    approval=authorized();script=read(S.SCRIPT);assert len(script['scenes'])==21
    source=native_sources();generated=generated_sources(source)
    math=read(V6/'math/outputs.json');math_source=[x for x in math['outputs']if int(x['id'][3:5])<=21]
    for key,row in source.items():
        if a.verify_source_hashes:
            assert sha(ROOT/row['clip'])==row['clipSha256'],key
            assert sha(ROOT/row['anchors'])==row['anchorsSha256'],key
            row['hashStatus']='current actual clip/anchor hashes recomputed and matched'
    paragraphs=[];sceneplans=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',64)
    width_errors=[]
    for key,(title,rows) in S.BOARDS.items():
        for line in rows:
            # Font fallback may differ in Manim; final actual pixels remain pending.
            if font.getlength(line)>830:width_errors.append({'board':key,'text':line,'widthAt64':font.getlength(line)})
    for n,s in enumerate(script['scenes'],1):
        assert s['id']==f'v7-a{n:02}' and len(s['lines'])==len(S.SPECS[n]),(s['id'],len(s['lines']),len(S.SPECS[n]))
        rows=[]
        for i,(text,(key,state)) in enumerate(zip(s['lines'],S.SPECS[n]),1):
            board=key[6:]if key.startswith('board-')else None
            row={'targetScene':s['id'],'targetParagraph':i,'targetParagraphId':s['id']+f'.L{i:02}',
                'sourceBeatId':key,'playState':{'0':'first exact state','1':'last exact state','m':'one finite native-speed motion'}[state],
                'nativeMotion':state=='m','speechCue':text[:min(len(text),28)],'textSha256':hashlib.sha256(text.encode()).hexdigest(),
                'actionCuePhrases':S.ACTION_CUES.get(s['id']+f'.L{i:02}',[]),
                'withinParagraphAssets':S.WITHIN_PARAGRAPH_ASSETS.get(s['id']+f'.L{i:02}',[]),
                'explicitNativeWindows':S.PARAGRAPH_WINDOWS.get(s['id']+f'.L{i:02}',[]),
                'pairActions':S.PAIR_ACTIONS.get(s['id']+f'.L{i:02}',[]),
                'speechStateSwitches':S.SPEECH_STATE_SWITCHES.get(s['id']+f'.L{i:02}',[]),
                'motionScheduling':S.MOTION_SCHEDULING.get(s['id']+f'.L{i:02}',{}),
                'baseSourceFrame':S.BASE_SOURCE_FRAMES.get(s['id']+f'.L{i:02}'),
                'coincidentConfirmationCue':S.COINCIDENT_CONFIRMATIONS.get(s['id']+f'.L{i:02}'),
                'motionStartPolicy':'Resolve actual ASR word cue; hold the exact before state under continuing definition speech until the action is spoken. Never autoplay at paragraph start.',
                'simultaneousWithLeftGame':True,'animationRequiresNarrationSilence':False,'forcedHoldFrames':0,
                'stopAfterObservedResult':True,'loopOrPadding':False,'ui':label_contract(n)}
            if n<3:
                row['pretermNumericReadoutPolicy']={'hideOnlyKnownUIReadoutBand':True,
                    'singleBand':[0,558,900,102],'pairBand':[0,490,900,170],
                    'reason':'h/p/b names are introduced in scene03; early concrete orientation/setup examples must not require unexplained parameter names. These bands contain new composited text only, no native geometry.',
                    'replacement':S.PRETERM_READOUTS.get(s['id']+f'.L{i:02}','앞·위·옆의 방향')}
            if board:
                row['board']={'key':board,'title':S.BOARDS[board][0],'rows':S.BOARDS[board][1],
                    'layout':'large reflowed semantic lines over dim retained detailed aircraft; not full-slide scaling',
                    'reveal':'current spoken clause only; no post-speech mandatory playback'}
            else:row['modelState']=state
            rows.append(row);paragraphs.append(row)
        sceneplans.append({'targetScene':s['id'],'title':s['title'],'paragraphs':rows,'rendererReason':'Unity controlled spatial relationships; 2D semantic labels/arithmetic composited beside matched game',
            'beforeActionResult':'See paragraph bindings and retained originalV6 screen-plan meaning; actual source/action stays on the left, controlled values on the right.',
            'sourceOldScene':'v6-'+f'{n:02}','pairLabel':'A 물체 축 | B 고정 축, both inside right explanation panel','humanPaceMotionReview':'pending actual narration and final moving paired output'})
    inventory=read(ROOT/'shared/assets/unity-asset-library.json')
    imported=[]
    for id,reason in [('026','Whole pirate boats/ships; no verified independently articulated sail/hook part matching this explanation. Current per-product license remains unverified.'),('035','Whole environment raft prefab; not the separate mast/cloth/log/hook manipulated in the lesson. Avoid replacing the approved controlled aircraft just to use an owned asset.')]:
        x=next(x for x in inventory['products']if x['id']==id);imported.append({'productId':id,'title':x['title'],'assetRoot':x['actualAssetPath'],'publicProductUrl':x['publicProductUrl'],'adopted':False,'reason':reason,'licenseStatus':x['licenseStatus']})
    plan={'schemaVersion':1,'revision':'story-gameplay-two-part-v7-part1-right-paired','status':'prepared; no new capture/movie render started',
        'authorization':approval,'script':rel(S.SCRIPT),'scriptSha256':sha(S.SCRIPT),'part':1,'scenes':sceneplans,
        'layout':{'fullCanvas':[1920,1080],'rightPane':[980,180,900,660],'leftGameSuggested':[40,250,896,504],
            'sharedCaption':[960,970],'keyFontPx':[64,72],'keyFontAt375px':[12.5,14.06],
            'singleModel':'crop only safe spatial content, preserve aspect/axes/rings/silhouette; native source ROI measured before capture finalization',
            'pair':'A and B horizontally inside the right pane; one shared large numeric relation. Do not shrink the entire old1920 slide.',
            'math':'reflowed short semantic lines with relevant controlled model dimmed behind, no full black reset'},
        'nativeSourceAssets':list(source.values()),'retainedMathSources':[{'sourceBeatId':x['id'],'clip':x['clipFile'],'clipSha256':x['files'][0]['sha256'],'frames':x['durationFrames'],'reuse':'same mathematical meaning/values; reflow UI to900px; source pixels only if readable'}for x in math_source],
        'generatedUnity':generated,'newMatchedModels':{'sail':['separate pole','crossbars','slightly curved cloth mesh','rope ties'],'log':['cylindrical timber','visible endgrain','bark grooves','rope bindings','independent stationary neighbor for parallel alignment; actual anchors exported'],'hook':['curved open metal hook','thick mount/neck','visible open direction'],'motionClipCount':4,'distinctObjectCount':3,'assetKind':'independently authored generic explanation geometry; no extracted Nintendo assets; no measured game rotation angles',
            'sailContinuity':{'moveEndEqualsRaiseStart':True,'controlledPosition':[1.1,0,0],'controlledEulerHPB':[0,90,0],'crop':'one union of actual geometry bounds across both finite clips; same size and position','speechCue':'v7-a02.L02: 세우고','pixelContinuityReview':'first bank90 sample exposed a vertical cloth panel; corrected controlledpitch90 makes cloth horizontal before raising. Corrected3endpoint sample pending; catalog state equality verified.'}},
        'importedAssetConsultation':{'catalog':rel(ROOT/'shared/assets/unity-asset-library.json'),'catalogSha256':sha(ROOT/'shared/assets/unity-asset-library.json'),'consultedGuide':'docs/UNITY_ASSET_LIBRARY.md','candidates':imported,'vendorOriginalsChanged':False},
        'paragraphCount':len(paragraphs),'unityExistingClipCount':len(source),'mathExistingClipCount':len(math_source),
        'newMathMotionSources':{'source':rel(H/'right-manim.py'),'sourceSha256':sha(H/'right-manim.py'),'renderer':'Manim Cairo CPU; native900x660 reflow over retained dim detailed model','clipCount':4,'plannedFrames':574,
            'plan':rel(O/'math-native/plan.json'),'targets':['v7-a16.L01','v7-a16.L03','v7-a16.L04','v7-a17.L02'],
            'meaning':'3vs9 storage slots;1-degree interval and0.5-degree half-distance;input20.0->20.4 whileoutput20 stays;one matrixentry stretchesX length. No tie-breaking or fabricated game values.',
            'status':'prepared source only; actual finite render and paired timing/pixels pending'},
        'canonicalAliasVisual':'v7-a19.L03 reuses exact final v6-18.B02A(0,135,0)/B(180,45,180), actual identical3D pose; reflowed numeric focus traces representative conversion, not a false intermediate path',
        'nativeProgramTimingChanges':{'v6-11.B03':{'object':'b','nativeSourceFramesSelected':[0,120],'nativeStepFrames':[[0,54],[66,120]],'captureFrameCount':420,'anglesAndOrder':'uprightY90 thenuprightX90; unchanged result','originalV6FilesChanged':False,'reason':'New authored V7 short motion, native1x; both changes complete before the spoken result. A remains the original seven-second program.'}},
        'newCaptureFrameCountExceptions':{'v6-18.B01':{'frames':541,'reason':'Exact360-degree halfway sample; original0-to720 linear program retained.'},'v6-20.B01':{'frames':481,'reason':'Exact80-degree halfway sample; endpoints/program retained.'},'v6-20.B02':{'frames':481,'reason':'Exact.45/.55 keys for20-degree equivalence and signed45-degree boundary examples; programs retained.'}},
        'rawBoardWidthFindings':width_errors,'rendererStarted':False,'gpuLeaseAcquired':False,
        'reuseNote':S.REUSE_NOTE,'pending':['root GPU handoff after voice/sourceASR','native clear-label sample and shape runtime review','current source ROI and larger labels native375','actual source/speech cues','all final moving paired/caption/cut review']}
    completed_math=O/'math-native/outputs.json'
    if completed_math.exists():
        actual=read(completed_math)
        if actual.get('complete')and actual.get('sourceSha256')==sha(H/'right-manim.py')and actual.get('scriptSha256')==sha(S.SCRIPT):
            assert len(actual['outputs'])==4 and sum(x['frames']for x in actual['outputs'])==574
            assert all((ROOT/x['files']['clip']['file']).exists()and sha(ROOT/x['files']['clip']['file'])==x['files']['clip']['sha256']for x in actual['outputs'])
            plan['status']='four native Manim diagrams rendered; Unity native capture and paired moving review pending'
            plan['rendererStarted']=True;plan['mathCpuRenderComplete']=True
            plan['newMathMotionSources'].update(status='actual4clips574frames900x660/60; word-bound paired review pending',
                actualManifest=rel(completed_math),actualManifestSha256=sha(completed_math))
    save(PLAN,plan);save(O/'paragraph-plan.json',{'scriptSha256':sha(S.SCRIPT),'paragraphs':paragraphs})
    # Odd counts place .5 on an exact native frame, and481 also samples .45
    # and .55 exactly. This allows true360°,80°,20° boundary snapshots to be
    # held while narration continues, rather than relabeling a nearby pose.
    exact_counts={'v6-18.B01':541,'v6-20.B01':481,'v6-20.B02':481}
    clips=[{'shotId':key,'frames':exact_counts.get(key,row['frames'])}for key,row in source.items()]
    clips += [{'shotId':k,'frames':31 if k=='v7-sail-raise'else 360}for k in ['v7-sail-move','v7-sail-raise','v7-hook-rotate','v7-log-align']]
    job={'outputDirectory':str(O/'spatial-native'),'ffmpegPath':shutil.which('ffmpeg'),'bakeScenes':True,'captureTestbed':False,'clips':clips,
         'approval':approval,'generatedSourceSha256':generated['generatedRuntimeSha256'],'generatedBridgeSha256':generated['generatedBridgeSha256'],
         'catalogSha256':generated['catalogSha256'],'mathSourceSha256':generated['mathSourceSha256'],
         'captureKind':'label-free V6 programs, explicit V7shortB11.B03 timing and four finite motions of three own matched shapes; no commercial-footage retiming'}
    save(O/'right-native-job.json',job)
    catalog={s['id']:s for s in read(ROOT/generated['catalog'])['shots']}
    programs=[motion_contract(catalog[c['shotId']],c['frames'],source.get(c['shotId'],{}).get('anchors'))for c in clips]
    save(O/'native-programs.json',{'scriptSha256':sha(S.SCRIPT),'sourceKind':'prepared exact native programs; new capture still pending','assets':programs,'paragraphs':paragraphs})
    if a.stage_isolated:
        import psutil
        for proc in psutil.process_iter(['name','cmdline']):
            if (proc.info['name']or'').lower()=='unity.exe' and str(ISO).lower().replace('\\','/')in' '.join(proc.info['cmdline']or[]).lower().replace('\\','/'):
                raise RuntimeError('Task isolated project already in use; no files touched.')
        target=ISO/'Assets/VideoScenes/game-math-euler-axis-angle/revision-v7-part1'
        target.resolve().relative_to(ISO.resolve())
        shutil.copytree(O/'prepared-unity',target,dirs_exist_ok=True)
        print('Staged owned V7 sources into task-local isolated project only.')
    print(json.dumps({'plan':rel(PLAN),'paragraphs':len(paragraphs),'existingUnityClips':len(source),'oldMathClips':len(math_source),
        'nativeFramesPlanned':sum(x['frames']for x in clips),'widthFindings':width_errors,'captureStarted':False},ensure_ascii=False))

if __name__=='__main__':main()
