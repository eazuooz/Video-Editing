import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
const titles=['입력 수신과 행동 성공을 구분하기','거절 이유가 다음 행동을 바꾼다','메뉴의 확인 의도와 조작 약속','컷신: 응답 → 확인 → 전환','받음 · 처리 중 · 완료는 다른 상태','현재 맥락에서 필요한 응답부터'];
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
class InputStateDiagram extends Node{
 constructor(private index:number,private clock:()=>number,private seconds:number){super({});}
 protected draw(c:CanvasRenderingContext2D){
  const t=this.clock(),u=clamp(t/this.seconds),drift=Math.sin(t*.26)*.009;
  const project=(x:number,y:number,z=0)=>[x+z*.39,y-z*.29+x*drift];
  const poly=(a:number[][],color:string)=>{c.beginPath();a.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=color;c.fill();};
  const face=(a:number[][],color:string)=>poly(a.map(([x,y,z])=>project(x,y,z)),color);
  const block=(x:number,y:number,w:number,h:number,d:number,col:string)=>{face([[x+10,y+h+10,0],[x+w+10,y+h+10,0],[x+w+10,y+h+10,d],[x+10,y+h+10,d]],'#dbe5e5');face([[x,y,0],[x+w,y,0],[x+w,y,d],[x,y,d]],'#e9eff0');face([[x+w,y,0],[x+w,y,d],[x+w,y+h,d],[x+w,y+h,0]],'#90a9a5');face([[x,y,0],[x+w,y,0],[x+w,y+h,0],[x,y+h,0]],col);};
  const txt=(s:string,x:number,y:number,size=33,color:string=P.ink)=>{c.font=`600 ${size}px "Malgun Gothic",sans-serif`;c.textAlign='center';c.textBaseline='middle';c.fillStyle=color;c.fillText(s,x,y);};
  const arrow=(x:number,y:number,x2:number,y2:number,col:string=P.blue)=>{const a=Math.atan2(y2-y,x2-x);c.strokeStyle=col;c.lineWidth=5;c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke();poly([[x2,y2],[x2-18*Math.cos(a-.5),y2-18*Math.sin(a-.5)],[x2-18*Math.cos(a+.5),y2-18*Math.sin(a+.5)]],col);};
  const floor=(x:number,y:number,w:number)=>face([[x,y,0],[x+w,y,0],[x+w,y,160],[x,y,160]],'#ecf2ee');
  const key=(x:number,y:number,s:string,col='#e4edf6',w=180)=>{block(x-w/2,y-42,w,84,45,col);txt(s,x,y,36);};
  const tag=(x:number,y:number,s:string,col='#f7edc8',w=420)=>{block(x-w/2,y-46,w,92,32,col);txt(s,x,y,34);};
  c.save();c.globalAlpha=clamp(t/.35);c.translate(Math.sin(t*.26)*4,0);
  if(this.index===0){
   floor(-760,222,1510);key(-550,-27,'SPACE');arrow(-422,-27,-280,-27);block(-238,-160,400,282,72,'#e2eee6');txt('누른 뜻을 받음',-37,-191,35,P.green);txt('입력 수신',-37,-81,46,P.green);txt('문은 아직 잠겨 있음',-37,18,31);arrow(194,-65,380,-140,'#a67d48');arrow(194,42,380,122,P.blue);tag(584,-140,'거절 · 열쇠 필요','#f1dfc7',402);tag(584,122,'성공 · 문 열림','#dceadb',402);txt('열쇠 조건 확인',281,-210,27,P.muted);
   const x=-423+clamp(u*2)*160;c.fillStyle=P.green;c.beginPath();c.arc(x,-27,9,0,Math.PI*2);c.fill();txt('누른 뜻을 받음 ≠ 실제 실행 완료',0,313,36,P.blue);
  }else if(this.index===1){
   for(let i=0;i<2;i++){const x=-714+i*796;floor(x,221,622);block(x,-156,595,314,55,'#e7eee6');const label=i?'재료가 부족함':'자리와 겹침';txt(label,x+285,-205,37,i?P.blue:'#a67d48');
    for(let j=0;j<4;j++)face([[x+80+j*105,30,0],[x+190+j*105,30,0],[x+190+j*105,120,65],[x+80+j*105,120,65]],'#c1d3b9');
    if(!i){block(x+140,-59,100,144,62,'#849d8d');block(x+215,-66,100,145,65,'#c9a17d');arrow(x+341,73,x+461,73,'#a67d48');}else{for(let j=0;j<2;j++)block(x+134+j*69,18,47,47,45,'#c4a471');txt('2 / 4',x+411,32,51,P.blue);}
    tag(x+289,225,i?'재료를 모아 보기':'빈자리로 옮기기','#fff1c9',530);
   }txt('하나의 “불가” 대신 실제 조건에 맞는 단서',0,342,32,P.blue);
  }else if(this.index===2){
   floor(-730,245,1460);block(-128,-166,548,327,69,'#e6eee5');txt('탐험 시작',147,-88,50,P.green);block(-90,3,470,77,32,'#c2d8c2');txt('연습 모드',145,42,36);key(-557,-79,'ENTER','#e3ebf6',230);key(-557,92,'SPACE','#f5e9c5',230);arrow(-416,-80,-160,-80,P.green);arrow(-416,90,-160,47,P.green);key(662,3,'ESC','#eee9e4',155);txt('돌아가기',662,124,32,P.muted);arrow(570,42,463,42,'#a48462');txt('같은 확인 의도는 연결 / 다른 결과는 분리',0,314,33,P.blue);txt('받을 수 있는 키를 화면에 표시',147,-221,32);
  }else if(this.index===3){
   floor(-740,231,1470);block(-691,-201,1340,322,74,'#e1ecef');txt('컷신은 계속 재생',-20,-139,43,P.blue);key(-559,222,'짧게 눌러 안내','#e7edf1',326);arrow(-350,222,-206,222);tag(66,222,'길게 확인','#f5ebc6',390);arrow(309,222,437,222,P.green);tag(592,222,'장면 전환','#dcebdc',290);
   block(-423,-39,875,53,31,'#bdcbd0');const fill=clamp((u-.18)/.62);block(-423,-39,875*fill,53,31,'#6c9a80');txt('확인 진행',-10,-74,29);txt('중간에 놓으면 취소 → 장면 계속',-10,89,31,P.muted);txt('수신을 알려도, 바로 실행할 필요는 없다',0,341,32,P.blue);
  }else if(this.index===4){
   floor(-753,200,1500);const labels=['요청 수신','처리 중','완료 확인'],cols=['#dfeaf2','#f4e6c3','#dcead9'];
   for(let i=0;i<3;i++){const x=-709+i*506;block(x,-102,412,223,74,cols[i]);txt(labels[i],x+198,-26,45,i===2?P.green:P.blue);txt(i===0?'누른 뜻을 받음':i===1?'다시 누름 → 진행 안내':'끝난 뒤 문구 변경',x+199,60,27);if(i<2)arrow(x+441,9,x+493,9);}
   const ix=-515+clamp((u-.1)/.8)*1012;face([[ix-12,-165,80],[ix+12,-165,80],[ix+12,-142,80],[ix-12,-142,80]],P.green);txt('“저장 중”을 “저장 완료”처럼 표시하지 않기',0,275,36,P.blue);txt('자체 테스트는 지연을 둔 모의 작업 · 실제 저장 실패도 별도 설계',0,326,27,P.muted);
  }else{
   floor(-745,226,1480);for(let i=0;i<2;i++){const x=-710+i*790;block(x,-188,598,352,67,i?'#e8eee3':'#e3edf0');txt(i?'메뉴 상태':'게임 상태',x+289,-233,38,i?P.green:P.blue);key(x+294,-58,i?'ENTER':'SPACE',i?'#d1e1c7':'#d0e2ef',256);txt(i?'확인':'대상에 상호작용',x+292,65,36);key(x+486,139,'Q','#eeeeeb',94);txt('의미 없는 키에 큰 경고를 쌓지 않기',x+291,231,26,P.muted);}
   txt('실행 가능해 보이는 행동이 막힐 때, 이유를 우선 응답',0,322,30,P.blue);
  }c.restore();
 }
}
export function* diagramScene(view:View2D,index:number,seconds:number){view.fill(P.background);const clock=createSignal(0);view.add(<Txt text={titles[index]} y={-348} fontFamily={P.font} fontSize={53} fontWeight={700} fill={P.ink}/>);view.add(new InputStateDiagram(index,()=>clock(),seconds));yield* tween(seconds,v=>clock(v*seconds));}
