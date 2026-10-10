"""Prepare a normal-speed final-flow review page on the existing loopback helper."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'shared/assets/presenting-game-scores/raw'
timeline=json.loads((ROOT/'projects/game-math-polar-3d/production/timeline.json').read_text(encoding='utf-8'))
markers=[{'id':'intro','time':0,'name':'고양이 원본2초'}]+[{'id':s['id'],'time':s['start'],'name':s['title']} for s in timeline['scenes']]+[{'id':'member','time':53515/60,'name':'원본 회원10초'}]
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>극좌표 2편 — 전체 수정본 흐름 검수</title>
<style>body{margin:16px;background:#151515;color:#fff;font:17px sans-serif}video{width:min(1152px,94vw);display:block}button{font:17px sans-serif;margin:8px;padding:8px}#status{white-space:pre-wrap;max-width:1152px}</style>
<h1>극좌표 2편 · 전체 수정본 흐름 검수 v3</h1>
<p>검수용 미승인 최종 파일. 원래 음성과 순서를 유지한 정상1배속 재생입니다. 빨간 핵심선과 역할별 색 도형이 실제 게임 행동과 설명을 연결합니다. 표시된 좌표 모델은 게임 내부 측정값이 아닙니다. 고정 한글 자막은 영상에 포함되어 있습니다.</p>
<video id="v" controls preload="metadata" src="polar-3d-final-flow-v3.mp4"></video>
<button id="whole">처음부터 전체1배속 재생</button><button id="pause">일시 정지</button><button id="resume">현재 위치부터1배속 계속</button>
<div id="chapters"></div><div id="status">미재생</div><script>
const v=document.getElementById('v'),status=document.getElementById('status'),markers=MARKERS;
let events=[],lastScene=null;
function record(kind,extra={}){events.push({kind,currentTime:v.currentTime,playbackRate:v.playbackRate,muted:v.muted,paused:v.paused,at:new Date().toISOString(),...extra})}
document.getElementById('whole').onclick=()=>{events=[];lastScene=null;v.currentTime=0;v.playbackRate=1;v.muted=false;v.play().then(()=>record('whole-start'))};
document.getElementById('pause').onclick=()=>{v.pause();record('manual-pause')};
document.getElementById('resume').onclick=()=>{v.playbackRate=1;v.muted=false;v.play().then(()=>record('manual-resume'))};
markers.forEach(s=>{let b=document.createElement('button');b.textContent=s.id+' '+s.name;b.onclick=()=>{v.currentTime=s.time;lastScene=null;record('manual-seek',{scene:s.id});v.playbackRate=1;v.muted=false;v.play()};document.getElementById('chapters').append(b)});
v.addEventListener('ended',()=>record('whole-ended'));v.addEventListener('error',()=>record('error',{code:v.error?.code}));
function update(){const sc=markers.filter(s=>s.time<=v.currentTime).at(-1);if(sc&&sc.id!==lastScene&&!v.paused){lastScene=sc.id;record('scene-enter',{scene:sc.id,title:sc.name})}status.textContent=JSON.stringify({currentTime:v.currentTime,duration:v.duration,playbackRate:v.playbackRate,muted:v.muted,paused:v.paused,currentScene:sc,events});requestAnimationFrame(update)}update();
</script></html>'''.replace('MARKERS',json.dumps(markers,ensure_ascii=False))
dest=RAW/'polar-3d-final-flow-v3.html';assert not dest.exists();dest.write_text(html,encoding='utf-8')
print(json.dumps({'helperPrepared':True,'source':'polar-3d-final-flow-v3.mp4','serverRestarted':False,'playbackObserved':False,'wholeFlowApproved':False}))
