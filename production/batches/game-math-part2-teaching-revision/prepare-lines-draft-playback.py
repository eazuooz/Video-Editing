from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision';items=[]
for group,ids in [('lines-grapple-drafts',['02','05','08','LG02-1','LG02-2','LG03-1','LG03-2']),('lines-portal-beam-drafts',['LG01-a','LG01-b']),('lines-shape-drafts',['10','13','16','LG04','LG06-blue','LG06-gray','LG05','LG07-a','LG07-c','19','21'])]:
 for ident in ids:
  path=O/group/(ident+'.mp4')
  if path.exists():items.append({'id':ident,'file':f'{group}/{ident}.mp4','sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
dest=O/'lines-draft-review.html'
dest.write_text('''<!doctype html><meta charset="utf-8"><title>직선과 경계 · 움직이는 관측 표시 초안</title><style>body{background:#171717;color:white;font:16px sans-serif;margin:18px}video{width:min(100%,1050px);display:block}button{padding:10px;margin:4px}h1{font-size:22px}#proof{white-space:pre-wrap}a{color:#9dd}</style><h1>직선·경계 관측 표시 초안 · 정상 속도 직접 검수</h1><p>완성 영상 승인이 아닙니다. 표시가 실제 대상에 붙는지 확인합니다.</p><button id="grapple">연결선·빛줄기 연속 재생</button><button id="shapes">윤곽·범위 연속 재생</button><div id="buttons"></div><video controls muted id="v"></video><p id="now"></p><pre id="proof"></pre><script>
const items='''+json.dumps(items,ensure_ascii=False)+''';const v=document.querySelector('video'),now=document.querySelector('#now'),proof=document.querySelector('#proof');let queue=[],at=0,seen=[];
for(const item of items){const b=document.createElement('button');b.textContent=item.id;b.onclick=()=>{queue=[item];at=0;start()};document.querySelector('#buttons').append(b)}
function start(){const item=queue[at];if(!item)return;v.src=item.file+'?sha='+item.sha256;v.playbackRate=1;now.textContent=item.id+' · SHA256 '+item.sha256;v.play()}
v.onended=()=>{seen.push({id:queue[at].id,sha256:queue[at].sha256,duration:v.duration,ended:v.ended,rate:v.playbackRate});proof.textContent=JSON.stringify(seen,null,2);at++;start()};
document.querySelector('#grapple').onclick=()=>{queue=items.filter(x=>!x.file.startsWith('lines-shape'));at=0;start()};document.querySelector('#shapes').onclick=()=>{queue=items.filter(x=>x.file.startsWith('lines-shape'));at=0;start()};</script>''',encoding='utf8')
(B/'lines-draft-playback-inputs.json').write_text(json.dumps({'items':items,'finalPixelApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(dest)
