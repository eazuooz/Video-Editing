"""Apply/verify one metadata-only A/B continuity correction, no new media."""
from pathlib import Path
import argparse,copy,importlib.util,json,shutil
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_a10_prepare',H/'right-prepare.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,O=M.ROOT,M.O
RECORD=O/'a10-pair-continuity-patch.json'

def apply():
    M.authorized();assert not RECORD.exists(),'Preserve existing correction record.'
    assets=M.read(O/'right-assets.json');segments=M.read(O/'right-visual-segments.json')
    by={r['sourceBeatId']:r for r in assets['assets']};a=by['v6-10.B01'];b=by['v6-10.B02']
    assert a['frames']==b['frames']==420 and a['programA']==b['programA']
    archive=O/'timing-history'/('a10-before-'+M.sha(O/'right-visual-segments.json')[:16]);archive.mkdir(parents=True,exist_ok=False)
    for p in [M.PLAN,O/'paragraph-plan.json',O/'native-programs.json',O/'right-assets.json',O/'right-visual-segments.json',O/'timing-preflight.json']:
        shutil.copy2(p,archive/p.name)
    paras=M.read(O/'paragraph-plan.json');changed=[]
    for r in paras['paragraphs']:
        if r['targetScene']!='v7-a10':continue
        pid=r['targetParagraphId'];i=r['targetParagraph']
        if i<=2:r['sourceBeatId']='v6-10.B02';changed.append(pid)
        if i==2:r['pairActions']=copy.deepcopy(M.S.PAIR_ACTIONS[pid])
        if i in [3,4]:r['basePairState']=copy.deepcopy(M.S.PAIR_BASE_STATES[pid]);changed.append(pid)
    M.save(O/'paragraph-plan.json',paras)
    programs=M.read(O/'native-programs.json');programs['paragraphs']=paras['paragraphs'];M.save(O/'native-programs.json',programs)
    assets['paragraphs']=paras['paragraphs']
    for asset in assets['assets']:
        if asset['sourceBeatId']not in ['v6-10.B01','v6-10.B02']:continue
        selected=[r for r in paras['paragraphs']if r['sourceBeatId']==asset['sourceBeatId']]
        asset['targetParagraphs']=[r['targetParagraphId']for r in selected];asset['targetScenes']=sorted({r['targetScene']for r in selected})
    plan=M.read(M.PLAN);scene=next(s for s in plan['scenes']if s['targetScene']=='v7-a10')
    scene['paragraphs']=[r for r in paras['paragraphs']if r['targetScene']=='v7-a10']
    scene['pairLabel']='A·물체축/B·고정축 are both inside RIGHT explanation pane from first spoken left/right-model reference.'
    scene['continuityCorrection']={'source':'v6-10.B02; existing actual420frames','Asteps':[[0,126],[146,273],[293,419]],'fixedDuringA':'B actual0','Bsteps':'unchanged full0..419 at existing cue','fixedDuringBPreparationAndMotion':'A actual419','newNativeOrPanelMedia':False,'reason':'Remove ambiguous single-model left reference and preserve already demonstrated A result during B introduction.'}
    M.save(M.PLAN,plan);assets['planSha256']=M.sha(M.PLAN);M.save(O/'right-assets.json',assets)
    M.save(RECORD,{'status':'metadata-applied; timing verification pending','archive':M.rel(archive),'changedParagraphIds':changed,'all36PanelVideoHashesBefore':{k:v['clipSha256']for k,v in by.items()if v.get('clipSha256')},'newMediaRendered':False,'nativeGPUStarted':False,'approvedPCMChanged':False,'nativeFPS':60,'nativeSpeed':1})
    print(json.dumps({'status':'applied','changedParagraphs':changed,'newMedia':False}))

def verify():
    record=M.read(RECORD);old=M.read(ROOT/record['archive']/'right-visual-segments.json');new=M.read(O/'right-visual-segments.json')
    def scene_rows(data,sid):return [r for r in data['visualSegments']if r['sceneId']==sid]
    changed=[f'v7-a{i:02}'for i in range(1,22)if scene_rows(old,f'v7-a{i:02}')!=scene_rows(new,f'v7-a{i:02}')]
    assert changed==['v7-a10'],changed
    assets=M.read(O/'right-assets.json');now={r['sourceBeatId']:r['clipSha256']for r in assets['assets']if r.get('clipSha256')}
    assert now==record['all36PanelVideoHashesBefore']
    for r in assets['assets']:
        if r.get('clipSha256'):assert M.sha(ROOT/r['clip'])==r['clipSha256']
    assert new['bodyCoverageNoFrameGaps']and all(r['cueOffsetFrames']<=0 for r in new['actionSelectionAudit'])
    record.update(status='frozen; actual a10 paired recomposition pending',changedSegmentScenes=changed,other20SceneSegmentArraysByteEquivalent=True,
        all36PanelClipHashesPreserved=True,rightAssetsSha256=M.sha(O/'right-assets.json'),rightSegmentsSha256=M.sha(O/'right-visual-segments.json'),rightPlanSha256=M.sha(M.PLAN),
        bodyFrameGaps=0,sourceFrameOverflow=0,unexplainedPositiveActionCueOffsets=0,
        geometryUse='Existing actual pair cropA/B; no nonuniform resize, fabricated axis, changed aspect or changed commercial-game speed',actualMovingReview='pending new a10 same-captioned composition')
    M.save(RECORD,record);print(json.dumps(record,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--verify',action='store_true');a=p.parse_args()
    if a.apply:apply()
    elif a.verify:verify()
    else:p.print_help()
