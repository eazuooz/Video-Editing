"""Map current inspected native marks into measured D21 v3 cuts.

    python map-source-annotations.py --dry-run
    python map-source-annotations.py --prepare

Input source-space-annotations.json retains the v2 marks schema and a current
sourceSelection:{path,sha256}. Each sourceKey/SHA must match current independent
selected gameplay. Optional speechCue:{scene,paragraph,koStartsWith} binds the
mark to one uniquely matching current caption cue (whitespace normalized).
Without speechCue, only the actually inspected native window is used. Every
mark is clipped to its own cut, never extrapolated, then passed through the
existing video_pipeline.annotations() all-frame geometry/protected-area check.
No decode, media extraction, render, TTS, ASR, browser or Git stage runs here.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import uuid

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
LOCAL=HERE.parents[1]/'production/local/reference-preserving-v3'
SOURCE=HERE/'source-space-annotations.json'
SELECTION=HERE/'source-selection.json'
TITLES=HERE/'title-selection.json'
PLAN=HERE/'edit-plan.json'
CAPTIONS=LOCAL/'edit/caption-layout.json'
OUTPUT=HERE/'source-annotations.json'
GAMES={'Splatoon Raiders','Animal Crossing: New Horizons','The Legend of Zelda: Breath of the Wild'}

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def rel(p): return p.resolve().relative_to(ROOT.resolve()).as_posix()
def scoped(value):
    p=Path(value);p=(p if p.is_absolute() else ROOT/p).resolve()
    p.relative_to(ROOT.resolve());return p
def receipt(p): return dict(path=rel(p),sha256=sha(p),bytes=p.stat().st_size)
def require(ok,message):
    if not ok: raise ValueError(message)
def norm(text): return re.sub(r'\s+',' ',str(text)).strip()

def sample(keys,time,shape):
    require(len(keys)>=2 and keys[0]['time']-1e-7<=time<=keys[-1]['time']+1e-7,
            'Requested tracking exceeds inspected keyframes; no extrapolation')
    for left,right in zip(keys,keys[1:]):
        if left['time']-1e-7<=time<=right['time']+1e-7:
            amount=(time-left['time'])/(right['time']-left['time'])
            field='rect' if shape in ('rect','circle') else 'path'
            if field=='rect': return [a+(b-a)*amount for a,b in zip(left[field],right[field])]
            require(len(left[field])==len(right[field])>=2,'Inspected paths need equal point counts')
            return [[a+(b-a)*amount for a,b in zip(p,q)] for p,q in zip(left[field],right[field])]
    raise ValueError('No inspected native interval spans requested time')

def speech_window(binding,rows):
    scene=str(binding['scene']).zfill(2)
    paragraph=binding['paragraph']
    if isinstance(paragraph,int): pid=f'{scene}-p{paragraph:02d}'
    elif re.fullmatch(r'\d+',str(paragraph)): pid=f'{scene}-p{int(paragraph):02d}'
    else: pid=str(paragraph)
    prefix=norm(binding['koStartsWith'])
    require(prefix,'speechCue.koStartsWith must identify an actual clause')
    matches=[row for row in rows if str(row['scene']).zfill(2)==scene
             and row['paragraph']==pid and norm(row['ko']).startswith(prefix)]
    require(len(matches)==1,f'speechCue must match exactly one current KO cue: {binding}')
    row=matches[0]
    return float(row['start']),float(row['end']),dict(cue=row.get('cue'),paragraph=pid,
            scene=scene,koStartsWith=prefix,start=row['start'],end=row['end'])

def shifted_intervals(intervals,cut_start,lo,hi):
    result=[]
    for a,b in intervals:
        a,b=max(float(a),lo),min(float(b),hi)
        if a<b: result.append([a-cut_start,b-cut_start])
    return result

def build():
    # Defer project dependencies until after --help so help has no media/data
    #or optional-package requirements. Imports themselves perform no jobs.
    from PIL import ImageFont
    from audio_pipeline import require_authorized
    from video_pipeline import annotations
    auth=require_authorized('map-current-inspected-source-annotations')
    approval=read(HERE/'authorization.json')
    require(set(approval.get('selectedGameTitles',[]))==GAMES,'Exact current titles required')
    selected,native,plan=read(SELECTION),read(SOURCE),copy.deepcopy(read(PLAN))
    require((native.get('slug'),native.get('revision'))==('player-customization',HERE.name),'Wrong native annotation revision')
    require((plan.get('slug'),plan.get('revision'))==('player-customization',HERE.name),'Wrong measured edit revision')
    require(plan.get('fps')==60 and (plan.get('width'),plan.get('height'))==(1920,1080),'Measured FHD60 plan required')
    require(native.get('sourceSelection',{}).get('sha256')==sha(SELECTION),'Native source-selection hash is stale')
    require(scoped(native['sourceSelection']['path'])==SELECTION.resolve(),'Wrong native source-selection path')
    require(set(read(TITLES).get('selectedTitles',[]))==GAMES,'Current title selection changed')
    require(selected.get('referenceOnlyMediaExcluded') is True,'Reference media must stay excluded')
    sources={s['key']:s for s in selected['sources']}
    require(len(sources)==len(selected['sources']),'Duplicate selected source key')
    marks=native['marks'];require(len({m['id'] for m in marks})==len(marks),'Native mark IDs must be unique')
    need_captions=any(mark.get('speechCue') for mark in marks)
    captions=read(CAPTIONS) if need_captions else None
    inputs=[receipt(SOURCE),receipt(SELECTION),receipt(TITLES),receipt(PLAN),receipt(Path(__file__)),
            receipt(HERE/'video_pipeline.py')]
    if captions: inputs.append(receipt(CAPTIONS))
    for mark in marks:
        source=sources[mark['sourceKey']]
        require(source.get('game') in GAMES and source.get('sourceRole')=='independent-gameplay'
                and source.get('referenceLesson') is False,'Native mark must reference current independent gameplay')
        require(mark['sourceSha256']==source['media']['sha256'],'Native mark source bytes differ')
        n=source['nativeSource'];require(n.get('minimum1080Passed') is True,'NativeFHD evidence missing')
        if mark.get('sourceFile'): require(scoped(mark['sourceFile'])==scoped(source['media']['path']),'Mark source path changed')
        require(mark.get('filled',False) is False,'Marks must preserve the explained detail')
        require(mark.get('evidenceFrames') or mark.get('reviewEvidence'),'Actual native-frame evidence required')
        keys=mark['keyframes'];require(len(keys)>=2 and all(a['time']<b['time'] for a,b in zip(keys,keys[1:])),'Strict inspected keyframes required')
        require(keys[0]['time']<=mark['localStart'] and keys[-1]['time']>=mark['localEnd'],'Native window exceeds inspected keyframes')
        require(mark['localStart']<mark['localEnd'],'Nonpositive native window')
    mapped=[];checks=[];bindings=[]
    for cut in plan['cuts']:
        if cut['kind']!='independent-gameplay': continue
        require(cut.get('sourceCrop') is None,'New crop requires a reviewed coordinate conversion')
        source=sources[cut['source']]
        require(source['media']['sha256']==cut['sourceSha256'],'Cut no longer identifies selected bytes')
        nw,nh=source['nativeSource']['decodedDimensions']
        require(nw>=1920 and nh>=1080,'NativeFHD coordinates required')
        x,y,w,h=cut['viewport'];scale=min(w/nw,h/nh)
        dx,dy=x+(w-nw*scale)/2,y+(h-nh*scale)/2
        cut_start=float(cut['sourceStart']);cut_end=cut_start+cut['frames']/60
        cut['marks']=[]
        for mark in marks:
            if mark['sourceKey']!=cut['source'] or mark['sourceSha256']!=cut['sourceSha256']: continue
            if mark.get('sourceDimensions'): require(mark['sourceDimensions']==[nw,nh],'Source coordinate dimensions changed')
            elif native.get('coordinateSystem',{}).get('dimensions'):
                require(native['coordinateSystem']['dimensions']==[nw,nh],'Global native coordinates differ from source')
            lo,hi=max(float(mark['localStart']),cut_start),min(float(mark['localEnd']),cut_end)
            bound=None
            if mark.get('speechCue'):
                begin,end,bound=speech_window(mark['speechCue'],captions['rows'])
                lo=max(lo,cut_start+begin-cut['startFrame']/60)
                hi=min(hi,cut_start+end-cut['startFrame']/60)
            if hi-lo<.2: continue
            shape='rect' if mark['type']=='rectangle' else mark['type']
            require(shape in ('rect','circle','path','arrow'),'Unsupported native editorial shape')
            times=sorted({lo,hi,*[key['time'] for key in mark['keyframes'] if lo<key['time']<hi]})
            frames=[]
            for time in times:
                geometry=sample(mark['keyframes'],time,shape);row=dict(t=time-cut_start)
                if shape in ('rect','circle'):
                    require(len(geometry)==4 and all(math.isfinite(v) for v in geometry)
                            and geometry[2]>0 and geometry[3]>0,'Invalid native rectangle')
                    row.update(x=dx+geometry[0]*scale,y=dy+geometry[1]*scale,w=geometry[2]*scale,h=geometry[3]*scale)
                else:
                    require(all(len(point)==2 and all(math.isfinite(v) for v in point)
                                for point in geometry),'Invalid native path coordinates')
                    row['points']=[[dx+px*scale,dy+py*scale] for px,py in geometry]
                frames.append(row)
            label=mark['label'];size=int(mark.get('fontSize',42))
            font_name=plan.get('annotationFontFile','C:/Windows/Fonts/malgun.ttf')
            font_path=Path(font_name) if Path(font_name).is_absolute() else scoped(font_name)
            font=ImageFont.truetype(str(font_path),size)
            lx=dx+mark['labelAnchorSource'][0]*scale-font.getlength(label)/2
            ly=dy+mark['labelAnchorSource'][1]*scale-size*.6
            require(math.isfinite(lx) and math.isfinite(ly),'Invalid native label anchor')
            lx=max(18,min(1902-font.getlength(label),lx));ly=max(72,min(820,ly))
            result=dict(id=mark['id'],shape=shape,t0=lo-cut_start,t1=hi-cut_start,
                color=mark['colorSemantics']['token'],thickness=max(8,mark['nativeLineWidth']*scale),
                label=label,labelPosition=[round(lx,2),round(ly,2)],fontSize=size,keyframes=frames,
                revealSeconds=float(mark.get('revealSeconds',.3)),sourceSpaceEvidenceId=mark['id'],
                meaning=mark['semanticPurpose'],detectorOutput=False)
            for name in ('hiddenIntervals','visibleIntervals'):
                if name in mark: result[name]=shifted_intervals(mark[name],cut_start,lo,hi)
            if mark.get('visibleIntervals') and not result.get('visibleIntervals'): continue
            cut['marks'].append(result)
            if bound: bindings.append(dict(markId=mark['id'],cutId=cut['id'],**bound))
            mapped.append(dict(cutId=cut['id'],sourceSha256=cut['sourceSha256'],
                sourceStartSeconds=cut_start,cutFrames=cut['frames'],viewport=cut['viewport'],mark=result))
        # The established renderer checks EVERY visible interpolated frame,
        #the actual label font, credits, caption area and protected UI regions.
        _,geometry=annotations(cut,plan);checks.append(dict(cutId=cut['id'],**geometry))
    plan['annotationSource']=rel(OUTPUT)
    plan['annotationsReview']='Current inspected native marks mapped; all-frame geometry/protection passed; actual encoded moving/mobile pixel review pending'
    result=dict(slug='player-customization',revision=HERE.name,inputs=inputs,authorization=auth,
        nativeSourcePlan=receipt(SOURCE),sourceSelection=receipt(SELECTION),titleSelection=receipt(TITLES),
        speechCueBinding=(dict(input=receipt(CAPTIONS),bindings=bindings) if captions else
                          dict(input=None,bindings=[],meaning='Native reviewed windows only; no speech cue fabricated')),
        annotations=mapped,allFrameGeometryChecks=checks,allFrameGeometryPassed=True,
        allEndTimesExclusive=True,noExtrapolation=True,clearAtEverySourceCut=True,
        movingOutputReviewed=False,humanWholeListening='pending')
    return plan,result

def write_atomic(path,value):
    temp=path.with_name('.'+path.name+'-'+uuid.uuid4().hex+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(path)

def main():
    parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run',action='store_true',help='Validate mapping/all-frame geometry without writing')
    mode.add_argument('--prepare',action='store_true',help='Write current mapped annotations and marks in current edit-plan')
    args=parser.parse_args()
    try:
        plan,result=build()
        if args.prepare:
            from audio_pipeline import require_authorized
            latest=require_authorized('write-current-inspected-source-annotations')
            require(latest['authorizationSha256']==result['authorization']['authorizationSha256'],'Authorization changed')
            for item in result['inputs']: require(sha(scoped(item['path']))==item['sha256'],'Annotation input changed before writing')
            write_atomic(OUTPUT,result);write_atomic(PLAN,plan)
        print(json.dumps(dict(status='prepared' if args.prepare else 'dry-run; no writes',
            mappedMarks=len(result['annotations']),allFrameGeometryPassed=True,
            actualMovingMobilePixelReview='pending'),ensure_ascii=False,indent=2))
    except (ValueError,KeyError,OSError) as exc: parser.exit(2,f'Current annotation mapping stopped: {exc}\n')

if __name__=='__main__': main()
