"""Dense current rendered pixels around narrated motion; no automatic approval."""
from pathlib import Path
import argparse, hashlib, json, math, re
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('slug',choices=['game-math-polygon-centers-v2','game-math-polygon-partition-v2']);p.add_argument('--final',action='store_true');p.add_argument('--scenes',help='Comma-separated current scenes; write a separate index without approving them');a=p.parse_args()
P=ROOT/'projects'/a.slug;m=json.loads((P/'project.json').read_text(encoding='utf8'));t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
D=ROOT/'shared/output'/a.slug/('final-detail-review' if a.final else 'clip-detail-review');D.mkdir(parents=True,exist_ok=True)
cv2.setNumThreads(1);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16);records=[]
def seconds(s):
    h,mi,z=s.split(':');return int(h)*3600+int(mi)*60+float(z)
for slot in t['scenes']:
    if a.scenes and slot['id'] not in set(a.scenes.split(',')):continue
    ident=slot['id'];times=[]
    if slot['classification']=='explanation' and not slot['preservedOriginal']:
        times=[.3,*range(2,math.ceil(slot['seconds']),2),slot['seconds']-.12]
        for c in slot.get('sentenceCues',[]):times.extend([c['start']+.25,c['start']+1.3])
        if ident=='PB08':times.extend([.5,slot['lineStarts'][1]-.1,*[slot['lineStarts'][1]+x for x in [.5,1,1.5,2,2.5]]])
    elif slot['classification']=='actual':
        ass=ROOT/'shared/output'/a.slug/f'overlays/{ident}.ass'
        observed=[];runs=[]
        for line in ass.read_text(encoding='utf8').splitlines():
            if not line.startswith('Dialogue:') or ',Shape,' not in line:continue
            if not any(c in line.lower() for c in ['\\c&h5053ef&','\\c&hf5a542&','\\c&hb8c626&']):continue
            parts=line.split(',',9);a0,a1=seconds(parts[1]),seconds(parts[2]);observed.extend([a0,a1]);runs.append((a0,a1))
        if observed:
            merged=[]
            for lo,hi in sorted(runs):
                if merged and lo<=merged[-1][1]+.04:merged[-1][1]=max(hi,merged[-1][1])
                else:merged.append([lo,hi])
            runs=merged
            # Sample the complete observed run, including the hide boundary.
            # Native full playback covers all motion. Dense pixels inspect each
            # visible tracked run at4Hz plus every reveal/hide boundary; avoid
            # wasting twelve samples/sec on the intervening unannotated gap.
            times=[.1,*range(2,math.ceil(slot['seconds']),2),slot['seconds']-.12]
            grid={round(lo*4)/4+i/4 for lo,hi in runs for i in range(math.ceil((hi-lo)*4)+1)}
            times.extend(grid)
            for lo,hi in runs:
                times.extend([max(0,lo-.08),min(slot['seconds']-.02,hi+.08)])
    if not times:continue
    times=sorted({round(x,5) for x in times if 0<=x<slot['seconds']-.01})
    src=ROOT/m['paths']['videoBurnedCaptions'] if a.final else ROOT/f'shared/output/{a.slug}/clips/{ident}.mp4'
    cap=cv2.VideoCapture(str(src));fps=cap.get(cv2.CAP_PROP_FPS);assert abs(fps-60)<1e-4
    pictures=[]
    for local in times:
        at=slot['start']+local if a.final else local;frame=round(at*60);cap.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,img=cap.read();assert ok,(ident,local,at)
        pictures.append((local,at,Image.fromarray(cv2.cvtColor(cv2.resize(img,(800,450)),cv2.COLOR_BGR2RGB))))
    cap.release();pages=[]
    for page in range(math.ceil(len(pictures)/6)):
        sheet=Image.new('RGB',(1600,1410),'white');draw=ImageDraw.Draw(sheet)
        for cell,(local,at,im) in enumerate(pictures[page*6:page*6+6]):
            x=cell%2*800;y=cell//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{ident} local{local:.3f}s final{slot["start"]+local:.3f}s',font=font,fill='black')
        file=D/f'{ident}-{page+1:02}.jpg';sheet.save(file,quality=95);pages.append(file.relative_to(ROOT).as_posix())
    records.append({'scene':ident,'source':src.relative_to(ROOT).as_posix(),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'localTimes':times,'pages':pages,'directReviewPassed':False})
    print('Dense current pixels',ident,len(pages),flush=True)
index_name='index-selected-'+a.scenes.replace(',','-')+'.json' if a.scenes else 'index.json'
(D/index_name).write_text(json.dumps({'mode':'final narration/captions' if a.final else 'current rendered clips','records':records,'automaticApproval':False,'imagesLocalOnly':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
