"""Pixel QA for the two actual native mannequin renders and their composited guides.

The masks identify the sample mannequin's orange material only. Distances are
QA diagnostics for our own overlay registration, never game/CV measurements.
"""
from pathlib import Path
import json, hashlib, subprocess, sys
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image, ImageDraw, ImageFont
from compose import H,L,proj

QA=L/'qa'; QA.mkdir(parents=True,exist_ok=True)
IDS=['A02-E005','A02-E004','A02-E011','A02-E013','A02-E014','A02-E015']
FONT=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',18)
def rd(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def extract(p,numbers):
    expected=sorted(set(numbers))
    expr='select='+'+'.join(f'eq(n\\,{n})' for n in expected)
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-vf',expr,'-fps_mode','passthrough',
                                  '-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'])
    frames=np.frombuffer(data,np.uint8).reshape(-1,1080,1920,3)
    assert len(frames)==len(expected)
    return {n:frames[i] for i,n in enumerate(expected)}
def orange_mask(pixels):
    rgb=pixels.astype('int16')
    return (rgb[:,:,0]-rgb[:,:,1]>13)&(rgb[:,:,1]-rgb[:,:,2]>9)
def bounds(mask,x0,x1):
    yy,xx=np.nonzero(mask[130:890,x0:x1]);assert len(xx)>200
    return [int(xx.min())+x0,int(yy.min())+130,int(xx.max())+x0,int(yy.max())+130]
def outside_distance(mask,x,y):
    crop=mask[y-60:y+61,x-60:x+61]
    return float(distance_transform_edt(~crop)[60,60])
def stroke_count(raw,over,x,y,side,joint):
    ref=np.array((46,94,151) if side=='left' else (20,108,74))
    a=raw[y-22:y+23,x-22:x+23].astype('int16');b=over[y-22:y+23,x-22:x+23].astype('int16')
    yy,xx=np.indices(a.shape[:2]);xx-=22;yy-=22;r2=xx*xx+yy*yy
    area=((r2>=9**2)&(r2<=17**2)) if joint=='wrist' else (((np.abs(xx)<=3)&(np.abs(yy)<=13))|((np.abs(yy)<=3)&(np.abs(xx)<=13)))
    colored=(np.max(np.abs(b-ref),axis=2)<53)&(np.max(np.abs(a-b),axis=2)>19)
    return int((area&colored).sum())
def review(cid):
    pose=rd(L/'poses'/f'{cid}.json');rec=rd(L/f'{cid}-capture.json')
    frames=pose['frames'];trials=[];numbers=[]
    for cue in pose['phases']:
        first=round(cue['start']*60)
        peak=next(r['frame'] for r in pose['evidence']['left'] if r['frame']>=first and r['phase']==cue['phase'] and r['progress']>=.9999)
        trials.append((cue['phase'],first,peak));numbers.extend((first,(first+peak)//2,peak))
    raw=extract(L/f'{cid}-raw.mp4',numbers);annot=extract(L/f'{cid}.mp4',numbers)
    closeups=Image.new('RGB',(1504,len(trials)*3*242),'#142025')
    titles=ImageDraw.Draw(closeups)
    contact=Image.new('RGB',(1125,len(trials)*238),'#142025');mobile=ImageDraw.Draw(contact)
    rows=[]
    for phaseindex,(phase,first,peak) in enumerate(trials):
        stage=[]
        for j,f in enumerate((first,(first+peak)//2,peak)):
            base=raw[f];over=annot[f];mask=orange_mask(base)
            im=Image.fromarray(over)
            thumb=im.resize((375,211),Image.Resampling.LANCZOS)
            contact.paste(thumb,(j*375,phaseindex*238))
            mobile.text((j*375+6,phaseindex*238+212),f'{cid[-4:]}  phase {phase}  f{f}',fill='white',font=FONT)
            y=(phaseindex*3+j)*242;targets={}
            for k,side in enumerate(('left','right')):
                s=pose['evidence'][side][f]
                # Final ASS uses one pose per decoded frame and intentionally
                # clears the marks around a native pose discontinuity.
                guide=pose['evidence'][side][f]
                side_bounds=bounds(mask,50 if k==0 else 1000,920 if k==0 else 1860)
                metrics={}
                for q,joint in enumerate(('shoulder','wrist')):
                    x,yy=np.rint(proj(guide[joint],side)).astype(int)
                    x=int(x);yy=int(yy)
                    dist=outside_distance(mask,x,yy)
                    pixels=stroke_count(base,over,x,yy,side,joint)
                    metrics[joint]={'guideXY':[x,yy],'orangeSurfaceDistancePx':round(dist,2),'matchingStrokePixels':pixels}
                targets[side]={'meshBBox':[int(a) for a in side_bounds],'joints':metrics,'motionProgress':s['progress'],
                  'marksExpected':not any(abs(f-round(c['start']*60))<=2 for c in pose['phases'][1:])}
                center=np.mean([metrics[z]['guideXY'] for z in ('shoulder','wrist')],axis=0)
                cx,cy=np.rint(center).astype(int);box=(cx-175,cy-101,cx+175,cy+101)
                for l,image in enumerate((Image.fromarray(base),im)):
                    crop=image.crop(box);xx=k*752+l*376;closeups.paste(crop,(xx,y))
                    titles.text((xx+4,y+203),f'{side} {"native" if l==0 else "guides"} · {phase}/{f}',fill='white',font=FONT)
            assert targets['left']['motionProgress']==targets['right']['motionProgress']
            stage.append({'frame':f,'sides':targets})
        rows.append({'phase':phase,'first':first,'peak':peak,'sampledFrames':stage})
    closeups.save(QA/f'{cid}-joint-targets.jpg',quality=94)
    contact.save(QA/f'{cid}-mobile.jpg',quality=92)
    result={'id':cid,'fileSha256':sha(L/f'{cid}.mp4'),'frames':frames,'facts':rows,
       'note':'Native orange surface distance only tests mesh proximity; shoulder/wrist identity is checked separately on the native-vs-guide crop.',
       'equalRigScale':pose['animations'][0]['tracks']['root']['s']==pose['animations'][1]['tracks']['root']['s'] if 'root' in pose['animations'][0]['tracks'] else None,
       'samePlaybackClock':'Both poses keyed at the same measured progress on these frames.',
       'humanFinalReview':False}
    assert result['fileSha256']==rec['movieSha256']
    (QA/f'{cid}-joint-targets.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(cid,'QA collected',len(numbers),'samples',flush=True)
if __name__=='__main__':
    for c in sys.argv[1:] or IDS:review(c)
