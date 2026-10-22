"""Encode short current-source annotation checks without assembling a master."""
import sys
from polish_common import *

e=Episode(sys.argv[1]);e.authorized()
plan_path=e.H/('observed-guides.json' if e.id=='M17' else 'restored-available-guides.json')
plan=read(plan_path)
windows={
 'M10':{'LG04':(6.6,11.6),'LG06':(19.2,24.2),'LG07':(2.7,5.8)},
 'M11':{'02':(3.9,7.2),'02-recap':(37.4,40.2),'05':(7.7,10),'08':(13.1,15.1),'08-link':(37.8,39.5)},
 'M12':{'11':(15.8,17.5),'17':(17.8,19.1),'19':(23.8,25.5),'21':(2.4,4.2),'21-recap':(39.4,41.7),'14-link':(7.8,9.5),'14-perspective':(31.1,33.1)},
 'M17':{'05':(0,4),'08':(3,5.1),'14-orbit':(11.8,14.7),'14-zoom':(83.1,85.5)},
}[e.id]
selected_names=set(sys.argv[2:])
if selected_names:
 assert selected_names<=windows.keys()
 windows={k:v for k,v in windows.items() if k in selected_names}
out=e.O/'moving-available-preflight';out.mkdir(exist_ok=True)
records=[]
previous=e.H/'moving-available-guide-preflight.json'
if selected_names and previous.exists():
 records=[dict(r,name=r.get('name',r['scene'])) for r in read(previous)['clips'] if r.get('name',r['scene']) not in selected_names]
for name,(start,end) in windows.items():
 sid=name.split('-')[0]
 e.authorized();slot=next(s for s in e.T['scenes'] if s['id']==sid)
 src=e.O/f'clips/{sid}.mp4';dst=out/f'{name}.mp4';frames=round((end-start)*60)
 inset='scale=1600:900:flags=lanczos,pad=1920:1080:160:0:black,setsar=1,' if sid in plan['captionClearanceScenes'] else ''
 vf=inset+f"settb=1/60,setpts=PTS+{slot['start']+start}/TB,ass=composition-polish.ass,ass=captions.ko.ass,setpts=PTS-STARTPTS"
 e.ff(['-ss',start,'-i',src,'-ss',slot['start']+start,'-i',e.O/'baseline-audio.m4a','-vf',vf,'-frames:v',frames,'-t',end-start,'-map','0:v','-map','1:a','-c:a','aac','-b:a','160k',*ENC,dst],'moving-available-'+sid+'.log',e.O)
 e.verify(dst,frames)
 records.append({'scene':sid,'name':name,'path':rel(dst),'sha256':sha(dst),'start':start,'end':end,'frames':frames,'currentPixels':'pending'})
 print(e.id,sid,'current 1080p60 selected preview encoded',flush=True)
buttons=''.join(f'<button data-src="{r["name"]}.mp4">{r["scene"]}: {r["start"]}–{r["end"]}s</button>' for r in records)
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Partial source guide check</title><style>body{background:#151515;color:white;font:18px system-ui}video{display:block;width:min(96vw,1280px)}button{margin:6px;padding:10px}</style><p>부분 장면 검사 · 전체 완성본 아님</p><video controls id="v"></video>'+buttons+'<script>for(const b of document.querySelectorAll("button"))b.onclick=()=>{v.src=b.dataset.src;v.play()}</script>',encoding='utf8')
save(e.H/'moving-available-guide-preflight.json',{'status':'await-current-pixel-inspection','partial':True,'clips':records,'planSha256':sha(plan_path),'assSha256':sha(e.O/'composition-polish.ass'),'captionSha256':sha(e.O/'captions.ko.ass'),'audio':'Recovered unchanged baseline narration; preview AAC is not a new TTS or final master.','fullMasterApproval':False})
