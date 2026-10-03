"""Verify candidate reserve edges. Does not modify frozen action/narration inputs."""
from pathlib import Path
import subprocess,json,hashlib
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/motion-sickness-games/production/source-fit-followup/edges'
BASE.mkdir(parents=True,exist_ok=True)
sources={id:ROOT/f'shared/assets/game-footage/motion-sickness-games/{id}.mp4' for id in ['PF5L_2g9UVQ','6slinvkF0Rs']}
times={'PF5L_2g9UVQ':[90.5,92,94,96,98,98.9,339.1,341.5,344.9,357.8,362,367,319.1,328.5,338.9,397,400,403.8,493.1,501,509.9],
       '6slinvkF0Rs':[16,16.033333,16.1,20.7,20.733333,23.033333,23.1,30.1,30.166667,31,31.033333,31.1,35.8,35.866667,35.966667,36,36.1,39.7,39.833333,40.133333,42.233333,48,52.2,52.266667,52.333333,52.4]}
rows=[]
for id,values in times.items():
    fps=60 if id=='PF5L_2g9UVQ' else 30
    indices=sorted(set(round(t*fps) for t in values))
    vf='select='+ '+'.join(f'eq(n\\,{n})' for n in indices)
    pattern=BASE/f'{id}-linear-%02d.jpg'
    result=subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',str(sources[id]),'-filter_threads','1','-vf',vf,'-fps_mode','vfr','-frames:v',str(len(indices)),'-q:v','2',str(pattern)],capture_output=True,text=True)
    if result.returncode or result.stderr:raise RuntimeError('Linear edge decode failed: '+result.stderr)
    for t in values:
        frame=round(t*fps);dest=BASE/f'{id}-linear-{indices.index(frame)+1:02}.jpg'
        assert dest.exists()
        rows.append({'sourceId':id,'requestedSeconds':t,'seconds':frame/fps,'nativeFrame':frame,'linearDecode':True,'file':dest.relative_to(ROOT).as_posix()})
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21);contacts=[]
for offset in range(0,len(rows),12):
    sheet=Image.new('RGB',(1920,936),'white');draw=ImageDraw.Draw(sheet)
    for k,row in enumerate(rows[offset:offset+12]):
        x,y=k%4*480,k//4*312;sheet.paste(Image.open(ROOT/row['file']).convert('RGB').resize((480,270)),(x,y))
        draw.text((x+6,y+276),f"{row['sourceId']} {row['seconds']:.4f}s",font=font,fill='#073c32')
    dest=BASE/f'contact-{offset//12+1}.jpg';sheet.save(dest,quality=93);contacts.append(dest.relative_to(ROOT).as_posix())
report={'images':rows,'contacts':contacts,'sourceSha256':{id:hashlib.sha256(p.read_bytes()).hexdigest() for id,p in sources.items()},'directReview':'pending','finalTimingApproved':False,
        'decodeMethod':'Full linear decoder path with native-frame select; exit0 and no stderr required for both sources.',
        'supersededFastSeek':'Original fast-seek research emitted two mmco reference warnings. Its individual images are preserved but not used for edge approval.'}
(BASE/'images.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'images':len(rows),'contacts':contacts}))
