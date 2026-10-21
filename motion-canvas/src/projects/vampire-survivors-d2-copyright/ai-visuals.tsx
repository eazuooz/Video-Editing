import {Img, Line, Node, Rect, Txt, type View2D} from '@motion-canvas/2d';
import {createSignal, linear} from '@motion-canvas/core';
import {DARK as D} from '../../styles/research-dark';

type Point = [number, number];
export function* aiLesson(view: View2D, d: {kind:string;title:string;duration:number;image:string;cueTimes?:number[]}) {
  const t=createSignal(0);
  const smooth=(v:number)=>{const x=Math.max(0,Math.min(1,v));return x*x*(3-2*x);};
  const cue=(i:number)=>d.cueTimes?.[i]??[.1,3.5,7][i];
  const visible=(i:number)=>()=>smooth((t()-cue(i))/.5);
  const text=(s:string,x:number,y:number,size=48,color:string=D.ink)=><Txt text={s} x={x} y={y} fontFamily={D.font} fontSize={size} lineHeight={size*1.35} fontWeight={600} fill={color}/>;
  const add=(i:number,node:any)=>view.add(<Node opacity={visible(i)}>{node}</Node>);
  const arrow=(i:number,points:Point[],color:string=D.teal)=>view.add(<Line points={points} stroke={color} lineWidth={8} endArrow arrowSize={20} end={visible(i)} lineCap={'round'} lineJoin={'round'}/>);
  view.fill(D.background);view.add(text(d.title,0,-440,56,D.title));
  add(0,<Node><Img src={d.image} x={-430} y={-70} width={900} height={506.25}/><Rect x={-430} y={-70} width={904} height={510.25} stroke={D.line} lineWidth={3}/></Node>);
  view.add(text('해설용 도식 · 실제 게임 화면',620,-365,27,D.muted));
  if(d.kind==='overview-ai') {
    add(0,text('AI와 함께 개발',490,-250,52,D.teal));
    add(0,text('Claude · 여러 에이전트',490,-170,39));
    add(1,text('어떤 재미를 만들었나?',490,5,47));
    arrow(1,[[490,-110],[490,-50]]);
    add(2,text('무엇을 썼고, 허락은?',490,205,47,D.title));
    arrow(2,[[490,65],[490,135]],D.title);
    add(2,text('제작 가능성과 공개 조건을 나누어 보기',0,315,44,D.title));
  } else if(d.kind==='ai-checklist') {
    add(0,text('코드 / 그림 / 음악',490,-245,51));
    add(1,text('각각의 출처와 사용 조건',490,-65,44,D.teal));
    arrow(1,[[490,-180],[490,-130]]);
    add(2,text('허락 · 필요한 표기 확인',490,115,44,D.title));
    arrow(2,[[490,0],[490,50]],D.title);
    add(2,text('불명확한 자산 → 대체하거나 권리자에게 확인',0,310,42,D.title));
  } else if(d.kind==='ai-questions') {
    add(0,text('공개하는 개발자',490,-255,51,D.teal));
    add(0,text('출처와 조건을 설명할 수 있나?',490,-145,39));
    add(1,<Line points={[[160,-25],[840,-25]]} stroke={D.line} lineWidth={4}/>);
    add(1,text('그림·음악을 만든 창작자',490,75,45,D.orange));
    add(2,text('어떤 이용 조건이라야 괜찮을까?',490,200,39));
    add(2,text('두 입장에서 공개 조건을 생각하기',0,315,45,D.title));
  } else {
    add(0,text('AI가 코드를 작성',490,-235,51,D.teal));
    add(1,text('그림 · 음악의 이용허락',490,5,46,D.orange));
    add(1,text('≠',490,-115,66,D.title));
    add(2,text('작동 확인 + 권리 확인',490,220,49,D.title));
    add(2,text('만들 수 있다 ≠ 공개해도 된다',0,320,51,D.title));
  }
  yield* t(d.duration,d.duration,linear);
}
