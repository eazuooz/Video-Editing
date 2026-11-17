'use strict';
const $=s=>document.querySelector(s),storeKey='yamyam-lofi-3d-v1',contexts=[];
// Register before the Unity loader. Keep native HTML editing defaults while
// preventing the game's global keyboard listeners from consuming note input.
for(const kind of ['keydown','keyup','keypress','paste','beforeinput'])window.addEventListener(kind,event=>{
 const el=event.target;
 if(event.key!=='Escape' && el instanceof HTMLElement && (el.matches('input,textarea,select')||el.isContentEditable))event.stopImmediatePropagation();
},true);
for(const key of ['AudioContext','webkitAudioContext'])if(window[key]){const Native=window[key];window[key]=class extends Native{constructor(...args){super(...args);contexts.push(this);}};}
let unity,entered=false,state={},noteTimer,timerEnd=0,timerRemaining=25*60;
const send=(method,value)=>{if(unity){if(value===undefined)unity.SendMessage('LofiRoom',method);else unity.SendMessage('LofiRoom',method,value);}};
const save=(key,value)=>{try{localStorage.setItem(storeKey+':'+key,JSON.stringify(value));return true;}catch{return false;}};
const load=(key,fallback)=>{try{const s=localStorage.getItem(storeKey+':'+key);return s===null?fallback:JSON.parse(s);}catch{return fallback;}};
const focusHtml=()=>send('SetUiFocus',($('#memo-panel').hidden&&$('#timer-panel').hidden)?'0':'1');
function openPanel(id){$('#'+id).hidden=!$('#'+id).hidden;focusHtml();if(!$('#memo-panel').hidden)$('#memo-text').focus();}
function saveNote(){clearTimeout(noteTimer);$('#memo-state').textContent=save('memo',$('#memo-text').value)?'이 브라우저에 저장됨 · '+new Date().toLocaleTimeString('ko-KR',{hour:'2-digit',minute:'2-digit'}):'저장하지 못했어요. 내용을 복사해 보관해 주세요.';}
$('#memo-text').value=load('memo','');$('#memo-text').addEventListener('input',()=>{$('#memo-state').textContent='저장 중…';clearTimeout(noteTimer);noteTimer=setTimeout(saveNote,650);});
$('#memo-open').onclick=()=>openPanel('memo-panel');$('#memo-close').onclick=()=>{saveNote();openPanel('memo-panel');};
$('#timer-open').onclick=()=>openPanel('timer-panel');$('#timer-close').onclick=()=>openPanel('timer-panel');
for(const b of document.querySelectorAll('[data-action]'))b.onclick=()=>send(b.dataset.action);
$('#read').onclick=()=>send('ReadBook');
for(const [id,method,fallback] of [['music-volume','SetMusicVolume',.18],['fire-volume','SetFireVolume',.42]]){$('#'+id).value=load(id,fallback);$('#'+id).oninput=e=>{send(method,e.target.value);save(id,+e.target.value);};}
$('#fullscreen').onclick=()=>{if(document.fullscreenElement)document.exitFullscreen();else $('#stage').requestFullscreen?.();};
// Keep canvas backing size consistent with Unity's configured devicePixelRatio=1.
function resize(){const c=$('#unity-canvas');c.width=Math.round(c.clientWidth);c.height=Math.round(c.clientHeight);}
new ResizeObserver(resize).observe($('#stage'));
window.addEventListener('lofi-state',e=>{state=e.detail;$('#phase').textContent=state.phase||'잠깐 쉬어가기';$('#audio-state').textContent=entered?(state.music?'로파이 재생 중':'로파이 일시정지'):'소리는 시작 버튼을 누르면 켜져요';$('#performance').textContent=Math.round(state.fps)+' fps';});
function clock(){const seconds=timerEnd?Math.max(0,Math.ceil((timerEnd-Date.now())/1000)):timerRemaining;$('#timer-clock').textContent=String(Math.floor(seconds/60)).padStart(2,'0')+':'+String(seconds%60).padStart(2,'0');if(timerEnd&&seconds===0){timerEnd=0;timerRemaining=0;$('#timer-toggle').textContent='다시 시작';$('#timer-state').textContent='집중 시간이 끝났어요. 잠깐 쉬어가세요.';save('timer',{end:0,remaining:0});}}
const savedTimer=load('timer',null);if(savedTimer){timerEnd=savedTimer.end||0;timerRemaining=savedTimer.remaining??1500;$('#timer-toggle').textContent=timerEnd?'잠시 멈춤':'계속하기';$('#timer-state').textContent=timerEnd?'진행하던 집중 시간을 이어가고 있어요.':'준비되면 다시 이어가세요.';}setInterval(clock,250);clock();
$('#timer-length').onchange=()=>{timerEnd=0;timerRemaining=+$('#timer-length').value*60;$('#timer-toggle').textContent='시작';save('timer',{end:0,remaining:timerRemaining});clock();};
$('#timer-toggle').onclick=()=>{if(timerEnd){timerRemaining=Math.max(0,Math.ceil((timerEnd-Date.now())/1000));timerEnd=0;}else{if(timerRemaining===0)timerRemaining=+$('#timer-length').value*60;timerEnd=Date.now()+timerRemaining*1000;}$('#timer-toggle').textContent=timerEnd?'잠시 멈춤':'계속하기';$('#timer-state').textContent=timerEnd?'탭을 바꿔도 실제 시간을 기준으로 이어져요.':'준비되면 다시 이어가세요.';save('timer',{end:timerEnd,remaining:timerRemaining});clock();};
$('#timer-reset').onclick=()=>$('#timer-length').onchange();
window.addEventListener('keydown',e=>{if(e.key==='Escape'){if(!$('#memo-panel').hidden){saveNote();$('#memo-panel').hidden=true;}if(!$('#timer-panel').hidden)$('#timer-panel').hidden=true;focusHtml();}if(e.key.toLowerCase()==='n'&&!['TEXTAREA','INPUT','SELECT'].includes(document.activeElement.tagName)){e.preventDefault();openPanel('memo-panel');}});
window.addEventListener('pagehide',()=>{saveNote();save('timer',{end:timerEnd,remaining:timerRemaining});});
$('#retry').onclick=()=>location.reload();
$('#enter').onclick=async()=>{for(const c of contexts)if(c.state==='suspended')await c.resume();entered=true;$('#welcome').hidden=true;send('StartWebAudio');send('SetMusicVolume',$('#music-volume').value);send('SetFireVolume',$('#fire-volume').value);$('#unity-canvas').focus();resize();};
const script=document.createElement('script');script.src=LOFI_BUILD.loader;script.onload=()=>{resize();createUnityInstance($('#unity-canvas'),{...LOFI_BUILD.config,devicePixelRatio:1,showBanner:(msg,type)=>{if(type==='error'){$('#loading').textContent='불러오기에 실패했어요. 다시 시도해 주세요.';$('#retry').hidden=false;}}},p=>{$('#progress').value=p;$('#loading').textContent='방 준비 중 · '+Math.round(p*100)+'%';}).then(instance=>{unity=instance;$('#loading').textContent='방이 준비됐어요.';$('#enter').textContent='음악과 함께 들어가기';$('#enter').disabled=false;}).catch(error=>{$('#loading').textContent='방을 불러오지 못했어요. 다른 탭을 닫고 다시 시도해 주세요.';$('#retry').hidden=false;console.error(error);});};script.onerror=()=>{$('#loading').textContent='게임 파일을 받지 못했어요.';$('#retry').hidden=false;};document.body.appendChild(script);
