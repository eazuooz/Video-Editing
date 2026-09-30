import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal, tween} from '@motion-canvas/core';
import {PAPER as P} from '../../styles/research-paper';

export const TITLES = ['버튼은 하나, 판단은 여러 개','연타 — 얼마나 빠르게 누를까','타이밍 — 지금 누르면 맞을까','반응 — 신호가 나오면 눌러라','누르기와 떼기 — 무엇을 받아들일까','같은 입력, 더 선명한 결과','버튼보다 먼저, 판단을 설계하자'];
const clamp = (v: number) => Math.max(0, Math.min(1, v));
class InputDiagram extends Node {
  constructor(private mode: number, private time: () => number) {super({});}
  protected draw(c: CanvasRenderingContext2D) {
    const elapsed = this.time(), phase=Math.floor(elapsed/6), t = elapsed%6;
    const label = (s: string, x: number, y: number, size = 36, color: string = P.ink, weight = 600) => {
      c.fillStyle = color; c.font = weight + ' ' + size + 'px "Malgun Gothic", sans-serif';
      c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(s, x, y);
    };
    const rect = (x: number,y: number,w: number,h: number,color: string) => {c.fillStyle=color;c.fillRect(x,y,w,h);};
    const ellipse = (x: number,y: number,rx: number,ry: number,color: string) => {
      c.beginPath(); c.ellipse(x,y,rx,ry,0,0,Math.PI*2); c.fillStyle=color;c.fill();
    };
    const poly = (pts: number[][], color: string) => {
      c.beginPath(); pts.forEach(([x,y],i)=>i ? c.lineTo(x,y) : c.moveTo(x,y));
      c.closePath();c.fillStyle=color;c.fill();
    };
    const button = (x: number,y: number,down: boolean, caption: string) => {
      poly([[x-150,y+80],[x,y+135],[x+150,y+80],[x,y+25]], '#dce2e8');
      ellipse(x,y+66,116,44,'#b7c3d0');
      rect(x-105,y+50,210,8,'#234773'); ellipse(x,y+58,105,40,'#234773');
      const dy=down?38:0;
      rect(x-105,y+dy,210,25,P.blue); ellipse(x,y+dy+25,105,40,P.blue);
      ellipse(x,y+dy,105,40,down?'#527cad':'#82a9d3'); label('A',x,y+dy,40,'#ffffff',700);
      label(caption,x,y+197,32);
    };
    const track = (x: number,y: number,w: number) => {
      poly([[x,y],[x+w,y],[x+w+65,y+38],[x+65,y+38]],'#e5edf5');
      poly([[x+65,y+38],[x+w+65,y+38],[x+w+65,y+63],[x+65,y+63]],'#bccbd8');
    };
    const avatar = (x: number,y: number,color: string=P.blue) => {
      ellipse(x+10,y+45,44,12,'#c5ced5');
      poly([[x-28,y-25],[x+22,y-40],[x+52,y-20],[x,y]],'#a7c6e2');
      poly([[x-28,y-25],[x,y],[x,y+45],[x-28,y+20]],'#24466c');
      poly([[x,y],[x+52,y-20],[x+52,y+24],[x,y+45]],color);
      ellipse(x+21,y+9,4,5,'#ffffff'); ellipse(x+36,y+4,4,5,'#ffffff');
    };
    const hint=(s:string)=>label(s,0,315,39,P.ink,500);
    c.save();
    if (this.mode===1) {
      const count=Math.min(16,Math.floor(t*3));
      button(-490,60,t<5.35&&(t*3)%1<.35,'짧게, 빠르게');
      track(-170,115,670); avatar(-150+count*36,70);
      label(String(count).padStart(2,'0'),215,-160,112,P.blue,700);
      label('누른 횟수',215,-60,30,P.muted,500); hint('입력의 빈도가 결과를 바꾼다');
    } else if (this.mode===2) {
      const targetWidth=phase%2===0?94:164;
      const x=-155+610*clamp(t/3.4);
      button(-490,60,t>=3.4&&t<4.15,t<3.4?'기다리기':'지금!'); track(-170,65,760);
      rect(454-targetWidth/2,-80,targetWidth,154,'#e2ecd9'); rect(438,-80,30,154,P.green);
      ellipse(x,33,24,12,P.blue); rect(x-24,-11,48,44,P.blue); ellipse(x,-11,24,12,'#86add1');
      label(t<3.4?'목표에 겹치는 순간':'맞았다!',220,-178,58,t<3.4?P.ink:P.green);
      label('너무 빠름',-90,175,28,P.muted); label(phase%2===0?'좁은 목표':'넓은 목표',456,175,28,P.green);
      hint('움직임을 읽고, 누를 순간을 고른다');
    } else if (this.mode===3) {
      const signal=t>=2.6, response=t>=2.85;
      button(-490,60,response&&t<3.7,response?'반응!':'아직 누르지 않기');
      ellipse(230,-55,108,108,signal?P.yellow:'#edf0f3'); label(signal?'!':'…',230,-58,120,signal?P.ink:P.muted,700);
      track(-150,167,690); avatar(response?410:-80,118);
      label(response?'신호 → 입력':signal?'지금!':'신호를 기다리는 중',230,-230,45);
      if(response)label('예시 250 ms',225,105,34,P.blue); hint('신호 확인 후, 빠르게 반응한다');
    } else if (this.mode===4) {
      const phase=Math.min(2,Math.floor(t/2)), local=(t%2)/2, bomb=phase===1, down=!bomb;
      button(-490,60,down,down?'누름 · 받기':'뗌 · 피하기'); track(-120,140,700);
      const x=540-local*620;
      if(bomb){
        ellipse(x,30,43,43,'#303d4b'); rect(x-5,-25,10,22,'#303d4b');
        poly([[x,-48],[x+9,-33],[x+25,-38],[x+12,-22],[x+19,-7],[x+1,-15],[x-10,-4],[x-9,-23],[x-23,-30],[x-7,-33]],'#d7883f');
      } else {
        const drop=80*clamp((local-.65)/.35);
        ellipse(x,20+drop,31,43,'#f2d56e'); ellipse(x-9,8+drop,9,16,'#fff7d6');
      }
      const basketY=down?110:210;
      poly([[-127,basketY],[-17,basketY],[-33,basketY+70],[-112,basketY+70]],'#507452');
      label(bomb?'폭탄은 피하고':'달걀은 받고',210,-170,57,bomb?P.red:P.green);
      label('다가오는 물체',300,240,29,P.muted,500); hint('같은 버튼으로, 서로 다른 상황을 판단한다');
    } else if(this.mode===5) {
      const press=t>=2.2&&t<3.2;
      button(-450,40,press,'입력만 표시'); button(450,40,press,'입력 + 결과');
      const jump=Math.max(0,Math.sin(clamp((t-2.2)/2)*Math.PI))*145;
      avatar(430,-150-jump); label(t>=2.2?'1':'0',-450,-170,92,P.muted);
      label('A',-450,-295,34,P.muted);label('B',450,-295,34,P.blue);
      hint('효과의 양보다, 행동과 결과의 연결');
    } else {
      button(0,80,t>1.1&&t<1.8,'버튼 하나');
      ['속도','순간','신호','상태'].forEach((s,i)=>{
        const x=-570+i*380;
        ellipse(x,-185,85,55,i===Math.min(3,Math.floor(t/1.5))?P.blueLight:P.panel); label(s,x,-185,42);
      });
      hint(this.mode===0?'조작은 단순하게, 판단은 흥미롭게':'무엇을 보고 · 언제 누르고 · 무엇이 달라질까');
    }
    c.restore(); this.drawChildren(c);
  }
}
export function* diagramScene(view: View2D, index: number, seconds: number) {
  view.fill(P.background);
  const clock=createSignal(0);
  view.add(<Txt text={String(index+1).padStart(2,'0')+'  ONE BUTTON'} x={-864} y={-477} offset={[-1,0]} fontSize={24} fontWeight={600} fontFamily={P.font} fill={P.blue}/>);
  view.add(<Txt text={TITLES[index]} x={-864} y={-405} offset={[-1,0]} fontSize={52} fontWeight={700} fontFamily={P.font} fill={P.ink}/>);
  const notes=[
    ['속도 · 순간 · 신호 · 상태','무엇을 보고 판단할까?'],
    ['짧은 집중 → 휴식 → 다음 시도','사람마다 다른 입력 속도도 고려하기'],
    ['목표 폭을 바꾸면 난이도도 달라진다','빠름 / 늦음을 알려주면 다음 시도가 쉬워진다'],
    ['기다림은 긴장, 신호는 명확하게','모양 + 색 + 소리로 신호를 함께 전달하기'],
    ['누르고 있는 상태와 뗀 상태','토글이 아니라, 상황을 보고 상태를 유지하거나 바꾸기'],
    ['숫자만 변화 ↔ 입력과 결과가 연결','누르는 동안 모으고, 떼는 순간 결과를 보여주기'],
    ['무엇을 보고 · 언제 결정할까?','입력의 개수보다 판단과 결과의 관계'],
  ];
  view.add(<Txt text={()=>notes[index][Math.floor(clock()/6)%2]} y={-340} fontSize={28} fontFamily={P.font} fill={P.muted}/>);
  view.add(new InputDiagram(index,()=>clock()));
  // Related original demonstrations, at natural event speed. External footage is never looped.
  yield* tween(seconds,v=>clock(v*seconds));
}
