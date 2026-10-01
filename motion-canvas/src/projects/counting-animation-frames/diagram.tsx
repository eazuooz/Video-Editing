import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';
const titles=['‘빠르게’ 바꾸려는 구간부터','프레임 수 × 기준 속도','입력 0에서, 판정과 회복까지','그림 수를 바꿔도 같은 판정 시계','멈추는 시계 · 계속 흐르는 시계','정상 속도로 찾고, 로그로 확인'];
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
class FrameDiagram extends Node{
 constructor(private index:number,private clock:()=>number,private seconds:number){super({});}
 protected draw(c:CanvasRenderingContext2D){
  const t=this.clock(),q=t/this.seconds,u=clamp((q-.08)/.76),drift=Math.sin(t*.2)*.009;
  const proj=(x:number,y:number,z=0)=>[x+z*.36,y-z*.30+x*drift];
  const poly=(a:number[][],col:string)=>{c.beginPath();a.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=col;c.fill();};
  const face=(a:number[][],col:string)=>poly(a.map(([x,y,z])=>proj(x,y,z)),col);
  const box=(x:number,y:number,w:number,h:number,d:number,col:string)=>{face([[x+10,y+h+13,0],[x+w+10,y+h+13,0],[x+w+10,y+h+13,d],[x+10,y+h+13,d]],'#dce5e7');face([[x,y,0],[x+w,y,0],[x+w,y,d],[x,y,d]],'#e4edf2');face([[x+w,y,0],[x+w,y,d],[x+w,y+h,d],[x+w,y+h,0]],'#9caeb9');face([[x,y,0],[x+w,y,0],[x+w,y+h,0],[x,y+h,0]],col);};
  const text=(s:string,x:number,y:number,size=31,col:string=P.ink)=>{c.font=`600 ${size}px "Malgun Gothic",sans-serif`;c.textAlign='center';c.textBaseline='middle';c.fillStyle=col;c.fillText(s,x,y);};
  const arrow=(x:number,y:number,x2:number,y2:number,col:string=P.blue)=>{const a=Math.atan2(y2-y,x2-x);c.strokeStyle=col;c.lineWidth=5;c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke();poly([[x2,y2],[x2-18*Math.cos(a-.5),y2-18*Math.sin(a-.5)],[x2-18*Math.cos(a+.5),y2-18*Math.sin(a+.5)]],col);};
  const marker=(x:number,y:number,col:string=P.blue)=>{poly([[x,y],[x-12,y-22],[x+12,y-22]],col);c.strokeStyle=col;c.lineWidth=3;c.beginPath();c.moveTo(x,y);c.lineTo(x,y+75);c.stroke();};
  const actor=(x:number,y:number,pose=0,col:string=P.blue)=>{box(x-19,y-45,38,46,20,col);box(x-13,y-76,26,28,15,'#a6c2d9');c.strokeStyle='#b38954';c.lineWidth=10;c.beginPath();c.moveTo(x+18,y-26);c.lineTo(x+45+pose*4,y-38+pose*3);c.stroke();};
  const strip=(x:number,y:number,count:number,unit:number,col:string,d=15)=>{for(let n=0;n<count;n++)box(x+n*unit,y,unit-4,36,d,col);};
  c.save();c.globalAlpha=clamp(t/.35);c.translate(Math.sin(t*.22)*3,0);
  face([[-775,246,0],[736,246,0],[736,246,280],[-775,246,280]],'#f0f4f5');
  if(this.index===0){
   const labels=['입력 → 준비','판정 → 충돌','회복 → 다음 행동'],details=['시작을 앞당기기','충돌 뒤 멈춤','회복을 줄이기'],colors=['#b6d1ea','#ddbf89','#bdd4bf'];
   for(let i=0;i<3;i++){const x=-750+i*520,active=Math.min(2,Math.floor(u*3))===i;text(labels[i],x+205,-226,35,active?P.blue:P.muted);box(x,-110,410,118,70,colors[i]);text(details[i],x+205,-51,32);actor(x+60+clamp(u*3-i)*280,165,i+1);if(i<2)arrow(x+428,-42,x+492,-42);}
   text('같은 요청도, 바꾸려는 시간 구간은 다르다',0,288,34);text('실제 게임 관찰 → 자체 테스트의 정확한 숫자',0,326,28,P.muted);
  }else if(this.index===1){
   const x=-690,w=54;for(let i=0;i<2;i++){const y=-109+i*254;text(i?'30번 / 초':'60번 / 초',-592,y-83,39,i?P.green:P.blue);strip(x,y,12,w,i?'#b9d0be':'#b1cee7');marker(x+clamp(u*(i?1:2))*12*w,y-16,i?P.green:P.blue);text('12눈금',72,y+62,30);text(i?'0.4초':'0.2초',510,y+15,65,i?P.green:P.blue);arrow(60,y+14,345,y+14,i?P.green:P.blue);}
   text('12 ÷ 60 = 0.2초     /     12 ÷ 30 = 0.4초',0,291,36);text('설계 메모: 눈금 수와 기준 속도를 함께',0,326,28,P.muted);
  }else if(this.index===2){
   const x=-750,y=17,w=49.5,count=Math.min(30,Math.floor(u*30));strip(x,y,12,w,'#adc8e4');strip(x+12*w,y,3,w,'#d8b677');strip(x+15*w,y,15,w,'#b6d0bb');
   text('준비 12',x+6*w,-99,42,P.blue);text('판정 3',x+13.5*w,-99,38,'#976b27');text('회복 15',x+22.5*w,-99,42,P.green);
   marker(x+count*w,y-14);actor(x+count*w,-185,Math.min(5,Math.floor(count/5)));for(const n of [0,12,15,30])text(String(n),x+n*w,128,30);
   text('입력 0',x,208,30);text('첫 판정 12',x+12*w,208,30,P.blue);text('다음 행동 30',x+30*w,208,30,P.green);
   text('60눈금 / 초 · 30눈금 전체 = 0.5초',0,291,35);text('[0,12) 준비 → [12,15) 판정 → [15,30) 회복 · 자체 테스트 기준',0,326,27,P.muted);
  }else if(this.index===3){
   const x=-710,spacing=178;for(let row=0;row<2;row++){const y=-136+row*270,n=row?8:2;box(x-33,y-65,1450,136,42,'#f6f8f8');text(row?'8개 그림':'2개 그림',-604,y-119,36,row?P.green:P.blue);for(let i=0;i<n;i++)actor(x+(n===2?i*1246:i*spacing),y+9,i%5,row?P.green:P.blue);arrow(-499,y+86,596,y+86,row?P.green:P.blue);text('판정 시계는 동일: 입력 → 12눈금',146,y+133,30);}
   const hitX=-499+u*1095;marker(hitX,-46);marker(hitX,224,P.green);text('그림 수 ≠ 기다리는 시간',0,326,33,P.blue);
  }else if(this.index===4){
   const x=-740,w=43.6;for(let row=0;row<2;row++){const y=-107+row*239;text(row?'실제 경과 시계 · 34눈금':'전투 시계 · 30눈금',-458,y-81,36,row?P.green:P.blue);for(let i=0;i<(row?34:30);i++){const pause=row&&i>=12&&i<16,col=pause?'#ebd2a1':i<(row?16:12)?'#b4cee5':'#b8d0bd';box(x+i*w,y,w-4,42,17,col);if(pause)text('Ⅱ',x+i*w+18,y+21,22,'#976b27');}
    let tick=Math.round(u*34);if(!row)tick=tick<=12?tick:tick<=16?12:tick-4;marker(x+Math.min(tick,row?34:30)*w,y-14,row?P.green:P.blue);text(row?'34 ÷ 60 ≈ 0.567초':'30 ÷ 60 = 0.5초',475,y-81,35,row?P.green:P.blue);}
   arrow(x+12*w,-34,x+14*w,91,'#ae7e31');text('충돌 뒤 4눈금 · 전투만 멈춤',x+16*w,283,33,'#976b27');text('공격 데이터 30은 그대로 · 배경은 계속 진행 · 자체 구현의 예시',0,326,27,P.muted);
  }else{
   const x=-706,w=69;for(let row=0;row<2;row++){const y=-112+row*239;text(row?'화면 60 / 규칙 60':'화면 30 / 규칙 60',-447,y-86,37,row?P.green:P.blue);for(let i=0;i<20;i++){const pose=row?i:Math.floor(i/2)*2;box(x+i*w,y,w-5,49,25,i===12?'#ddbb81':row?'#c1d6c4':'#b9cfe4');text(String(pose),x+i*w+30,y+23,23);}
    marker(x+Math.min(12,Math.floor(u*20))*w,y-13,row?P.green:P.blue);arrow(x+12*w,y+75,678,y+75,row?P.green:P.blue);text('같은 0.2초에 판정',-204,y+114,29,row?P.green:P.blue);}
   text('녹화 그림은 표본 · 입력 / 판정 / 다음 행동 로그를 함께',0,326,30,P.blue);
  }
  c.restore();
 }
}
export function* diagramScene(view:View2D,index:number,seconds:number){view.fill(P.background);const clock=createSignal(0);view.add(<Txt text={titles[index]} y={-348} fontFamily={P.font} fontSize={55} fontWeight={700} fill={P.ink}/>);view.add(new FrameDiagram(index,()=>clock(),seconds));yield* tween(seconds,v=>clock(v*seconds));}
