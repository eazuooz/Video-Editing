// Original executable test. Keyboard input, independent pose/collision clocks,
// actual rectangle collision, accepted/blocked inputs and tick boundaries.
// Input acceptance is elapsed tick 0; hit starts after 12 intervals, at tick 12.
// This convention is explicitly ours, not a claim about commercial move data.
const canvas=document.querySelector('canvas'),ctx=canvas.getContext('2d');
const params=new URLSearchParams(location.search),mode=params.get('mode')||'interval';
window.recording=params.has('capture');
const names={rate:'12눈금 · 기준 속도만 바꾸기',interval:'기본 공격(B)과 준비를 줄인 수정안(A)',poses:'그림 수와 판정 시계 분리',pause:'충돌 뒤 전투 시계만 멈추기',render:'화면은 30 / 60 · 판정은 같은 60'};
const keys=new Set();window.inputLog=[];window.outcomeLog=[];window.soundLog=[];
let wallTick=0,seconds=0;
const panels=[0,1].map(i=>({id:i,ruleHz:mode==='rate'&&i===1?30:60,displayHz:mode==='render'&&i===0?30:60,poseCount:mode==='poses'?(i?8:2):4,startup:12,active:3,recovery:15,pauseTicks:mode==='pause'&&i===1?4:0,x:240,target:410,attack:null,last:null,attackCount:0,hitCount:0,blockedCount:0,poseSnapshot:null,history:[]}));
function log(kind,p,extra={}){const e={kind,panel:p.id,wallTick,wallSeconds:wallTick/60,...extra};window.outcomeLog.push(e);p.history.push(e);return e;}
function begin(p){if(p.attack){p.blockedCount++;log('input-blocked',p,{combatTick:p.attack.tick});return;}p.attack={id:++p.attackCount,startWall:wallTick,tick:0,pauseLeft:0,hit:false,startup:p.startup,active:p.active,recovery:p.recovery,pauseTicks:p.pauseTicks};log('input-accepted',p,{attackId:p.attack.id,startup:p.startup,referenceHz:p.ruleHz,poseCount:p.poseCount,displayHz:p.displayHz,pauseTicks:p.pauseTicks});window.soundLog.push({time:wallTick/60,kind:'input'});}
document.addEventListener('keydown',e=>{e.preventDefault();if(e.repeat)return;keys.add(e.code);window.inputLog.push({kind:'down',code:e.code,wallTick,time:wallTick/60});
 if(e.code==='Space')panels.forEach(begin);
 if(mode==='interval'&&e.code==='Digit1')panels[0].startup=6;
 if(mode==='interval'&&e.code==='Digit2')panels[0].startup=12;
 if(mode==='poses'&&e.code==='Digit3')panels[0].poseCount=panels[0].poseCount===2?8:2;
 if(mode==='pause'&&e.code==='Digit4')panels[0].pauseTicks=panels[0].pauseTicks===0?4:0;
 if(e.code==='KeyT')panels.forEach(p=>p.target=p.x+110);
 if(e.code==='KeyM')panels.forEach(p=>p.target=p.x+380);
});
document.addEventListener('keyup',e=>{keys.delete(e.code);window.inputLog.push({kind:'up',code:e.code,wallTick,time:wallTick/60});});
function advance(){wallTick++;seconds=wallTick/60;for(const p of panels){
 if(keys.has('ArrowRight'))p.x=Math.min(610,p.x+3);if(keys.has('ArrowLeft'))p.x=Math.max(120,p.x-3);
 if(p.ruleHz===30&&wallTick%2)continue;
 const a=p.attack;if(!a)continue;
 if(a.pauseLeft>0){a.pauseLeft--;log('combat-clock-paused',p,{attackId:a.id,combatTick:a.tick,remaining:a.pauseLeft});continue;}
 a.tick++;
 if(a.tick===a.startup)log('hit-area-begins',p,{attackId:a.id,combatTick:a.tick,elapsedSeconds:(wallTick-a.startWall)/60});
 const active=a.tick>=a.startup&&a.tick<a.startup+a.active;
 // Attack rectangle [x+24,x+174] versus target [target-28,target+28].
 const collides=p.x+24<p.target+28&&p.x+174>p.target-28;
 if(active&&collides&&!a.hit){a.hit=true;p.hitCount++;log('collision',p,{attackId:a.id,combatTick:a.tick,elapsedSeconds:(wallTick-a.startWall)/60});a.pauseLeft=a.pauseTicks;window.soundLog.push({time:wallTick/60,kind:'hit'});}
 if(a.tick>=a.startup+a.active+a.recovery){p.last={...a,endWall:wallTick,elapsedSeconds:(wallTick-a.startWall)/60};log('action-ready',p,{attackId:a.id,combatTick:a.tick,elapsedSeconds:p.last.elapsedSeconds,hit:a.hit});p.attack=null;}
 }}
