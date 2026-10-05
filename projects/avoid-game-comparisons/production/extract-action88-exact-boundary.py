"""New exact samples for the independently observed action88 editorial dissolve."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
DEST=BASE/'measured-edit-v5/action88-exact-boundary-local'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not DEST.exists();DEST.mkdir()
asset=next(x for x in read(ROOT/'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/source-research/acquisition-plucky-mine.json')['results'] if x['videoId']=='CJ0_Xh59b98')
assert sha(ROOT/asset['localMediaPath'])==asset['fileSha256']
frames=list(range(4843,4853))+[5028,5032,5036,5040,5044,5048,5052]
select='+'.join(f'eq(n\\,{n})' for n in frames)
cmd=['C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe','-v','error','-nostdin','-threads','2','-i',str(ROOT/asset['localMediaPath']),'-vf',f"select='{select}'",'-fps_mode','passthrough','-frames:v',str(len(frames)),str(DEST/'raw-%03d.png')]
with (DEST/'extraction.log').open('wb') as f:
 p=subprocess.Popen(cmd,stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW);code=p.wait()
assert code==0 and not (DEST/'extraction.log').read_text().strip()
images=[dict(path=q.relative_to(ROOT).as_posix(),sha256=sha(q),nativeFrame=n,directlyRead=False) for q,n in zip(sorted(DEST.glob('raw-*.png')),frames)]
assert len(images)==len(frames)
sheets=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',24)
for off in range(0,len(images),6):
 sheet=Image.new('RGB',(1920,1740),'white');d=ImageDraw.Draw(sheet)
 for k,r in enumerate(images[off:off+6]):
  x,y=k%2*960,k//2*580
  with Image.open(ROOT/r['path']) as im:sheet.paste(im.resize((960,540)),(x,y+40))
  d.text((x+8,y+7),f"native {r['nativeFrame']}",font=font,fill='black')
 q=DEST/f'review-sheet-{off//6+1:03d}.jpg';sheet.save(q,quality=96)
 sheets.append(dict(path=q.relative_to(ROOT).as_posix(),sha256=sha(q),directlyRead=False))
state=dict(pid=os.getpid(),childPid=p.pid,command=cmd,endedAt=datetime.now(timezone.utc).isoformat(),exitCode=code,status='closed-awaiting-exact-native-direct-review',source='CJ0_Xh59b98',sourceSha256=asset['fileSha256'],images=images,sheets=sheets,newGitImages=0)
(DEST/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(pid=state['pid'],images=len(images),sheets=len(sheets),exitCode=code)))
