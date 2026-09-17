import {Node,Rect,Txt,Line,View2D} from '@motion-canvas/2d';
import {cancel,easeInOutCubic,usePlayback,ThreadGenerator} from '@motion-canvas/core';
import {BOOK as P} from '../styles';
import board from '../../../../../projects/choice-driven-classics/script/storyboard.json';

export const shots = board.scenes;
export function page(view:View2D,index:number,ui=false) {
  view.fill(P.paper);
  const content = new Node({opacity:0}); view.add(content);
  const top = ui ? '기획 화면 예시' : index===5 ? '디지털 출판사 · 창업 아이디어' : '세계 고전 · 선택형 PC 게임';
  content.add(<>
    <Txt x={-856} y={-491} offset={[-1,0]} text={top} fontFamily={P.sans} fontSize={24} fill={P.muted}/>
    <Txt x={856} y={-491} offset={[1,0]} text={`${String(index+1).padStart(2,'0')} / 06`} fontFamily={P.sans} fontSize={22} fill={P.muted}/>
    <Line points={[[-856,416],[856,416]]} stroke={P.line} lineWidth={1}/>
    <Txt key="bottom-caption" y={472} text={shots[index].caption} fontFamily={P.sans} fontSize={36} fill={P.ink}/>
  </>);
  return content;
}
export function* envelope(node:Node,duration:number,action:ThreadGenerator) {
  // Count frames explicitly: concurrent tween completion can otherwise add a
  // frame at a scene boundary. This project has a user-mandated 3600-frame cut.
  yield action;
  const fps=usePlayback().fps;
  const frames=Math.round(duration*fps);
  for(let frame=0;frame<frames;frame++){
    const time=frame/fps;
    const fade=Math.min(1,time/.7,(duration-time)/.7);
    node.opacity(easeInOutCubic(Math.max(0,fade)));
    yield;
  }
  cancel(action);
}
export function label(parent:Node,text:string,x:number,y:number,size=28,muted=false) {
  const t = new Txt({text,x,y,fontFamily:P.sans,fontSize:size,fill:muted?P.muted:P.ink});
  parent.add(t); return t;
}
export function heading(parent:Node,text:string,x:number,y:number,size=58,width?:number) {
  const t = new Txt({text,x,y,fontFamily:P.serif,fontSize:size,fill:P.ink,lineHeight:size*1.5,width,textAlign:'left'});
  parent.add(t);return t;
}
