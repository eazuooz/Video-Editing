"""Inspect actual shoulder/wrist regions at both end poses, not only metadata."""
from pathlib import Path
import json,hashlib,subprocess,io,sys,math
import numpy as np
from PIL import Image, ImageDraw
from compose import H,L,R,proj
def frame(path,t):
    raw=subprocess.check_output(['ffmpeg','-v','error','-ss',f'{t:.5f}','-i',str(path),'-frames:v','1','-vf','format=rgb24','-f','image2pipe','-vcodec','png','-threads','1','-'])
    return Image.open(io.BytesIO(raw)).convert('RGB')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def check(cids):
    figs=[];summary=[]
    for cid in cids:
        pose=json.loads((L/'poses'/f'{cid}.json').read_text(encoding='utf-8'));cap=json.loads((L/f'{cid}-capture.json').read_text(encoding='utf-8'))
        movie=R/cap['movie'];assert sha(movie)==cap['movieSha256']
        # Validate the rendered mesh moves beneath the guides, using raw frames with no ASS.
        raw=L/f'{cid}-raw.mp4';native=R/cap['nativePixels']['path'];assert sha(raw)==cap['nativePixels']['sha256']
        intervals=[]
        for cue in pose['phases']:
            first=round(cue['start']*60);last=next(i for i in range(first,pose['frames']) if pose['evidence']['left'][i]['progress']>=.9999 and pose['evidence']['left'][i]['phase']==cue['phase'])
            a=frame(raw,first/60);b=frame(raw,last/60)
            lefts=[]
            for side in ['left','right']:
                p=proj(pose['evidence'][side][last]['wrist'],side)
                box=(int(p[0]-62),int(p[1]-60),int(p[0]+62),int(p[1]+60))
                assert 0<box[0]<box[2]<1920 and 120<box[1]<box[3]<885,(cid,box)
                diff=np.abs(np.asarray(a.crop(box),dtype=float)-np.asarray(b.crop(box),dtype=float)).mean(axis=2)
                frac=float(np.mean(diff>12));assert frac>.012,(cid,side,last,box,frac)
                lefts.append(round(frac,4))
            intervals.append({'phase':cue['phase'],'firstFrame':first,'peakFrame':last,'nativeChangedFractionNearPeakWrist':lefts})
        cue=intervals[-1]
        for index in [cue['firstFrame'],cue['peakFrame']]:
            im=frame(movie,index/60);im.thumbnail((640,360));figs.append((cid,index,im))
        summary.append({'id':cid,'frameCount':pose['frames'],'mp4Sha256':cap['movieSha256'],'sampledIntervals':intervals,'nativeReceipt':str((L/f'{cid}-capture.json').relative_to(R))})
    qa=L/'qa';qa.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1280,385*len(cids)),'#111713');d=ImageDraw.Draw(sheet)
    for i,(cid,k,im) in enumerate(figs):
        x=i%2*640;y=i//2*385;sheet.paste(im,(x,y));d.text((x+12,y+360),f'{cid}    frame {k}',fill='white')
    sheet.save(qa/('poses-'+str(len(cids))+'.jpg'),quality=91)
    if len(cids)==6:(H/'encoded-motion-evidence.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print('Actual frame comparisons:',len(summary))
if __name__=='__main__':check(sys.argv[1:] or ['A02-E004','A02-E005','A02-E011','A02-E013','A02-E014','A02-E015'])
