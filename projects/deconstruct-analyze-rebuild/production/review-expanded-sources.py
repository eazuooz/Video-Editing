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

if sys.argv[1]=='closing-action':
    PROOF.mkdir(parents=True,exist_ok=True)
    map=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
    times=[88.8+n*.25 for n in range(25)]
    sheets([{'file':map['sources']['noita3']['file'],'seconds':round(t,4),'label':f'noita3 {t:.4f}s'} for t in times],'closing-action')
elif sys.argv[1]=='replace-dark-transition':
    PROOF.mkdir(parents=True,exist_ok=True)
    map=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
    times=[43.8+n*.2 for n in range(21)]+[26.5+n*.1 for n in range(15)]+[66.95,67,67.05,67.1,85.5,86,86.5,86.75,86.8]
    sheets([{'file':map['sources']['noita3']['file'],'seconds':round(t,4),'label':f'noita3 {t:.4f}s'} for t in times],'replace-dark-transition')
    sheets([{'file':map['sources']['noita2']['file'],'seconds':t,'label':f'noita2 {t:.4f}s'} for t in [57.5,57.6,57.6333,57.65,57.7]],'replace-dark-transition-noita2')
elif sys.argv[1]=='fresh-blue-action':
    PROOF.mkdir(parents=True,exist_ok=True)
    map=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
    times=[69.45+n*.2 for n in range(25)]
    times.extend([73.85,73.8667,73.9,74.1])
    sheets([{'file':map['sources']['noita3']['file'],'seconds':round(t,4),'label':f'noita3 {t:.4f}s'} for t in times],'fresh-blue-action')
elif sys.argv[1]=='snow-action-start':
    PROOF.mkdir(parents=True,exist_ok=True)
    map=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
    times=[21+n*.05 for n in range(11)]+[25.05,25.0667,25.1,25.15]
    sheets([{'file':map['sources']['noita3']['file'],'seconds':round(t,4),'label':f'noita3 {t:.4f}s'} for t in times],'snow-action-start')
elif sys.argv[1]=='repair-boundaries':
    PROOF.mkdir(parents=True,exist_ok=True)
    map=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
    points=[]
    for key,times in {'noita2':[1.6,1.7,1.8,1.9,2], 'noita3':[20.3,20.4,20.5,20.6,20.7,20.8,20.9,21,24.9,25,25.1,25.2,25.3,25.4,25.5,43.8,43.9,44,47.2,47.3,47.4,47.5,47.6,47.7,47.8]}.items():
        points.extend({'file':map['sources'][key]['file'],'seconds':t,'label':f'{key} {t:.2f}s'} for t in times)
    sheets(points,'transition-repair-boundaries')
elif sys.argv[1] in ['fine','fine-extra','ftl-extra']:
    PROOF.mkdir(parents=True,exist_ok=True)
    ranges={
      'noita1':[(.2,5),(60.2,68.7),(81.5,88),(94.5,99.7)],
      'noita2':[(1,9.8),(19.9,26.9),(44.3,54)],
      'noita3':[(21,29.7),(35,70),(77,85)],
      'ftl':[(1.5,35),(52,58.5),(64.6,73),(76,80)],
      'breach':[(5,28.8),(42,54)],
    }
    if sys.argv[1]=='fine-extra':
        ranges={
          'noita2':[(10,19.8),(27,44.2),(54.1,67)],
          'noita3':[(2,19),(30,34.8),(86,103)]
        }
    if sys.argv[1]=='ftl-extra':
        ranges={'ftl':[(35.2,52.3)]}
    map=json.loads((WORK/'example-map.json').read_text(encoding='utf8'))
    points=[]
    for key,windows in ranges.items():
        for a,b in windows:
            t=a
            while t<b:
                points.append({'file':map['sources'][key]['file'],'seconds':round(t,3),'label':f'{key} {t:.2f}s'})
                t+=.5 if key.startswith('noita') else 1
            points.append({'file':map['sources'][key]['file'],'seconds':b-1/60,'label':f'{key} last {b-1/60:.2f}s'})
    sheets(points,{'fine':'fine-action-candidates','fine-extra':'fine-action-extra','ftl-extra':'fine-ftl-states'}[sys.argv[1]])
elif sys.argv[1]=='press':
    PROOF.mkdir(parents=True,exist_ok=True)
    record=json.loads((ROOT/'projects/deconstruct-analyze-rebuild/sources/breach-advanced-actions.json').read_text(encoding='utf8'))
    points=[]
    for source in record['files']:
        for t in [.05, source['nativeDurationSeconds']*.25, source['nativeDurationSeconds']*.5, source['nativeDurationSeconds']*.75, source['nativeDurationSeconds']-.1]:
            points.append({'file':source['file'],'seconds':t,'label':f"{source['key'].replace('breach-','')} {t:.2f}s"})
    sheets(points,'press-action-review')
elif sys.argv[1]=='bounds':
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
