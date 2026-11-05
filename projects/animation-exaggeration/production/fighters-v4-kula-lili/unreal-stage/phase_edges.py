"""Sample the actual composited guide throughout discontinuous phase changes."""
import json,sys
from PIL import Image, ImageDraw
import numpy as np
from review_guides import QA,L,rd,extract,stroke_count
from compose import proj
def run(cid):
    pose=rd(L/'poses'/f'{cid}.json')
    bounds=[round(p['start']*60) for p in pose['phases'][1:]]
    if not bounds:return
    inds=sorted({f+d for f in bounds for d in (-3,-2,-1,0,1,2,3)})
    base=extract(L/f'{cid}-raw.mp4',inds);over=extract(L/f'{cid}.mp4',inds)
    result=[];sheet=Image.new('RGB',(7*224,len(bounds)*2*185),'#142025');draw=ImageDraw.Draw(sheet)
    for j,f0 in enumerate(bounds):
        for k,f in enumerate(range(f0-3,f0+4)):
            for n,side in enumerate(('left','right')):
                row=pose['evidence'][side][f];pt=proj(row['wrist'],side)
                x,y=np.rint(pt).astype(int)
                p_old=proj(pose['evidence'][side][f-1]['wrist'],side)
                ax,ay=np.rint(p_old).astype(int)
                count=stroke_count(base[f],over[f],x,y,side,'wrist')
                old_count=stroke_count(base[f],over[f],ax,ay,side,'wrist')
                x0,x1=(100,840) if side=='left' else (1020,1820)
                a=base[f][220:795,x0:x1].astype('int16');b=over[f][220:795,x0:x1].astype('int16')
                color=np.array((46,94,151) if side=='left' else (20,108,74))
                on=np.max(np.abs(b-color),axis=2)<36
                changed=np.max(np.abs(a-b),axis=2)>18
                result.append(dict(phaseStartFrame=f0,frame=f,side=side,expectedCurrentRingPixels=count,previousFrameRingPixels=old_count,
                   coloredGuidePixelsAcrossNativeFigure=int(np.sum(on&changed)),marksExpected=abs(f-f0)>2,
                   actualVsSettled=float(np.abs(base[f][230:705,x0:x1].astype(float)-base[f0+3][230:705,x0:x1].astype(float)).mean())))
                if side=='right':
                    fixed=(1375,410)
                    for view,pixels in enumerate([base[f],over[f]]):
                        rect=(fixed[0]-180,fixed[1]-125,fixed[0]+180,fixed[1]+125)
                        im=Image.fromarray(pixels).crop(rect).resize((224,156),Image.Resampling.LANCZOS)
                        xx=k*224;yy=(j*2+view)*185;sheet.paste(im,(xx,yy));draw.text((xx+5,yy+157),f'{side} {f} '+('native' if view==0 else 'guides'),fill='white')
    sheet.save(QA/f'{cid}-phase-edges.jpg',quality=94)
    (QA/f'{cid}-phase-edges.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(cid,[(r['frame'],r['side'],r['expectedCurrentRingPixels'],r['previousFrameRingPixels']) for r in result if r['frame']==r['phaseStartFrame']],flush=True)
if __name__=='__main__':
    for c in sys.argv[1:]:run(c)
