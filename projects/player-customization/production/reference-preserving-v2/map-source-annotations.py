"""Map inspected native marks into the measured cut, never invent tracking."""
from pathlib import Path
import json,hashlib,math
from PIL import ImageFont
from audio_pipeline import require_authorized
from video_pipeline import annotations

R=Path(__file__).resolve().parents[4]
H=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def sample(keys,time,shape):
    for a,b in zip(keys,keys[1:]):
        if a['time']-1e-7<=time<=b['time']+1e-7:
            u=(time-a['time'])/(b['time']-a['time'])
            field='rect' if shape in ('rect','circle') else 'path'
            if field=='rect':return [x+(y-x)*u for x,y in zip(a[field],b[field])]
            return [[x+(y-x)*u for x,y in zip(p,q)] for p,q in zip(a[field],b[field])]
    raise ValueError('Requested native tracking outside its inspected keyframes')

def main():
    require_authorized('map-inspected-source-annotations')
    source=read(H/'source-space-annotations.json')
    plan=read(H/'edit-plan.json')
    caption_path=R/'projects/player-customization/production/local/reference-preserving-v2/edit/caption-layout.json'
    captions=read(caption_path)
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',42)
    mapped=[]
    for cut in plan['cuts']:
        if cut['kind']!='independent-gameplay':continue
        assert cut.get('sourceCrop') is None,'New crop requires a reviewed coordinate conversion'
        x,y,w,h=cut['viewport']
        scale=min(w/1920,h/1080)
        dx,dy=x+(w-1920*scale)/2,y+(h-1080*scale)/2
        cut['marks']=[]
        for native in source['marks']:
            if native['sourceSha256']!=cut['sourceSha256']:continue
            lo=max(native['localStart'],cut['sourceStart'])
            hi=min(native['localEnd'],cut['sourceStart']+cut['frames']/60)
            if native['id']=='acvi-qb-energy':
                cue=next(row for row in captions['rows'] if row['paragraph']=='03-p02' and row['ko'].startswith('순간적으로'))
                lo=max(lo,cut['sourceStart']+cue['start']-cut['startFrame']/60)
                hi=min(hi,cut['sourceStart']+cue['end']-cut['startFrame']/60)
            if hi-lo<.2:continue
            shape=native['type']
            times=sorted({lo,hi,*[k['time'] for k in native['keyframes'] if lo<k['time']<hi]})
            frames=[]
            for time in times:
                geometry=sample(native['keyframes'],time,shape)
                row=dict(t=time-cut['sourceStart'])
                if shape in ('rect','circle'):
                    row.update(x=dx+geometry[0]*scale,y=dy+geometry[1]*scale,w=geometry[2]*scale,h=geometry[3]*scale)
                else:row['points']=[[dx+px*scale,dy+py*scale] for px,py in geometry]
                frames.append(row)
            label={'acvi-boost-speed':'속도 표시 306 → 320',
                   'acvi-qb-energy':'퀵부스트 소비 480 → 560'}.get(native['id'],native['label'])
            # Anchors are label centres in native pixels; the ASS API takes
            # top-left. Clamp only the label into the existing clear image area.
            lx=dx+native['labelAnchorSource'][0]*scale-font.getlength(label)/2
            ly=dy+native['labelAnchorSource'][1]*scale-25
            lx=max(18,min(1902-font.getlength(label),lx))
            ly=max(72,min(820,ly))
            mark=dict(id=native['id'],shape=shape,t0=lo-cut['sourceStart'],t1=hi-cut['sourceStart'],color=native['colorSemantics']['token'],thickness=max(8,native['nativeLineWidth']*scale),label=label,labelPosition=[round(lx,2),round(ly,2)],fontSize=42,keyframes=frames,revealSeconds=.3,sourceSpaceEvidenceId=native['id'],meaning=native['semanticPurpose'],detectorOutput=False)
            cut['marks'].append(mark)
            mapped.append(dict(cutId=cut['id'],sourceSha256=cut['sourceSha256'],sourceStartSeconds=cut['sourceStart'],cutFrames=cut['frames'],viewport=cut['viewport'],mark=mark))
        # Check EVERY interpolated output-frame bound, labels and caption area.
        annotations(cut,plan)
    plan['annotationSource']='projects/player-customization/production/reference-preserving-v2/source-annotations.json'
    plan['annotationsReview']='Mapped from inspected native keyframes; all-frame geometry/caption bounds passed; actual encoded moving/mobile pixels pending'
    result=dict(slug='player-customization',revision='reference-preserving-v2',nativeSourcePlan=dict(path=(H/'source-space-annotations.json').relative_to(R).as_posix(),sha256=sha(H/'source-space-annotations.json')),sourceSelectionMetaRebinding='Native source bytes, dimensions and LOCAL keyframes unchanged after bank/role corrections; input source-selection identity preserved in native record.',speechCueBinding=dict(path=caption_path.relative_to(R).as_posix(),sha256=sha(caption_path),change='Energy mark starts with the actual energy clause,0.6967s later than the original native-window onset; geometry unchanged.'),annotations=mapped,movingOutputReviewed=False,humanWholeListening='pending')
    (H/'source-annotations.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (H/'edit-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Mapped',len(mapped),'inspected marks; actual encoded moving review remains pending')

if __name__=='__main__':main()
