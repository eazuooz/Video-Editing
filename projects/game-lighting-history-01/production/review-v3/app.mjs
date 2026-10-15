import {Lesson} from './lesson.mjs';
await document.fonts.load("500 48px 'YamYamCaptionMedium'");await document.fonts.ready;
const [design,plan]=await Promise.all(['design.json','measured-scene-plan.json'].map(p=>fetch(p).then(r=>r.json())));
if(!plan.currentVoiceReviewed||!plan.sentenceBoundariesDirectlyReviewed)throw Error('Current voice review is pending');
const rows=new Map(design.rows.map(r=>[r.key,r])),blocks=new Map(plan.scenes.map(b=>[b.key,b]));
const sel=document.querySelector('#paragraph'),slider=document.querySelector('#frame'),state=document.querySelector('#state'),out=document.querySelector('#output'),lesson=new Lesson(out,document.querySelector('#spatial'));
for(const p of plan.scenes){const o=document.createElement('option');o.value=p.key;o.textContent=p.key+' · '+rows.get(p.key).title;sel.append(o);}
let f=0,playing=false,last=0,showCaptions=true;
function draw(){const b=blocks.get(sel.value),cue=showCaptions?b.koCues.find(c=>c.seconds[0]<=f/60&&f/60<c.seconds[1]):null;state.textContent=JSON.stringify(lesson.draw(rows.get(sel.value),b,f,cue),null,2);slider.value=f;}
function choose(){playing=false;f=0;slider.max=blocks.get(sel.value).frames-1;draw();}
sel.onchange=choose;slider.oninput=()=>{playing=false;f=+slider.value;draw();};document.querySelector('#start').onclick=()=>{playing=false;f=0;draw();};document.querySelector('#end').onclick=()=>{playing=false;f=blocks.get(sel.value).frames-1;draw();};
function tick(t){if(!playing)return;const n=Math.floor((t-last)*.06);if(n){f=Math.min(blocks.get(sel.value).frames-1,f+n);last+=n/.06;draw();}if(f<blocks.get(sel.value).frames-1)requestAnimationFrame(tick);else playing=false;}
document.querySelector('#play').onclick=()=>{playing=!playing;last=performance.now();if(playing)requestAnimationFrame(tick);};choose();
async function send(op,key,body){const r=await fetch(`http://127.0.0.1:9295/${op}?key=${encodeURIComponent(key)}`,{method:'POST',body});if(!r.ok)throw Error(await r.text());return r.json();}
async function exportOne(){playing=false;showCaptions=false;const key=sel.value,b=blocks.get(key),controls=[...document.querySelectorAll('button,select,input')];controls.forEach(x=>x.disabled=true);let encoder;try{
 const config={codec:'avc1.64002a',width:1920,height:1080,bitrate:18000000,framerate:60,hardwareAcceleration:'prefer-hardware',avc:{format:'annexb'},latencyMode:'realtime'};
 if(!(await VideoEncoder.isConfigSupported(config)).supported)throw Error('Encoder unavailable');await send('start',key,'{}');let chunks=[],error=null;
 encoder=new VideoEncoder({output:c=>{const a=new Uint8Array(c.byteLength);c.copyTo(a);chunks.push(a);},error:e=>error=e});encoder.configure(config);
 for(f=0;f<b.frames;f++){draw();const vf=new VideoFrame(out,{timestamp:Math.round(f*1e6/60),duration:Math.round((f+1)*1e6/60)-Math.round(f*1e6/60)});encoder.encode(vf,{keyFrame:f%120===0});vf.close();if(f%60===59||f===b.frames-1){await encoder.flush();if(error)throw error;const a=new Uint8Array(chunks.reduce((n,c)=>n+c.length,0));let j=0;for(const c of chunks){a.set(c,j);j+=c.length;}chunks=[];await send('chunk',key,a);await new Promise(requestAnimationFrame);}}
 encoder.close();await send('finish',key,JSON.stringify({frames:b.frames}));return true;
 }catch(e){state.textContent=String(e);return false;}finally{if(encoder?.state!=='closed')encoder?.close();showCaptions=true;controls.forEach(x=>x.disabled=false);}}
document.querySelector('#export').onclick=exportOne;
document.querySelector('#batch').onclick=async()=>{const s=await fetch('http://127.0.0.1:9295/status').then(r=>r.json());if(s.active)throw Error('A scene is already rendering');for(const p of plan.scenes){if(s.completed.some(c=>c.key===p.key))continue;sel.value=p.key;choose();if(!await exportOne())return;}state.textContent='선택 장면 렌더 완료 · 최종 합성/검수/업로드는 별도';};
