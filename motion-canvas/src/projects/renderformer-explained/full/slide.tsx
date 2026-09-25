import {Img,Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {createSignal,tween} from '@motion-canvas/core';
import {LectureCaption} from '../preview/caption';
import {pages} from './pages.generated';
import overlayData from './overlays.generated.json';

export interface PageTiming {
  id:string;sourcePage:number;title:string;frames:number;duration:number;
  cues:{start:number;end:number;ko:string;en?:string}[];
}
const SCALE=1472/960;
type Overlay=[number,number,number,number,string,number];
const overrides=overlayData.pages as unknown as Record<string,Overlay[]>;
const point=(x:number,y:number):[number,number]=>[(x-480)*SCALE,(y-270)*SCALE];
const ramp=(t:number,a:number,b:number)=>Math.max(0,Math.min(1,(t-a)/(b-a)));
function wrapText(text:string,size:number,width:number){
  const context=document.createElement('canvas').getContext('2d')!;
  context.font=`500 ${size}px 'Malgun Gothic'`;
  const lines:string[]=[];
  for(const paragraph of text.split('\n')){
    let line='';
    for(const char of paragraph){
      if(line&&context.measureText(line+char).width>width){lines.push(line);line='';}
      line+=char;
    }
    lines.push(line);
  }
  return lines.join('\n');
}

export function* lectureSlide(view:View2D,data:PageTiming,captions=true) {
  const clock=createSignal(0),time=()=>clock();view.fill('#fff');
  const paper=new Node({y:-106,opacity:()=>ramp(time(),0,.25)*(1-ramp(time(),data.duration-.25,data.duration))});
  view.add(paper);
  paper.add(<Img src={pages[data.sourcePage-1]} width={1472} height={828}/>);
  // White masks replace inaccurate pixels, not small footnote disclaimers.
  // All replacements remain text in code/JSON; the source PDF is unchanged.
  for(const [x,y,w,h,text,size] of overrides[data.id]??[]){
    const box=new Node({position:point(x+w/2,y+h/2)});paper.add(box);
    box.add(<Rect width={w*SCALE} height={h*SCALE} fill={'#fff'}/>);
    box.add(<Txt text={wrapText(text,size,w-14)} x={(-w/2+7)*SCALE} y={(-h/2+7)*SCALE} offset={[-1,-1]}
      width={(w-14)*SCALE} fontFamily={'Malgun Gothic'} fontSize={size*SCALE}
      lineHeight={size*1.5*SCALE} fill={y<=42?'#1b2c50':'#202020'} textWrap={'pre'} fontWeight={y<=42?700:500}/>);
  }
  if(data.sourcePage===75){
    const box=(x:number,y:number,w:number,label:string)=>paper.add(<Rect position={point(x,y)} width={w*SCALE}
      height={50*SCALE} fill={'#f2f4f7'} stroke={'#aab5c8'} lineWidth={1.5}>
      <Txt text={label} fontFamily={'Malgun Gothic'} fontSize={19*SCALE} fill={'#1b2c50'}/></Rect>);
    const arrow=(points:[number,number][])=>paper.add(<Line points={points.map(p=>point(...p))}
      stroke={'#2f5faa'} lineWidth={2.5} endArrow arrowSize={9}/>);
    arrow([[150,245],[175,245],[175,175],[210,175]]);
    arrow([[175,245],[175,305],[210,305]]);
    arrow([[350,175],[390,175]]);arrow([[500,175],[565,175],[565,245],[575,245]]);
    arrow([[350,305],[550,305],[550,245],[575,245]]);
    arrow([[695,245],[735,245]]);
    box(100,245,100,'입력 X');box(280,175,140,'Wgate');box(280,305,140,'Wvalue');
    box(445,175,110,'SiLU');box(635,245,120,'원소별 곱');box(805,245,140,'Wout → 출력');
  }
  if(data.sourcePage===48){
    const at=(i:number)=>data.cues[i]?.start??(.25+i*.45);
    const box=(x:number,y:number,w:number,label:string,sub:string,start:number)=>{
      const n=new Node({position:point(x,y),opacity:()=>ramp(time(),start,start+.5)});paper.add(n);
      n.add(<Rect width={w*SCALE} height={68*SCALE} fill={'#f2f4f7'} stroke={'#aab5c8'} lineWidth={1.5}/>);
      n.add(<Txt text={label} y={-10} fontFamily={'Malgun Gothic'} fontSize={22*SCALE} fontWeight={600} fill={'#1b2c50'}/>);
      n.add(<Txt text={sub} y={24} fontFamily={'Malgun Gothic'} fontSize={13*SCALE} fill={'#65728a'}/>);
    };
    const arrow=(p:[number,number],q:[number,number],start:number)=>paper.add(<Line points={[point(...p),point(...q)]}
      stroke={'#2f5faa'} lineWidth={3} endArrow arrowSize={10} end={()=>ramp(time(),start,start+.5)}/>);
    box(232,188,180,'삼각형 토큰','메시 · 재질 · 발광',at(1));
    arrow([328,188],[424,188],at(2));box(520,188,180,'장면 특징','시점 독립 단계',at(2)+.2);
    box(232,340,180,'카메라 레이','관찰 방향을 토큰으로',at(3));
    arrow([328,340],[424,340],at(4));arrow([520,230],[520,292],at(4));
    box(520,340,180,'정보 조회','시점 의존 단계',at(4)+.2);
    arrow([616,340],[660,340],at(4)+.5);box(722,340,108,'이미지','디코더',at(4)+.7);
  }
  if(data.sourcePage===14&&data.cues.length){
    // No unverified numeric values are animated as computed results.
    [161.6,308.8,448].forEach((cy,i)=>paper.add(<Rect position={point(843.2,cy)} width={140.8*SCALE}
      height={88*SCALE} stroke={'#2f5faa'} lineWidth={3} fill={'#00000000'}
      opacity={()=>{const start=data.cues[1]?.start??0;return time()>=start+i*2&&time()<start+(i+1)*2?.85:0;}}/>));
  }
  if(captions){const caption=new LectureCaption({y:400});caption.text(()=>data.cues.find(c=>time()>=c.start&&time()<c.end)?.ko??'');view.add(caption);}
  // End inside the final frame interval: avoids an extra frame at exact boundaries.
  yield* tween((data.frames-.5)/60,p=>clock(p*data.duration));
}
