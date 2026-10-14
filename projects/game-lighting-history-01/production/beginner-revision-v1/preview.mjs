import {BeginnerLesson} from './lesson-renderer.mjs';
const [changes,story]=await Promise.all(['./changes.json','../animation-storyboard-v4.json'].map(p=>fetch(p).then(r=>r.json())));
const paragraphs=new Map(story.scenes.flatMap(s=>s.paragraphs.map(p=>[p.key,p])));
const rows=changes.rows.filter(r=>!r.key.startsWith('g')&&r.sceneDesign.renderer!=='Manim');
const sel=document.querySelector('#paragraph'),slider=document.querySelector('#frame'),out=document.querySelector('#output'),lesson=new BeginnerLesson(out,document.querySelector('#spatial'));
for(const r of rows){const op=document.createElement('option');op.value=r.key;op.textContent=r.key+' · '+r.beginnerGoal;sel.append(op);}
let frame=0,playing=false,last=0;
function draw(){const r=rows.find(r=>r.key===sel.value),p=paragraphs.get(r.key),u=frame/1000,sentences=r.ko.split(/(?<=[.?!])\s+/),sentence=sentences[Math.min(sentences.length-1,Math.floor(u*sentences.length))];const state=lesson.draw(p,r,frame,{frames:1001,actionStartFrame:220,actionEndFrame:850},sentence);document.querySelector('#script').textContent=r.ko;document.querySelector('#counter').textContent=Math.round(u*100)+'%';document.querySelector('#state').textContent=JSON.stringify({...state,preflightOnly:true,measuredSpeechBound:false},null,2);slider.value=frame;}
function choose(){playing=false;frame=0;lesson.model.kind=null;draw();}
sel.value='09b-p2';sel.onchange=choose;slider.oninput=()=>{playing=false;frame=+slider.value;draw();};document.querySelector('#start').onclick=()=>{playing=false;frame=0;draw();};document.querySelector('#end').onclick=()=>{playing=false;frame=1000;draw();};document.querySelector('#play').onclick=()=>{playing=!playing;last=performance.now();if(playing)requestAnimationFrame(tick);};function tick(t){if(!playing)return;frame=Math.min(1000,frame+(t-last)/16);last=t;draw();if(frame<1000)requestAnimationFrame(tick);else playing=false;}choose();
