import {makeScene2D,Node,Rect,Txt} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {DARK as P} from '../../../styles/research-dark';
import {heading} from '../../game-lighting-history-shared/depth-space';
import {ddgiModel} from './ddgi-model-v1';
const titles=['표면에서 공간의 조사량을 질의','카메라와 프로브의 서로 다른 좌표','벽 너머 빛이 그대로 섞이는 문제','가림에 따라 기여를 줄여 비교','간격·저장·갱신의 교환','새 표본과 캐시의 시간 차이'];
const pairs=[[0,1],[2,3],[4,4],[4,5],[6,7],[8,9]];
export function ddgiProof(i:number){return makeScene2D(function*(view){
 const m=ddgiModel();view.fill(P.background);view.add(heading(`15a · 문단 ${i+1}`,titles[i],'프로브 · 가림 · 공간과 시간의 비교','게임 렌더링 역사 3편'));
 view.add(m.node);m.reset(m.poses[pairs[i][0]]);
 view.add(<Node y={430}><Rect x={12} y={12} width={1570} height={112} fill={'#073c32'}/><Rect width={1570} height={112} fill={'#fff'} stroke={'#111'} lineWidth={2}/><Txt text={titles[i]+'\n입체·계산·고정 자막 공간 검수'} fontFamily={P.font} fontSize={48} lineHeight={54} fill={'#111'} textAlign={'center'}/></Node>);
 yield*waitFor(.5);yield*m.transition(m.poses[pairs[i][1]],2);yield*waitFor(.5);
});}
