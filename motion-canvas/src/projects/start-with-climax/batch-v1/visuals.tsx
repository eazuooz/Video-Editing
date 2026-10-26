import {Img, Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {createRef, easeInOutCubic, waitFor} from '@motion-canvas/core';
import {DARK} from '../../../styles/research-dark';

export type OpeningDiagram = 'overview' | 'informationOrder' | 'control' | 'earlyPeak' | 'quietPlay' | 'firstAct' | 'evidenceSelection' | 'ruleUse';
export interface OpeningTiming {
  kind: OpeningDiagram;
  title: string;
  duration: number;
  cues: number[];
  images?: {before:string;after:string;aspect?:number};
  image?: string;
  orderState?: 'setup' | 'reordered';
  showFallback?: boolean;
}

// All marks are authored relationships, not measured player-retention data.
// World action stays in independent gameplay. These diagrams explain its order.
export function* openingDiagram(view: View2D, t: OpeningTiming) {
  const root = createRef<Node>();
  view.add(<Node ref={root}>
    <Rect width={1920} height={1080} fill={DARK.background}/>
    <Txt text={t.title} x={-16} y={-439} fontFamily={DARK.font} fontSize={58} fontWeight={700} fill={DARK.title}/>
    <Txt text="해설용 · 정보와 조작의 순서" x={590} y={-362} fontFamily={DARK.font} fontSize={30} fill={DARK.muted}/>
  </Node>);
  const stage = createRef<Node>();
  root().add(<Node ref={stage}/>);
  const cue = (i: number) => Math.max(0, Math.min(t.duration, t.cues[i] ?? t.duration));
  let clock = 0;
  function* until(i: number) { const next = cue(i); yield* waitFor(Math.max(0, next - clock)); clock = Math.max(clock, next); }
  const label = (text: string, x: number, y: number, color: string = DARK.ink, size = 50) =>
    <Txt text={text} x={x} y={y} fill={color} fontFamily={DARK.font} fontSize={size} fontWeight={600}/>;
  const line = (a: [number, number], b: [number, number], color: string = DARK.teal) =>
    <Line points={[a,b]} stroke={color} lineWidth={10} endArrow arrowSize={22}/>;

  if(t.kind==='overview') {
    stage().add(label('시작부터 빠져드는 이유',0,-250,DARK.title,56));
    const words=['첫 전투','거대한 적','첫 재판'];
    for(let i=0;i<words.length;i++) {
      yield* until(i);
      stage().add(label(words[i],-570+i*570,-60,i===2?DARK.green:DARK.ink,56));
      if(i)stage().add(line([-570+(i-1)*570+210,-60],[-570+i*570-210,-60]));
    }
    yield* until(3);
    stage().add(label('핵심 재미를 먼저 경험합니다',0,220,DARK.title,56));
  } else if(t.kind==='evidenceSelection'||t.kind==='ruleUse') {
    if(!t.images?.before||!t.images?.after) throw new Error('Inspected native before/after screenshots are required.');
    const isEvidence=t.kind==='evidenceSelection';
    const imageHeight=760/(t.images.aspect??(16/9));
    stage().add(label(isEvidence?'변호사 배지':'스핀 전',-470,-290,DARK.teal,50));
    stage().add(<Img src={t.images.before} x={-470} y={-20} width={760} height={imageHeight}/>);
    yield* until(1);
    stage().add(label(isEvidence?'조각상':'스핀 후',470,-290,DARK.green,50));
    const after=createRef<Node>();
    stage().add(<Node ref={after} opacity={0}>
      <Img src={t.images.after} x={470} y={-20} width={760} height={imageHeight}/>
      {line([-65,-20],[65,-20])}
    </Node>);
    yield* after().opacity(1,.24);clock+=.24;
    yield* until(2);
    stage().add(label(isEvidence?'선택을 바꾸면':'새로 배운 규칙을 쓰면',0,235,DARK.ink,46));
    stage().add(label(isEvidence?'제시할 증거도 바뀝니다':'크리스털이 깨집니다',0,310,DARK.green,48));
  } else if (t.kind === 'informationOrder') {
    stage().add(label('사건이 생긴 순서', -555,-250,DARK.muted,42));
    const nouns = ['관계와 배경','사건 발생','직접 행동'];
    const xs = [-550,0,550];
    nouns.forEach((text,i) => stage().add(label(text,xs[i],-120)));
    stage().add(line([-360,-120],[-210,-120],DARK.line));
    stage().add(line([210,-120],[355,-120],DARK.line));
    yield* until(1);
    stage().add(label('플레이어가 만나는 순서',-485,55,DARK.title,42));
    const reveal = createRef<Node>();
    stage().add(<Node ref={reveal} opacity={0}>
      {label('사건 속에서 행동',-535,185,DARK.green,50)}
      {line([-270,185],[-145,185])}
      {label('왜 이런 일이?',40,185,DARK.ink,48)}
      {line([260,185],[365,185])}
      {label('배경을 알아감',585,185,DARK.teal,48)}
    </Node>);
    yield* reveal().opacity(1,.3); clock += .3;
  } else if (t.kind === 'control') {
    if(!t.image) throw new Error('The inspected opening-action screenshot is required beside the control flow.');
    stage().add(label('DOOM · 첫 전투',-470,-310,DARK.teal,46));
    stage().add(<Img src={t.image} x={-470} y={-15} width={900} height={506.25}/>);
    const items = ['조작을 해본다','화면이 반응한다','할 일을 이해한다'];
    const colors = [DARK.teal,DARK.green,DARK.title];
    for (let i=0;i<3;i++) {
      if(i) yield* until(i);
      const n=createRef<Node>();
      stage().add(<Node ref={n} opacity={0} x={470} y={-180+i*175}>
        <Rect width={740} height={110} radius={0} stroke={colors[i]} lineWidth={7}/>
        {label(items[i],0,0,colors[i],48)}
      </Node>);
      if(i) stage().add(line([470,-180+(i-1)*175+65],[470,-180+i*175-65],colors[i]));
      yield* n().opacity(1,.24); clock += .24;
    }
  } else if (t.kind === 'earlyPeak') {
    stage().add(<Line points={[[-750,230],[750,230]]} stroke={DARK.muted} lineWidth={6} endArrow arrowSize={18}/>);
    stage().add(<Line points={[[-750,230],[-750,-260]]} stroke={DARK.muted} lineWidth={6} endArrow arrowSize={18}/>);
    stage().add(label('시작',-710,275,DARK.muted,42));
    stage().add(label('진행',700,275,DARK.muted,42));
    stage().add(label('관심과 긴장',-620,-310,DARK.muted,38));
    stage().add(label('이야기 배치 예시',350,-290,DARK.muted,38));
    const curve = createRef<Line>();
    stage().add(<Line ref={curve} points={[[-700,200],[-480,150],[-220,130],[0,-50],[220,30],[450,-160],[700,-230]]}
      stroke={DARK.teal} lineWidth={12} end={0}/>);
    yield* curve().end(1,.8); clock += .8;
    yield* until(1);
    yield* curve().points([[-700,190],[-550,-145],[-330,80],[-80,115],[200,-20],[440,-150],[700,-230]],.7,easeInOutCubic); clock += .7;
    stage().add(<Line points={[[-550,-145],[-550,230]]} stroke={DARK.title} lineWidth={5} lineDash={[14,14]}/>);
    stage().add(label('도입의 작은 절정',-385,-230,DARK.title,48));
    yield* until(2);
    stage().add(label(t.showFallback?'큰 사건이 어렵다면, 조작까지의 길을 짧게':'핵심 재미를 먼저 경험합니다',0,315,DARK.ink,t.showFallback?38:48));
  } else if (t.kind === 'quietPlay') {
    stage().add(label('같은 조용한 일상',0,-240,DARK.title,54));
    stage().add(label('설명이 끝나길 기다림',-450,-70,DARK.muted,48));
    yield* until(1);
    stage().add(label('걸어보고 · 만져보고 · 고름',430,-70,DARK.green,48));
    stage().add(line([-450,10],[-450,150],DARK.line));
    stage().add(line([430,10],[430,150],DARK.green));
    stage().add(label('보는 시간',-450,220,DARK.muted,48));
    stage().add(label('경험하는 시간',430,220,DARK.green,48));
  } else {
    if(!t.image) throw new Error('The inspected first-trial evidence screenshot is required beside the role flow.');
    stage().add(label('첫 재판 · 증거 목록',-470,-310,DARK.teal,46));
    stage().add(<Img src={t.image} x={-470} y={-15} width={900} height={506.25}/>);
    stage().add(label('게임을 대표하는 첫 행동',470,-310,DARK.title,46));
    const tasks=['할 일을 만난다','필요한 규칙을 안다','스스로 해본다'];
    for(let i=0;i<tasks.length;i++) {
      if(i) yield* until(i);
      stage().add(label(tasks[i],470,-180+i*175,i===2?DARK.green:DARK.ink,50));
      if(i) stage().add(line([470,-180+(i-1)*175+55],[470,-180+i*175-55],DARK.line));
    }
  }
  yield* waitFor(Math.max(0,t.duration-clock));
  root().remove();
}
