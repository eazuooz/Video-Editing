// Local review controls. Seeking selects a native frame; it never approves source quota.
const fs=require('node:fs');
const src='production/research/game-lighting-history/local/native-boundary-review-v113.html',out='production/research/game-lighting-history/local/native-boundary-controls-v114.html';
if(fs.existsSync(out))throw Error('Preserve previous player');
let html=fs.readFileSync(src,'utf8');
html=html.replace('<p id="ranges">','<label>원본 초 <input id="nativeTime" type="number" min="0" step="0.016666667" value="0"></label><button id="seek">이 시각 보기</button><button id="backFrame">이전 프레임</button><button id="nextFrame">다음 프레임</button><button id="continue">현재부터 재생</button><p id="ranges">');
html=html.replace('v.onerror=()=>',`const time=document.querySelector('#nativeTime');function seek(t){playing=false;v.pause();v.currentTime=Math.max(0,t);time.value=v.currentTime.toFixed(6)}
document.querySelector('#seek').onclick=()=>seek(Number(time.value));document.querySelector('#backFrame').onclick=()=>seek(v.currentTime-1/60);document.querySelector('#nextFrame').onclick=()=>seek(v.currentTime+1/60);document.querySelector('#continue').onclick=async()=>{v.playbackRate=1;interval=0;playing=true;await v.play()};
v.onerror=()=>`);
fs.writeFileSync(out,html);console.log(JSON.stringify({out,reviewOnly:true,newImages:0}));
