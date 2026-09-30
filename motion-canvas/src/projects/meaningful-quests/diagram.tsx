import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
const titles=['심부름 안에 있는 세 가지 경험','재료보다, 찾는 동안의 선택','완료 표시와 세계의 변화','같은 물건 · 같은 속도 · 같은 보상','돌아오는 길에 생기는 새로운 조건','목표 아래 세 줄을 더 적어 보기'];
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
class QuestDiagram extends Node {
 constructor(private index:number,private clock:()=>number,private seconds:number){super({});}
 protected draw(c:CanvasRenderingContext2D){
  const t=this.clock(),q=t/this.seconds,u=clamp((q-.1)/.7),drift=Math.sin(t*.22)*.013;
  const proj=(x:number,y:number,z=0)=>[x+z*.43,y-z*.31+x*drift];
  const poly=(a:number[][],col:string)=>{c.beginPath();a.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=col;c.fill();};
  const face=(a:number[][],col:string)=>poly(a.map(([x,y,z])=>proj(x,y,z)),col);
  const box=(x:number,y:number,w:number,h:number,d:number,col:string)=>{face([[x+10,y+h+15,0],[x+w+12,y+h+15,0],[x+w+12,y+h+15,d],[x+10,y+h+15,d]],'#dce5e7');face([[x,y,0],[x+w,y,0],[x+w,y,d],[x,y,d]],'#e1edf2');face([[x+w,y,0],[x+w,y,d],[x+w,y+h,d],[x+w,y+h,0]],'#9cafb5');face([[x,y,0],[x+w,y,0],[x+w,y+h,0],[x,y+h,0]],col);};
  const text=(s:string,x:number,y:number,size=31,col:string=P.ink)=>{c.font=`600 ${size}px "Malgun Gothic",sans-serif`;c.textAlign='center';c.textBaseline='middle';c.fillStyle=col;c.fillText(s,x,y);};
  const arrow=(x:number,y:number,x2:number,y2:number,col:string=P.blue)=>{const a=Math.atan2(y2-y,x2-x);c.strokeStyle=col;c.lineWidth=5;c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke();poly([[x2,y2],[x2-18*Math.cos(a-.5),y2-18*Math.sin(a-.5)],[x2-18*Math.cos(a+.5),y2-18*Math.sin(a+.5)]],col);};
  const actor=(x:number,y:number,col:string=P.blue)=>{box(x-17,y-33,34,37,22,col);text('··',x,y-20,23,'white');};
  const wood=(x:number,y:number)=>box(x,y,39,19,28,'#d3ad73');
  const route=(points:number[][],col:string,width=10)=>{c.lineWidth=width;c.strokeStyle=col;c.lineJoin='round';c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.stroke();};
  c.save();c.globalAlpha=clamp(t/.35);c.translate(Math.sin(t*.25)*4,0);
  // Shared projected ground gives the diagrams depth and a common spatial frame.
  face([[-770,240,0],[740,240,0],[740,240,320],[-770,240,320]],'#f0f4f5');
  if(this.index===0){
   const labels=['가는 동안','완료한 뒤','돌아오는 길'],detail=['선택','상태 변화','새 정보'],active=Math.min(2,Math.floor(q*3));
   for(let i=0;i<3;i++){const x=-740+i*515;text(labels[i],x+195,-223,37,i===active?P.blue:P.muted);box(x,-140,390,75,58,i===active?'#d8e9f4':'#e7ecef');text(detail[i],x+195,-102,35);route([[x+30,120],[x+350,120]],'#bccdd3',14);actor(x+50+clamp((q*3-i))*270,90,i===active?P.blue:'#8c9fa9');if(i===0){arrow(x+110,10,x+280,-12);wood(x+285,45);}else if(i===1){box(x+164,85,92,26,74,q>.43?'#a9c8ab':'#e6e9ea');text(q>.43?'길 열림':'길 막힘',x+205,191,28,P.green);}else{route([[x+70,120],[x+200,30],[x+335,120]],'#b6cfa6',10);text('다른 경로',x+205,191,28,P.green);}}
   text('물건 개수 대신, 부탁 사이의 경험을 설계한다',0,292,34);
  }else if(this.index===1){
   box(-680,-110,930,260,150,'#e6f2f7');text('물속에서 찾는 동안',-215,-224,37,P.blue);
   const depth=clamp(q<.6?q/.6:(1-q)/.4),x=-560+Math.sin(q*Math.PI)*620,y=-35+depth*125;actor(x,y);
   for(let i=0;i<3;i++)wood(-450+i*220,76+i%2*42);
   c.strokeStyle='#aac6d5';c.lineWidth=3;for(let i=0;i<8;i++){c.beginPath();c.arc(-610+i*110, -90+Math.sin(i+t)*9,7,0,Math.PI*2);c.stroke();}
   box(420,-130,95,285,60,'#e5ecef');const oxygen=q<.65?1-q*.9:.42+(q-.65)*1.6;box(435,145-245*oxygen,64,245*oxygen,12,P.blue);text('산소',466,-203,34,P.blue);
   arrow(145,3,332,-53,P.green);text(q<.58?'더 탐색할까?':'수면으로 돌아갈까?',45,230,35,P.blue);text('탐색 거리 ↔ 남은 산소',0,298,33);
  }else if(this.index===2||this.index===3){
   const compare=this.index===3;
   for(let i=0;i<2;i++){const x=-735+i*800;text(i?'B · 길도 달라진다':'A · 숫자만 달라진다',x+330,-238,35,i?P.green:P.blue);box(x,-136,640,335,75,'#f5f7f7');
    route([[x+60,125],[x+270,125],[x+525,125]],'#c7d2d7',13);box(x+290,19,62,153,45,'#c4e2ed');
    const done=q>.43,open=i===1&&done;
    if(open){box(x+277,103,105,25,60,'#bed4ac');arrow(x+180,53,x+466,53,P.green);}else{wood(x+271,104);wood(x+351,104);}
    actor(x+100+(open?clamp((q-.43)/.45)*405:Math.min(u*270,156)),88,i?P.green:P.blue);
    text(`점수 ${done?'50':'0'}`,x+330,-68,32);text(open?'충돌 해제 → 통과 가능':'완료해도 경로는 그대로',x+330,244,28,i?P.green:P.muted);
    if(compare){for(let j=0;j<3;j++)wood(x+51+j*46,-35);text('속도 / 위치 / 점수 동일',x+330,-180,26,P.muted);}
   }
   text(compare?'확인된 결과: 세계 상태 변화  /  재미 평가는 사람에게':'완료를 알아볼 수 있는 변화가 있는가?',0,312,32);
  }else if(this.index===4){
   const a=[-645,42],b=[585,42];box(-760,-150,1460,348,110,'#f4f7f5');route([a,[-245,42],[200,42],b], '#83a9bc',17);route([a,[-420,173],[385,173],b],'#b3cba5',17);
   box(-66,-68,66,160,58,q<.5?'#d0a585':'#bbd1ad');text('빈 가방만',-52,-126,33,P.green);text('빠른 길 / 물건 포기',164,-207,32,P.blue);text('우회로 / 물건 유지',133,238,32,P.green);
   const upper=q>.52,v=q<.5?q*2:(q-.5)*2;const x=-620+v*1170,y=upper?42:42+Math.sin(v*Math.PI)*130;actor(x,y-31,upper?P.blue:P.green);if(!upper)wood(x+24,y-47);
   arrow(-210,-21,194,-21,P.blue);text('같은 공간에, 다른 조건과 결과가 생긴다',0,316,32);
  }else{
   const labels=['가는 길의 선택','완료 뒤의 변화','돌아오는 새 정보'],icons=['경로','다리','조건'],active=Math.min(2,Math.floor(q*3));
   for(let i=0;i<3;i++){const x=-735+i*505;box(x,-135,405,244,95,i===active?'#e0edf5':'#f0f3f4');text(labels[i],x+202,-202,33,i===active?P.blue:P.muted);route([[x+65,28],[x+202,28],[x+337,28]],'#b5c9d2',10);actor(x+80+clamp(q*3-i)*215,-5,i===active?P.blue:'#91a7ac');if(i===1)box(x+179,2,56,26,65,'#c6d7b9');if(i===2)box(x+189,-48,24,79,42,'#d0b579');text(icons[i],x+202,177,27,P.muted);}
   text('설계한 의도와, 플레이어가 알아본 결과를 비교한다',0,276,33);text('동작 로그 ≠ 인간의 재미 평가',0,329,28,P.muted);
  }
  c.restore();
 }
}
export function* diagramScene(view:View2D,index:number,seconds:number){view.fill(P.background);const clock=createSignal(0);view.add(<Txt text={titles[index]} y={-348} fontFamily={P.font} fontSize={55} fontWeight={700} fill={P.ink}/>);view.add(new QuestDiagram(index,()=>clock(),seconds));yield* tween(seconds,v=>clock(v*seconds));}
