"""Prepare three observed official trailers for comparison, without selection.

Steam's Valve-video policy is not assigned to these other developers.
"""
from pathlib import Path
import json, subprocess, hashlib, shutil, math
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-fresh-official'
S=ROOT/'shared/output/game-math-part2-full-series/sources'
data=json.loads((O/'steam-app-details.json').read_text(encoding='utf8'))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
records=[]
for app,ident in [('477160',257175671),('477160',257076768),('1055540',256755947)]:
    d=next(m for m in data[app]['movies'] if m['id']==ident)
    source_id=f'{"human-fall-flat" if app=="477160" else "a-short-hike"}-steam-{ident}'
    source=S/(source_id+'.mp4')
    if not source.exists():
        streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',d['dash_h264']],creationflags=subprocess.CREATE_NO_WINDOW))['streams']
        videos=[v for v in streams if v['codec_type']=='video']
        fitting=[v for v in videos if v['width']<=1920]
        selected=max(fitting or videos,key=lambda s:s['width']*s['height'])
        subprocess.run(['ffmpeg','-v','error','-y','-i',d['dash_h264'],'-map',f'0:{selected["index"]}','-an','-c:v','copy','-movflags','+faststart',str(source)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
    source.with_suffix('.info.json').write_text(json.dumps({'app':app,'game':data[app]['name'],'officialStore':f'https://store.steampowered.com/app/{app}/','movie':d,'rights':'Official source provenance; third-party game IP/usage permission human review pending. Valve policy is inapplicable.'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    shutil.copy2(source,O/source.name)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)],creationflags=subprocess.CREATE_NO_WINDOW))
    seconds=float(probe['format']['duration']);video=next(v for v in probe['streams'] if v['codec_type']=='video')
    frames=[]
    for at in [*range(0,math.floor(seconds),2),seconds-.2]:
        raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(at),'-i',str(source),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
        if len(raw)==800*450*3:frames.append((at,Image.frombytes('RGB',(800,450),raw)))
    for page in range(math.ceil(len(frames)/8)):
        sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
        for j,(at,im) in enumerate(frames[page*8:page*8+8]):
            x=j%2*800;y=j//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'{source_id} source{at:.2f}s',font=font,fill='black')
        sheet.save(O/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
    records.append({'id':source_id,'game':data[app]['name'],'movie':d['name'],'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceFile':source.relative_to(ROOT).as_posix(),'seconds':seconds,'resolution':[video['width'],video['height']],'selected':False,'nativeCompared':False,'humanRightsComplete':False,'sourceAudioUsed':False})
    print(json.dumps(records[-1],ensure_ascii=False),flush=True)
(O/'candidate-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
buttons=''.join(f'<button data-id="{r["id"]}">{r["game"]}: {r["movie"]}</button>' for r in records)
(O/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>새 게임 평면 예시 후보</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1100px);display:block}button{padding:10px;margin:5px}</style><h1>새 게임 예시 · 평면과 유한한 발판 비교</h1><p>모두 후보입니다. 행동 전·이동·착지, 보이는 면의 꼭짓점과 카메라 가림을 비교합니다.</p><button id="all">전체 후보 연속 재생</button>'''+buttons+'''<video controls muted id="v"></video><p id="now"></p><pre id="proof"></pre><script>const records='''+json.dumps(records,ensure_ascii=False)+''';const v=document.querySelector('video');let queue=[],at=0,seen=[];function start(){const r=queue[at];if(!r)return;v.src=r.id+'.mp4';v.playbackRate=1;document.querySelector('#now').textContent=r.game+' '+r.movie;v.play()}document.querySelector('#all').onclick=()=>{queue=records;at=0;start()};for(const b of document.querySelectorAll('[data-id]'))b.onclick=()=>{queue=records.filter(x=>x.id===b.dataset.id);at=0;start()};v.onended=()=>{seen.push({id:queue[at].id,sha256:queue[at].sha256,seconds:v.duration,ended:v.ended,rate:v.playbackRate});document.querySelector('#proof').textContent=JSON.stringify(seen,null,2);at++;start()};</script>''',encoding='utf8')
