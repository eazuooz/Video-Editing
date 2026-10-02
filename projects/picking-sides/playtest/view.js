const game=Cloudpost, canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
let state=game.create(7), last=performance.now(), camX=0, scale=1, input={right:false};
const params=new URLSearchParams(location.search);
if(params.get('capture')==='1')document.body.classList.add('capture');
const requestedSeed=Number(params.get('seed'));if(Number.isInteger(requestedSeed)&&params.has('seed'))state=game.create(requestedSeed);
function polygon(points,color){ctx.fillStyle=color;ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fill();}
function round(x,y,w,h,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill();}
function text(v,x,y,size=24,color='#234747',align='left',weight=600){ctx.font=`${weight} ${size}px 'Malgun Gothic',sans-serif`;ctx.textAlign=align;ctx.fillStyle=color;ctx.fillText(v,x,y);}
function ellipse(x,y,rx,ry,color){ctx.fillStyle=color;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,Math.PI*2);ctx.fill();}
function tree(x,y,size=1){ctx.save();ctx.translate(x,y);ctx.scale(size,size);ellipse(0,20,36,10,'#4c736544');round(-7,-55,14,74,3,'#7c6449');ellipse(-19,-61,32,36,'#46785e');ellipse(21,-70,31,34,'#5e9770');ellipse(0,-98,33,36,'#6b9d75');ctx.restore();}
function world(){
  const sky=ctx.createLinearGradient(0,0,0,1080);sky.addColorStop(0,'#cce7ec');sky.addColorStop(1,'#eaf1df');ctx.fillStyle=sky;ctx.fillRect(0,0,1920,1080);
  for(let i=0;i<10;i++){const x=((i*371-state.time*7-camX*.045)%2380+2380)%2380-200;ellipse(x,150+i%3*135,150,33,'#ffffff66');ellipse(x+45,130+i%3*135,90,36,'#ffffff66');}
  polygon([[0,520],[210,310],[410,480],[700,240],[930,500],[1220,330],[1550,520],[1740,345],[1920,480],[1920,800],[0,800]],'#a2c7bf');
  polygon([[0,640],[290,440],[520,640],[910,405],[1190,640],[1620,440],[1920,650],[1920,1000],[0,1000]],'#84ada5');
  ctx.save();ctx.translate(180-camX*scale,540*(1-scale));ctx.scale(scale,scale);
  // The race occupies the upper/middle picture; y=885..1055 remains caption-safe.
  polygon([[-130,715],[game.finish+380,715],[game.finish+260,850],[-70,830]],'#647e77');
  polygon([[-130,380],[game.finish+380,380],[game.finish+380,715],[-130,715]],'#8aac72');
  polygon([[1780,388],[2110,402],[2530,390],[3080,410],[3015,704],[2520,688],[2070,708],[1820,689]],'#5d9da3');
  for(let i=0;i<3;i++){const yy=540+(i-1)*96;round(-90,yy-29,1940,58,12,'#d8cbab');round(3030,yy-29,game.finish-2670,58,12,'#d8cbab');if(i!==1){round(1820,yy-(i===0?17:24),1230,i===0?34:48,4,'#bb9771');for(let x=1840;x<3030;x+=38){ctx.fillStyle='#e4c797';ctx.fillRect(x,yy-(i===0?16:23),6,i===0?32:46);}}}
  // A separate wide leaf route bends around the narrow central rocks.
  ctx.strokeStyle='#8b755e';ctx.lineWidth=69;ctx.beginPath();ctx.moveTo(1850,540);ctx.bezierCurveTo(2180,440,2700,440,3030,540);ctx.stroke();
  ctx.strokeStyle='#e0c5a0';ctx.lineWidth=58;ctx.stroke();
  for(let x=1860;x<3020;x+=36){const y=540-Math.sin((x-1850)/1180*Math.PI)*70;ctx.strokeStyle='#a68a68';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(x,y-26);ctx.lineTo(x,y+26);ctx.stroke();}
  for(let x=1900;x<2900;x+=120){const y=650+Math.sin(x*.027+state.time*1.4)*8;ctx.strokeStyle='#c2e6d944';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(x+62,y);ctx.stroke();}
  for(let x=160;x<game.finish;x+=270){ellipse(x,695,12,3,'#6b9565');ctx.fillStyle='#8aa674';ctx.fillRect(x,690,3,11);}
  for(const x of game.obstacles)for(let i=0;i<3;i++){const p={x,id:game.identities[i].id,lane:i-1},y=game.routeY(p);ellipse(x,y+7,31,12,'#756d5555');polygon([[x-25,y-8],[x+10,y-17],[x+27,y-3],[x-6,y+6]],'#bf7654');polygon([[x-25,y-8],[x-6,y+6],[x-6,y-30],[x-25,y-44]],'#a66248');polygon([[x-6,y+6],[x+27,y-3],[x+27,y-39],[x-6,y-30]],'#c98a60');polygon([[x-25,y-44],[x+9,y-54],[x+27,y-39],[x-6,y-30]],'#dbac75');}
  for(let x=490;x<game.finish;x+=570){tree(x,380,.85);if(x%2===0)tree(x+100,725,.7);}
  // Three finish gates and a post office are part of the world, not a scoreboard.
  ctx.fillStyle='#f4edc9';ctx.fillRect(game.finish-5,378,12,337);
  for(let y=380;y<715;y+=24){ctx.fillStyle=y%48<24?'#355f59':'#f9f5df';ctx.fillRect(game.finish-11,y,24,24);}
  round(game.finish+95,413,178,188,10,'#ede7d0');polygon([[game.finish+80,423],[game.finish+186,347],[game.finish+290,423]],'#bf7155');round(game.finish+152,497,62,104,3,'#547d72');text('POST',game.finish+183,474,28,'#487469','center');
  const sorted=[...state.racers].sort((a,b)=>game.routeY(a)-game.routeY(b));
  for(const p of sorted){
    const y=game.routeY(p),x=p.x,bob=p.finishTime===null&&state.phase==='racing'?Math.sin(state.time*18+p.lane)*3:0;
    ellipse(x,y+12,27-p.height*.1,10,'#314e4544');
    if(p.id===state.selected){ctx.strokeStyle='#ffe274';ctx.lineWidth=5;ctx.beginPath();ctx.ellipse(x,y+10,36,15,0,0,Math.PI*2);ctx.stroke();}
    ctx.save();ctx.translate(x,y-p.height+bob);let color=state.markers?p.color:'#789697';
    const stride=Math.sin(state.time*18+p.lane)*8*(state.phase==='racing'?1:0);
    round(-19,-7,12,24+stride,4,'#294c55');round(6,-7,12,24-stride,4,'#294c55');
    round(-27,-58,54,56,13,color);round(-20,-84,40,37,12,'#e4ded0');round(-15,-76,30,15,6,'#345259');ellipse(-7,-69,3,3,'#fbf9e7');ellipse(7,-69,3,3,'#fbf9e7');
    round(-33,-43,11,28,4,color);round(22,-43,11,28,4,color);round(-16,-35,32,22,3,'#f5edce');polygon([[-16,-35],[0,-23],[16,-35]],'#c9b98d');
    if(state.markers){text(p.emblem,0,-91,33,p.color,'center');round(-36,-128,72,27,8,'#ffffffe8');text(p.name,0,-108,18,'#294646','center');}
    if(p.stun>0){text('✦',-34,-53,26,'#ffd866','center');text('✧',34,-71,22,'#fff1b3','center');}
    ctx.restore();
  }
  // A foreground canopy creates a genuine brief occlusion away from the subtitle strip.
  for(const x of [1630,3680,5620])tree(x,637,1.05);
  ctx.restore();
  round(45,35,404,92,15,'#ffffffe8');text('CLOUDPOST RELAY',69,74,27);text('구름섬 우편 경주 · 자체 플레이테스트',69,108,20,'#5b7c75');
  const selected=state.racers.find(p=>p.id===state.selected);round(1374,35,501,92,15,'#ffffffe8');text(selected?`${selected.emblem} ${selected.name} 배달원 따라가는 중`:'전체 관전 · 선택하지 않아도 괜찮아요',1397,76,23);text(state.cameraMode==='follow'?'대상과 앞쪽 경로 함께 보기':'전체 경로 보기',1397,108,19,'#5b7c75');
  if(state.phase==='ready'){
    round(457,167,1006,125,20,'#fffffff0');text('누구의 배달을 따라가 볼까요?',960,210,31,'#244941','center');
    state.racers.forEach((p,i)=>{text(`${p.emblem} ${p.name} · ${p.style}`,650+i*309,258,22,p.color,'center');});
  }
  if(state.phase==='paused'){round(764,164,392,68,15,'#ffffffe8');text('경주 일시정지',960,208,29,'#264e45','center');}
  if(state.phase==='finished'){
    const order=[...state.racers].sort((a,b)=>a.finishTime-b.finishTime);round(532,158,856,84,18,'#ffffffe8');text('결승선 도착  '+order.map((p,i)=>`${i+1}. ${p.emblem}${p.name}`).join('   '),960,211,28,'#294d45','center');
  }
}
function frame(now){const dt=Math.min(.05,(now-last)/1000);last=now;let left=dt;while(left>0){const n=Math.min(left,1/60);game.tick(state,n,input);left-=n;}
 const target=state.racers.find(p=>p.id===state.selected)||[...state.racers].sort((a,b)=>b.x-a.x)[0];
 const targetScale=state.cameraMode==='overview'?.245:1;scale+=(targetScale-scale)*Math.min(1,dt*4);
 const targetX=state.cameraMode==='overview'?-70:Math.max(-50,Math.min(game.finish-1300,target.x-470));camX+=(targetX-camX)*Math.min(1,dt*4);
 world();document.querySelector('#status').textContent=`${state.phase} · ${state.time.toFixed(1)}초 · 충돌 ${state.racers.reduce((n,p)=>n+p.hits,0)}회 · 선택은 승패 계산에 영향 없음`;
 requestAnimationFrame(frame);
}
document.querySelectorAll('[data-action]').forEach(b=>b.addEventListener('click',()=>{game.act(state,b.dataset.action,b.dataset.value);if(b.dataset.action==='select'&&b.dataset.value)game.act(state,'camera','follow');}));
document.querySelector('#markers').onclick=e=>{game.act(state,'markers',!state.markers);e.currentTarget.setAttribute('aria-pressed',String(state.markers));};
document.querySelector('#auto').onclick=e=>{game.act(state,'auto',!state.auto);e.currentTarget.setAttribute('aria-pressed',String(state.auto));};
document.querySelector('#restart').onclick=()=>{state=game.create(state.seed+1);};
addEventListener('keydown',e=>{if(['Space','ArrowRight'].includes(e.code))e.preventDefault();if(e.code==='ArrowRight')input.right=true;if(e.repeat)return;const n=Number(e.key);if(n>=1&&n<=3){game.act(state,'select',game.identities[n-1].id);game.act(state,'camera','follow');}if(e.code==='Space')game.act(state,'jump');if(e.code==='Enter')game.act(state,'start');if(e.code==='KeyO')game.act(state,'camera','overview');if(e.code==='KeyF')game.act(state,'camera','follow');if(e.code==='KeyM')game.act(state,'markers',!state.markers);if(e.code==='KeyP')game.act(state,'pause');});
addEventListener('keyup',e=>{if(e.code==='ArrowRight')input.right=false;});
// Read-only state export for local capture receipts; test inputs use the visible controls.
window.cloudpostSnapshot=()=>structuredClone(state);
requestAnimationFrame(frame);
