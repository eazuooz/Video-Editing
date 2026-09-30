// Original playable experiments. Physics, collision, retries and outcomes are
// evaluated from keyboard input; recorded pictures are not a looping animation.
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
const mode=new URLSearchParams(location.search).get('mode')||'landing';
const keys=new Set();let time=0,last=0,frame=0;
window.inputLog=[];window.soundLog=[];window.outcomeLog=[];
const sound=(kind,lane)=>window.soundLog.push({time,kind,lane});
const control=(key,down)=>{if(keys.has(key)===down)return;down?keys.add(key):keys.delete(key);window.inputLog.push({time,key,down});};
addEventListener('keydown',e=>{if(['Space','ArrowRight','ArrowLeft','KeyD','KeyA'].includes(e.code)){e.preventDefault();control(e.code,true);}});
addEventListener('keyup',e=>control(e.code,false));
const count=mode==='variants'?3:2,width=1920/count;
const lanes=Array.from({length:count},(_,i)=>({i,x:90,y:728,vy:0,onGround:true,ready:true,state:'play',retryAt:0,attempt:1,success:0,failed:0,trail:[],lastJump:false}));
const names=mode==='landing'?['넓은 착지 공간','좁은 착지 공간']:mode==='retry'?['실패 후 바로 다시','실패 후 1.8초 대기']:mode==='variants'?['틈을 건너기','문이 열릴 때 통과','빛 신호일 때 이동']:['보고 · 선택하고','행동 · 결과 확인'];
function reset(p){p.x=mode==='variants'?[90,150,45][p.i]:90;p.y=728;p.vy=0;p.onGround=true;p.ready=true;p.state='play';p.attempt++;p.trail=[];}
function finish(p,ok){if(p.state!=='play')return;p.state=ok?'success':'failed';ok?p.success++:p.failed++;p.retryAt=time+(ok?1.05:mode==='retry'&&p.i===1?1.8:.18);window.outcomeLog.push({time,lane:p.i,attempt:p.attempt,success:ok,x:p.x});sound(ok?'success':'fail',p.i);}
function platforms(p){if(mode==='variants'&&p.i!==0)return [[32,width-40]];const target=mode==='landing'&&p.i===1?[width*.64,width*.77]:[width*.53,width*.91];return [[32,width*.30],target];}
function step(dt){
 time+=dt;frame++;
 for(const p of lanes){
  if(p.state!=='play'){if(time>=p.retryAt)reset(p);continue;}
  const right=keys.has('ArrowRight')||keys.has('KeyD'),left=keys.has('ArrowLeft')||keys.has('KeyA'),jump=keys.has('Space');
  const speed=mode==='variants'?260:350,dx=((right?1:0)-(left?1:0))*speed*dt;
  if(jump&&!p.lastJump&&p.onGround){p.vy=-700;p.onGround=false;p.ready=false;sound('jump',p.i);}
  p.lastJump=jump;const oldY=p.y;p.x=Math.max(35,p.x+dx);
  if(!p.onGround)p.vy+=1100*dt;p.y+=p.vy*dt;
  const supported=platforms(p).some(([a,b])=>p.x+18>a&&p.x-18<b);
  if(p.vy>=0&&oldY<=728&&p.y>=728&&supported){p.y=728;p.vy=0;if(!p.onGround)sound('land',p.i);p.onGround=true;}
  else if(p.onGround&&!supported)p.onGround=false;
  if(mode==='variants'&&p.i===1){const open=(time%4.4)>1.65&&(time%4.4)<3.45;if(p.x>width*.48&&p.x<width*.56&&!open){finish(p,false);continue;}}
  if(mode==='variants'&&p.i===2){const light=(time%4.4)>1.65&&(time%4.4)<3.45;if(p.x>width*.36&&p.x<width*.74&&Math.abs(dx)>.01&&!light){finish(p,false);continue;}}
  if(p.y>925)finish(p,false);else if(p.x>width*(mode==='landing'?.69:.86)&&p.onGround)finish(p,true);
  if(frame%4===0){p.trail.push([p.x,p.y]);if(p.trail.length>28)p.trail.shift();}
 }
}
const rect=(x,y,w,h,col)=>{ctx.fillStyle=col;ctx.fillRect(x,y,w,h);};
const text=(s,x,y,size=32,col='#f4f8fa',align='left')=>{ctx.fillStyle=col;ctx.font=`600 ${size}px "Malgun Gothic", sans-serif`;ctx.textAlign=align;ctx.textBaseline='middle';ctx.fillText(s,x,y);};
function draw(){
 const sky=ctx.createLinearGradient(0,0,0,1080);sky.addColorStop(0,'#20394e');sky.addColorStop(1,'#345969');rect(0,0,1920,1080,sky);
 text('직접 만든 플레이테스트',48,54,30,'#a4ceda');text(mode==='landing'?'착지 폭 하나만 바꾸기':mode==='retry'?'재시도 대기 하나만 바꾸기':mode==='variants'?'같은 도형 · 다른 규칙':'한 번의 플레이를 기록하기',48,121,58);
 text('SPACE 점프    ← → 이동    동일한 입력으로 실제 실행',48,183,27,'#b8d0da');
 for(const p of lanes){
  const ox=p.i*width;ctx.save();ctx.beginPath();ctx.rect(ox,220,width,640);ctx.clip();
  for(let j=0;j<8;j++){const x=ox+((j*170+p.i*43)%width);rect(x,495+Math.sin(j*2)*28,110,335,'#2b495a');rect(x+8,501+Math.sin(j*2)*28,8,120,'#365969');}
  text(names[p.i],ox+width/2,264,mode==='variants'?35:42,'#f4f8fa','center');
  text(`시도 ${p.attempt}   성공 ${p.success}   실패 ${p.failed}`,ox+width/2,322,28,'#b9d6df','center');
  for(const [a,b]of platforms(p)){rect(ox+a+12,789,b-a,38,'#172f3e');rect(ox+a,752,b-a,40,'#8aa8a7');rect(ox+a,752,b-a,9,'#bad0bc');for(let x=a;x<b;x+=48)rect(ox+x,790,2,48,'#486f72');}
  if(mode==='variants'&&p.i===1){const open=(time%4.4)>1.65&&(time%4.4)<3.45,h=open?68:225;rect(ox+width*.5,752-h,32,h,'#e7b768');rect(ox+width*.5-8,494,48,22,open?'#8ee0b9':'#e5917e');text(open?'열림':'닫힘',ox+width*.5+16,456,28,open?'#a2ead0':'#f1aa9f','center');}
  if(mode==='variants'&&p.i===2){const lit=(time%4.4)>1.65&&(time%4.4)<3.45;rect(ox+width*.36,368,width*.38,390,lit?'#527d73':'#36535d');text(lit?'이동 가능':'기다리기',ox+width*.55,417,31,lit?'#c5f0d2':'#d0dbe0','center');}
  ctx.globalAlpha=.20;for(const [x,y]of p.trail)rect(ox+x-16,y-34,32,32,'#a8dced');ctx.globalAlpha=1;
  if(p.state==='play'){
   rect(ox+p.x-22+8,759,44,9,'#17353f');rect(ox+p.x-22,p.y-44,44,44,p.i===1?'#e2b56a':'#78bfd5');rect(ox+p.x-22,p.y-44,44,7,p.i===1?'#f0d49d':'#b6e2ee');rect(ox+p.x+1,p.y-29,5,6,'#14333e');rect(ox+p.x+12,p.y-29,5,6,'#14333e');
  }else{const wait=Math.max(0,p.retryAt-time);text(p.state==='success'?'도착!':wait>.3?`재시도까지 ${wait.toFixed(1)}초`:'다시 시도',ox+width/2,587,43,p.state==='success'?'#b7e4c8':'#e5bbad','center');}
  rect(ox+width*(mode==='landing'?.69:.87),644,4,108,'#d5e8db');rect(ox+width*(mode==='landing'?.69:.87)+4,647,38,27,'#93d4b4');
  ctx.restore();if(p.i)rect(ox-2,225,4,635,'#658593');
 }
 text('입력',48,854,27,'#b8d0da');['ArrowLeft','ArrowRight','Space'].forEach((key,i)=>{const on=keys.has(key);rect(155+i*210,832,188,47,on?'#c4ded2':'#264656');text(['←','→','SPACE'][i],249+i*210,856,27,on?'#173b36':'#b8d0da','center');});
}
window.captureStep=(t)=>{while(time+1/120<t)step(1/60);draw();};
function tick(now){if(!window.recording){const dt=Math.min((now-last)/1000,1/30);step(dt||1/60);draw();}last=now;requestAnimationFrame(tick);}requestAnimationFrame(tick);
