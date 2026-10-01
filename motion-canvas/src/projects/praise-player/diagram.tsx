import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
const titles=['점수 계산 → 내가 해냈다는 인정','성공 직후, 짧은 반응','‘잘했어’에서 ‘무엇을 했는가’로','작은 성공 · 이어진 성공 · 완료','실패를 숨기지 않고, 진짜 성과를 인정','칭찬 뒤에도 다음 행동은 계속된다'];
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
class PraiseDiagram extends Node{
 constructor(private index:number,private clock:()=>number,private seconds:number){super({});}
 protected draw(c:CanvasRenderingContext2D){
  const t=this.clock(),u=clamp((t/this.seconds-.10)/.72),drift=Math.sin(t*.3)*.008;
  const project=(x:number,y:number,z=0)=>[x+z*.36,y-z*.32+x*drift];
  const poly=(a:number[][],color:string)=>{c.beginPath();a.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=color;c.fill();};
  const face=(a:number[][],color:string)=>poly(a.map(([x,y,z])=>project(x,y,z)),color);
  const box=(x:number,y:number,w:number,h:number,d:number,color:string)=>{face([[x+12,y+h+12,0],[x+w+12,y+h+12,0],[x+w+12,y+h+12,d],[x+12,y+h+12,d]],'#dce5e8');face([[x,y,0],[x+w,y,0],[x+w,y,d],[x,y,d]],'#e5edf1');face([[x+w,y,0],[x+w,y,d],[x+w,y+h,d],[x+w,y+h,0]],'#98adb8');face([[x,y,0],[x+w,y,0],[x+w,y+h,0],[x,y+h,0]],color);};
  const txt=(s:string,x:number,y:number,size=32,color:string=P.ink)=>{c.font=`600 ${size}px "Malgun Gothic",sans-serif`;c.textAlign='center';c.textBaseline='middle';c.fillStyle=color;c.fillText(s,x,y);};
  const arrow=(x:number,y:number,x2:number,y2:number,col:string=P.blue)=>{const a=Math.atan2(y2-y,x2-x);c.strokeStyle=col;c.lineWidth=5;c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke();poly([[x2,y2],[x2-19*Math.cos(a-.5),y2-19*Math.sin(a-.5)],[x2-19*Math.cos(a+.5),y2-19*Math.sin(a+.5)]],col);};
  const bubble=(x:number,y:number,w:number,label:string,col='#fff4bf',size=37)=>{box(x-w/2,y-43,w,86,28,col);poly([[x-20,y+43],[x+10,y+43],[x-3,y+67]],col);txt(label,x,y,size);};
  const cat=(x:number,y:number,col:string=P.blue)=>{box(x-22,y-40,44,57,20,col);poly([[x-23,y-38],[x-21,y-68],[x-2,y-41]],col);poly([[x+23,y-38],[x+21,y-68],[x+2,y-41]],col);txt('•  •',x,y-17,22,'white');};
  const floor=(x:number,y:number,w:number)=>face([[x,y,0],[x+w,y,0],[x+w,y,180],[x,y,180]],'#eef3f4');
  c.save();c.globalAlpha=clamp(t/.35);c.translate(Math.sin(t*.3)*3,0);
  if(this.index===0){
   const x=-722;floor(x,236,1450);box(x,-150,380,220,65,'#e5edf6');txt('성공 판정',x+190,-187,35,P.blue);txt('점수 +10',x+190,-65,53,P.blue);cat(x+190,186);arrow(-300,-40,-140,-40);
   box(-74,-150,690,220,65,'#e4eee6');txt('행동을 알아본 표현',271,-187,35,P.green);
   bubble(271,-41,448,'방어 성공!','#fff3bb',50);cat(271,186,P.green);for(let i=0;i<5;i++){const a=i*1.26+u*4,r=75+u*55;txt('✦',271+Math.cos(a)*r,158+Math.sin(a)*r,25,'#c8a950');}
   txt('보상은 그대로 · 성공을 반기는 표현을 설계',0,298,35);txt('자체 테스트의 점수이며, 상용 게임 수치가 아님',0,339,26,P.muted);
  }else if(this.index===1){
   const x=-697;for(let row=0;row<2;row++){const y=-132+row*258;floor(x,y+120,1400);txt(row?'늦은 반응':'가까운 반응',-590,y-75,35,row?P.muted:P.blue);box(x,y,1390,45,30,'#dce8ee');const hit=x+250,praise=x+(row?1110:375);arrow(hit,y-110,hit,y-10);txt('성공',hit,y-151,30,P.blue);cat(hit,y+134);arrow(hit,y+22,praise,y+22,row?P.muted:P.green);const px=x+u*1390;c.fillStyle=P.blue;c.beginPath();c.arc(px,y+22,10,0,Math.PI*2);c.fill();if(u>(row?.75:.18))bubble(praise,y-100,300,'방어 성공',row?'#eceff1':'#fff3bb',34);}
   txt('어느 행동에 대한 반응인지 연결되는가?',0,326,34,P.blue);
  }else if(this.index===2){
   for(let i=0;i<2;i++){const x=-713+i*800;floor(x,223,630);cat(x+157,126,i?P.green:P.blue);box(x+302,50,48,94,35,'#d6b86e');txt(i?'회피 판정':'방어 판정',x+292,-213,37,i?P.green:P.blue);arrow(x+160,38,x+280,-51,i?P.green:P.blue);bubble(x+292,-99,470,u<.5?'잘했어요':i?'회피 성공':'방어 성공','#fff3bc',44);txt(i?'위로 이동 → 공격을 피함':'막기 입력 → 실제 충돌을 막음',x+292,288,27,P.muted);}
   txt('문구의 근거는 입력 버튼이 아니라 실제 결과',0,335,33,P.blue);
  }else if(this.index===3){
   const labels=['한 번의 성공','실제 연속 성공','긴 구간의 완료'],sizes=[34,48,62],heights=[50,112,190],cols=['#c1d4e7','#bcd3c1','#dfc284'];
   for(let i=0;i<3;i++){const x=-748+i*520;floor(x,260,435);const h=heights[i]*(.5+.5*u);box(x+37,214-h,354,h,70,cols[i]);cat(x+210,201-h,i===1?P.green:P.blue);txt(labels[i],x+210,292,31);bubble(x+210,-150,300+i*70,i===0?'방어 성공':i===1?'연속 방어!':'구간 완료!',cols[i],sizes[i]);}
   txt('같은 점수 규칙 · 성과의 차이에 맞는 표현 강도',0,342,31,P.blue);
  }else if(this.index===4){
   for(let i=0;i<2;i++){const x=-712+i*795;floor(x,214,628);cat(x+215,124,i?P.green:P.blue);const bx=x+590-u*400;box(bx,68,27,27,16,'#da9563');txt('체력 3 → 2',x+290,275,36,'#a9673c');bubble(x+290,-137,490,i?'피격 · 다시 준비':'완벽해요!','#f8e1c7',i?38:51);if(i){txt('앞선 방어 성공은 별도로 인정',x+290,-235,28,P.green);arrow(x+216,30,x+290,-75,P.green);}else{txt('결과와 맞지 않는 표현',x+290,-235,30,'#a9673c');}}
   txt('따뜻한 말도, 실제 성공과 실패를 구분한다',0,336,33,P.blue);
  }else{
   for(let i=0;i<2;i++){const x=-738+i*805;floor(x,235,665);box(x,-146,642,314,46,'#e6eef1');cat(x+155,90,i?P.green:P.blue);const bx=x+590-u*400;box(bx,65,32,32,17,'#d89760');arrow(x+575,89,x+210,89,'#b47a42');if(i)bubble(x+315,-197,430,'방어 성공','#fff4c3',37);else{box(x+45,-22,558,150,26,'#fff4c3');txt('방어 성공!',x+322,58,76);}
    txt(i?'진행 공간을 남긴 반응':'다음 위협 위를 덮는 반응',x+320,283,30,i?P.green:P.muted);}
   txt('무엇을 · 언제 · 얼마나 크게 / 모바일에서도 확인',0,338,31,P.blue);
  }
  c.restore();
 }
}
export function* diagramScene(view:View2D,index:number,seconds:number){view.fill(P.background);const clock=createSignal(0);view.add(<Txt text={titles[index]} y={-348} fontFamily={P.font} fontSize={53} fontWeight={700} fill={P.ink}/>);view.add(new PraiseDiagram(index,()=>clock(),seconds));yield* tween(seconds,v=>clock(v*seconds));}
