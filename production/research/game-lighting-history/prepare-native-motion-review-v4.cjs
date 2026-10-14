const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history',read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const entries=[];
for(const version of [3,5,6]){
 const state=read(`${base}/local/episode03-native-v${version}/execution.json`);
 for(const a of state.completed)entries.push({id:a.slug,title:a.title||a.slug,url:a.url,src:path.relative(path.join(root,base,'local'),path.join(root,a.media)).replaceAll('\\','/'),sha256:a.sha256,sourceWindow:a.requestedSourceWindow||null});
}
entries.push({id:'ue5-reveal-2020',title:'UE5 2020 PS5 reveal',url:'https://www.youtube.com/watch?v=qC5KtatMcUw',src:'ue5-reveal-youtube-2020.mp4'});
const html=`<!doctype html><html lang="ko"><meta charset="utf-8"><title>원본 동작·설정 검수</title>
<style>body{margin:10px;background:#101418;color:#fff;font:16px sans-serif}h1{font-size:20px;margin:0 0 5px}video{display:block;height:calc(100vh - 200px);max-height:540px;max-width:100%;aspect-ratio:16/9;background:#000}button,select,input{font:inherit;margin:3px;padding:4px}input{width:74px}p{margin:5px 0;color:#ddd}#clock{color:#ffd36c}</style>
<h1>공식 시연 원본 · 동작과 설정 검수</h1><label>자료<select id="selection"></select></label><span id="label"></span>
<video id="video" controls muted preload="metadata"></video><p id="clock">준비 중</p>
<label>시작<input id="start" type="number" value="100" step="0.01"></label><label>끝<input id="end" type="number" value="115" step="0.01"></label><button id="play">지정 구간 재생</button><button id="pause">일시정지</button><button id="seek">시작 프레임 확인</button>
<p id="status">원속도·원색. 무음 시각 검수; 권리·최종 믹스·최종 픽셀 승인은 별도입니다.</p>
<script>const entries=${JSON.stringify(entries)},s=document.getElementById('selection'),v=document.getElementById('video'),a=document.getElementById('start'),z=document.getElementById('end'),c=document.getElementById('clock'),st=document.getElementById('status');let until=null;
for(const e of entries){const o=document.createElement('option');o.value=e.id;o.textContent=e.id;s.append(o)}
function load(){v.pause();until=null;const e=entries.find(e=>e.id===s.value);v.src=e.src;document.getElementById('label').textContent=e.sourceWindow?'요청 원본 '+e.sourceWindow.start+'–'+e.sourceWindow.end+'초 · 현재 시계는 확보 창 기준':'전체 확보 원본 기준';st.textContent='자료 '+e.id+' · 재생 구간 직접 지정';}s.addEventListener('change',load);
document.getElementById('play').onclick=()=>{const x=+a.value,y=+z.value;if(!(x>=0&&y>x&&y<=v.duration))throw Error('Invalid range');until=y;v.currentTime=x;v.playbackRate=1;v.muted=true;v.play();st.textContent='재생 중 '+s.value+' '+x+'–'+y+'초';};
document.getElementById('pause').onclick=()=>{v.pause();until=null;st.textContent='직접 일시정지 '+v.currentTime.toFixed(3)+'초';};document.getElementById('seek').onclick=()=>{v.pause();until=null;v.currentTime=+a.value;};
v.addEventListener('timeupdate',()=>{c.textContent='현재 '+v.currentTime.toFixed(3)+' / '+v.duration.toFixed(3)+'초 · '+(v.paused?'일시정지':'재생 중')+' · 속도'+v.playbackRate;if(until!==null&&v.currentTime>=until){v.pause();st.textContent='구간 종료 '+s.value+' '+until+'초 도달 · 최종 승인 별도';until=null}});v.addEventListener('loadedmetadata',()=>c.textContent='현재 '+v.currentTime.toFixed(3)+' / '+v.duration.toFixed(3)+'초');s.value='nanite-editor-motion-2021';load();</script></html>`;
const file=path.join(root,base,'local/native-motion-review-v4.html');fs.writeFileSync(file,html);
console.log(JSON.stringify({file,sources:entries.length,mediaStarted:false,sha256:crypto.createHash('sha256').update(html).digest('hex')}));
