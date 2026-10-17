from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];L=R/'projects/making-game-sequels/production/local/reference-preserving-v2'
clips=[['피크민: 지시와 운반','pikmin4-day2',85,115],['피크민: 벽을 부수고 열린 길','pikmin4-day2',225,255],['피크민: 와치 돌진과 항아리','pikmin4-day2',331.5,349.5],['GT7: 조향과 코너','gt7-sunday',22,40],['Wii U: 공격과 대미지','smash-wiiu',35,85],['Ultimate: 대미지와 밀어내기','smash-ultimate',0,36],['Ultimate: 다음 대전','smash-ultimate',175,206]]
html='''<!doctype html><meta charset="utf-8"><title>D19 independent footage inspection</title><style>body{background:#101214;color:#eee;font:18px system-ui;margin:24px}video{width:min(100%,1120px);display:block}button{padding:10px;margin:4px}output{display:block;margin:16px}</style><h1>속편 만들기 · 독립 게임 원본 검수</h1><nav></nav><output></output><video controls preload="metadata"></video><button id="pause">일시정지</button><button id="play">재생</button><script>
const clips=CLIPS,v=document.querySelector('video'),o=document.querySelector('output');let end=0,name='';
clips.forEach(([label,file,a,b],i)=>{const bt=document.createElement('button');bt.textContent=label;bt.onclick=()=>{name=label;end=b;v.src='../media/'+file+'.mp4';v.onloadedmetadata=()=>{v.currentTime=a;v.play()};};document.querySelector('nav').append(bt)});
v.ontimeupdate=()=>{o.textContent=name+' | '+v.currentTime.toFixed(2)+' s / '+end+' s';if(v.currentTime>=end)v.pause()};document.querySelector('#pause').onclick=()=>v.pause();document.querySelector('#play').onclick=()=>v.play();</script>'''.replace('CLIPS',json.dumps(clips,ensure_ascii=False))
(L/'research/source-review.html').write_text(html,encoding='utf8')
print('Source inspection page saved')
