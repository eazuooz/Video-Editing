"""Download observed official movie descriptors, then prepare comparison pixels.
No selection or license/human/pixel approval is inferred from a trailer title.
"""
from pathlib import Path
import json,subprocess,hashlib,math,shutil
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-portal-secondary';S=ROOT/'shared/output/game-math-part2-full-series/sources';font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
movies=json.loads((O/'portal2-official-movies.json').read_text(encoding='utf8'))['movies'];records=[]
for ident in [5926,5786]:
 descriptor=next(m for m in movies if m['id']==ident);url=descriptor['dash_h264'];source=S/f'portal2-steam-{ident}.mp4';metadata=source.with_suffix('.info.json')
 if not source.exists():
  streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',url],creationflags=subprocess.CREATE_NO_WINDOW))['streams'];stream=max([s for s in streams if s['codec_type']=='video'],key=lambda s:s['width']*s['height'])
  subprocess.run(['ffmpeg','-v','error','-y','-i',url,'-map',f'0:{stream["index"]}','-an','-c:v','copy','-movflags','+faststart',str(source)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 metadata.write_text(json.dumps(descriptor,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 shutil.copy2(source,O/f'portal2-steam-{ident}.mp4')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(source)],creationflags=subprocess.CREATE_NO_WINDOW));duration=float(probe['format']['duration']);video=next(s for s in probe['streams'] if s['codec_type']=='video');frames=[]
 for t in [*range(0,math.floor(duration),2),max(0,duration-.3)]:
  raw=subprocess.check_output(['ffmpeg','-v','error','-threads','1','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=800:450','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],creationflags=subprocess.CREATE_NO_WINDOW)
  if len(raw)==800*450*3:frames.append((t,Image.frombytes('RGB',(800,450),raw)))
 for page in range(math.ceil(len(frames)/8)):
  sheet=Image.new('RGB',(1600,1880),'white');draw=ImageDraw.Draw(sheet)
  for j,(t,im) in enumerate(frames[page*8:page*8+8]):
   x=j%2*800;y=j//2*470;sheet.paste(im,(x,y+20));draw.text((x+5,y),f'Official Steam{ident} source{t:.3f}s',font=font,fill='black')
  sheet.save(O/f'{ident}-sheet-{page+1:02}.jpg',quality=95)
 records.append({'id':f'portal2-steam-{ident}','name':descriptor['name'],'sourceFile':source.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceMetadata':metadata.relative_to(ROOT).as_posix(),'seconds':duration,'resolution':[video['width'],video['height']],'sourceAudioUsed':False,'historicalPreview':True,'nativeCompared':False,'selected':False,'rightsPolicy':'https://store.steampowered.com/video_policy/','humanRightsComplete':False});print(json.dumps(records[-1]),flush=True)
(O/'candidate-records.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
buttons=''.join(f'<button data-id="{r["id"]}">{r["name"]}</button>' for r in records)
(O/'index.html').write_text('''<!doctype html><meta charset="utf-8"><title>평면 강의 · 공식 게임 예시 비교</title><style>body{background:#222;color:white;font:16px sans-serif}video{width:min(100%,1050px);display:block}button{padding:10px;margin:5px}</style><h1>평면·발판 예시 후보 · 정상 속도 비교</h1><p>아직 선택하지 않았습니다. 발사 전·이동·표면 도착과 가장자리, 카메라 가림을 비교합니다.</p><button id="all">전체 후보 연속 재생</button>'''+buttons+'''<video controls muted id="v"></video><p id="now"></p><pre id="proof"></pre><script>
const records='''+json.dumps(records,ensure_ascii=False)+''';const v=document.querySelector('video');let queue=[],at=0,seen=[];
function start(){const r=queue[at];if(!r)return;v.src=r.id+'.mp4';v.playbackRate=1;document.querySelector('#now').textContent=r.name+' / '+r.sha256;v.play()}
document.querySelector('#all').onclick=()=>{queue=records;at=0;start()};for(const b of document.querySelectorAll('[data-id]'))b.onclick=()=>{queue=records.filter(x=>x.id===b.dataset.id);at=0;start()};v.onended=()=>{seen.push({id:queue[at].id,sha256:queue[at].sha256,seconds:v.duration,ended:v.ended,rate:v.playbackRate});document.querySelector('#proof').textContent=JSON.stringify(seen,null,2);at++;start()};</script>''',encoding='utf8')
