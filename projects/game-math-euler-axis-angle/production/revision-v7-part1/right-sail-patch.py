"""Preserve and prepare/merge the single root-authorized31-frame sail correction.

This metadata/source helper starts no renderer. Capture/build remain separate
finite-lease CLIs. The other31 native captures and four math sources are reused.
"""
from pathlib import Path
import argparse,copy,importlib.util,json,shutil
from PIL import Image,ImageChops,ImageStat
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_sail_prepare',H/'right-prepare.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,O=M.ROOT,M.O
STATE=O/'sail31-patch.json'

def prepare():
    M.authorized();assert not STATE.exists(),'Preserve previous correction record.'
    old=M.read(O/'spatial-native/capture-receipt.json');assert len(old['outputs'])==32
    oldrow=next(r for r in old['outputs']if r['sourceBeatId']=='v7-sail-raise');assert oldrow['frames']==360
    archive=O/'spatial-patch/superseded'/oldrow['files']['clip']['sha256'];archive.mkdir(parents=True,exist_ok=False)
    paths=[M.PLAN,O/'right-native-job.json',O/'native-programs.json',O/'spatial-native/capture-receipt.json',O/'right-assets.json',O/'right-visual-segments.json',O/'timing-preflight.json',H/'right-saved-scenes.json']
    for p in [O/'prepared-unity/Editor/EulerV7RightCapture.cs',O/'prepared-unity/spatial-shots.json']+paths:
        target=archive/p.name;assert not target.exists();shutil.copy2(p,target)
    beforecat=M.read(O/'prepared-unity/spatial-shots.json');plan=M.read(M.PLAN);oldgenerated=plan['generatedUnity']
    generated=M.generated_sources(set(M.native_sources()))
    assert generated['generatedRuntimeSha256']==oldgenerated['generatedRuntimeSha256'],'Native geometry/runtime must be identical.'
    aftercat=M.read(ROOT/generated['catalog']);a=copy.deepcopy(aftercat);b=copy.deepcopy(beforecat)
    next(s for s in a['shots']if s['id']=='v7-sail-raise')['motionSeconds']=6
    assert a==b,'Only authored sail duration may change.'
    plan['generatedUnity']={**oldgenerated,**generated,'savedSceneStatus':'previous26saved; corresponding sail duration patch save pending'}
    plan['nativeProgramTimingChanges']['v7-sail-raise']={'oldFrames':360,'newFrames':31,'nativeFPS':60,'program':'same p90→0 smoothstep, authored duration0.5second; exact endpoints retained','reason':'Actual paired scene shows game upright while the six-second model remains almost flat; align visible action with unchanged spoken cue3513.'}
    plan['rightDelivery']['pairedReview']='actuala02saildurationfinding; narrow correction in progress'
    M.save(M.PLAN,plan)
    job=M.read(O/'right-native-job.json');next(x for x in job['clips']if x['shotId']=='v7-sail-raise')['frames']=31
    for k in ['generatedBridgeSha256','catalogSha256']:job[k]=generated[k]
    M.save(O/'right-native-job.json',job)
    programs=M.read(O/'native-programs.json');shot=next(s for s in aftercat['shots']if s['id']=='v7-sail-raise')
    programs['assets']=[M.motion_contract(shot,31)if r['sourceBeatId']=='v7-sail-raise'else r for r in programs['assets']];M.save(O/'native-programs.json',programs)
    M.save(STATE,{'status':'prepared','oldCaptureRow':oldrow,'preservedRecordDirectory':M.rel(archive),'nativeUnchanged31Hashes':{r['sourceBeatId']:r['files']['clip']['sha256']for r in old['outputs']if r['sourceBeatId']!='v7-sail-raise'},'oldCatalogSha256':oldgenerated['catalogSha256'],'newCatalogSha256':generated['catalogSha256'],'sharedRuntimeGeometryUnchanged':True,'gameSpeedChanged':False,'approvedPCMChanged':False})
    print(json.dumps({'status':'prepared','catalogSha256':generated['catalogSha256'],'frames':31}))

