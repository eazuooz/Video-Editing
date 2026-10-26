import {Img,Line, Node, Rect, Txt, View2D} from '@motion-canvas/2d';
import {createRef, waitFor} from '@motion-canvas/core';
import {DARK} from '../../../styles/research-dark';

export type CutsceneDiagram = 'overview' | 'formats' | 'fixedVideo' | 'quality' | 'storyFocus' | 'pacing' | 'viewingReward' | 'advance' | 'playbackControls' | 'skipScope' | 'wholeSkip' | 'skipChoice' | 'qte' | 'conclusion';
export interface CutsceneTiming {
  kind:CutsceneDiagram;title:string;duration:number;cues:number[];
  image?:string;focus?:[number,number,number,number];
  rewardOutside?:boolean;
}

export function* cutsceneDiagram(view:View2D,t:CutsceneTiming) {
  const root=createRef<Node>();
  view.add(<Node ref={root}>
    <Rect width={1920} height={1080} fill={DARK.background}/>
    <Txt text={t.title} y={-439} fontSize={58} fontWeight={700} fontFamily={DARK.font} fill={DARK.title}/>
    <Txt text="해설용 · 재생과 조작의 관계" x={590} y={-362} fontSize={30} fontFamily={DARK.font} fill={DARK.muted}/>
  </Node>);
  const stage=createRef<Node>();root().add(<Node ref={stage}/>);
  let clock=0;
  function* until(i:number) {const next=Math.min(t.duration,t.cues[i]??t.duration);yield* waitFor(Math.max(0,next-clock));clock=Math.max(clock,next);}
  const label=(text:string,x:number,y:number,color:string=DARK.ink,size=50)=><Txt text={text} x={x} y={y} fill={color} fontFamily={DARK.font} fontSize={size} fontWeight={600}/>;
  const arrow=(a:[number,number],b:[number,number],color:string=DARK.teal)=><Line points={[a,b]} stroke={color} lineWidth={10} endArrow arrowSize={22}/>;
  if(t.kind==='overview') {
    const ko=['화면의 품질','이야기와 휴식','재생 조절'];
    for(let i=0;i<3;i++) {
      if(i)yield* until(i);
      stage().add(label(ko[i],-570+i*570,-50,i===2?DARK.green:DARK.ink,56));
      if(i)stage().add(arrow([-570+(i-1)*570+210,-50],[-570+i*570-220,-50]));
    }
    stage().add(label('플레이와 이어지는 컷신',0,220,DARK.title,58));
  } else if(t.kind==='storyFocus') {
    if(!t.image||!t.focus)throw new Error('An inspected screenshot and normalized visible face bounds are required.');
    const [x,y,w,h]=t.focus;
    if(x<0||y<0||w<=0||h<=0||x+w>1||y+h>1)throw new Error('Focus must be inside the source screenshot.');
    stage().add(<Img src={t.image} x={-250} y={-20} width={1100} height={618.75}/>);
    yield* until(1);
    stage().add(<Rect x={-250+(x+w/2-.5)*1100} y={-20+(y+h/2-.5)*618.75} width={w*1100} height={h*618.75} stroke={DARK.teal} lineWidth={8}/>);
    stage().add(label('표정과 시선',650,-170,DARK.teal,50));
    yield* until(2);
    stage().add(label('장면의 의미',650,-35,DARK.ink,50));
    stage().add(arrow([650,25],[650,110]));
    stage().add(label('다음 행동의 마음',650,185,DARK.green,43));
  } else if(t.kind==='fixedVideo'||t.kind==='formats'||t.kind==='quality') {
    const leftColumn=createRef<Node>();const rightColumn=createRef<Node>();
    stage().add(<Node ref={leftColumn} opacity={t.kind==='formats'?0:1}>
      {label('실시간 컷신',-490,-245,DARK.teal,54)}
      {label('Real-time cutscene',-490,-180,DARK.muted,34)}
      {label('실행 중에 새 그림을 만듦',-490,-95,DARK.ink,43)}
    </Node>);
    stage().add(<Node ref={rightColumn} opacity={t.kind==='formats'?0:1}>
      {label('프리렌더링 영상',490,-245,DARK.title,54)}
      {label('Pre-rendered video',490,-180,DARK.muted,34)}
      {label('저장된 그림을 순서대로 재생',490,-95,DARK.ink,43)}
    </Node>);
    if(t.kind==='fixedVideo') {
      yield* until(0);
      stage().add(label('Frame rate · 프레임 레이트',0,-325,DARK.title,42));
      stage().add(label('일 초에 보여주는 그림 수',0,-15,DARK.ink,44));
      yield* until(1);
      stage().add(label('초당 60장',-490,65,DARK.teal,62));
      stage().add(label('초당 30장',490,65,DARK.title,62));
      stage().add(label('가상의 비교 예시 · 실제 게임 성능 측정값 아님',0,285,DARK.muted,36));
      const left=createRef<Rect>();const right=createRef<Rect>();
      stage().add(<Rect ref={left} x={-490} y={175} width={0} height={55} fill={DARK.teal}/>);
      stage().add(<Rect ref={right} x={340} y={175} width={0} height={55} fill={DARK.title}/>);
      yield* left().width(600,.4);yield* right().width(300,.4);clock+=.8;
    } else if(t.kind==='quality') {
      yield* until(1);
      stage().add(label('발전하는 실시간 표현',-490,90,DARK.teal,48));
      stage().add(label('저장 당시의 해상도·프레임 레이트',490,90,DARK.title,39));
      stage().add(label('저장 영상이 덜 선명하거나 덜 부드러울 수도 있음',0,280,DARK.ink,43));
    } else {
      yield* until(0);
      yield* leftColumn().opacity(1,.2);clock+=.2;
      yield* until(1);
      yield* rightColumn().opacity(1,.2);clock+=.2;
      yield* until(2);
      stage().add(label('연출을 보여주는 두 제작 방식',0,200,DARK.ink,50));
    }
  } else if(t.kind==='pacing') {
    stage().add(label('다음 행동을 준비하는 틈',0,-245,DARK.title,56));
    stage().add(label('전투',-650,-60,DARK.orange,54));
    stage().add(arrow([-510,-60],[-260,-60]));
    stage().add(label('컷신을 본다',0,-60,DARK.teal,50));
    stage().add(arrow([230,-60],[500,-60]));
    stage().add(label('다음 전투',670,-60,DARK.orange,50));
    yield* until(1);
    stage().add(label('직접 걸으며 쉰다',0,160,DARK.green,50));
    stage().add(<Line points={[[-510,-40],[-400,160],[-275,160]]} stroke={DARK.green} lineWidth={8} endArrow arrowSize={20}/>);
    stage().add(<Line points={[[280,160],[420,160],[510,-40]]} stroke={DARK.green} lineWidth={8} endArrow arrowSize={20}/>);
    stage().add(label('위협이 없는 구간도 같은 휴식을 만들 수 있습니다',0,315,DARK.muted,38));
  } else if(t.kind==='viewingReward') {
    const words=['직접 돌파한 과정','새로 열리는 장면','이야기의 보상'];
    words.forEach((s,i)=>{stage().add(label(s,-560+i*560,-85,i===2?DARK.title:DARK.ink,47));if(i)stage().add(arrow([-560+(i-1)*560+225,-85],[-560+i*560-230,-85]));});
    if(t.rewardOutside) {
      yield* until(0);
      stage().add(label('장면만 따로 볼 수 있는 환경',0,160,DARK.teal,52));
      yield* until(1);
      stage().add(label('장면만 여는 보상의 힘이 약해짐',0,300,DARK.ink,44));
    } else {
      yield* until(1);
      stage().add(label('게임 안에서 겪은 과정과 결과의 연결',0,230,DARK.ink,44));
    }
  } else if(t.kind==='advance') {
    stage().add(label('한 대사씩 진행',-500,-255,DARK.teal,54));
    stage().add(label('연속 장면의 재생',490,-255,DARK.title,54));
    const active=createRef<Rect>();
    stage().add(<Rect ref={active} x={-500} y={-120} width={650} height={100} stroke={DARK.teal} lineWidth={6}/>);
    ['첫 대사','다음 대사','그다음 대사'].forEach((s,i)=>stage().add(label(s,-500,-120+i*125,DARK.ink,46)));
    stage().add(<Line points={[[150,-100],[825,-100]]} stroke={DARK.line} lineWidth={12}/>);
    stage().add(label('현재',185,-170,DARK.title,40));
    stage().add(label('다음 구간',715,-170,DARK.title,40));
    yield* until(1);
    stage().add(arrow([200,-100],[710,-100],DARK.title));
    stage().add(label('부분 건너뛰기 / 빠르게 재생',490,110,DARK.ink,43));
    const moviePosition=createRef<Rect>();
    stage().add(<Rect ref={moviePosition} x={185} y={-100} width={14} height={62} fill={DARK.title}/>);
    yield* moviePosition().x(710,.3);clock+=.3;
    yield* until(2);
    stage().add(label('전체 건너뛰기와는 다른 조절 단위',0,315,DARK.muted,38));
  } else if(t.kind==='playbackControls') {
    stage().add(label('재생 속도를 조절',-480,-190,DARK.teal,54));
    stage().add(<Line points={[[-800,0],[-120,0]]} stroke={DARK.line} lineWidth={10}/>);
    const marker=createRef<Rect>();
    stage().add(<Rect ref={marker} x={-780} y={0} width={18} height={70} fill={DARK.teal}/>);
    yield* marker().x(-500,.8);clock+=.8;
    yield* until(1);
    yield* marker().x(-150,.35);clock+=.35;
    stage().add(label('원하는 구간으로 이동',460,-190,DARK.title,54));
    stage().add(<Line points={[[130,0],[800,0]]} stroke={DARK.line} lineWidth={10}/>);
    stage().add(arrow([220,0],[660,0],DARK.title));
    stage().add(label('시청 방식에 맞는 재생 설계',0,240,DARK.ink,54));
  } else if(t.kind==='skipScope') {
    stage().add(label('컷신',-470,-140,DARK.teal,60));
    yield* until(1);
    stage().add(label('전체 건너뛰기',0,180,DARK.green,60));
    stage().add(arrow([-470,-60],[-120,110],DARK.teal));
    yield* until(2);
    stage().add(label('스태프 크레디트',460,-140,DARK.title,56));
    stage().add(arrow([460,-60],[120,110],DARK.title));
  } else if(t.kind==='wholeSkip') {
    stage().add(label('처음 만든 저장 데이터',-485,-195,DARK.teal,51));
    stage().add(label('이미 본 사람',485,-195,DARK.title,51));
    stage().add(label('데이터의 상태',-485,-80,DARK.muted,40));
    stage().add(label('사람의 시청 경험',485,-80,DARK.muted,40));
    yield* until(1);
    stage().add(<Line points={[[-485,0],[-485,105],[485,105],[485,0]]} stroke={DARK.line} lineWidth={7}/>);
    stage().add(arrow([0,105],[0,185]));
    stage().add(label('볼지, 건너뛸지 선택',0,255,DARK.green,58));
    yield* until(2);
    stage().add(label('컷신과 스태프 크레디트 모두',0,315,DARK.muted,38));
  } else if(t.kind==='skipChoice') {
    stage().add(label('보기와 다음 플레이를 선택',0,-260,DARK.title,50));
    stage().add(label('계속 보기',-520,-70,DARK.teal,56));
    stage().add(label('건너뛰기',520,-70,DARK.green,56));
    stage().add(arrow([-520,0],[-520,150],DARK.teal));
    stage().add(label('장면을 계속 본다',-520,220,DARK.ink,48));
    yield* until(1);
    stage().add(arrow([520,0],[520,100],DARK.green));
    stage().add(label('필요하면 확인 입력',520,160,DARK.title,45));
    stage().add(label('다음 플레이로',520,285,DARK.green,48));
  } else if(t.kind==='qte') {
    stage().add(label('Quick Time Event · QTE',0,-250,DARK.title,58));
    stage().add(label('연출 도중, 짧은 시간 안에 정해진 입력',0,-140,DARK.ink,48));
    stage().add(<Line points={[[-720,90],[720,90]]} stroke={DARK.line} lineWidth={10}/>);
    const playhead=createRef<Rect>();
    stage().add(<Rect ref={playhead} x={-720} y={90} width={18} height={68} fill={DARK.title}/>);
    stage().add(label('장면을 보는 중',-500,0,DARK.muted,44));
    yield* until(1);
    stage().add(<Rect x={185} y={90} width={330} height={110} stroke={DARK.orange} lineWidth={7}/>);
    stage().add(label('입력 기회',185,-5,DARK.orange,48));
    stage().add(label('알림',10,215,DARK.orange,42));
    stage().add(label('입력 마감',355,215,DARK.orange,42));
    yield* playhead().x(185,.65);clock+=.65;
    yield* until(2);
    yield* playhead().fill(DARK.orange,.15);clock+=.15;
    stage().add(label('보는 상태에서 반응하는 상태로 전환',0,315,DARK.ink,44));
  } else {
    stage().add(label('장면이 전할 감정과 정보',0,-190,DARK.title,58));
    stage().add(arrow([0,-115],[0,-5]));
    stage().add(label('플레이어가 조절할 재생',0,65,DARK.teal,58));
    yield* until(1);
    stage().add(arrow([0,135],[0,225]));
    stage().add(label('다음 행동으로 자연스럽게',0,285,DARK.green,56));
  }
  yield* waitFor(Math.max(0,t.duration-clock));root().remove();
}
