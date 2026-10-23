"""Decode the actual delivered files and extract captioned evidence; does not approve human review."""
from common import *
import math,html
from PIL import Image,ImageDraw,ImageFont
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';D=R/'output/game-math-rendering-light-concept-fit-v2';Q=O/'qa';Q.mkdir(exist_ok=True)
T=read(H/'timeline.json');outputs=read(H/'outputs.json');slug=P.name;records=[]
for kind in ['clean','captioned']:
 p=D/f'{slug}.{kind}.mp4';meta=probe(p);v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',T['frames']);assert a['sample_rate']=='48000' and a['channels']==2
 assert abs(float(meta['format']['duration'])-T['seconds'])<.08
 log=Q/f'{kind}-decode.log'
 with log.open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-v','error','-nostdin','-i',str(p),'-f','null','-'],stdout=f,stderr=f,check=True)
 assert not log.read_text(encoding='utf8').strip(),'Inspect decode warnings'
 records.append(dict(kind=kind,path=rel(p),sha256=sha(p),frames=v['nb_frames'],duration=meta['format']['duration'],decodeErrors=0))
frames=[]
for s in T['scenes']:
 times=[s['start']+max(.1,s['seconds']*.35),s['start']+s['seconds']*.80]
 for key,shot in __import__('runpy').run_path(str(B/'compose-m15.py'))['SHOTS'].items():
  if shot['scene']!=s['id']:continue
  offset=shot['offset'];times += [s['start']+offset+.2+i*.5 for i in range(math.floor(shot['seconds']*2))]+[s['start']+offset+shot['seconds']+.2]
 for tm in sorted(set(round(x,3) for x in times)):
  p=Q/f'{tm:09.3f}.png';subprocess.run(['ffmpeg','-v','error','-nostdin','-ss',str(tm),'-i',str(D/f'{slug}.captioned.mp4'),'-frames:v','1','-y',str(p)],check=True,capture_output=True)
  frames.append(dict(scene=s['id'],time=tm,path=rel(p)))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',20);sheets=[]
for start in range(0,len(frames),12):
 im=Image.new('RGB',(1920,1560),'#111');dr=ImageDraw.Draw(im)
 for n,r in enumerate(frames[start:start+12]):
  l=n%3*640;t=n//3*390;im.paste(Image.open(R/r['path']).resize((640,360)),(l,t+30));dr.text((l+5,t+4),f"M15 {r['scene']} {r['time']:.3f}s",font=font,fill='white')
 p=Q/f'sheet-{start//12+1:02}.jpg';im.save(p,quality=92);sheets.append(rel(p))
mobile=[]
for sid in ['02','05','08','11','14','17','19','21','09','13','18','22']:
 candidates=[x for x in frames if x['scene']==sid];r=candidates[len(candidates)//2];im=Image.open(R/r['path']).resize((375,211));p=Q/f'mobile-{sid}.png';im.save(p);mobile.append(dict(scene=sid,time=r['time'],path=rel(p)))
save(H/'qa.json',dict(checkedAt=now(),technical=records,frames=frames,sheets=sheets,mobile=mobile,captionCues=len(read(H/'captions.json')['cues']),directVisualReview='pending',nativePlayback='pending',actualListening=False,humanReview='pending'))
# Controls are authored locally: browser automation invokes these visible controls.
buttons=''.join(f'<button data-start="{s["start"]}" data-end="{s["start"]+s["seconds"]}">{s["id"]} {html.escape(s["title"])}</button>' for s in T['scenes'])
(D/'internal-review.html').write_text(f'''<!doctype html><meta charset="utf-8"><title>M15 내부 검수</title><style>body{{background:#101512;color:white;font:18px system-ui}}video{{width:min(95vw,1440px)}}button{{padding:8px;margin:3px}}</style><h1>M15 · 1배속 검수</h1><button id="all">전체 재생</button><button id="stop">일시정지</button><p id="state"></p><video controls src="{slug}.captioned.mp4"></video><div>{buttons}</div><pre id="proof"></pre><script>const v=document.querySelector('video');let limit=Infinity,record=[],start=0;function play(a,b){{start=a;limit=b;v.currentTime=a;v.playbackRate=1;v.play()}}document.querySelector('#all').onclick=()=>play(0,Infinity);document.querySelector('#stop').onclick=()=>v.pause();document.querySelectorAll('button[data-start]').forEach(b=>b.onclick=()=>play(+b.dataset.start,+b.dataset.end));v.ontimeupdate=()=>{{document.querySelector('#state').textContent=v.currentTime.toFixed(3)+' / '+v.duration+' · '+v.playbackRate+'배속';if(v.currentTime>=limit){{v.pause();record.push({{start,end:v.currentTime,rate:v.playbackRate}});limit=Infinity;document.querySelector('#proof').textContent=JSON.stringify(record,null,2)}}}};v.onended=()=>{{record.push({{start,end:v.currentTime,rate:v.playbackRate,ended:true}});document.querySelector('#proof').textContent=JSON.stringify(record,null,2)}};</script>''',encoding='utf8')
print('Actual-file decode passed;',len(frames),'frames on',len(sheets),'sheets; direct review still pending',flush=True)
