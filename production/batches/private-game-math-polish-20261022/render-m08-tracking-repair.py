"""Selective current-caption previews for defects actually found in final QA."""
from PIL import Image,ImageDraw,ImageFont
from polish_common import *
e=Episode('M08');e.authorized();out=e.O/'tracking-repair/moving';out.mkdir(parents=True,exist_ok=True)
comp=read(e.H/'composition-polish.json');records=[];tiles=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for sid,a,z in [('IG05',11.7,13.4),('IG08',1.9,4.2),('IG06',4.8,6.2)]:
 s=next(s for s in e.T['scenes'] if s['id']==sid);src=R/comp['inputs'][sid]['path'];dst=out/f'{sid}.mp4'
 vf=f"settb=1/60,setpts=PTS+{s['start']+a}/TB,ass=composition-polish.ass,ass=captions.ko.ass,setpts=PTS-STARTPTS"
 e.ff(['-ss',a,'-i',src,'-ss',s['start']+a,'-i',e.O/'baseline-audio.m4a','-vf',vf,'-frames:v',round((z-a)*60),'-t',z-a,'-map','0:v','-map','1:a','-c:a','aac','-b:a','160k',*ENC,dst],'repair-moving-'+sid+'.log',e.O)
 e.verify(dst,round((z-a)*60));frames=[]
 for k in range(round((z-a)*10)):
  t=k/10+.05;p=out/f'{sid}-{k:02d}.png'
  e.ff(['-ss',t,'-i',dst,'-frames:v','1','-threads','1',p],'repair-moving-sample.log')
  tile=Image.new('RGB',(375,240),'#222222');tile.paste(Image.open(p).resize((375,211)),(0,29));ImageDraw.Draw(tile).text((5,3),f'{sid} +{a+t:.2f}s',font=font,fill='white');tiles.append(tile)
  frames.append({'localSeconds':a+t,'path':rel(p),'sha256':sha(p)})
 records.append({'scene':sid,'start':a,'end':z,'path':rel(dst),'sha256':sha(dst),'samples':frames})
for i in range(0,len(tiles),12):
 sheet=Image.new('RGB',(1500,720),'#222222')
 for j,tile in enumerate(tiles[i:i+12]):sheet.paste(tile,(j%4*375,j//4*240))
 sheet.save(out/f'sheet-{i//12+1:02d}.jpg',quality=96)
(out/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>Tracking repair QA</title><style>body{background:#111;color:white}video{display:block;width:min(95vw,1280px)}button{padding:12px;margin:8px}</style><video id="v" controls></video><button onclick="v.style.width='375px'">375px</button><button onclick="v.style.width='min(95vw,1280px)'">Large</button>'''+''.join(f'''<button onclick="v.src='{r['scene']}.mp4';v.play()">{r['scene']}</button>''' for r in records),encoding='utf8')
save(e.H/'tracking-repair-moving.json',{'status':'await-direct-inspection','clips':records,'compositionSha256':sha(e.H/'composition-polish.json'),'globalAssSha256':sha(e.O/'composition-polish.ass'),'fullMasterApproval':False})
print('M08 three repair previews and54 intermediate frames generated',flush=True)