def merge():
    record=M.read(STATE);assert record['status']=='prepared'
    job=M.read(O/'right-sail-patch-job.json');folder=Path(job['outputDirectory']);patch=M.read(folder/'capture-receipt.json')
    assert patch['patchOnly']and len(patch['outputs'])==1
    row=patch['outputs'][0];assert row['sourceBeatId']=='v7-sail-raise'and row['frames']==31
    assert M.sha(ROOT/row['files']['clip']['file'])==row['files']['clip']['sha256']
    receipt=M.read(O/'spatial-native/capture-receipt.json');receipt['outputs']=[row if r['sourceBeatId']=='v7-sail-raise'else r for r in receipt['outputs']]
    assert {r['sourceBeatId']:r['files']['clip']['sha256']for r in receipt['outputs']if r['sourceBeatId']!='v7-sail-raise'}==record['nativeUnchanged31Hashes']
    receipt['finitePatchHistory']=[{'patchReceipt':M.rel(folder/'capture-receipt.json'),'patchReceiptSha256':M.sha(folder/'capture-receipt.json'),'originalReceipt':record['preservedRecordDirectory']+'/capture-receipt.json','originalJobSha256':receipt['jobSha256'],'reason':'Actual paired visible rotation onset/result alignment; one self-authored clip only; original31movies untouched.'}]
    receipt['captureProvenance']='Mixed original32-clip receipt with one separately leased31-frame patch; per-output exact files/hashes and finite job history retained.'
    M.save(O/'spatial-native/capture-receipt.json',receipt)
    record.update(status='captured-and-merged',actualPatchReceipt=M.rel(folder/'capture-receipt.json'),actualPatchReceiptSha256=M.sha(folder/'capture-receipt.json'),newNativeRow=row,selectedSavedReceipt=M.rel(folder/'selected-scenes-saved.json'))
    M.save(STATE,record);print(json.dumps({'status':record['status'],'nativeFrames':sum(r['frames']for r in receipt['outputs'])}))

def reuse_endpoints():
    record=M.read(STATE);assert record['status']=='captured-and-merged'
    archive=ROOT/record['preservedRecordDirectory'];prior=M.read(archive/'right-assets.json')
    old=next(r for r in prior['assets']if r['sourceBeatId']=='v7-sail-raise')
    manifest=M.read(O/'right-assets.json');new=next(r for r in manifest['assets']if r['sourceBeatId']=='v7-sail-raise')
    assert new['frames']==31 and old['sourceROI']==new['sourceROI']
    evidence=[];decoded=archive/'new31-decoded-endpoints';decoded.mkdir(exist_ok=True)
    for name,logical,original in [('firstFrame',0,0),('lastFrame',30,359)]:
        assert ImageChops.difference(Image.open(ROOT/record['oldCaptureRow']['files'][name]['file']),Image.open(ROOT/record['newNativeRow']['files'][name]['file'])).getbbox()is None
        oldpng=O/'right-assets/superseded'/('v7-sail-raise.'+old['clipSha256'][:16]+('.first.png'if logical==0 else'.last.png'))
        current=ROOT/new[name];diff=ImageChops.difference(Image.open(oldpng),Image.open(current))
        evidence.append({'state':name,'nativeOriginalPNGPixelIdentity':True,'reencodedPanelPixelIdentity':diff.getbbox()is None,'panelChannelDifferenceExtrema':diff.getextrema(),'panelMeanAbsoluteDifference':ImageStat.Stat(diff).mean,'newNativeFrame':logical,'originalNativeFrame':original,'originalDecodedPosePNG':old[name],'originalDecodedPosePNGSha256':old[name+'Sha256'],'reason':'Exact identical original Unity geometry/state/ROI; reuse previously reviewed PNG instead of codec-dependent endpoint pixels.'})
        shutil.copy2(current,decoded/(name+'.png'));shutil.copy2(oldpng,current);new[name+'Sha256']=old[name+'Sha256']
        oldstate=next(s for s in old['nativeStateFiles']if s['sourceFrame']==original)
        newstate=next(s for s in new['nativeStateFiles']if s['sourceFrame']==logical)
        oldstatefile=O/'right-assets/superseded'/('v7-sail-raise.'+old['clipSha256'][:16]+'.states')/Path(oldstate['file']).name
        target=ROOT/oldstate['file'];target.parent.mkdir(exist_ok=True);shutil.copy2(oldstatefile,target)
        newstate.update(file=oldstate['file'],sha256=M.sha(target),pixelSourceKind='prior exact-pose independently exported PNG; native Unity state identical, new H264 endpoint differs only in encoding',originalNativeFrame=original)
    new['endpointPoseReuse']={'sourceStateFrameAliases':{'0':0,'30':359},'originalCaptureRow':record['oldCaptureRow'],'endpointEvidence':evidence,'retainedStaticSegmentMetadata':'sourceStateFrame identifies the retained original pose PNG; moving clip has31frames and is separately bounded.'}
    M.save(O/'right-assets.json',manifest);record['endpointReuse']=new['endpointPoseReuse'];M.save(STATE,record)
    print(json.dumps({'status':'same-pose-original-endpoints-reused','nativePixelIdentity':True}))

