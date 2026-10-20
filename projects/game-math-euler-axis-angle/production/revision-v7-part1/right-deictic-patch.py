"""Narrow verified-state corrections; no motion render, voice or GPU job.

Only a05 comparison continuity, a11 intermediate-state recall and a13 bank-zero
prerequisite change. Existing actual native geometry and all36 movies survive.
"""
from pathlib import Path
import argparse,copy,importlib.util,json,shutil
from PIL import Image,ImageDraw,ImageFont
H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_deictic_prepare',H/'right-prepare.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,O=M.ROOT,M.O
RECORD=O/'deictic-state-patch.json'

def bank_zero(assets,replace_sha=None):
    source=assets['v6-11.B02'];target=assets['v6-13.B01']
    native=O/'spatial-native/v6-11.B02.last.png'
    proof=M.read(O/'spatial-native/capture-receipt.json')
    out=next(x for x in proof['outputs']if x['sourceBeatId']=='v6-11.B02')
    assert M.sha(native)==out['files']['lastFrame']['sha256']
    state=source['sourceStateAfter'];matrix=state['rowMatrixA'];other=state['rowMatrixB']
    assert max(abs(a-b)for a,b in zip(matrix,other))<1e-6
    assert state['eulerDegreesA']==dict(x=30.0,y=20.0,z=0.0)
    layout=target['sourceROI'];x,y,w,h=layout['crop'];dw,dh=layout['size'];px,py=layout['position'];sx,sy=layout['scale']
    # Full native frame is mapped with the existing target-camera placement.
    # This retains silhouette parts outside the previous union crop as well.
    bg='#080b0d';im=Image.new('RGB',(900,660),bg)
    src=Image.open(native).convert('RGB')
    transformed=src.resize((round(src.width*sx),round(src.height*sy)),Image.Resampling.LANCZOS)
    im.paste(transformed,(round(px-x*sx),round(py-y*sy)))
    d=ImageDraw.Draw(im)
    # The borrowed source carries no lesson UI. New labels keep a13's role and
    # truthful stored angles, never importing the old fixed-axis wording.
    d.rectangle((0,0,899,134),fill=bg);d.rectangle((0,486,899,659),fill=bg)
    def text(x,y,t,size,col):d.text((x,y),t,font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',size),fill=col,anchor='mm',stroke_width=2,stroke_fill=bg)
    text(450,34,'어느 단계의 축인가',54,'#e8cf83')
    text(225,102,'A · 오일러 피치',58,'#73c7c2');text(675,102,'B · 물체 X',58,'#e8cf83')
    for prefix in ['a','b']:
        anchor=next(a['pixelTopLeft']for a in state['anchors']if a['name']==prefix+'.bodyX')
        xx=max(75,min(825,(anchor['x']-x)*sx+px));yy=max(170,min(450,(anchor['y']-y)*sy+py-32))
        text(xx,yy,prefix.upper()+' X',64,'#ef5a63')
    text(450,522,'A/B  30° / 20° / 0°',64,'#73c7c2');text(450,604,'b = 0° · 같은 회전축',64,'#e8cf83')
    cfg=copy.deepcopy(M.S.BASE_EXACT_STATES['v7-a13.L01']);dst=ROOT/cfg['file']
    assert not dst.exists()or(replace_sha and M.sha(dst)==replace_sha)
    im.save(dst);cfg['sha256']=M.sha(dst);cfg['provenance'].update(nativeSourceFile=M.rel(native),nativeSourceSha256=M.sha(native),
        nativeSourceRowMatrixA=matrix,nativeSourceRowMatrixB=other,targetROI=layout,
        pipeline='Actual label-free native endpoint PNG → existing a13 camera crop/scale/placement → new a13 labels/readout; no3D image synthesis or new motion')
    return cfg

def refresh_static():
    M.authorized();rec=M.read(RECORD);assets=M.read(O/'right-assets.json')
    cfg=bank_zero({r['sourceBeatId']:r for r in assets['assets']},rec['newStaticComposite']['sha256'])
    for path in [O/'paragraph-plan.json',O/'native-programs.json',O/'right-assets.json']:
        data=M.read(path)
        for row in data['paragraphs']:
            if row['targetParagraphId']=='v7-a13.L01':row['baseExactState']=cfg
        M.save(path,data)
    plan=M.read(M.PLAN)
    for scene in plan['scenes']:
        for row in scene['paragraphs']:
            if row['targetParagraphId']=='v7-a13.L01':row['baseExactState']=cfg
    plan['deicticStateCorrection']['newStaticComposite']=cfg;M.save(M.PLAN,plan)
    assets=M.read(O/'right-assets.json');assets['planSha256']=M.sha(M.PLAN);M.save(O/'right-assets.json',assets)
    rec['newStaticComposite']=cfg;M.save(RECORD,rec)
    print(json.dumps({'refreshedOneStatic':cfg['file'],'sha256':cfg['sha256']}))

def extend_a12():
    M.authorized();rec=M.read(RECORD);pid='v7-a12.L04';assert pid not in rec['changedParagraphIds']
    for path in [O/'paragraph-plan.json',O/'native-programs.json',O/'right-assets.json']:
        data=M.read(path)
        for row in data['paragraphs']:
            if row['targetParagraphId']==pid:row['basePairState']=copy.deepcopy(M.S.PAIR_BASE_STATES[pid])
        M.save(path,data)
    plan=M.read(M.PLAN)
    for scene in plan['scenes']:
        for row in scene['paragraphs']:
            if row['targetParagraphId']==pid:row['basePairState']=copy.deepcopy(M.S.PAIR_BASE_STATES[pid])
    plan['deicticStateCorrection']['changedParagraphIds'].append(pid);M.save(M.PLAN,plan)
    assets=M.read(O/'right-assets.json');assets['planSha256']=M.sha(M.PLAN);M.save(O/'right-assets.json',assets)
    rec['changedParagraphIds'].append(pid);rec['a12Reason']='A retains its completed current-bodyY yaw result while B is introduced/prepared to change fixed-uprightY heading.';M.save(RECORD,rec)
    print(json.dumps({'additionalMetadataOnlyParagraph':pid,'newMedia':False}))

def apply():
    M.authorized();assert not RECORD.exists(),'Preserve prior correction proof.'
    oldassets=M.read(O/'right-assets.json');by={r['sourceBeatId']:r for r in oldassets['assets']}
    archive=O/'timing-history'/('deictic-before-'+M.sha(O/'right-visual-segments.json')[:16]);archive.mkdir(parents=True,exist_ok=False)
    for p in [M.PLAN,O/'paragraph-plan.json',O/'native-programs.json',O/'right-assets.json',O/'right-visual-segments.json',O/'timing-preflight.json']:
        shutil.copy2(p,archive/p.name)
    bzero=bank_zero(by);paras=M.read(O/'paragraph-plan.json')
    changed=[]
    for row in paras['paragraphs']:
        pid=row['targetParagraphId']
        if pid in ['v7-a05.L04','v7-a12.L04']:
            if pid in M.S.PAIR_ACTIONS:row['pairActions']=copy.deepcopy(M.S.PAIR_ACTIONS[pid])
            row['basePairState']=copy.deepcopy(M.S.PAIR_BASE_STATES[pid]);changed.append(pid)
        elif pid=='v7-a11.L03':
            row['exactPairRecalls']=copy.deepcopy(M.S.EXACT_PAIR_RECALLS[pid]);changed.append(pid)
        elif pid=='v7-a13.L01':row['baseExactState']=bzero;changed.append(pid)
    M.save(O/'paragraph-plan.json',paras)
    programs=M.read(O/'native-programs.json');programs['paragraphs']=paras['paragraphs'];M.save(O/'native-programs.json',programs)
    oldassets['paragraphs']=paras['paragraphs'];plan=M.read(M.PLAN)
    for s in plan['scenes']:
        if s['targetScene']in['v7-a05','v7-a11','v7-a12','v7-a13']:
            s['paragraphs']=[r for r in paras['paragraphs']if r['targetScene']==s['targetScene']]
    plan['deicticStateCorrection']={'changedParagraphIds':changed,'reason':'Preserve completed A while the other model moves; show actual intermediate states during intermediate-state recap; bank0→35 changes only bank, holding h30/p20.',
        'nativeMoviesReRendered':0,'approvedPCMChanged':False,'newStaticComposite':bzero}
    M.save(M.PLAN,plan);oldassets['planSha256']=M.sha(M.PLAN);M.save(O/'right-assets.json',oldassets)
    M.save(RECORD,dict(status='metadata applied; timing verification pending',archive=M.rel(archive),changedParagraphIds=changed,
        all36PanelVideoHashesBefore={k:a['clipSha256']for k,a in by.items()if a.get('clipSha256')},newStaticComposite=bzero,
        newNative=False,newMotionMovie=False,approvedPCMChanged=False))
    print(json.dumps({'changedParagraphs':changed,'newNative':False,'static':bzero['file']},ensure_ascii=False))

def verify():
    rec=M.read(RECORD);old=M.read(ROOT/rec['archive']/'right-visual-segments.json');new=M.read(O/'right-visual-segments.json')
    def rows(data,sid):return [r for r in data['visualSegments']if r['sceneId']==sid]
    changed=[f'v7-a{i:02}'for i in range(1,22)if rows(old,f'v7-a{i:02}')!=rows(new,f'v7-a{i:02}')]
    assert changed==['v7-a05','v7-a11','v7-a12','v7-a13'],changed
    assets=M.read(O/'right-assets.json');now={r['sourceBeatId']:r['clipSha256']for r in assets['assets']if r.get('clipSha256')}
    assert now==rec['all36PanelVideoHashesBefore']
    assert new['bodyCoverageNoFrameGaps']and all(r['cueOffsetFrames']<=0 for r in new['actionSelectionAudit'])
    recall=next(r for r in new['exactStateRecallAudit']if r['paragraphId']=='v7-a11.L03')
    prior=[r for r in new['actionSelectionAudit']if r['paragraphId']=='v7-a11.L02'][-1]
    end=prior['actualStartFrame']+prior['sourceFrames'][1]-prior['sourceFrames'][0]+1
    assert end<=recall['frame']and recall['endFrameExclusive']==44005
    rec.pop('other18SceneSegmentArraysIdentical',None)
    rec.update(status='frozen; actual a05/a11/a12/a13 paired recomposition pending',changedSegmentScenes=changed,other17SceneSegmentArraysIdentical=True,
        all36PanelMoviesPreserved=True,intermediateRecall={'startFrame':recall['frame'],'endFrameExclusive':recall['endFrameExclusive'],'priorFullBEndFrameExclusive':end,'noDemonstrationTruncated':True},
        rightAssetsSha256=M.sha(O/'right-assets.json'),rightSegmentsSha256=M.sha(O/'right-visual-segments.json'),rightPlanSha256=M.sha(M.PLAN),
        bodyFrameGaps=0,sourceFrameOverflow=0,unexplainedPositiveCueDelays=0,actualPairedPixelReview='pending')
    M.save(RECORD,rec);print(json.dumps(rec,ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--verify',action='store_true');p.add_argument('--refresh-static',action='store_true');p.add_argument('--extend-a12',action='store_true');a=p.parse_args()
    if a.apply:apply()
    elif a.verify:verify()
    elif a.refresh_static:refresh_static()
    elif a.extend_a12:extend_a12()
    else:p.print_help()
