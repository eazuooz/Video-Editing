import {Img,Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {LectureCaption} from './caption';
import timeline from './timing.generated.json';
import page01 from './assets/page01.png';
import page14 from './assets/page14.png';
import page48 from './assets/page48.png';
const S=1472/1200;
const pt=(x:number,y:number):[number,number]=>[(x-600)*S,(y-337.5)*S];
const ramp=(t:number,a:number,b:number)=>Math.max(0,Math.min(1,(t-a)/(b-a)));
const navy='#1b2c50',blue='#2f5faa';
export function* slide(view:View2D,index:number,captions=true){
  const data=timeline.scenes[index],clock=createSignal(0),t=()=>clock();view.fill('#fff');
  const page=new Node({y:-106,opacity:()=>ramp(t(),0,.25)*(1-ramp(t(),data.duration-.25,data.duration))});view.add(page);
  page.add(<Img src={[page01,page14,page48][index]} width={1472} height={828}/>);
  if(index===1){
    // Rings stay outside the original matrices; their values are unaltered.
    const cue=data.cues[1];
    const active=()=>data.emphasis.reduce((current,e,i)=>t()>=e.time?i:current,-1);
    [202,386,560].forEach((cy,i)=>{
      const at=data.cues[0].start+i*1.7;
      page.add(<Rect position={pt(1054,cy)} width={176*S} height={110*S} stroke={blue} lineWidth={3} fill={'#00000000'} opacity={()=>t()<cue.start?.5*ramp(t(),at,at+.5):active()===i?1:.12}/>);
    });
  }
  if(index===2){
    // Two independent inputs meet: scene features do not create camera tokens.
    const a=data.cues[2].start,b=data.cues[3].start,d=data.cues[4].start;
    const box=(x:number,y:number,w:number,label:string,at:number,sub='')=>{
      const n=new Node({position:pt(x,y),opacity:()=>ramp(t(),at,at+.7)});page.add(n);
      n.add(<Rect width={w*S} height={85*S} fill={'#f2f4f7'} stroke={'#aab5c8'} lineWidth={1.5}/>);
      n.add(<Txt text={label} y={sub?-12:0} fontFamily={'Malgun Gothic'} fontSize={25*S} fontWeight={600} fill={navy}/>);
      if(sub)n.add(<Txt text={sub} y={24} fontFamily={'Malgun Gothic'} fontSize={15*S} fill={'#65728a'}/>);
    };
    const arrow=(p:[number,number],q:[number,number],at:number)=>page.add(<Line points={[pt(...p),pt(...q)]} stroke={blue} lineWidth={3.5} endArrow arrowSize={11} end={()=>ramp(t(),at,at+.7)} opacity={()=>ramp(t(),at,at+.15)}/>);
    box(290,235,225,'삼각형 토큰',data.cues[1].start,'메시 · 재질 · 발광');
    arrow([410,235],[530,235],a);box(650,235,225,'장면 특징',a+.3,'시점 독립 단계');
    box(290,425,225,'카메라 레이',b,'관찰 방향을 토큰으로');
    arrow([410,425],[530,425],d);arrow([650,287],[650,365],d);
    box(650,425,225,'정보 조회',d+.3,'시점 의존 단계');
    arrow([770,425],[825,425],d+1.7);box(890,425,115,'이미지',d+2.2,'디코더');
    page.add(<Txt position={pt(570,548)} text={'삼각형의 정보  +  카메라의 관찰 방향'} fontFamily={'Malgun Gothic'} fontSize={23*S} fill={navy} opacity={()=>ramp(t(),d+3,d+3.7)}/>);
  }
  if(captions){const c=new LectureCaption({y:400});c.text(()=>data.cues.find(c=>t()>=c.start&&t()<c.end)?.ko??'');view.add(c);}
  yield* tween(data.frames/60,p=>clock(p*data.duration));
}