def finalize():
    record=M.read(STATE);assert record['endpointReuse']
    archive=ROOT/record['preservedRecordDirectory'];oldassets=M.read(archive/'right-assets.json');assets=M.read(O/'right-assets.json')
    before={r['sourceBeatId']:r for r in oldassets['assets']};after={r['sourceBeatId']:r for r in assets['assets']}
    changed=[k for k,r in after.items()if r.get('clipSha256')!=before[k].get('clipSha256')]
    assert changed==['v6-20.B02','v6-20.B03','v7-sail-raise'],changed
    receipt=M.read(O/'spatial-native/capture-receipt.json');assert sum(r['frames']for r in receipt['outputs'])==11554
    proof=M.read(H/'right-saved-scenes.json');oldproof=M.read(archive/'right-saved-scenes.json')
    origfiles={r['file']:r for r in oldproof['files']};changedcanonical=[r['file']for r in proof['files']if r['sha256']!=origfiles[r['file']]['sha256']]
    assert {Path(r).name for r in changedcanonical}=={'EulerV7RightCapture.cs','spatial-shots.json','v7-a02-sail-raise.unity'},changedcanonical
    plan=M.read(M.PLAN);plan['generatedUnity'].update(savedSceneStatus='actual26canonicalunityscenes verified; selected sail31 duration scene/catalog/bridge updated; other25scenes byte-identical',savedProofSha256=M.sha(H/'right-saved-scenes.json'))
    plan['nativeCapture'].update(sha256=M.sha(O/'spatial-native/capture-receipt.json'),frames=11554,finitePatch=M.rel(STATE))
    plan['rightDelivery']['pairedReview']='actuala02raise and a20pair-guide findings corrected; updated actual paired1080/375 QA pending'
    M.save(M.PLAN,plan);assets['planSha256']=M.sha(M.PLAN);M.save(O/'right-assets.json',assets)
    record.update(status='media-correction-frozen',changedRightVideoIds=changed,unchangedRightVideos=33,unchangedCanonicalSceneCount=25,changedCanonicalFiles=changedcanonical,
        original31NativeClipHashesPreserved=True,original4MathClipHashesPreserved=True,panelSailMoveClipHashUnchanged=True,
        newRightVideoHashes={k:after[k]['clipSha256']for k in changed},allOtherStaticPNGsUnchanged=True,
        actual31NativeProgram='frame0..30 normalized0..1 at60fps; smoothstep90→0, duration0.5s; no gameplay retiming',
        spokenCueGlobalFrame=3513,newMotionEndFrameExclusive=3544,followingState='same previously approved upright PNG; speech continuous',
        gimbalUIChange='pair B02/B03 omit A-only h/b leaders; single proof/rings/current orthogonal basis/A-B numeric bundles retained',
        actualNewPairedReview='pending root recomposition',mainURPRuntimeExecuted=False)
    M.save(STATE,record);print(json.dumps({'status':record['status'],'changedRightVideoIds':changed,'canonicalScenesUnchanged':25}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--merge',action='store_true');p.add_argument('--reuse-endpoints',action='store_true');p.add_argument('--finalize',action='store_true');a=p.parse_args()
    if a.prepare:prepare()
    elif a.merge:merge()
    elif a.reuse_endpoints:reuse_endpoints()
    elif a.finalize:finalize()
    else:p.print_help()
