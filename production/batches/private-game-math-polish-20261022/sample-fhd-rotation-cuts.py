"""Decode proposed cuts at 2s intervals, retaining source/scene timestamps."""
import html,math,subprocess,sys
from PIL import Image,ImageDraw
from polish_common import *

for ident in sys.argv[1:]:
 e=Episode(ident);e.authorized();plan=read(e.H/'fhd-replacement-cuts.json')
 out=e.O/'fhd-cut-review';out.mkdir(exist_ok=True);samples=[];buttons=[]
 for sid,scene in plan['scenes'].items():
  local_start=0
  for j,seg in enumerate(scene['segments']):
   src=R/seg['sourceFile'];duration=seg['frames']/60;tag=f'{sid}-{j+1}'
   dest=out/tag;dest.mkdir(exist_ok=True)
   assert video(src)['r_frame_rate']=='60/1'
   command=['ffmpeg','-hide_banner','-loglevel','error','-ss',str(seg['in']),'-t',str(duration),'-i',str(src),'-vf',"select='not(mod(n,120))',scale=480:270",'-fps_mode','vfr','-q:v','2','-y',str(dest/'%03d.jpg')]
   signature={'sourceSha256':scene['sourceSha256'],'in':seg['in'],'frames':seg['frames'],'sampling':'exact-decoded-frame-mod-120-v1'}
   receipt=dest/'sampling.json'
   if not(receipt.exists() and read(receipt)==signature):
    subprocess.run(command,check=True,capture_output=True)
    save(receipt,signature)
   frames=[]
   for k,p in enumerate(sorted(dest.glob('*.jpg'))[:math.ceil(duration/2)]):
    t=min(2*k,duration-.02);sample={'scene':sid,'segment':j,'localSeconds':local_start+t,'sourceSeconds':seg['in']+t,'image':rel(p),'imageSha256':sha(p)}
    frames.append(sample);samples.append(sample)
   for start in range(0,len(frames),12):
    sheet=Image.new('RGB',(1440,1184),'#121212');draw=ImageDraw.Draw(sheet)
    for k,rec in enumerate(frames[start:start+12]):
     x=k%3*480;y=k//3*296;sheet.paste(Image.open(R/rec['image']),(x,y+26))
     draw.text((x+6,y+5),f"{sid}/{j+1} local {rec['localSeconds']:.1f} / src {rec['sourceSeconds']:.1f}",fill='white')
    sheet.save(out/f'{tag}-sheet-{start//12+1:02}.jpg',quality=94)
   buttons.append({'label':f'{sid}/{j+1} ({seg["in"]:.2f}-{seg["in"]+duration:.2f}s)','url':'/'+rel(src),'start':seg['in'],'end':seg['in']+duration})
   local_start+=duration
  print(ident,sid,'candidate cut states decoded',flush=True)
 save(e.H/'fhd-cut-review.json',{'status':'await-direct-cut-inspection','cutMapSha256':sha(e.H/'fhd-replacement-cuts.json'),'samples':samples,'sheets':[rel(p) for p in sorted(out.glob('*-sheet-*.jpg'))],'movingPlayback':'pending','fullMasterApproval':False})
 page='''<!doctype html><meta charset="utf-8"><title>FHD replacement source review</title><style>body{background:#161616;color:white;font:18px system-ui}video{width:min(96vw,1280px);display:block}button{margin:4px;padding:8px}output{display:block}</style><video controls muted id="v"></video><output id="info"></output><button id="pause">Pause</button><div id="buttons"></div><script>
const data=DATA;const v=document.querySelector('video');let end=0;
for(const item of data){const b=document.createElement('button');b.textContent=item.label;b.onclick=()=>{v.src=item.url;v.currentTime=item.start;end=item.end;v.play()};document.querySelector('#buttons').appendChild(b)}
document.querySelector('#pause').onclick=()=>v.pause();v.ontimeupdate=()=>{document.querySelector('#info').textContent=v.currentTime.toFixed(2)+' / '+end.toFixed(2)+'s';if(v.currentTime>=end)v.pause()};</script>'''
 import json
 (out/'playback.html').write_text(page.replace('DATA',json.dumps(buttons)),encoding='utf8')
 print(ident,len(samples),'states awaiting direct review',flush=True)
