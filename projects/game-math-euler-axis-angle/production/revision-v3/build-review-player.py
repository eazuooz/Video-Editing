"""Local complete-master player with explicit scene/cue controls for visual review."""
from pathlib import Path
import json,html
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3'
t=json.loads((Path(__file__).parent/'timeline.json').read_text(encoding='utf8'))
buttons=''.join(f'<button data-time="{s["start"]}">{s["id"]} {html.escape(s["title"])}</button>' for s in t['scenes'])
content='''<!doctype html><html lang="ko"><meta charset="utf-8"><title>M04 닌텐도 수정본 검수</title>
<style>body{background:#121512;color:#fff;font:18px sans-serif;margin:12px}video{width:min(100%,1920px);display:block}button,input{font:17px sans-serif;padding:8px;margin:3px}#chapters{display:flex;flex-wrap:wrap}#status{padding:10px}h1{font-size:23px}</style>
<h1>M04 · Nintendo ·1080p60 · 추가 배경음악 없음</h1><video id="video" preload="metadata" src="euler-captioned.mp4"></video><div id="status"></div>
<button id="play">재생</button><button id="pause">일시정지</button><button id="back">5초 이전</button><button id="next">5초 다음</button><button id="mobile">모바일375</button><button id="large">전체폭</button>
<label>검수 위치(초) <input id="time" type="number" min="0" step="0.1" value="0"></label><button id="seek">이동</button><div id="chapters">'''+buttons+'''</div>
<script>const v=document.querySelector('#video');const status=document.querySelector('#status');
document.querySelector('#play').onclick=()=>v.play();document.querySelector('#pause').onclick=()=>v.pause();
document.querySelector('#back').onclick=()=>{v.currentTime=Math.max(0,v.currentTime-5)};document.querySelector('#next').onclick=()=>{v.currentTime=Math.min(v.duration,v.currentTime+5)};
document.querySelector('#mobile').onclick=()=>v.style.width='375px';document.querySelector('#large').onclick=()=>v.style.width='min(100%,1920px)';
document.querySelector('#seek').onclick=()=>{v.pause();v.currentTime=Math.max(0,Number(document.querySelector('#time').value))};
document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{v.pause();v.currentTime=Number(b.dataset.time)});
v.ontimeupdate=()=>status.textContent=`${v.currentTime.toFixed(2)} / ${v.duration.toFixed(2)}초 · ${v.videoWidth}×${v.videoHeight}`;
</script></html>'''
(O/'playback.html').write_text(content,encoding='utf8');print('Review player prepared')
