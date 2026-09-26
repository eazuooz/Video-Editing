import {Node, Txt, View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';

export const titles=['게임을 담는 작은 창','화면 비율: 창의 모양','FOV: 화면 안에 담는 범위','화면 점유율: 대상의 크기','보이는 화면 ≠ 읽을 수 있는 공간','지금 필요한 것이 보이는가?'];
class Diagram extends Node {
  constructor(private index:number,private time:()=>number){super({y:-40});}
  protected draw(c:CanvasRenderingContext2D){
    const t=this.time(),phase=(1-Math.cos(t*.45))/2;
    const text=(s:string,x:number,y:number,size=34,color:string=P.ink)=>{c.fillStyle=color;c.font=`600 ${size}px 'Malgun Gothic'`;c.textAlign='center';c.fillText(s,x,y);};
    const rect=(x:number,y:number,w:number,h:number,color:string)=>{c.fillStyle=color;c.fillRect(x,y,w,h);};
    const poly=(pts:number[][],color:string)=>{c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();c.fillStyle=color;c.fill();};
    const road=(cx:number,cy:number,w:number,h:number,hfov:number,occlusion=0)=>{
      c.save();c.translate(cx-w/2,cy-h/2);c.beginPath();c.rect(0,0,w,h);c.clip();
      rect(0,0,w,h,'#eaf0f4');rect(0,h*.42,w,h*.58,'#ccd9cc');
      const f=w/2/Math.tan(hfov*Math.PI/360),p=(x:number,z:number,y=0)=>[w/2+f*x/z,h*.42+f*(1.8-y)/z];
      poly([p(-4,80),p(4,80),p(4,2),p(-4,2)],'#859099');
      for(let z=65;z>5;z-=6){const zz=z-t*3%6;poly([p(-.07,zz),p(.07,zz),p(.07,zz+2),p(-.07,zz+2)],'#fff');}
      for(let z=60;z>6;z-=8){const zz=z-t*2%4;for(const s of [-1,1]){const a=p(s*6,zz),b=p(s*6,zz,3.8);poly([[a[0]-f*.45/zz,a[1]],b,[a[0]+f*.45/zz,a[1]]],'#678773');}}
      const a=p(0,14),size=f*2/14;rect(a[0]-size/2,a[1]-size*.5,size,size*.5,P.blue);poly([[a[0]-size*.4,a[1]-size*.5],[a[0]-size*.27,a[1]-size*.8],[a[0]+size*.27,a[1]-size*.8],[a[0]+size*.4,a[1]-size*.5]],'#adc9df');
      if(occlusion){c.globalAlpha=occlusion;poly([[0,h*.64],[w*.2,h*.58],[w*.8,h*.58],[w,h*.64],[w,h],[0,h]],'#3d4b56');rect(w*.73,h*.18,w*.24,h*.29,'#f6f7f8');c.globalAlpha=1;}
      c.restore();c.strokeStyle=P.line;c.lineWidth=3;c.strokeRect(cx-w/2,cy-h/2,w,h);
    };
    c.save();
    if(this.index===0){
      road(260,0,1100,590,85);
      poly([[-660,0],[-305,-295],[-305,295]],P.blueLight);
      c.beginPath();c.ellipse(-660,0,50,30,0,0,Math.PI*2);c.fillStyle='#fff';c.fill();c.strokeStyle=P.ink;c.lineWidth=3;c.stroke();c.beginPath();c.arc(-647,0,17,0,Math.PI*2);c.fillStyle=P.blue;c.fill();
      rect(-308,-310,18,620,P.blue);text('크기 · 거리',-650,145);text('화면 속 카메라',260,365);
    }else if(this.index===1){
      const h=360,v=50,hf=(w:number)=>2*Math.atan(w/h*Math.tan(v*Math.PI/360))*180/Math.PI;
      road(-460,0,640,h,hf(640));road(380,0,840,h,hf(840));
      text('16:9',-460,-230,48);text('21:9',380,-230,48);text('세로 FOV 고정',0,285,36,P.blue);text('같은 물체 크기 · 양옆은 더 넓게',0,350,32);
    }else if(this.index===2){
      road(-440,0,800,510,60);road(440,0,800,510,100);text('수평 FOV 60°',-440,-300,40);text('수평 FOV 100°',440,-300,40);
      text('대상은 크게',-440,325,36,P.blue);text('주변은 넓게',440,325,36,P.blue);
    }else if(this.index===3){
      for(const [x,s,label] of [[-440,35,'멀리서 정밀 조준'],[440,120,'가까이서 동작 읽기']] as [number,number,string][]){
        rect(x-400,-250,800,500,'#edf1f5');poly([[x-400,250],[x,0],[x+400,250]],'#cdd8e2');
        c.fillStyle=P.red;c.beginPath();c.arc(x,-s*.9,s*.23,0,Math.PI*2);c.fill();poly([[x-s*.25,-s*.6],[x+s*.25,-s*.6],[x+s*.45,s*.45],[x-s*.45,s*.45]],P.red);
        rect(x-s*.32,s*.35,s*.22,s*.6,P.red);rect(x+s*.1,s*.35,s*.22,s*.6,P.red);text(label,x,-300,40);
      }
      text('크기 · 거리 · 대비',0,340,36,P.blue);
    }else if(this.index===4){
      road(-440,0,800,510,85,1);road(440,0,800,510,85,.08);
      text('가림이 많은 화면',-440,-300,40);text('판단할 공간 확보',440,-300,40);text('필수 정보는 남기고 · 가리는 요소는 조절',0,340,34,P.blue);
    }else{
      road(0,-50,1320,500,70+phase*15,.15*(1-phase));
      for(const [x,head,body] of [[-560,'화면 비율','창의 모양'],[0,'FOV','담는 범위'],[560,'화면 점유율','대상의 크기']] as [number,string,string][]){
        text(head,x,295,36,P.blue);text(body,x,350,30);
      }
    }
    c.restore();this.drawChildren(c);
  }
}
export function* diagramScene(view:View2D,index:number,seconds:number){
  view.fill(P.background);const clock=createSignal(0);
  view.add(<Txt text={titles[index]} y={-425} fontFamily={P.font} fontSize={54} fontWeight={700} fill={P.ink}/>);
  view.add(new Diagram(index,()=>clock()));
  yield* tween(seconds,v=>clock(v*seconds));
}
