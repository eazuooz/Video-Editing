"""Current clips, narration-timed captions, and native-speed review windows.

Preparation is not viewing approval. Readbacks and screenshots are recorded
separately after actual playback.
"""
from pathlib import Path
import argparse,json,subprocess,hashlib,html
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('slug');parser.add_argument('--scenes');args=parser.parse_args()
P=ROOT/'projects'/args.slug;W=ROOT/'shared/output'/args.slug
t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'))
D=ROOT/'shared/output/game-math-part2-teaching-revision/render-review'/args.slug;D.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',15)
selected=set(args.scenes.split(',')) if args.scenes else None
records=[]
for s in t['scenes']:
 if selected and s['id'] not in selected:continue
 clip=W/f'clips/{s["id"]}.mp4'
 if not clip.exists():continue
 # Use the SAME final subtitle ASS, transformed into this scene's local time.
 cues=[{**c,'start':c['start']-s['start'],'end':c['end']-s['start']} for c in t['koCaptions'] if c['scene']==s['id']]
 import importlib.util
 spec=importlib.util.spec_from_file_location('caps',ROOT/'projects/game-math-polar-sample/production/build.py');caps=importlib.util.module_from_spec(spec);spec.loader.exec_module(caps)
 original_ass=(P/'script/final.ko.ass').read_text(encoding='utf8')
 header=original_ass[:original_ass.index('Dialogue:')];events=[]
 def seconds(stamp):
  a,b,c=stamp.split(':');return int(a)*3600+int(b)*60+float(c)
 for event in original_ass.splitlines():
  if not event.startswith('Dialogue:'):continue
  fields=event.split(',',9);start,end=seconds(fields[1]),seconds(fields[2])
  if start<s['start']-.02 or end>s['start']+s['seconds']+.02:continue
  fields[1]=caps.ass_time(max(0,start-s['start']));fields[2]=caps.ass_time(end-s['start']);events.append(','.join(fields))
 ass=D/f'{s["id"]}.ko.ass';ass.write_text(header+'\n'.join(events)+'\n',encoding='utf8')
 target=D/f'{s["id"]}.mp4';sha=hashlib.sha256(clip.read_bytes()).hexdigest();receipt=D/f'{s["id"]}.json'
 signature={'clipSha256':sha,'assSha256':hashlib.sha256(ass.read_bytes()).hexdigest(),'narrationSha256':hashlib.sha256((W/'narration-final.wav').read_bytes()).hexdigest()}
 if not target.exists() or not receipt.exists() or json.loads(receipt.read_text(encoding='utf8')).get('signature')!=signature:
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-i',str(clip),'-ss',str(s['start']),'-i',str(W/'narration-final.wav'),'-map','0:v','-map','1:a','-vf','ass='+str(ass.relative_to(ROOT)).replace('\\','/'),'-frames:v',str(s['frames']),'-t',str(s['seconds']),'-c:v','libx264','-preset','fast','-crf','21','-threads','3','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(target)],cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  receipt.write_text(json.dumps({'scene':s['id'],'signature':signature,'seconds':s['seconds'],'nativeSourceSpeed':1,'continuousReview':False},indent=2)+'\n',encoding='utf8')
 name=s['id'];video_sha=hashlib.sha256(target.read_bytes()).hexdigest();records.append({'scene':name,'seconds':s['seconds'],'url':target.relative_to(D).as_posix()+'?v='+video_sha[:16],'sha256':video_sha})
 print('Captioned review clip',name,flush=True)
rows=''.join('<button data-id="'+html.escape(x['scene'])+'" data-src="'+html.escape(x['url'])+'">'+html.escape(x['scene'])+' 재생</button>' for x in records)
windows={'GA07':[(5.5,8.5),(11,14)],'GA08':[(7.5,10),(19,24.7)],'GA05':[(35,44.5)],'GB07':[(6.5,7.8),(7.8,9.7)]}
for x in records:
 for a,z in windows.get(x['scene'],[]):
  rows+=f'<button data-id="{x["scene"]} {a}–{z}s 정상속도 검수" data-src="{x["url"]}" data-start="{a}" data-end="{z}">{x["scene"]} {a}–{z}초 검수</button>'
page='''<!doctype html><meta charset="utf-8"><title>쿼터니언 렌더 검수</title><style>body{margin:16px;background:#222;color:white;font:16px sans-serif}button{margin:3px;padding:8px}video{display:block;width:min(100%,1100px);max-height:62vh;background:#000}#state{margin:10px}</style><h1>쿼터니언 · 현재 음성·고정 자막·편집 가능 주석</h1><div>'''+rows+'''</div><video id="v" controls></video><div id="state">장면을 선택하세요</div><script>const v=document.querySelector('video'),s=document.querySelector('#state');for(const b of document.querySelectorAll('button'))b.onclick=()=>{v.src=b.dataset.src;v.play();s.textContent=b.dataset.id};v.ontimeupdate=()=>s.textContent=s.textContent.split(' | ')[0]+' | '+v.currentTime.toFixed(2)+' / '+v.duration.toFixed(2);v.onended=()=>s.textContent+=' | ended';</script>'''
page=page.replace("v.src=b.dataset.src;v.play();", "v.src=b.dataset.src;v.dataset.end=b.dataset.end||'';v.onloadedmetadata=()=>{v.currentTime=Number(b.dataset.start||0);v.play()};")
page=page.replace("v.ontimeupdate=()=>s.textContent=", "v.ontimeupdate=()=>{if(v.dataset.end&&v.currentTime>=Number(v.dataset.end))v.pause();s.textContent=").replace("v.duration.toFixed(2);v.onended", "v.duration.toFixed(2)};v.onended")
(D/'index.html').write_text(page,encoding='utf8')
(D/'index.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print('Review UI ready; no viewing or listening claim')
