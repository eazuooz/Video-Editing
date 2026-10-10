import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {bvhModel} from './bvh-model-v1';
const headings=['레이의 점과 경계 상자','부모 상자에서 하위 가지 생략','세 축 구간을 공통 t로 비교','[4,5]에서 겹침 없음으로','상자 통과와 삼각형 교차 분리','가장 가까운 표면과 불투명 가림','성긴 상자의 불필요한 후보','교차·셰이딩·갱신의 서로 다른 비용'];
const pairs=[[0,1],[1,2],[1,3],[4,5],[1,6],[1,7],[1,8],[1,9]];
export function bvhProof(i:number){return makeScene2D(function*(view){
 const m=bvhModel();view.fill(P.background);view.add(heading(`13a · 문단 ${i+1}`,headings[i],'원래 전체 내레이션은 보존 · 독립 도식 동작 검수','게임 렌더링 역사 3편'));
 m.node.y(15);view.add(m.node);m.reset(m.poses[pairs[i][0]]);
 view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#ffffff'} stroke={'#111111'} lineWidth={2}/><Txt text={headings[i]+'\n입체·계산·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111111'} textAlign={'center'}/></Node>);
 yield*waitFor(.5);yield*m.transition(m.poses[pairs[i][1]],2);yield*waitFor(.5);
});}
