import {Circle,Txt,makeScene2D} from '@motion-canvas/2d';
import {all,createSignal,linear,waitFor} from '@motion-canvas/core';
import {PAPER as P} from '../../../styles/research-paper';
import {depthSpace,heading} from '../../../shared/depth-diagrams';
import {caption,note} from './common';
export default makeScene2D(function*(view){
 view.fill(P.background);const yaw=createSignal(24),phase=createSignal(0),lamp=createSignal(-200),write=createSignal(0),flow=createSignal(0);
 const w=depthSpace(yaw,[0,45],1.1);
 view.add(heading('24 · 1편의 답','저장한 것, 다시 계산할 것, 모르는 것','방법의 이름보다 데이터와 갱신 조건으로 읽기','게임 렌더링의 역사'));
 view.add(w.box(-410,0,0,280,280,15,'#e5eaf1'));
 view.add(w.box(-410,0,15,100,90,115,'#7791b5'));
 view.add(<Circle position={()=>w.point(lamp(),-120,180)} size={35} fill={P.yellow}/>);
 view.add(w.path(()=>[[lamp(),-120,180],[-410,45,17]],P.yellow));
 view.add(w.box(0,0,0,250,280,15,'#f3df9b'));
 view.add(w.path(()=>[[-250,0,90],[-150,0,90]],P.blue,write));
 for(let i=0;i<12;i++){const cell=w.box(-80+i%3*80,-100+Math.floor(i/3)*65,15,72,56,6,i%4===0?'#acb6b0':'#f3e7b6');cell.opacity(write);view.add(cell);}
 view.add(w.box(420,0,0,280,280,15,'#d3e5d9'));
 view.add(w.path(()=>[[150,0,90],[270,0,90]],P.green,flow));
 for(const [x,label]of [[-410,'표면과 가림'],[0,'저장 데이터'],[420,'평가·갱신 조건']]as const)view.add(w.label(label,x,210,0,28));
 view.add(note(()=>['구역 밝기 → 표면 라이트맵 → 동적 그림자 → 재질과 조명의 계산 순서','정적 결과는 실행 비용을 줄이지만 변경 상태가 입력에 없을 수 있다','다음 편: 반사 · 간접광 · 물과 안개 · 많은 광원의 선택','약20분 단위로 완결된 질문과 사례를 이어 간다'][phase()]));
 const cues=['밝기를 정하고, 계산 결과를 저장하고\n움직이는 빛의 가림을 다시 검사했습니다.','무엇을 저장하고 언제 갱신하는지\n입력에 없는 정보는 무엇인지 확인하세요.','다음 편은 반사와 간접광, 물과 안개\n포워드 플러스와 클러스터드로 이어집니다.','직접 구현하며 익히고 싶다면\n설명란의 프로그래밍 코칭 링크도 확인하세요.'];view.add(caption(()=>cues[phase()]));
 yield*write(1,5,linear);yield*waitFor(1);phase(1);yield*lamp(-20,5,linear);yield*waitFor(1);phase(2);yield*flow(1,5,linear);yield*waitFor(1);phase(3);yield*yaw(32,4,linear);yield*waitFor(2);
});
