"""Inspect the one changed caption edge without repeating other pixel extraction."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent; WORK=BASE/'measured-edit-v4'
DEST=WORK/'overhead-caption-edge-cropped-local-v6'; assert not DEST.exists(); DEST.mkdir()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(ROOT).as_posix()
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
state=dict(schemaVersion=1,startedAt=datetime.now(timezone.utc).isoformat(),pid=os.getpid(),threads=2,images=[],sheets=[],newGitImages=0,status='one-caption-edge-target-preparing',finalVideoApproved=False)
def save():
    (DEST/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
try:
    save(); compiled=read(WORK/'native-review-v4/compiled.json'); plan=read(WORK/'plan.json')
    old_ass=(WORK/'captions.ko.candidate.v4.ass').read_bytes()
    cuts=[next(c for c in compiled['cuts'] if c['id']==n) for n in ['12-p1-action-44-17160-17280','12-p1-action-48-19530-19742']]
    for cut in cuts:
        p=ROOT/cut['video']; assert sha(p)==cut['sha256']
        points=([116,117,118,119] if cut['id'].startswith('12-p1-action-44') else [0,1,2,3,4,5,10,40,106,211])
        select='+'.join(f'eq(n\\,{n})' for n in points)
        x,y,w,h=cut['composition']['proposedCrop']; assert [x,y,w,h]==[0,0,1472,828]
        vf=f"crop={w}:{h}:{x}:{y},scale=1920:1080,setsar=1,setpts=PTS+{cut['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.v5.ass,select='{select}'"
        prefix='wall' if cut['id'].startswith('12-p1-action-44') else 'overhead'
        log=DEST/(prefix+'.log')
        with log.open('wb') as fh:
            args=[FF,'-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(p),'-vf',vf,'-fps_mode','passthrough','-frames:v',str(len(points)),str(DEST/(prefix+'-%03d.png'))]
            proc=subprocess.Popen(args,cwd=WORK,stdout=fh,stderr=fh,creationflags=subprocess.CREATE_NO_WINDOW)
            state['activeTask']=dict(pid=proc.pid,command=args,log=rel(log)); save(); code=proc.wait()
        assert code==0 and not log.read_text().strip()
        files=sorted(DEST.glob(prefix+'-*.png')); assert len(files)==len(points)
        for f,n in zip(files,points): state['images'].append(dict(path=rel(f),sha256=sha(f),cut=cut['id'],localFrame=n,globalFrame=cut['startFrame']+n,directlyRead=False))
        save()
    font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
    for off in range(0,len(state['images']),6):
        subset=state['images'][off:off+6]; image=Image.new('RGB',(1920,1740),'white'); draw=ImageDraw.Draw(image)
        for i,r in enumerate(subset):
            x,y=i%2*960,i//2*580
            with Image.open(ROOT/r['path']) as im:image.paste(im.resize((960,540)),(x,y+40))
            draw.text((x+8,y+7),f'{off+i+1} {r["cut"].split("-action-")[-1]} n{r["localFrame"]} global{r["globalFrame"]}',font=font,fill='black')
        f=DEST/f'edge-sheet-{off//6+1:03d}.jpg'; image.save(f,quality=94)
        state['sheets'].append(dict(path=rel(f),sha256=sha(f),imageIndices=list(range(off+1,off+len(subset)+1)),directlyRead=False))
    assert old_ass==(WORK/'captions.ko.candidate.v4.ass').read_bytes()
    state.update(endedAt=datetime.now(timezone.utc).isoformat(),exitCode=0,status='closed-one-caption-edge-awaiting-direct-read',activeTask=None);save()
    print(json.dumps(dict(images=len(state['images']),sheets=len(state['sheets']),newGitImages=0)))
except BaseException as e:
    state.update(endedAt=datetime.now(timezone.utc).isoformat(),exitCode=1,status='closed-target-failure',error=str(e));save();raise