const colors={ink:'#172832',muted:'#6a7c83',blue:'#2d639e',green:'#386750',orange:'#cd985d',pale:'#eef3f4'};
function rect(x,y,w,h,col){ctx.fillStyle=col;ctx.fillRect(x,y,w,h);}
function text(s,x,y,size=26,col=colors.ink,align='left',weight=600){ctx.fillStyle=col;ctx.font=`${weight} ${size}px "Malgun Gothic",sans-serif`;ctx.textAlign=align;ctx.textBaseline='middle';ctx.fillText(s,x,y);}
function draw(){rect(0,0,1920,1080,'#fff');rect(0,0,1920,12,'#ffd823');text('FRAME TIMING LAB · 직접 만든 입력 / 충돌 테스트',65,66,29,colors.muted);text(names[mode],65,123,50);
 text('SPACE 공격   ← → 이동   T 타깃 가까이   M 타깃 멀리',65,182,27);text(mode==='interval'?'1 준비 6   2 준비 12 · 나머지 판정 / 회복 동일':mode==='poses'?'3 A의 그림 수만 변경 · 준비 / 판정 / 회복 동일':mode==='pause'?'4 A의 충돌 멈춤만 변경 · 배경은 계속 진행':'입력 / 판정 데이터 동일 · 표시된 기준 속도만 비교',65,224,24,colors.muted);
 text(`실제 경과 ${seconds.toFixed(2)}s · 배경 시계 ${wallTick}`,1845,67,27,colors.blue,'right');
 for(const p of panels){const ox=65+p.id*925,w=865;rect(ox+9,281,w,505,'#d7e3e5');rect(ox,272,w,505,'#f7f9f9');rect(ox,272,w,6,p.id?colors.green:colors.blue);
 const label=mode==='rate'?`${p.ruleHz}번 / 초`:mode==='poses'?`${p.poseCount}개 그림`:mode==='pause'?`${p.pauseTicks}눈금 멈춤`:mode==='render'?`화면 ${p.displayHz} / 규칙 ${p.ruleHz}`:`준비 ${p.startup} / 판정 3 / 회복 15`;
 text(`${p.id?'B':'A'}${mode==='interval'?(p.id?' 기본':' 수정안'):''} · ${label}`,ox+26,311,30,p.id?colors.green:colors.blue);
 const a=p.attack||p.last;let tick=a?a.tick:0,total=a?a.startup+a.active+a.recovery:p.startup+p.active+p.recovery;
 if(p.displayHz===60||wallTick%2===0||!p.poseSnapshot)p.poseSnapshot={x:p.x,tick,a:a?{...a}:null};const shown=p.poseSnapshot,sa=shown.a;
 rect(ox+30,555,w-60,8,'#c9d7dc');for(let i=0;i<6;i++)rect(ox+40+i*135+(wallTick%135),590,48,5,'#e1e7e9');
 const pose=sa?Math.min(p.poseCount-1,Math.floor(shown.tick/Math.max(1,total)*p.poseCount)):0;
 const actorX=ox+shown.x,ground=550,swing=sa&&shown.tick>=sa.startup&&shown.tick<sa.startup+sa.active;
 ctx.save();ctx.translate(actorX,ground);ctx.rotate(sa&&shown.tick<sa.startup?-.14*(pose%3):swing?.25:0);rect(-23,-88,46,76,p.id?colors.green:colors.blue);rect(-18,-117,36,32,p.id?'#9ec7ac':'#97b7dc');rect(18,-64,swing?123:48,15,colors.orange);ctx.restore();
 rect(ox+p.target-28,ground-105,56,100,'#cbb9a0');text('타깃',ox+p.target,ground+45,25,colors.muted,'center');
 if(p.attack&&tick>=p.attack.startup&&tick<p.attack.startup+p.attack.active){ctx.strokeStyle=colors.orange;ctx.lineWidth=4;ctx.strokeRect(ox+p.x+24,ground-110,150,95);}
 const recentHit=p.history.filter(e=>e.kind==='collision').at(-1);if(recentHit&&wallTick-recentHit.wallTick<45)text('충돌!',ox+p.target,ground-144,36,colors.orange,'center');
 const bx=ox+35,by=640,bw=w-70;const start=a?a.startup:p.startup,active=a?a.active:p.active,recovery=a?a.recovery:p.recovery;
 rect(bx,by,bw*start/total,37,'#a7c3e0');rect(bx+bw*start/total,by,bw*active/total,37,'#ceac70');rect(bx+bw*(start+active)/total,by,bw*recovery/total,37,'#b2cbb8');rect(bx+bw*Math.min(tick/total,1),by-13,4,61,colors.ink);
 text(`준비 ${start}`,bx,701,25);text(`판정 ${active}`,bx+bw*start/total+3,701,25);text(`회복 ${recovery}`,bx+bw*(start+active)/total+30,701,25);
 const status=p.attack?(p.attack.pauseLeft?'전투 시계 멈춤':tick<start?'준비':tick<start+active?'판정 활성':'회복'):'다음 행동 가능';text(`눈금 ${tick} / ${total} · ${status}`,ox+30,743,26);
 const last=p.history.filter(e=>e.kind==='hit-area-begins').at(-1),ready=p.history.filter(e=>e.kind==='action-ready').at(-1);text(`판정 시작 ${last?last.elapsedSeconds.toFixed(3)+'s':'—'} · 완료 ${ready?ready.elapsedSeconds.toFixed(3)+'s':'—'}`,ox+30,818,28,colors.blue);
 text(`충돌 ${p.hitCount} · 입력 차단 ${p.blockedCount} · 그림 인덱스 ${pose}`,ox+30,859,25,colors.muted);
 }
 text('입력 0 → 시간 눈금 12 뒤 판정 · 상용 게임의 기술 수치가 아닌 자체 실험',960,954,25,colors.muted,'center');
}
window.captureStep=t=>{const target=Math.round(t*60);if(target<wallTick)throw Error('Never rewind recorded test');while(wallTick<target)advance();draw();};
window.testState=()=>({mode,wallTick,seconds,panels:panels.map(p=>({...p,history:p.history.slice()}))});
function live(){if(!window.recording)window.captureStep((performance.now()-initial)/1000);requestAnimationFrame(live);}const initial=performance.now();draw();requestAnimationFrame(live);
