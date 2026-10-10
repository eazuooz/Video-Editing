"""Review the actual burned final file with visible native playback controls."""
from pathlib import Path
import json,html,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parents[3];slug=sys.argv[1];P=ROOT/'projects'/slug
t=json.loads((P/'production/timeline.json').read_text(encoding='utf8'));m=json.loads((P/'project.json').read_text(encoding='utf8'))
D=ROOT/'shared/output/game-math-part2-teaching-revision/final-review'/slug;D.mkdir(parents=True,exist_ok=True)
src=ROOT/m['paths']['videoBurnedCaptions'];dst=D/'captioned.mp4'
source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
if not dst.exists() or dst.stat().st_size!=src.stat().st_size or hashlib.sha256(dst.read_bytes()).hexdigest()!=source_sha:shutil.copy2(src,dst)
assert source_sha==hashlib.sha256(dst.read_bytes()).hexdigest()
rows=''
for s in t['scenes']:
 rows+='<button data-start="'+str(s['start'])+'" data-end="'+str(s['start']+s['seconds'])+'">'+html.escape(s['id']+' '+s['title'])+' 전체 재생</button> '
windows={'GB07':[(6.5,8.5),(8.5,9.95)],'GB01':[(4,12)],'GB02':[(8,17)],'GB03':[(10,21)],'GB04':[(5,14)],'GB05':[(3,11)],'GB06':[(5,12)]}
for s in t['scenes']:
 for a,z in windows.get(s['id'],[]):
  rows+=f'<button data-start="{s["start"]+a}" data-end="{s["start"]+min(z,s["seconds"])}">{s["id"]} {a}–{z}초 주석 검수</button> '
rows+='<button data-start="0" data-end="'+str(t['seconds'])+'">전체 강의 연속 재생</button>'
page='''<!doctype html><meta charset="utf-8"><title>쿼터니언 최종 렌더 검수</title><style>body{background:#222;color:white;font:16px sans-serif;margin:14px}video{display:block;width:min(100%,1100px);max-height:62vh}button{margin:3px;padding:6px}#controls{max-height:190px;overflow:auto}#status{margin:8px}</style><h1>'''+html.escape(m['titles']['ko'])+'''</h1><p>실제 납품 후보 · 원본 배속 · 한글 고정 자막 · BGM 없음</p><video id="v" src="captioned.mp4" controls></video><div id="status">장면을 선택하세요</div><div id="controls">'''+rows+'''</div><script>const v=document.querySelector('video'),s=document.querySelector('#status');let stopAt=Infinity,current='';for(const b of document.querySelectorAll('button'))b.onclick=()=>{current=b.textContent;stopAt=+b.dataset.end;v.currentTime=+b.dataset.start;v.play();s.textContent=current};v.ontimeupdate=()=>{s.textContent=current+' | '+v.currentTime.toFixed(2)+' / '+v.duration.toFixed(2);if(v.currentTime>=stopAt){v.pause();s.textContent+=' | segment ended'}};</script>'''
page=page.replace('src="captioned.mp4"', 'src="captioned.mp4?v='+source_sha[:16]+'"')
(D/'index.html').write_text(page,encoding='utf8')
(D/'review-manifest.json').write_text(json.dumps({'source':m['paths']['videoBurnedCaptions'],'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'nativeSpeed':1,'playbackApproval':False},indent=2)+'\n',encoding='utf8')
print('Actual final render review page ready; viewing is pending')
