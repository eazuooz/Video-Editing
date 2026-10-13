import {Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
export default makeScene2D(function*(view){
 view.fill(P.background);const yaw=createSignal(26),phase=createSignal(0),move=createSignal(-230);
 // Adjacent sectors meet at X=-190. This is a discrete lookup, never an interpolated lamp value.
 const brightness=()=>move()<-190?96:160;
 const w=depthSpace(yaw,[-170,100],1.02);
 view.add(heading('03 · 1993','둠: 공간에 적어 둔 밝기 숫자','원본 코드의 sector light · 축 방향 보정 · scale별 색상표 조회','게임 렌더링의 역사'));
 for(const [x,color]of [[-350,'#aebbb7'],[-30,'#e1e5dc']]as const){view.add(w.box(x,0,0,320,310,15,color));view.add(w.box(x,-135,15,320,14,140,color));}
 // Two side-wall pieces leave a real doorway around the actor's Y=40 path.
 for(const y of [-117,117])view.add(w.box(-190,y,15,14,76,140,'#bec9c6'));
 view.add(w.box(120,0,15,14,310,140,'#e1e5dc'));
 view.add(w.label('구역 A: 96',-350,215,0,30));view.add(w.label('구역 B: 160',-30,215,0,30));
 view.add(w.actor(move,40,P.green,'●',15));
 view.add(<Txt x={480} y={-70} text={()=>`lightnum = (${brightness()} >> 4) + extra`} fontFamily={P.mono} fontSize={30} fill={P.ink}/>);
 view.add(<Txt x={480} y={10} text={()=>phase()<2?'색상표 인덱스로 밝기 변환':'축 방향 벽: 수평 −1 / 수직 +1'} fontFamily={P.font} fontSize={30} fill={P.blue}/>);
 view.add(<Txt x={480} y={100} text={()=>phase()<3?'구역을 바꾸면 기준 밝기도 바뀐다':'투영 scale → 별도 lookup · 범위 제한'} fontFamily={P.font} fontSize={29} fill={P.muted}/>);
 view.add(note(()=>['도식의 색은 색상표 선택 과정을 설명하며 원본 게임 픽셀이 아니다','구역 밝기와 거리·방향 보정을 한 값으로 혼동하지 않는다','원본 축 보정은 연속 Lambert 조명식과 다르다','광원까지의 가림을 추적하지 않으므로 정확한 물체 그림자는 별도 문제'][phase()]));
 const cues=['둠은 구역마다 정한 밝기에서\n화면의 색상표를 선택합니다.','다른 구역으로 이동하면\n그 구역의 기준 밝기를 읽습니다.','축 방향 벽에는 별도 보정을 주며\n연속적인 조명 각도 계산과는 다릅니다.','거리와 투영 크기의 조회도 있지만\n광원까지의 가림을 매번 계산하지는 않습니다.'];view.add(caption(()=>cues[phase()]));
 yield*waitFor(6);phase(1);yield*move(40,5,linear);yield*waitFor(1);phase(2);yield*yaw(34,5,linear);yield*waitFor(1);phase(3);yield*waitFor(6);
});
