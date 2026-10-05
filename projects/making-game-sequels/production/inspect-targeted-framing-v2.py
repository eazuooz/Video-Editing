"""Decode limited alternatives for resource UI and distant action; local only."""
from pathlib import Path
import hashlib, json, subprocess
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
WORK = BASE / 'measured-edit-v2'
DEST = WORK / 'targeted-framing-local-v2'
assert not DEST.exists(), 'Preserve previous targeted trials.'
DEST.mkdir()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
compiled = read(WORK/'native-review-v1/compiled.json')
plan = read(WORK/'plan.json')
FF = 'C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe'
rows=[]
for prefix, variants in [('08-p3-action-28', [('raw', None),('lower', [0,252,1472,828])]),
                         ('13-p1-action-49', [('raw', None),('zoom', [192,270,1056,594])])]:
    media = next(c for c in compiled['cuts'] if c['id'].startswith(prefix))
    cut = next(c for s in plan['scenes'] for c in s['segments'] if c['id']==media['id'])
    for label,crop in variants:
        for f in [0,cut['frames']//2,cut['frames']-1]:
            output = DEST/f'{prefix}-{label}-{f}.png'
            vf=(f'crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]},scale=1920:1080,' if crop else '')
            if crop:
                vf+=f"setpts=PTS+{cut['startFrame']/60:.9f}/TB,subtitles=captions.ko.candidate.v2.ass,"
            vf+=f"select='eq(n\\,{f})'"
            cmd=[FF,'-v','error','-nostdin','-threads','2','-filter_threads','1','-i',str(ROOT/media['video']),
                 '-vf',vf,'-frames:v','1',str(output)]
            r=subprocess.run(cmd,cwd=WORK,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
            assert r.returncode==0 and not r.stderr, r.stderr
            rows.append({'cut':media['id'],'localFrame':f,'variant':label,'crop':crop,
                         'path':output.relative_to(ROOT).as_posix(),
                         'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'finalApproved':False})
for start in [0,6]:
    board=Image.new('RGB',(1920,1740),'white');draw=ImageDraw.Draw(board)
    for k,row in enumerate(rows[start:start+6]):
        x,y=k%2*960,k//2*580
        with Image.open(ROOT/row['path']) as im: board.paste(im.resize((960,540)),(x,y+40))
        draw.text((x+8,y+8),f"{start+k+1} {row['variant']} n{row['localFrame']}",fill='black')
    board.save(DEST/f'board-{start//6+1}.jpg',quality=94)
(WORK/'targeted-framing-v2.json').write_text(json.dumps({'images':rows,'newGitImages':0,
    'allDirectlyRead':False,'finalApproved':False,'sourceAudioUsed':False},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'images':len(rows),'CPUExit':0,'newGitImages':0}))
