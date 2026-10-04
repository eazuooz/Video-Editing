"""Read only the two extended current encoded intervals; preserve other65 proofs."""
from pathlib import Path
import json,hashlib,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];WORK=Path(__file__).resolve().parent/'measured-edit-v3/source-review-v2';DEST=WORK/'encoded-boundaries';DEST.mkdir(exist_ok=False)
FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';j=json.loads((WORK/'compiled.json').read_text(encoding='utf8'));rows=[]
for c in j['cuts']:
 if c.get('reusedByteIdentical'):continue
 folder=DEST/c['id'];folder.mkdir();points=[0,c['frames']//2,c['frames']-1]
 vf="select='"+'+'.join('eq(n\\,%d)'%n for n in points)+"'"
 p=subprocess.run([FF,'-v','error','-threads','2','-i',str(ROOT/c['video']),'-vf',vf,'-fps_mode','vfr','-q:v','2',str(folder/'frame-%02d.jpg')],capture_output=True,text=True)
 (folder/'extract.log').write_text(p.stderr,encoding='utf8');assert p.returncode==0 and not p.stderr
 files=sorted(folder.glob('frame-*.jpg'));assert len(files)==3
 for role,n,f in zip(['first','middle','last'],points,files):rows.append({'cut':c['id'],'role':role,'encodedFrame':n,'sourceSecond':c['sourceInSeconds']+n/60,'image':f.relative_to(ROOT).as_posix(),'directlyRead':False,'encodedSha256':c['sha256']})
page=Image.new('RGB',(1920,2*580),'#eee');d=ImageDraw.Draw(page);font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
for k,r in enumerate(rows):
 x=k%3*640;y=k//3*580;page.paste(Image.open(ROOT/r['image']).resize((640,360)),(x,y));d.text((x+8,y+370),f"{r['cut']} {r['role']} {r['sourceSecond']:.3f}",font=font,fill='black')
f=DEST/'page-01.jpg';page.save(f,quality=97)
(DEST/'index.json').write_text(json.dumps({'compiledSha256':hashlib.sha256((WORK/'compiled.json').read_bytes()).hexdigest(),'rows':rows,'page':f.relative_to(ROOT).as_posix(),'directReading':'pending','captionPixelApproval':False},indent=2)+'\n',encoding='utf8');print(json.dumps({'views':len(rows),'page':str(f)}))
