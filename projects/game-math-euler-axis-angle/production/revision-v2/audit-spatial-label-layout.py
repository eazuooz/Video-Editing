"""CPU-only current-anchor/bbox audit and clearly marked Pillow diagnostics.

No encoder, media extraction, Unity invocation or ASR is called. Existing final
stills provide layout context; masked old lettering is not a new renderer image.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,itertools,json,math,subprocess,sys
from PIL import Image,ImageDraw,ImageFont

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
LOCAL=HERE.parent/'local/revision-v2';QA=LOCAL/'qa';DIAG=QA/'label-layout-v3'
SOURCE=HERE/'render-spatial.py'
spec=importlib.util.spec_from_file_location('m04_label_layout',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
read=lambda p:json.loads(Path(p).read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
key=lambda v:(v['group'],v['axis'],v['text'])

def main():
    timeline=read(HERE/'timeline.json');placement=read(LOCAL/'unity-spatial-placement.json')['placements']
    rows=read(QA/'pixel-sample-index.json');pair=read(LOCAL/'pair-source.json')
    saved=read(ROOT/'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/baked-scene-provenance.json')
    for scene in saved['scenes']:assert sha(ROOT/scene['path'])==scene['sha256']
    reports=read(LOCAL/'spatial/spatial-render-report.json')['reports']
    clip_hashes={k:v for report in reports for k,v in report['sourceClipHashes'].items()}
    anchor_hashes={k:v for report in reports for k,v in report['anchorHashes'].items()}
    for path,digest in {**clip_hashes,**anchor_hashes}.items():assert sha(path)==digest,path
    layouts_by_slot={};states_by_slot={};previous={};summary={};jumps=[];max_leader=[]
    for slot in placement:
        if 'lineIndex' not in slot:continue
        sid=slot['sceneId'];states=[json.loads(s) for s in Path(slot['anchors']).read_text().splitlines()]
        pair_scene=sid in m.PAIRS;layouts=m.clip_label_layouts(states,pair_scene,previous.get(sid));previous[sid]=layouts[-1]
        layouts_by_slot[(sid,slot['lineIndex'])]=layouts;states_by_slot[(sid,slot['lineIndex'])]=states
        info=summary.setdefault(sid,dict(clips=0,states=0,omittedNames=0,boxCollisions=0,boundsFailures=0,identityChangesWithinClip=0))
        info['clips']+=1
        identities=[{key(v) for v in labels} for labels in layouts]
        info['identityChangesWithinClip']+=sum(a!=b for a,b in zip(identities,identities[1:]))
        for index,(state,labels) in enumerate(zip(states,layouts)):
            info['states']+=1
            expected={(g,k,axis) for g in (['a','b'] if pair_scene else ['a']) for k in ['world','body'] for axis in 'xyz'}
            cover={(v['group'],kind,v['axis']) for v in labels for kind in (['world','body'] if v['text'].startswith('world/body') else [v['kind']])}
            info['omittedNames']+=len(expected-cover)
            assert not(expected-cover),(sid,index,expected-cover)
            for a,b in itertools.combinations(labels,2):
                assert not m.boxes_overlap(a['bbox'],b['bbox']),(sid,index,a,b)
                # ASS rounds positions to whole pixels; retain a6px hard gap.
                assert not m.boxes_overlap(m.axis_label_box(a,round(a['x']),round(a['y'])),m.axis_label_box(b,round(b['x']),round(b['y'])),gap=6)
            for v in labels:
                box=v['bbox'];bound=v['plotBounds']
                assert box[0]>=bound[0]-1e-6 and box[1]>=bound[1]-1e-6 and box[2]<=bound[2]+1e-6 and box[3]<=bound[3]+1e-6
                max_leader.append(dict(scene=sid,line=slot['lineNumber'],frame=index,label=v['group']+'.'+v['text'],pixels=math.dist(v['target'],v['leaderEnd'])))
                if v['text'].startswith('world/body'):
                    anchors={a['name']:a for a in state['anchors']};g=v['group'];axis=v['axis']
                    world=('worldA' if g=='a' else 'worldB') if pair_scene else 'world'
                    body_dir=m.mathematical_direction(anchors[g+'.body'+axis.upper()],anchors[g+'.center'])
                    world_dir=m.mathematical_direction(anchors[world+'.'+axis],anchors[world+'.origin'])
                    assert m.positively_collinear(body_dir,world_dir)
            if index:
                old={key(v):v for v in layouts[index-1]}
                for v in labels:
                    z=old[key(v)];anchor=(v['target'][0]-z['target'][0],v['target'][1]-z['target'][1]);move=(v['x']-z['x'],v['y']-z['y'])
                    residual=math.hypot(move[0]-anchor[0],move[1]-anchor[1])
                    jumps.append(dict(scene=sid,line=slot['lineNumber'],frame=index,label=v['group']+'.'+v['text'],anchorMotion=math.hypot(*anchor),labelMotion=math.hypot(*move),layoutResidual=residual))
        assert not info['identityChangesWithinClip']
    # Current raw clip/anchor and saved scene hashes are checked above. This
    # report is tied to the current source pair; a new pair needs new pixel QA.
    old_code=subprocess.check_output(['git','show','HEAD:'+str(SOURCE.relative_to(ROOT)).replace('\\','/')],cwd=ROOT,text=True,encoding='utf8')
    old={'__file__':str(SOURCE),'__name__':'old_m04_labels'};exec(compile(old_code,str(SOURCE),'exec'),old)
    chosen=[325,424]
    for wanted in ('21 visual1','22 visual3','03 motion2 middle'):
        chosen.append(next(i+1 for i,row in enumerate(rows) if wanted in row['labels']))
    DIAG.mkdir(parents=True,exist_ok=True);diagnostics=[]
    for number in chosen:
        row=rows[number-1];scene=next(s for s in timeline['scenes'] if s['startFrame']<=row['frame']<s['endFrame'])
        sid=scene['id'];local_frame=row['frame']-scene['startFrame']
        slot=next(v for v in placement if v['sceneId']==sid and v['startFrame']<=local_frame<v['endFrame'])
        frame=min(local_frame-slot['startFrame'],slot['captureFrames']-1)
        state=states_by_slot[(sid,slot['lineIndex'])][frame];labels=layouts_by_slot[(sid,slot['lineIndex'])][frame]
        original=QA/f'frame-{number:04}.jpg';im=Image.open(original).convert('RGB');draw=ImageDraw.Draw(im)
        # Diagnostic only: old text ink is masked. Underlying geometry hidden
        # by old text cannot be recovered and is not claimed as freshly drawn.
        for label in old['label_candidates'](state,sid in m.PAIRS):
            box=m.axis_label_box(label);draw.rectangle((box[0]-5,box[1]-5,box[2]+5,box[3]+5),fill='white')
        if sid=='21':
            draw.rectangle((0,0,1920,219),fill='white');draw.rectangle((0,735,1920,1080),fill='white')
            def txt(text,x,y,size,bold=False):
                font=ImageFont.truetype(str(m.BOLD if bold else m.FONT),size)
                # libass supplies font fallback in production. Mirror the
                # canonical minus in this Pillow-only header diagnostic.
                fallback=ImageFont.truetype('C:/Windows/Fonts/seguisym.ttf',size)
                for line_number,line in enumerate(text.split('\n')):
                    cursor=x;baseline=y+font.getmetrics()[0]+line_number*(size+5)
                    for char in line:
                        face=fallback if char=='−' else font
                        draw.text((cursor,baseline),char,font=face,fill='#101810',anchor='ls')
                        cursor+=face.getlength(char)
            lesson=next(s for s in read(HERE/'lesson.json')['scenes'] if s['id']==sid)
            txt(m.TERM_TITLES.get(sid,lesson['title']),120,35,54,True)
            txt('world: 고정 축   /   body: 물체와 함께 도는 축',120,105,32)
            for text,x in zip(m.ROLES[sid],[160,1080]):txt(text,x,155,38,True)
            txt(m.FORMULAS[sid][slot['lineIndex']].replace('\n',' / '),120,750,48,True)
            txt(m.NOTES[sid][slot['lineIndex']],120,815,39)
            txt('진단용: 하단 고정 자막 영역은 보호 밴드 아래에 최종 합성',120,955,30)
        leader=Image.new('RGBA',im.size);ld=ImageDraw.Draw(leader)
        for label in labels:ld.line([label['target'],label['leaderEnd']],fill=(105,105,105,255),width=3)
        if sid in m.PAIRS:
            clipped=Image.new('RGBA',im.size);clipped.paste(leader.crop((60,220,1860,735)),(60,220));leader=clipped
        im=Image.alpha_composite(im.convert('RGBA'),leader).convert('RGB');draw=ImageDraw.Draw(im)
        for label in labels:
            color='#'+''.join([label['color'][4:6],label['color'][2:4],label['color'][0:2]])
            draw.text((label['x'],label['y']),label['text'],font=m.AXIS_LABEL_FONT,anchor='mm',fill=color,stroke_width=3,stroke_fill='white')
            draw.rectangle(label['bbox'],outline='#bdbdbd',width=1)
        font=ImageFont.truetype(str(m.FONT),20);draw.text((1500,1045),'CPU LAYOUT DIAGNOSTIC',font=font,fill='#7b258b')
        dest=DIAG/f'{sid}-sample-{number:04}-layout.png';im.save(dest)
        diagnostics.append(dict(scene=sid,sample=number,time=row['time'],stateFrame=frame,file=str(dest.relative_to(ROOT)).replace('\\','/'),sha256=sha(dest),original=str(original.relative_to(ROOT)).replace('\\','/'),method='Existing native still context; old text rectangles masked; proposed labels and measured boxes drawn by Pillow. Not a newly rendered geometry/final frame.'))
    top=sorted(jumps,key=lambda v:v['layoutResidual'],reverse=True)
    report=dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),scope='CPU full current finite motion and actual Pillow bbox audit; diagnostic pixel viewing recorded separately',sourceSha256=sha(SOURCE),captionedBaseline=pair['outputs']['captioned'],clipsChecked=len(clip_hashes),anchorFilesChecked=len(anchor_hashes),statesChecked=sum(v['states'] for v in summary.values()),savedSceneHashesPreserved=12,sourceClipAndAnchorHashesPreserved=True,affectedScenes=sorted(summary),scenes=summary,labelMotion=dict(maxResidualPixels=top[0]['layoutResidual'],over20Pixels=sum(v['layoutResidual']>20 for v in top),topResiduals=top[:12],meaning='Residual is label displacement minus actual screen-anchor displacement. Remaining residuals are continuous boundary clamping, not lane changes. Cue/reset transitions excluded; constant semantic label identities within every finite clip.'),longestLeaders=sorted(max_leader,key=lambda v:v['pixels'],reverse=True)[:8],geometryProtection=dict(scene='21',headerBand=[0,0,1920,220],workedExplanationAndCaptionBand=[0,735,1920,1080],leaderClip=[60,220,1860,735],geometryChanged=False),diagnostics=diagnostics,diagnosticsDirectlyViewed='pending',newUnityCapture=False,videoRenderStarted=False,audioOrTimingChanged=False,finalMovingAndPixelQA='pending new composed final pair; baseline approval is not reused for changed label pixels')
    out=HERE/'label-layout-review.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(report=str(out),states=report['statesChecked'],clips=report['clipsChecked'],diagnostics=[d['file'] for d in diagnostics],maxResidual=top[0]['layoutResidual'],over20=report['labelMotion']['over20Pixels']),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
