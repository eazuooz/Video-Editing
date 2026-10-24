from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def rd(p):return json.loads(p.read_text('utf-8-sig'))
entries={e['id']:e for e in rd(B/'edit-list-audit.json')['entries']};items=[]
for ep in sys.argv[1:]:
 e=entries[ep];slug=e['slug'];h=R/'projects'/slug/'production/gameplay-v3'
 if (h/'outputs.json').exists() and (h/'patches.json').exists():
  o=rd(h/'outputs.json');cap=next(x for x in o['outputs'] if x['path'].endswith('.captioned.mp4'));clips=rd(h/'patches.json')['patches'];ranges=[dict(scene=x.get('key',x['scene']),start=max(0,x['start']-1),end=x['start']+x['duration']+1) for x in clips]
 else:
  old=R/'projects'/slug/'production/concept-fit-v2';o=rd(old/'outputs.json');cap=next(x for x in o['outputs'] if x['path'].endswith('.captioned.mp4'));T={s['id']:s for s in rd(old/'timeline.json')['scenes']};ranges=[dict(scene=str(i)+'-'+s['scene'],start=T[s['scene']]['start']+s['offset']-1,end=T[s['scene']]['start']+s['offset']+s['seconds']+1) for i,s in enumerate(e['shots'])]
 for s in ranges:items.append(dict(s,episode=ep,title=e['title'],sha256=cap['sha256'],url='/'+cap['path']+'?v='+cap['sha256']))
out=R/'output/private-math-gameplay-20261024/continuous-review.html'
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><style>body{background:#101412;color:#eee;font:18px/1.5 system-ui;margin:20px}video{width:min(1100px,95vw);display:block}button{padding:12px;margin:6px}pre{white-space:pre-wrap;font:12px monospace}</style><h1>변경 구간과 앞뒤 연결 검수</h1><p id="now"></p><video id="v" controls muted></video><button id="start">전 구간 정상 재생</button><button id="stop">일시 정지</button><button id="mobile">375px 전환</button><p id="time"></p><pre id="proof"></pre><script>
const items=ITEMS;const v=document.querySelector('#v');let i=0,active=false,seeking=false,started=0,proof=[],mobile=false;
function show(){document.querySelector('#proof').textContent=JSON.stringify(proof)}
function ready(){if(!active)return;seeking=true;v.currentTime=items[i].start;}
v.onseeked=()=>{if(!active)return;seeking=false;started=performance.now();v.playbackRate=1;v.play().catch(e=>{proof.push({error:String(e)});show()})};
function next(){if(i>=items.length){active=false;v.pause();show();return}const x=items[i];document.querySelector('#now').textContent=x.episode+' · '+x.scene+' · '+x.title;if(v.getAttribute('src')!==x.url){v.src=x.url;v.onloadedmetadata=ready;v.load()}else ready()}
v.ontimeupdate=()=>{document.querySelector('#time').textContent=v.currentTime.toFixed(2)+' / '+v.playbackRate+'배속';if(active&&!seeking&&v.currentTime>=items[i].end){let x=items[i];proof.push({episode:x.episode,scene:x.scene,sha256:x.sha256,start:x.start,end:v.currentTime,rate:v.playbackRate,elapsed:(performance.now()-started)/1000,error:v.error?.message||null,width:mobile?375:'desktop'});show();v.pause();i++;next()}};
document.querySelector('#start').onclick=()=>{v.pause();proof=[];i=0;active=true;next()};document.querySelector('#stop').onclick=()=>{active=false;v.pause()};document.querySelector('#mobile').onclick=()=>{mobile=!mobile;v.style.width=mobile?'375px':'min(1100px,95vw)'};
</script></html>'''.replace('ITEMS',json.dumps(items,ensure_ascii=False));out.write_text(page,encoding='utf8');print(len(items),'intervals',sum(x['end']-x['start'] for x in items),'seconds')
