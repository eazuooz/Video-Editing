import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';

export const TITLES = ['버튼은 하나, 판단은 여러 개','연타 — 얼마나 빠르게 누를까','타이밍 — 지금 누르면 맞을까','반응 — 신호가 나오면 눌러라','누르기와 떼기 — 무엇을 받아들일까','같은 입력, 더 선명한 결과','버튼보다 먼저, 판단을 설계하자'];
const clamp=(v:number)=>Math.max(0,Math.min(1,v));
// Original explanatory geometry. Every object has depth, a projected shadow,
// and a restrained camera drift. The geometry remains editable, not a bitmap slide.
class InputDiagram extends Node {
 constructor(private mode:number,private time:()=>number,private duration:number){super({});}
 protected draw(c:CanvasRenderingContext2D){
  const elapsed=this.time(),phase=Math.floor(elapsed/5),t=elapsed%5;
  const camera=Math.sin(elapsed*.30)*.045;
  const pt=(x:number,y:number,z=0)=>[x*(1+z*.00028)+z*.48+z*camera,y-z*.31+x*camera*.08];
  const polygon=(pts:number[][],color:string,stroke=false)=>{c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=color;c.fill();if(stroke){c.strokeStyle='#b8c7d2';c.lineWidth=1.5;c.stroke();}};
  const poly3=(pts:number[][],color:string,stroke=false)=>polygon(pts.map(([x,y,z])=>pt(x,y,z)),color,stroke);
  const label=(s:string,x:number,y:number,size=34,color:string=P.ink,weight=600)=>{c.fillStyle=color;c.font=weight+' '+size+'px "Malgun Gothic", sans-serif';c.textAlign='center';c.textBaseline='middle';c.fillText(s,x,y);};
  const ellipse=(x:number,y:number,rx:number,ry:number,color:string)=>{c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fillStyle=color;c.fill();};
  const block=(x:number,y:number,w:number,h:number,d:number,top:string,front:string,side='#bdccda')=>{
   poly3([[x,y,0],[x+w,y,0],[x+w,y,d],[x,y,d]],top,true);
   poly3([[x,y,0],[x+w,y,0],[x+w,y+h,0],[x,y+h,0]],front,true);
   poly3([[x+w,y,0],[x+w,y,d],[x+w,y+h,d],[x+w,y+h,0]],side,true);
  };
  const shadow=(x:number,y:number,w:number,d:number)=>{c.save();c.globalAlpha=.28;poly3([[x,y,0],[x+w,y,0],[x+w,y,d],[x,y,d]],'#a1aeb7');c.restore();};
  const platform=(x:number,y:number,w:number,depth=105)=>{shadow(x+12,y+38,w,depth);block(x,y,w,27,depth,'#e5edf5','#b6c6d4','#cedae4');};
  const arrow=(x:number,y:number,x2:number,y2:number,color:string=P.blue)=>{const a=Math.atan2(y2-y,x2-x);c.strokeStyle=color;c.lineWidth=6;c.beginPath();c.moveTo(x,y);c.lineTo(x2,y2);c.stroke();polygon([[x2,y2],[x2-19*Math.cos(a-.45),y2-19*Math.sin(a-.45)],[x2-19*Math.cos(a+.45),y2-19*Math.sin(a+.45)]],color);};
  const avatar=(x:number,y:number,color:string=P.blue)=>{ellipse(x+20,y+56,49,15,'#d3dde4');block(x-26,y-25,50,66,47,'#a5c9e7',color,'#24466c');const face=pt(x+4,y+2,0);ellipse(face[0],face[1],4,5,'white');ellipse(face[0]+14,face[1],4,5,'white');};
  const button=(x:number,y:number,down:boolean,caption:string)=>{
   shadow(x-154,y+105,288,95);block(x-154,y+70,288,18,95,'#e3e9ef','#c2cfda');
   ellipse(x,y+60,118,43,'#aebdcb');c.fillStyle='#234773';c.fillRect(x-103,y+27,206,34);ellipse(x,y+61,103,39,'#234773');
   const dy=down?29:0;c.fillStyle=P.blue;c.fillRect(x-103,y-6+dy,206,27);ellipse(x,y+21+dy,103,38,P.blue);ellipse(x,y-6+dy,103,38,down?'#527cad':'#82a9d3');label('A',x,y-6+dy,39,'white',700);label(caption,x,y+154,29);
  };
  const hint=(s:string)=>label(s,0,320,35,P.ink,500);
  c.save();c.globalAlpha=clamp(elapsed/.4);c.translate(Math.sin(elapsed*.2)*5,0);
  // Faint original floor grid establishes a ground plane rather than a flat card.
  c.save();c.globalAlpha=.20;c.strokeStyle='#c3d0db';c.lineWidth=1;
  for(let z=0;z<=240;z+=40){const a=pt(-720,245,z),b=pt(680,245,z);c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();}
  for(let x=-720;x<=680;x+=100){const a=pt(x,245,0),b=pt(x,245,240);c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(b[0],b[1]);c.stroke();}c.restore();
  if(this.mode===1){
   const active=t<3.5,count=Math.min(14,Math.floor(t*4)),speed=phase%2===0?31:23;
   button(-540,35,active&&(t*4)%1<.4,active?'짧게 집중':'잠깐 쉬기');
   platform(-190,120,690);avatar(-160+count*speed,46,active?P.blue:P.green);
   arrow(-345,5,-235,5);block(125,-178,180,86,45,'#dfeaf5',P.blue,'#234773');label(String(count).padStart(2,'0'),222,-130,72,'white',700);
   label(active?'입력 횟수 → 이동 거리':'회복 → 다음 시도',190,-258,39,active?P.blue:P.green);
   label('집중',-75,222,27,P.blue);arrow(0,220,140,220,P.muted);label('휴식',210,222,27,P.green);arrow(255,220,400,220,P.muted);label('다음 시도',497,222,27,P.blue);
   hint('빈도를 결과로 연결하고, 짧은 휴식을 준다');
  }else if(this.mode===2){
   const wide=phase%2!==0,target=wide?164:84,hitTime=phase===1?2.25:phase===2?3.25:2.8;
   const x=-185+650*clamp(t/3.3),pressed=t>=hitTime&&t<hitTime+.65;
   button(-555,50,pressed,t<hitTime?'움직임을 읽기':'누른 순간');platform(-190,100,790);
   c.save();c.globalAlpha=.75;block(425-target/2,-100,target,200,100,'#d6e6d0','#e4efdf','#b7d0b0');c.restore();
   const stopX=t<hitTime?x:-185+650*clamp(hitTime/3.3);avatar(stopX,18);arrow(-345,-30,-240,-30);
   const outcome=phase===1?'조금 빨랐다':phase===2?'조금 늦었다':'목표에 맞았다';
   label(t<hitTime?'예측 → 기다림 → 입력':outcome,200,-238,43,t<hitTime?P.ink:phase===0?P.green:P.red);
   label(wide?'넓은 판정 구간':'좁은 판정 구간',446,172,28,P.green);
   label('빠름',-125,175,26,P.muted);label('늦음',622,175,26,P.muted);
   hint('판정 폭과 실패 이유가 다음 판단을 만든다');
  }else if(this.mode===3){
   const signal=t>=2.1,response=t>=2.36;
   button(-540,55,response&&t<3.4,response?'신호 확인 → 입력':'신호 전에는 기다리기');
   platform(-190,177,760);block(165,-178,144,255,74,'#d5e3ef','#dae2e9','#a6b8c8');
   ellipse(236,-86,82,82,signal?P.yellow:'#eef1f4');ellipse(225,-101,55,22,signal?'#fff3be':'#fafbfc');label(signal?'!':'…',236,-81,93,signal?P.ink:P.muted,700);
   avatar(response?465:-70,95);if(response)arrow(-12,130,390,130,P.green);
   label(response?'확인한 뒤 빠르게':signal?'명확한 신호!':'대기 시간에도 긴장',224,-270,41);
   if(response)label('예시 260 ms',365,237,27,P.blue);
   hint('모양 · 색 · 소리로 같은 신호를 전달한다');
  }else if(this.mode===4){
   const local=(elapsed%6)/2,item=Math.min(2,Math.floor(local)),p=local%1,bomb=item===1,down=!bomb;
   button(-550,50,down,down?'누름 · 받기':'뗌 · 피하기');platform(-210,155,820);
   const x=570-p*720;
   if(bomb){ellipse(x+12,141,40,12,'#d3dde4');ellipse(x,13,41,41,'#303d4b');ellipse(x-12,-1,13,18,'#75808b');arrow(x+1,-27,x+16,-63,P.red);}
   else{const drop=85*clamp((p-.74)/.26);ellipse(x+7,143,33,10,'#d3dde4');ellipse(x,8+drop,29,40,'#f2d56e');ellipse(x-9,-1+drop,8,16,'#fff7d6');}
   const y=down?105:213;block(-171,y,125,66,76,'#e2eedf',P.green,'#36513a');
   label(bomb?'같은 경로 · 피할 물체':'같은 경로 · 받을 물체',200,-230,43,bomb?P.red:P.green);
   arrow(500,190,245,190,P.muted);label('상황을 보고 상태 바꾸기',185,244,29,P.muted);
   hint('토글이 아니라, 지금 누르는 상태를 선택한다');
  }else if(this.mode===5){
   const holdDemo=elapsed>=this.duration*.42;
   if(!holdDemo){
    const press=t>=1.4&&t<2.25,jump=Math.sin(clamp((t-1.4)/2.3)*Math.PI)*175;
    platform(-675,-8,315);platform(238,-8,345);button(-440,60,press,'입력만 표시');button(435,60,press,'입력과 결과');
    label(t>=1.4?'1':'0',-440,-125,91,P.muted);avatar(427,-60-jump);label('A · 숫자만 변화',-440,-305,34,P.muted);label('B · 움직임과 결과',440,-305,34,P.blue);
    if(press)arrow(435,-12,435,-75,P.green);hint('내가 눌렀다는 사실과, 결과를 함께 보여준다');
   }else{
    const p=clamp((t-.7)/2.5),x=-220+780*p,shortY=42-Math.sin(p*Math.PI)*100,longY=42-Math.sin(p*Math.PI)*225;
    button(-580,77,t<1.4,'짧게 / 길게 누르기');platform(-265,152,360);platform(325,152,350);
    c.save();c.setLineDash([9,7]);c.strokeStyle='#a9bed1';c.lineWidth=3;c.beginPath();c.moveTo(-220,42);c.quadraticCurveTo(140,-420,560,42);c.stroke();c.restore();
    avatar(x,longY,P.blue);c.save();c.globalAlpha=.32;avatar(x,shortY,P.green);c.restore();
    arrow(-75,-120,-75,-205,P.blue);label('누르는 길이 → 높이',200,-271,43,P.blue);
    label('짧은 점프',-100,235,27,P.green);label('높은 점프',452,235,27,P.blue);hint('길게 누르는 동안에도 판단할 것이 있어야 한다');
   }
  }else{
   const names=['속도','순간','신호','상태'],active=Math.min(3,Math.floor(elapsed/(this.duration/4)));
   for(let i=0;i<4;i++){
    const x=-700+i*405,z=(i===active?26:0);shadow(x+8,-15,264,80);block(x,-185-z,264,155,85,i===active?'#d4e5f4':'#edf1f4',i===active?P.blue:'#dbe3ea',i===active?'#24466c':'#b6c6d4');
    label(names[i],x+132,-132-z,42,i===active?'white':P.ink,700);
    label(['얼마나 빠르게','언제 맞출까','나왔는지 확인','유지할까 바꿀까'][i],x+132,-66-z,25,i===active?'white':P.muted,500);
   }
   button(0,78,t>1.3&&t<2,'하나의 버튼');arrow(-8,-28,-8,-90,P.blue);
   hint(this.mode===0?'입력은 하나여도, 판단은 여러 개':'무엇을 보고 · 언제 누르고 · 무엇이 달라질까');
  }
  c.restore();this.drawChildren(c);
 }
}
export function* diagramScene(view:View2D,index:number,seconds:number){
 view.fill(P.background);const clock=createSignal(0);
 view.add(<Txt text={String(index+1).padStart(2,'0')+'  ONE BUTTON'} x={-864} y={-477} offset={[-1,0]} fontSize={24} fontWeight={600} fontFamily={P.font} fill={P.blue}/>);
 view.add(<Txt text={TITLES[index]} x={-864} y={-405} offset={[-1,0]} fontSize={52} fontWeight={700} fontFamily={P.font} fill={P.ink}/>);
 const notes=[['커비 · 캐너볼트 · 지오메트리 대시','같은 버튼이 만드는 서로 다른 판단'],['집중과 휴식의 흐름','사람마다 다른 입력 속도도 고려하기'],['읽고 기다려서 누르기','빠름 / 늦음을 알려주면 다음 시도가 쉬워진다'],['신호 전에 기다리고, 신호 뒤에 반응하기','신호를 숨기는 것과 긴장을 만드는 것은 다르다'],['누른 상태 ↔ 뗀 상태','다가오는 물체에 따라 유지하거나 바꾸기'],['숫자만 변화 ↔ 행동과 결과가 연결','캐너볼트: 누르는 길이도 결과를 바꾼다'],['입력의 수보다 판단의 내용','판단 → 입력 → 이해할 수 있는 결과']];
 view.add(<Txt text={()=>notes[index][clock()<seconds*.55?0:1]} y={-342} fontSize={28} fontFamily={P.font} fill={P.muted}/>);
 view.add(new InputDiagram(index,()=>clock(),seconds));yield* tween(seconds,v=>clock(v*seconds));
}
