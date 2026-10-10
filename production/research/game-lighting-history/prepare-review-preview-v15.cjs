const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const plan=JSON.parse(fs.readFileSync(path.join(root,'projects/game-lighting-history-03/production/review-input-plan-v15.json'),'utf8'));
const clips=plan.inputs.filter(x=>x.kind==='explanation-review-input');
const out=path.join(__dirname,'local/review-preview-v15.html');
if(fs.existsSync(out))throw Error('Preserve existing preview');
const options=clips.map(x=>`<option value="${x.fromFrame/60}">${x.scene} · ${x.id}</option>`).join('');
const html=`<!doctype html><html lang="ko"><meta charset="utf-8"><title>3편 현재 합성 검수본</title>
<style>body{background:#171717;color:#eee;font:17px sans-serif;margin:14px}h1{font-size:20px;margin:0 0 8px}button,input,select{font-size:17px;padding:7px;margin:3px}video{width:min(1280px,95vw);height:auto;display:block;background:black}output{display:block;white-space:pre-wrap;margin:8px 0;color:#f4d578}</style>
<h1>3편 현재 합성 검수본 · 25분 51.4초 · 최종 픽셀·혼합 음성 승인 대기</h1>
<label>설명 구간 <select id="selection">${options}</select></label>
<label>검수 시각 <input id="time" type="number" step="0.016666667" value="2"></label>
<button id="seek">시각으로 이동</button><button id="play">재생</button><button id="pause">정지</button>
<output id="state">미로드</output>
<video id="video" preload="metadata" controls src="/@fs/D:/Github/Video-Editing/production/research/game-lighting-history/local/explanation-framing-v15/silent-review-visual-v15.mp4"></video>
<script>
const video=document.querySelector('#video'),state=document.querySelector('#state'),time=document.querySelector('#time');
function show(){state.textContent='현재 시각 '+video.currentTime.toFixed(6)+'초 / '+video.duration.toFixed(6)+'초 · '+(video.paused?'정지':'재생')+' · 무음 검수본';}
document.querySelector('#selection').onchange=e=>{time.value=e.target.value;video.pause();video.currentTime=Number(time.value);};
document.querySelector('#seek').onclick=()=>{video.pause();video.currentTime=Number(time.value);};
document.querySelector('#play').onclick=()=>video.play();document.querySelector('#pause').onclick=()=>video.pause();
for(const event of ['loadedmetadata','seeked','pause','play','timeupdate'])video.addEventListener(event,show);
</script></html>`;
fs.writeFileSync(out,html);console.log(JSON.stringify({preview:out,mediaCreated:0,imagesCreated:0}));
