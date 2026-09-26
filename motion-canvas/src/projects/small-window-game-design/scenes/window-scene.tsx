import {Node,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

const titles=['세상은 넓고, 화면은 작다','운전석의 몰입 · 도로의 가시성','FOV: 주변 범위와 표적 크기','크기보다 먼저, 어떤 판단인가?','이동 방향과 보는 방향','다음 행동이 보이는 화면'];
const captions=['실제 화면의 크기와 카메라 FOV는 다릅니다','어떤 시점이 좋은지는 게임의 목적에 따라 달라집니다','같은 카메라 위치 · 같은 표적 · 같은 화면 폭','크기 · 거리 · 대비를 함께 설계합니다','모니터와 VR은 각각의 표시 조건에서 확인합니다','대상은 보이는가? 가려지는가? 실제 화면에서도 읽히는가?'];
class WindowDiagram extends Node {
  constructor(private chapter:number,private clock:()=>number){super({});}
  protected draw(c:CanvasRenderingContext2D){
    const t=this.clock(),phase=(Math.sin(t*.7)+1)/2;
    const text=(s:string,x:number,y:number,size=30,color:string=P.ink)=>{c.fillStyle=color;c.font=`500 ${size}px 'Malgun Gothic',sans-serif`;c.textAlign='center';c.fillText(s,x,y);};
    const poly=(points:number[][],fill:string)=>{c.beginPath();points.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=fill;c.fill();};
    const rect=(x:number,y:number,w:number,h:number,fill:string)=>{c.fillStyle=fill;c.fillRect(x,y,w,h);};
    const line=(p:number[][],color:string=P.blue,width=4)=>{c.beginPath();p.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.strokeStyle=color;c.lineWidth=width;c.stroke();};
    const road=(cx:number,cy:number,w:number,h:number,fov=80,cockpit=0)=>{
      c.save();c.translate(cx-w/2,cy-h/2);c.beginPath();c.rect(0,0,w,h);c.clip();
      rect(0,0,w,h,'#eaf0f4');rect(0,h*.42,w,h*.58,'#ced9cd');
      const f=(w/2)/Math.tan(fov*Math.PI/360),project=(x:number,z:number,y=0)=>[w/2+f*x/z,h*.42+f*(1.8-y)/z];
      poly([project(-4,60),project(4,60),project(4,2),project(-4,2)],'#858f98');
      for(let z=55;z>3;z-=5){const zz=z-(t*5%5);poly([project(-.06,zz),project(.06,zz),project(.06,zz+2),project(-.06,zz+2)],'#fff');}
      for(let z=45;z>5;z-=8){const zz=z-(t*2%4);for(const sign of [-1,1]){const a=project(sign*5,zz),top=project(sign*5,zz,3);poly([[a[0]-8,a[1]],top,[a[0]+8,a[1]]],'#668579');}}
      const size=f*1.8/17,car=project(0,17);rect(car[0]-size/2,car[1]-size*.5,size,size*.5,P.blue);poly([[car[0]-size*.4,car[1]-size*.5],[car[0]-size*.25,car[1]-size*.8],[car[0]+size*.25,car[1]-size*.8],[car[0]+size*.4,car[1]-size*.5]],'#86a8c8');
      if(cockpit){c.globalAlpha=cockpit;poly([[0,h*.66],[w*.24,h*.61],[w*.76,h*.61],[w,h*.66],[w,h],[0,h]],'#4c5967');line([[0,0],[w*.13,h*.64]],'#394854',18);line([[w,0],[w*.87,h*.64]],'#394854',18);c.beginPath();c.arc(w*.36,h*.97,h*.23,0,Math.PI*2);c.strokeStyle='#1c2938';c.lineWidth=20;c.stroke();c.globalAlpha=1;}
      c.restore();c.strokeStyle=P.line;c.lineWidth=2;c.strokeRect(cx-w/2,cy-h/2,w,h);
    };
    c.save();
    if(this.chapter===0){
      road(310,10,950,530,85);poly([[-625,20],[-200,-250],[-200,275]],'#dfeaf5');
      c.beginPath();c.ellipse(-625,20,48,27,0,0,Math.PI*2);c.fillStyle='#fff';c.fill();c.strokeStyle=P.ink;c.lineWidth=3;c.stroke();c.beginPath();c.arc(-612,20,14,0,Math.PI*2);c.fillStyle=P.blue;c.fill();
      rect(-215,-265,30,555,P.blue);text('실제 화면',-200,355);text('플레이어',-625,115);text('화면 속 카메라가 담은 세계',325,355);
    }else if(this.chapter===1){
      road(-440,10,800,510,80,.35+.65*phase);road(440,10,800,510,80,0);text('운전석 가림의 영향',-440,-285);text('같은 도로 · 운전석 레이어 없음',440,-285);text('시점 선호도나 실제 게임 수치를 측정한 비교가 아닙니다',0,345,26,P.muted);
    }else if(this.chapter===2){
      road(-440,10,800,510,60);road(440,10,800,510,100);text('수평 FOV 60°',-440,-285);text('수평 FOV 100°',440,-285);text('중앙 대상은 크게',-440,345,32,P.blue);text('주변 범위는 넓게',440,345,32,P.blue);
    }else if(this.chapter===3){
      for(const [x,s,label] of [[-440,26,'원거리 정밀 조준'],[440,100,'가까운 동작 읽기']] as [number,number,string][]){
        road(x,10,800,510,90);const y=20;c.fillStyle=P.red;c.beginPath();c.arc(x,y-s*.7,s*.22,0,Math.PI*2);c.fill();poly([[x-s*.25,y-s*.4],[x+s*.25,y-s*.4],[x+s*.4,y+s*.45],[x-s*.4,y+s*.45]],P.red);line([[x-s*.2,y+s*.4],[x-s*.28,y+s]],P.red,s*.15);line([[x+s*.2,y+s*.4],[x+s*.28,y+s]],P.red,s*.15);text(label,x,-285);}
      text('게임의 목적에 따라 필요한 정보 크기가 달라집니다',0,345,30,P.blue);
    }else if(this.chapter===4){
      c.save();c.translate(0,-70);c.scale(.83,.83);
      poly([[-650,215],[40,-150],[680,145],[-10,440]],'#d6e0e7');poly([[-200,450],[180,220],[20,100],[-360,335]],'#708591');
      const x=-80,y=170,angle=-Math.PI/2+(phase-.5)*1.4;
      poly([[x,y],[x+460*Math.cos(angle-.32),y+460*Math.sin(angle-.32)],[x+460*Math.cos(angle+.32),y+460*Math.sin(angle+.32)]],'#dfeaf5');
      rect(x-45,y-45,90,140,P.blue);rect(x-30,y-25,60,45,'#adc9de');line([[x+135,y+65],[x+135,y-210]],P.green,8);poly([[x+135,y-230],[x+119,y-198],[x+151,y-198]],P.green);line([[x,y],[x+330*Math.cos(angle),y+330*Math.sin(angle)]],P.blue,7);
      c.restore();
      text('이동 방향',400,130,34,P.green);text('관찰 방향',-490,-220,34,P.blue);text('고개 회전 · 눈의 움직임 · 시선 추적은 구분합니다',0,365,29,P.muted);
    }else{
      road(0,0,1500,540,85);c.globalAlpha=1-phase;rect(-735,-240,390,400,'#fafafa');rect(390,-240,330,400,'#fafafa');text('큰 안내창',-540,-30);text('장식 UI',555,-30);c.globalAlpha=1;
      text('핵심 대상',0,330,34,P.blue);line([[0,275],[0,70]],P.blue,3);
    }
    c.restore();this.drawChildren(c);
  }
}
export function* windowScene(view:View2D,index:number,duration=6,showDraftLabel=true){
  view.fill(P.background);const clock=createSignal(0);
  view.add(<Txt text={titles[index]} y={-424} fontFamily={P.font} fontSize={54} fontWeight={700} fill={P.ink}/>);
  view.add(new WindowDiagram(index,()=>clock()));
  view.add(<Txt text={captions[index]} y={450} fontFamily={P.font} fontSize={32} fill={P.ink}/>);
  if(showDraftLabel)view.add(<Txt text={'무음 콘셉트 · 자체 설명용 재현 · 실제 게임 미삽입'} y={-495} fontFamily={P.font} fontSize={22} fill={P.muted}/>);
  yield* tween(duration,p=>clock(p*duration));
}
