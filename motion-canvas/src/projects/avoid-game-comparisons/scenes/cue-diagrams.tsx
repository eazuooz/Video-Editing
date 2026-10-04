import {Line,Node,Rect,Txt,View2D} from '@motion-canvas/2d';
import {all,createRef,easeInOutCubic,usePlayback} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
const content:Record<string,[string,string,string,string]>={
  '06-2':['같은 이동이라는 말에 숨은 차이','곡선을 따라 이동','얼음길에서 이동','공간과 동사를 함께 적습니다.'],
  '06-4':['보인 진입과 확인하지 못한 조건','인쇄면으로 진입','시간 · 연료 조건?','짧은 시연에서 확인한 범위만 설명합니다.'],
  '10-2':['서로 다른 컷을 연속 추격으로 묶지 않기','평평한 물 위','파도 위로 떠오름','컷 사이의 인과관계는 따로 확인합니다.'],
  '10-4':['도움 기능 시연의 문맥을 보존','무적 · 한방처치 ON','기본 난이도?','이 설정을 게임 전체의 기본 규칙으로 옮기지 않습니다.'],
  '12-2':['보인 장치와 아직 확인하지 못한 조건','장치에 들어감','비용 · 승리 조건?','보인 행동과 미확인 조건을 구별합니다.'],
  '15-3':['움직임과 대상을 함께 말하기','공간 + 움직임','향하는 대상','동사 하나에 빠져 있던 정보를 덧붙입니다.'],
};
function card(x:number,title:string,color:string){return <Node x={x}>
  <Rect x={16} y={20} width={710} height={180} fill={'#e1e7eb'}/>
  <Line points={[[-355,-90],[-343,-102],[367,-102],[367,78],[355,90]]} fill={'#d8e2ec'} stroke={P.line} lineWidth={1}/>
  <Rect width={710} height={180} fill={'white'} stroke={color} lineWidth={2}/>
  <Txt text={title} fontFamily={P.font} fontSize={35} fontWeight={700} fill={color}/>
</Node>;}
// Short cue diagrams have two readable cards, distinct from the preserved
// multi-paragraph explanations. Final timing and pixels must be approved.
export function* cueDiagram(view:View2D,id:string,duration:number){
  const c=content[id];if(!c||duration<2)throw Error(`Cue${id}: meaningful diagram timing required`);
  view.fill(P.background);const cards=createRef<Node>();
  view.add(<>
    <Txt text={c[0]} x={-850} y={-385} offset={[-1,0]} fontFamily={P.font} fontSize={44} fontWeight={700} fill={P.ink}/>
    <Node ref={cards} y={25} opacity={0}>{card(-435,c[1],P.blue)}{card(435,c[2],P.green)}
      <Line points={[[-55,0],[55,0]]} stroke={P.blue} lineWidth={4} endArrow arrowSize={16}/>
    </Node>
    <Txt text={c[3]} y={225} fontFamily={P.font} fontSize={30} fill={P.muted}/>
  </>);
  const playback=usePlayback(),start=playback.frame;
  yield*all(cards().opacity(1,.3),cards().y(0,.3,easeInOutCubic));
  while(playback.frame-start<Math.round(duration*playback.fps))yield;
}
