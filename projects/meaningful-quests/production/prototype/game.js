// Original interactive mechanics: these pictures are drawn from real keyboard
// movement, pickups, inventory, delivery and collision state, not a video loop.
const canvas=document.querySelector('canvas'),c=canvas.getContext('2d'),mode=new URLSearchParams(location.search).get('mode')||'comparison';
const keys=new Set();let time=0,last=0,stepCount=0;
window.inputLog=[];window.soundLog=[];window.outcomeLog=[];
const lanes=Array.from({length:mode==='comparison'?2:1},(_,i)=>({i,x:150,y:180,inventory:0,score:0,delivered:false,bridge:mode==='shortcut',bonus:false,items:[{x:600,y:100,taken:false},{x:600,y:180,taken:false},{x:600,y:260,taken:false}],blocked:false,trail:[],lastE:false,lastQ:false}));
const event=(p,kind,extra={})=>{window.outcomeLog.push({time,lane:p.i,kind,x:+p.x.toFixed(2),y:+p.y.toFixed(2),inventory:p.inventory,...extra});window.soundLog.push({time,lane:p.i,kind});};
function control(e,down){if(['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','KeyE','KeyQ'].includes(e.code)){e.preventDefault();if(keys.has(e.code)!==down){down?keys.add(e.code):keys.delete(e.code);window.inputLog.push({time,key:e.code,down});}}}
addEventListener('keydown',e=>control(e,true));addEventListener('keyup',e=>control(e,false));
function blocked(p,x,y){if(x<45||x>760||y<45||y>390)return true;const river=x>420&&x<470&&y<330;const bridge=p.bridge&&y>155&&y<205;if(river&&!bridge)return true;if(mode==='shortcut'&&x>375&&x<407&&y>155&&y<205&&p.inventory>0)return true;return false;}
function step(dt){time+=dt;stepCount++;
 for(const p of lanes){
  let dx=(keys.has('ArrowRight')?1:0)-(keys.has('ArrowLeft')?1:0),dy=(keys.has('ArrowDown')?1:0)-(keys.has('ArrowUp')?1:0);const n=Math.hypot(dx,dy)||1;dx=dx/n*200*dt;dy=dy/n*200*dt;
  let hit=false;if(!blocked(p,p.x+dx,p.y))p.x+=dx;else hit=Math.abs(dx)>.01;if(!blocked(p,p.x,p.y+dy))p.y+=dy;else hit=hit||Math.abs(dy)>.01;
  if(hit&&!p.blocked)event(p,'blocked',{reason:mode==='shortcut'&&p.inventory?'inventory-gate':'river'});p.blocked=hit;
  for(const it of p.items)if(!it.taken&&Math.hypot(p.x-it.x,p.y-it.y)<28){it.taken=true;p.inventory++;event(p,'pickup');}
  const e=keys.has('KeyE'),q=keys.has('KeyQ');
  if(e&&!p.lastE&&p.inventory>=3&&Math.hypot(p.x-150,p.y-180)<42&&!p.delivered){p.inventory-=3;p.score+=50;p.delivered=true;if(mode!=='comparison'||p.i===1){p.bridge=true;event(p,'bridge-open',{collisionChanged:true});}event(p,'delivery',{score:p.score});}
  if(q&&!p.lastQ&&p.inventory){p.inventory=0;event(p,'drop-items',{gateNowPassable:mode==='shortcut'});}p.lastE=e;p.lastQ=q;
  if(p.bridge&&p.delivered&&!p.bonus&&p.x>580&&Math.abs(p.y-180)<50){p.bonus=true;event(p,'new-area-reached');}
  if(stepCount%5===0){p.trail.push([p.x,p.y]);if(p.trail.length>22)p.trail.shift();}
 }
}
const rect=(x,y,w,h,col)=>{c.fillStyle=col;c.fillRect(x,y,w,h);};
const text=(s,x,y,size=28,col='#20342b',align='left')=>{c.fillStyle=col;c.font=`700 ${size}px "Malgun Gothic",sans-serif`;c.textAlign=align;c.textBaseline='middle';c.fillText(s,x,y);};
function box(x,y,w,h,depth,col){rect(x+7,y+10,w,h,'#8da793');rect(x+w,y-depth,w*.13,h+depth,'#739b7a');rect(x,y-depth,w,h+depth,col);rect(x,y-depth,w,8,'#ffffff66');}
function tree(x,y,size){c.fillStyle='#97b99666';c.beginPath();c.ellipse(x+8,y+10,size*.7,size*.23,0,0,Math.PI*2);c.fill();rect(x-5,y-size*.75,10,size*.8,'#977956');c.fillStyle='#4c8656';c.beginPath();c.moveTo(x-size*.62,y-10);c.lineTo(x,y-size*1.7);c.lineTo(x+size*.62,y-10);c.fill();c.fillStyle='#74a869';c.beginPath();c.moveTo(x-size*.4,y-size*.35);c.lineTo(x,y-size*1.55);c.lineTo(x,y-10);c.fill();}
function draw(){
 const bg=c.createLinearGradient(0,0,0,1080);bg.addColorStop(0,'#f9fcf5');bg.addColorStop(1,'#e4eee0');rect(0,0,1920,1080,bg);
 text('ORIGINAL PLAYTEST  /  BRIDGE DELIVERY LAB',50,45,24,'#5b8066');
 text(mode==='comparison'?'같은 배달, 완료 뒤의 변화 비교':mode==='shortcut'?'짧은 길의 조건: 빈 가방':'물건 세 개를 모아 다리를 고치기',50,105,48);
 text('방향키 이동   E 전달   Q 물건 내려놓기   ·   실제 입력 / 충돌 / 상태 변화',50,164,26,'#5b7560');
 for(const p of lanes){
  const width=mode==='comparison'?900:960,scale=width/800,ox=mode==='comparison'?55+p.i*955:480,oy=320;
  text(mode==='comparison'?(p.i?'B · 같은 보상 + 다리 연결':'A · 점수 보상만'):mode==='shortcut'?'빠른 길은 빈 가방만 / 물건을 들면 아래 우회로':'이동 → 채집 → 전달 → 새 길',ox,239,32,p.i?'#245d45':'#355f81');
  text(`나무 ${p.inventory}/3    점수 ${p.score}    ${p.delivered?'부탁 완료':'채집 중'}`,ox,286,28);
  c.save();c.translate(ox,oy);c.scale(scale,scale);
  rect(0,0,800,430,'#b8d39f');rect(8,14,784,408,'#cde2b5');
  for(let j=0;j<40;j++){const x=(j*191+53)%800,y=(j*71+31)%425;c.fillStyle='#b5cc96';c.beginPath();c.ellipse(x,y,7,2,0,0,Math.PI*2);c.fill();}
  const river=c.createLinearGradient(420,0,475,0);river.addColorStop(0,'#65b7ca');river.addColorStop(.5,'#8bc7d6');river.addColorStop(1,'#5aabc2');rect(420,0,50,330,river);
  for(let j=0;j<12;j++){const y=(j*31+time*19)%326;rect(432+Math.sin(j+time)*6,y,21,2,'#c4edf0');}
  rect(120,345,530,28,'#dec89d');rect(136,176,27,192,'#dec89d');rect(586,86,27,285,'#dec89d');
  for(const [x,y]of [[55,90],[735,75],[690,320],[80,325],[335,65],[520,60]])tree(x,y,23);
  // Cabin, original carpenter NPC and delivery spot.
  box(73,143,57,34,28,'#d2b382');c.fillStyle='#7c6351';c.beginPath();c.moveTo(65,113);c.lineTo(101,85);c.lineTo(139,113);c.fill();
  box(135,191,23,25,15,'#cba774');text('E',153,141,21,'#285f42','center');
  if(p.bridge){rect(407,153,72,62,'#987448');for(let x=413;x<477;x+=10)rect(x,151,6,58,'#d9b985');rect(403,145,79,6,'#694f3c');rect(403,210,79,6,'#694f3c');}
  else{rect(406,156,19,51,'#a8895b');rect(467,156,16,51,'#a8895b');text('끊어진 다리',443,125,20,'#456869','center');}
  if(mode==='shortcut'){box(376,198,25,30,37,p.inventory?'#bd7461':'#96b977');text(p.inventory?'가방을 비우세요':'통과 가능',390,118,20,p.inventory?'#9e4d3b':'#285f42','center');}
  for(const it of p.items)if(!it.taken){box(it.x-12,it.y+6,24,12,10,'#bd9361');rect(it.x-10,it.y-7,4,15,'#e6cda8');}
  if(p.bridge&&p.delivered){box(644,210,47,22,25,'#ddb568');text('새 장소',665,144,22,'#5b733e','center');}
  c.globalAlpha=.22;for(const [x,y]of p.trail)rect(x-8,y-10,16,16,'#296a77');c.globalAlpha=1;
  c.fillStyle='#6b835955';c.beginPath();c.ellipse(p.x+5,p.y+6,15,6,0,0,Math.PI*2);c.fill();box(p.x-11,p.y,22,20,18,p.i?'#d7a34d':'#4c92ad');rect(p.x-7,p.y-22,16,11,'#f5ddb4');rect(p.x-9,p.y-29,19,8,'#527d5d');rect(p.x+5,p.y-20,3,3,'#20342b');
  c.restore();
 }
 text('입력',52,850,24,'#557762');['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','KeyE','KeyQ'].forEach((k,i)=>{rect(130+i*120,826,103,43,keys.has(k)?'#315f48':'#d7e5cc');text(['←','→','↑','↓','E','Q'][i],181+i*120,848,25,keys.has(k)?'white':'#557762','center');});
 text('자동 입력은 동작 검증용입니다. 재미 평가는 인간 플레이테스트가 필요합니다.',1900,850,22,'#557762','right');
}
window.captureStep=t=>{while(time+1/120<t)step(1/60);draw();};
window.testState=()=>lanes.map(p=>({x:p.x,y:p.y,inventory:p.inventory,score:p.score,delivered:p.delivered,bridge:p.bridge,bonus:p.bonus}));
function tick(now){if(!window.recording){step(Math.min((now-last)/1000,1/30)||1/60);draw();}last=now;requestAnimationFrame(tick);}requestAnimationFrame(tick);
