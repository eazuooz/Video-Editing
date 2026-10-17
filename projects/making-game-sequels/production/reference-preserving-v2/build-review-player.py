"""Local final-master playback at actual speed, with scene/mark review ranges."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';V=P/'production/reference-preserving-v2';O=P/'production/local/reference-preserving-v2/edit'
plan=json.loads((V/'edit-plan.json').read_text(encoding='utf8'));assert plan['timing']=='measured-and-asr-aligned'
ranges=[]
for c in plan['cuts']:
 if c['kind']=='explanation':ranges.append([c['id']+' · '+c['visual'],c['startFrame']/60,c['endFrame']/60])
 for m in c.get('marks',[]):
  a=max(c['sourceStart'],m['from']);b=min(c['sourceStart']+c['frames']/60,m['to'])
  if b>a:ranges.append([c['id']+' · '+m['label'],c['startFrame']/60+a-c['sourceStart']-.5,c['startFrame']/60+b-c['sourceStart']+.5])
for a,b in zip(plan['scenes'],plan['scenes'][1:]):ranges.append(['연결 '+a['id']+' → '+b['id'],b['startFrame']/60-3,b['startFrame']/60+4])
html='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>속편 만들기 · 완성본 검수</title>
<style>body{background:#101214;color:#eee;font:17px system-ui;margin:20px}video{width:min(100%,900px);display:block;background:black}video.mobile{width:375px;max-width:100%}button{padding:9px;margin:3px;background:#242930;color:white;border:1px solid #747a80;border-radius:4px}output{display:block;margin:10px}nav{max-width:1200px}h1{font-size:24px}</style>
<h1>속편 만들기 · 1080p 60fps 완성본 검수</h1><video controls preload="metadata" src="making-game-sequels-v2-captioned.mp4"></video><output>재생할 구간을 선택하세요.</output>
<section><button id="all">전체 재생</button><button id="pause">일시정지</button><button id="play">재생</button><button id="mobile">모바일 375px</button><button id="desktop">큰 화면</button><button id="previous">이전 프레임</button><button id="next">다음 프레임</button></section><nav></nav><script>
const ranges=RANGES,v=document.querySelector('video'),o=document.querySelector('output');let end=Infinity,name='전체';
for(const [label,a,b] of ranges){const bt=document.createElement('button');bt.textContent=label;bt.onclick=()=>{name=label;end=b;v.currentTime=Math.max(0,a);v.play()};document.querySelector('nav').append(bt)}
v.ontimeupdate=()=>{o.textContent=name+' | '+v.currentTime.toFixed(3)+' / '+(Number.isFinite(end)?end.toFixed(3):v.duration.toFixed(3))+'초 · 1배속';if(v.currentTime>=end)v.pause()};
document.querySelector('#all').onclick=()=>{name='전체';end=Infinity;v.currentTime=0;v.play()};document.querySelector('#pause').onclick=()=>v.pause();document.querySelector('#play').onclick=()=>v.play();document.querySelector('#mobile').onclick=()=>v.classList.add('mobile');document.querySelector('#desktop').onclick=()=>v.classList.remove('mobile');
for(const [id,delta] of [['previous',-1],['next',1]])document.getElementById(id).onclick=()=>{v.pause();v.currentTime=Math.max(0,v.currentTime+delta/60)};
</script></html>'''.replace('RANGES',json.dumps(ranges,ensure_ascii=False))
(O/'playback.html').write_text(html,encoding='utf8');print('Local master review player prepared; no playback approval inferred.')
