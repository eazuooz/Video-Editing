"""Make direct-review sheets from actual normal-speed source and rendered cuts."""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
WORK = Path(__file__).parent / 'final-v2'
PROOF = WORK / 'source-proof'
FONT = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 16)

def frame(file, seconds):
    result = subprocess.run(['ffmpeg','-v','error','-ss',str(seconds),'-i',str(ROOT/file),'-frames:v','1','-vf','scale=400:225','-f','image2pipe','-vcodec','mjpeg','-'], capture_output=True, check=True)
    import io
    return Image.open(io.BytesIO(result.stdout)).convert('RGB')

def sheets(points, stem):
    records=[]
    for page in range(0, len(points), 24):
        batch=points[page:page+24]
        sheet=Image.new('RGB',(1600,260*((len(batch)+3)//4)),'white')
        draw=ImageDraw.Draw(sheet)
        for i,p in enumerate(batch):
            x=(i%4)*400; y=(i//4)*260
            sheet.paste(frame(p['file'],p['seconds']),(x,y+30))
            draw.text((x+6,y+4),p['label'],font=FONT,fill='black')
        target=PROOF/f'{stem}-{page//24+1:02}.jpg'
        sheet.save(target,quality=92)
        records.append({'sheet':str(target.relative_to(ROOT)).replace('\\','/'),'points':batch})
    (PROOF/f'{stem}.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if sys.argv[1]=='bounds':
    PROOF.mkdir(parents=True,exist_ok=True)
    map=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
    points=[];seen=set()
    for chapter in map['chapters']:
        for group in chapter['groups']:
            for key,a,b in group['windows']:
                for t in [a, (a+b)/2, b-1/60]:
                    if (key,t) in seen:continue
                    seen.add((key,t));points.append({'file':map['sources'][key]['file'],'seconds':t,'label':f'{key} {t:.2f}s'})
    sheets(points,'selected-interval-boundaries')
elif sys.argv[1]=='cuts':
    plan=json.loads((WORK/'plan.json').read_text(encoding='utf8')); points=[]
    for scene in plan['scenes']:
        if scene['role']!='additional-commentary':continue
        for c in scene['cuts']:
            for t in [0,c['seconds']/2,c['seconds']-1/60]:
                points.append({'file':c['video'],'seconds':t,'label':f"{scene['id']} {c['key']} {c['sourceIn']+t:.2f}s"})
    sheets(points,'repaired-action-cuts')
elif sys.argv[1]=='scan':
    import numpy as np
    plan=json.loads((WORK/'plan.json').read_text(encoding='utf8')); scans=[]; points=[]
    for scene in plan['scenes']:
        if scene['role']!='additional-commentary':continue
        for c in scene['cuts']:
            result=subprocess.run(['ffmpeg','-v','error','-ss',str(c['sourceIn']),'-t',str(c['seconds']),'-i',str(ROOT/c['file']),'-vf','fps=4,scale=96:54','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True)
            frames=np.frombuffer(result.stdout,dtype=np.uint8).reshape(-1,54,96,3)
            white=(frames.min(axis=3)>220).mean(axis=(1,2))
            black=(frames.max(axis=3)<25).mean(axis=(1,2))
            flags=[]
            for n,(w,b) in enumerate(zip(white,black)):
                if w>.45 or b>.85:
                    flags.append({'offset':n/4,'whiteFraction':float(w),'blackFraction':float(b)})
                    points.append({'file':c['file'],'seconds':c['sourceIn']+n/4,'label':f"{scene['id']} {c['key']} {c['sourceIn']+n/4:.2f}s"})
            scans.append({'scene':scene['id'],'source':c['key'],'in':c['sourceIn'],'out':c['sourceIn']+c['seconds'],'sampledAtFps':4,'maxWhite':float(white.max()),'maxBlack':float(black.max()),'flags':flags})
    (PROOF/'all-action-transition-scan.json').write_text(json.dumps(scans,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    if points:sheets(points,'action-scan-flags')
    print(json.dumps({'cuts':len(scans),'samples':sum(round((x['out']-x['in'])*4) for x in scans),'flags':len(points)}))
