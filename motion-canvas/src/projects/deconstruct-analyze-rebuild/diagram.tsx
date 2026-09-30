import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';

export const TITLES=['같은 기능, 다른 판단','한 번의 행동을 네 단계로','느낌을 확인할 조건으로','한 번에 하나만 바꾸기','판단을 다른 규칙에 넣기','기능 목록 대신 플레이 기록'];
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
// Original projected geometry: depth faces, floor shadows, camera drift and
// meaningful moving comparisons. All labels and shapes remain editable.
class AnalysisDiagram extends Node {
 constructor(private index:number,private clock:()=>number,private seconds:number){super({});}
 protected draw(c:CanvasRenderingContext2D){
  const t=this.clock(),q=t/this.seconds,phase=t%5,drift=Math.sin(t*.25)*.025;
  const project=(x:number,y:number,z=0)=>[x+z*.42+x*z*.00015,y-z*.30+x*drift];
  const poly=(pts:number[][],col:string)=>{c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=col;c.fill();};
  const p3=(pts:number[][],col:string)=>poly(pts.map(([x,y,z])=>project(x,y,z)),col);
  const box=(x:number,y:number,w:number,h:number,d:number,col:string)=>{
   p3([[x+12,y+h+17,0],[x+w+15,y+h+17,0],[x+w+15,y+h+17,d],[x+12,y+h+17,d]],'#dce3e8');
   p3([[x,y,0],[x+w,y,0],[x+w,y,d],[x,y,d]],'#e1edf5');
   p3([[x,y,0],[x+w,y,0],[x+w,y+h,0],[x,y+h,0]],col);
   p3([[x+w,y,0],[x+w,y,d],[x+w,y+h,d],[x+w,y+h,0]],'#9db2c3');
  };
  const txt=(s:string,x:number,y:number,size=34,col:string=P.ink,weight=600)=>{c.font=`${weight} ${size}px "Malgun Gothic", sans-serif`;c.fillStyle=col;c.textAlign='center';c.textBaseline='middle';c.fillText(s,x,y);};
  const arrow=(a:number,b:number,x:number,y:number,col:string=P.blue)=>{const ang=Math.atan2(y-b,x-a);c.lineWidth=5;c.strokeStyle=col;c.beginPath();c.moveTo(a,b);c.lineTo(x,y);c.stroke();poly([[x,y],[x-17*Math.cos(ang-.5),y-17*Math.sin(ang-.5)],[x-17*Math.cos(ang+.5),y-17*Math.sin(ang+.5)]],col);};
  const actor=(x:number,y:number,col:string=P.blue)=>{box(x-21,y-40,42,46,32,col);txt('··',x+1,y-25,23,'white');};
  const platform=(x:number,y:number,w:number)=>box(x,y,w,23,110,'#b2c4ce');
  const path=(x:number,y:number,x2:number,y2:number)=>{c.save();c.setLineDash([7,8]);c.strokeStyle='#96b2c8';c.lineWidth=3;c.beginPath();c.moveTo(x,y);c.quadraticCurveTo((x+x2)/2,Math.min(y,y2)-225,x2,y2);c.stroke();c.restore();};
  c.save();c.globalAlpha=clamp(t/.3);c.translate(Math.sin(t*.22)*4,20);
  // Ground plane supplies readable depth without a dark dashboard or a flat slide.
  c.save();c.globalAlpha=.28;c.strokeStyle='#c9d5de';c.lineWidth=1;
  for(let z=0;z<=200;z+=40){const a=project(-760,250,z),b=project(710,250,z);c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();}
  for(let x=-760;x<730;x+=100){const a=project(x,250,0),b=project(x,250,200);c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();}c.restore();
  if(this.index===0){
   const names=['점프','대시','공간 이동'],games=['슈퍼 미트 보이','할로우 나이트','포털'],decisions=['어디에 착지할까','언제 거리를 줄일까','입구와 출구를 어디에'];
   for(let i=0;i<3;i++){
    const x=-740+i*510,active=Math.min(2,Math.floor(q*3))===i;
    box(x,-198,420,80,65,active?P.blue:'#d5dfe7');txt(names[i],x+210,-158,40,active?'white':P.ink);txt(games[i],x+210,-260,29,P.muted);
    platform(x+20,123,350);const u=(phase/5),jump=i===0?Math.sin(u*Math.PI)*120:0;
    actor(x+65+u*250,91-jump,active?P.blue:'#708da4');if(i===1)arrow(x+140,36,x+286,36);if(i===2){box(x+19,-40,25,147,42,P.blue);box(x+309,-40,25,147,42,P.green);}
    txt(decisions[i],x+210,235,29,active?P.blue:P.muted);
   }
   txt('기능 이름은 같아도, 플레이어가 읽는 상황은 다르다',0,300,35);
  }else if(this.index===1){
   const labels=['보기','선택하기','행동하기','결과 확인'],details=['발판과 틈','시점과 방향','입력과 조절','착지 / 실패'];
   const active=Math.min(3,Math.floor(q*4));
   for(let i=0;i<4;i++){const x=-760+i*395;box(x,-100-(i===active?20:0),278,120,80,i===active?P.blue:'#dce4eb');txt(labels[i],x+139,-53-(i===active?20:0),35,i===active?'white':P.ink);txt(details[i],x+139,13-(i===active?20:0),26,i===active?'white':P.muted);if(i<3)arrow(x+300,-35,x+363,-35,i<active?P.blue:'#adbcca');}
   platform(-625,193,470);platform(199,193,430);const u=clamp((phase-.8)/3.4);path(-500,149,425,149);actor(-500+925*u,150-Math.sin(u*Math.PI)*150);
   txt('한 번의 행동을 적으면, 관찰할 대상이 선명해진다',0,300,35);
  }else if(this.index===2){
   const active=Math.min(2,Math.floor(q*3)),names=['이동 속도','위험을 통과','재시도 간격'];
   for(let i=0;i<3;i++){const x=-725+i*515;box(x,-220,360,90,62,i===active?P.blue:'#dce4eb');txt(names[i],x+180,-175,37,i===active?'white':P.ink);}
   platform(-685,159,1320);const u=phase/5;actor(-565+u*1060,122);
   if(active===0){arrow(-530,44,450,44);txt('빠르게 움직여서 좋은가?',0,244,35,P.blue);}
   else if(active===1){for(let i=0;i<3;i++)poly([[-140+i*125,152],[-101+i*125,45],[-61+i*125,152]],'#d7a4a4');arrow(-245,-30,205,-30,P.blue);txt('위험을 넘는 판단이 좋은가?',0,244,35,P.blue);}
   else{box(-55,-50,190,92,60,'#dbe8dc');txt((Math.max(0,1.8-phase)).toFixed(1)+'초',40,-4,36,P.green);txt('다시 시도할 수 있어서 좋은가?',0,244,35,P.blue);}
   txt('느낌을 조건으로 적고, 서로 다른 가능성을 비교한다',0,300,33);
  }else if(this.index===3){
   const retry=q>.54;
   for(let i=0;i<2;i++){
    const x=-755+i*815;txt(retry?(i?'대기 후 재시도':'바로 재시도'):(i?'착지 공간 좁게':'착지 공간 넓게'),x+330,-239,38,i?P.green:P.blue);
    platform(x,-3,200);platform(x+410,-3,i&&!retry?135:310);const u=clamp((phase-.4)/3.1);path(x+103,-38,x+531,-38);actor(x+103+428*u,-40-Math.sin(u*Math.PI)*138);
    box(x+50,177,570,59,55,'#e4ebf1');txt(retry?(i?`대기 ${Math.max(0,1.8-phase).toFixed(1)}초`:'실패 → 다음 입력'):'같은 속도 · 같은 점프 · 같은 입력',x+335,206,27,P.muted);
   }
   txt(retry?'규칙을 배우는 시간인가, 기다리는 시간인가?':'하나를 바꿔야 그 조건의 영향을 비교할 수 있다',0,300,35);
  }else if(this.index===4){
   const active=Math.min(2,Math.floor(q*3)),names=['점프','문 통과','신호 이동'];
   for(let i=0;i<3;i++){
    const x=-750+i*515;txt(names[i],x+202,-232,39,i===active?P.blue:P.muted);platform(x+10,157,420);
    const go=phase>1.7,u=clamp((phase-1.7)/2.2);actor(x+50+u*315,113-(i===0?Math.sin(u*Math.PI)*130:0),i===active?P.blue:'#849bab');
    if(i===1)box(x+220,go?-55:2,28,go?32:155,40,'#d8bd75');
    if(i===2){box(x+170,-19,110,125,40,go?'#d7e8db':'#e8ecef');txt(go?'이동':'대기',x+225,25,26,go?P.green:P.muted);}
    txt(i===0?'발판을 보고 기다림':i===1?'문을 보고 기다림':'빛 신호를 보고 기다림',x+202,235,28);
   }
   txt('남길 판단을 정하고, 기다릴 대상을 바꿔 본다',0,300,35);
  }else{
   const active=Math.min(2,Math.floor(q*3)),labels=['행동을 관찰','조건 하나 변경','새 규칙에 조립'],sub=['무엇을 보고 선택했나','어떤 차이가 생겼나','직접 플레이로 확인'];
   for(let i=0;i<3;i++){const x=-750+i*535,z=i===active?20:0;box(x,-160-z,400,158,90,i===active?P.blue:'#dbe4ec');txt(String(i+1),x+200,-213-z,34,P.blue);txt(labels[i],x+200,-99-z,37,i===active?'white':P.ink);txt(sub[i],x+200,-39-z,27,i===active?'white':P.muted);if(i<2)arrow(x+430,-64,x+484,-64);}
   box(-600,125,1160,83,55,'#e5edf4');txt('본 장면 → 했던 선택 → 알게 된 결과',0,168,39,P.blue);
   txt('최근 재미있었던 한 장면부터, 작은 테스트로',0,300,35);
  }
  c.restore();this.drawChildren(c);
 }
}
export function* diagramScene(view:View2D,index:number,seconds:number){
 view.fill(P.background);const clock=createSignal(0);
 view.add(<Txt text={String(index+1).padStart(2,'0')+'  ANALYZE & REBUILD'} x={-864} y={-477} offset={[-1,0]} fontFamily={P.font} fontSize={24} fontWeight={600} fill={P.blue}/>);
 view.add(<Txt text={TITLES[index]} x={-864} y={-405} offset={[-1,0]} fontFamily={P.font} fontSize={52} fontWeight={700} fill={P.ink}/>);
 const notes=['겉으로 보이는 기능에서, 실제 플레이의 선택으로','보기 → 선택 → 행동 → 결과','가능한 이유를 비교하고 직접 확인하기','속도·그림·보상을 한꺼번에 바꾸지 않는다','새 테스트의 재미는 플레이로 확인해야 한다','관찰 → 비교 → 새 설계'];
 view.add(<Txt text={notes[index]} y={-337} fontFamily={P.font} fontSize={28} fill={P.muted}/>);
 view.add(new AnalysisDiagram(index,()=>clock(),seconds));yield* tween(seconds,p=>clock(p*seconds));
}
